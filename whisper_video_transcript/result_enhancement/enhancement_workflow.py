import logging
import math
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
os.environ["IMAGEMAGICK_BINARY"] = "/opt/homebrew/bin/convert"

from faster_whisper import WhisperModel
from moviepy.editor import TextClip, VideoFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import numpy as np
import pandas as pd
import pickle

from whisper_video_transcript.transcribe.openai_whisper_transcription import OpenAIWhisperTranscription

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

from whisper_video_transcript.result_enhancement.utils import (
    top_consecutive_occurrences,
    extract_mp4_clips,
    update_timestamp_enhance_result,
    drop_enhancement_original_index,
    delete_working_files,
)


class EnhancementWorkflow:
    def __init__(
        self,
        result_dict = None,
        enhanced_dict = None
    ):
        self.input_dict = result_dict if result_dict is not None else enhanced_dict

    def create_index_dict_consecutive_occurrences(self, video, result_text = None, threshold=5):
        index_dict = top_consecutive_occurrences(result_text if result_text is not None else self.input_dict[video]['text'], threshold)
        return index_dict
    
    def extract_mp4_clips(self, video, index_dict):
        enhance_video_list = extract_mp4_clips(video, index_dict, self.input_dict[video])
        self.enhance_video_list = enhance_video_list
        return self.enhance_video_list
    
    def init_whisper_transcription(self, video_list):
        whisper_transcription = OpenAIWhisperTranscription(enhance_video_list=video_list)
        return whisper_transcription
    
    def enhance_transcribe_to_df(self, whisper_transcription):
        enhance_result_dict = whisper_transcription.openai_transcribe_to_df(enhance=True)
        return enhance_result_dict

    def create_final_result_dict(self, enhance_result_dict, index_dict, result_df):
        updated_timestamp_enhance_result_dict = update_timestamp_enhance_result(enhance_result_dict, index_dict, result_df)
        dropped_result_df = drop_enhancement_original_index(index_dict, result_df)
        enhance_video_df = [value for _, value in updated_timestamp_enhance_result_dict.items()]
        final_result_list = [dropped_result_df] + enhance_video_df
        final_result_df = pd.concat(final_result_list).sort_values(by='start').reset_index(drop=True)
        return final_result_df
    
    def create_enhanced_subs_dict(self, final_result_df):
        subs = []
        for _, row in final_result_df.iterrows():
            start = row["start"]
            end = row["end"]
            text = row["text"]
            subs.append(((start, end), text))
        return subs
    
    def add_enhanced_subs_to_video(
        self,
        whisper_transcription,
        video_file_path: str,
        subs: list,
        font: str = "arial-bold",
        fontsize: int = 40,
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: float = 3,
        size: tuple = (1100, 720),
        method: str = "caption",
        align: str = "South"
    ):
        generator = lambda txt: TextClip(txt, font=font, fontsize=fontsize, color=color, stroke_color=stroke_color, stroke_width=stroke_width, size=whisper_transcription.size, method=method, align=align)

        subtitles = SubtitlesClip(subs, generator)
        video = VideoFileClip(video_file_path)
        result = CompositeVideoClip(
            [video, subtitles.set_pos(("center", "bottom"))]
        )
        output_video_file_name = video_file_path[:-4]
        result.write_videofile(
            f"{output_video_file_name}_output.mp4",
            fps=video.fps,
            temp_audiofile=f"temp-audio.m4a",
            remove_temp=True,
            codec="libx264",
            audio_codec="aac",
        )

    def delete_index_dict_mp4(self, video_list):
        delete_working_files(video_list)

    def consecutive_text_workflow(self, consecutive_text_threshold=4, process=False, output=False):
        
        for video in self.input_dict:
            index_dict = self.create_index_dict_consecutive_occurrences(video, threshold=consecutive_text_threshold)

            if index_dict:
                print(video, index_dict)
                if process:
                    final_result_df = self._generic_workflow(video, index_dict, output)
                    self.input_dict[video] = final_result_df
                    new_index_dict = self.create_index_dict_consecutive_occurrences(video=video, result_text=final_result_df['text'], threshold=consecutive_text_threshold)
                    print(video, new_index_dict)
                    self.delete_index_dict_mp4(self.enhance_video_list)
                else:
                    print("Enhancements for consecutive texts not processed.")
                
            else:
                print("No consecutive texts are found.")
                if output:
                    subs = self.create_enhanced_subs_dict(self.input_dict[video])
                    whisper_transcription_enhance = self.init_whisper_transcription([])
                    self.add_enhanced_subs_to_video(whisper_transcription_enhance, video, subs)
            
        return self.input_dict

    def duration_workflow(self, duration_threshold=10, process=False, output=False):
        for video in self.input_dict:
            final_result_df = self.input_dict[video]
            final_result_df['duration'] = final_result_df['end']  - final_result_df['start']
            final_result_df_longer_than_duration = final_result_df[final_result_df['duration'] >= duration_threshold]
            print(final_result_df_longer_than_duration)

            if not final_result_df_longer_than_duration.empty:
                if process:
                    index_dict = {}

                    for index, row in final_result_df_longer_than_duration.iterrows():
                        current_value = index
                        index_dict.setdefault(current_value, {'index_range': None})
                        index_dict[current_value]['index_range'] = [index, index]
                        index_dict[current_value]['cleaned_key'] = f"duration_{index}"

                    new_final_results_df = self._generic_workflow(video, index_dict, output)

                    self.input_dict[video] = new_final_results_df
                    new_final_results_df['duration'] = new_final_results_df['end']  - new_final_results_df['start']
                    new_final_result_df_longer_than_duration = new_final_results_df[new_final_results_df['duration'] >= duration_threshold]

                    print(new_final_result_df_longer_than_duration)
                    
                    self.delete_index_dict_mp4(self.enhance_video_list)
                else:
                    print("Enhancements for duration not processed.")
            else:
                print(f"No durations longer than {duration_threshold} seconds are found.")
                if output:
                    subs = self.create_enhanced_subs_dict(self.input_dict[video])
                    whisper_transcription_enhance = self.init_whisper_transcription([video])
                    self.add_enhanced_subs_to_video(whisper_transcription_enhance, video, subs)

    def numeric_workflow(self, process=False, output=False):
        
        for video in self.input_dict:
            final_result_df = self.input_dict[video]
            final_result_df['is_numeric'] = pd.to_numeric(final_result_df['text'], errors='coerce')
            final_result_df['is_numeric'] = np.where(final_result_df['is_numeric'].isna(), 0, 1)
            grouped_indices = final_result_df[final_result_df['is_numeric'] == 1].index
            consecutive_groups = np.split(grouped_indices, np.where(np.diff(grouped_indices) != 1)[0] + 1)

            index_dict = {}

            if list(consecutive_groups[0]):
                for i in consecutive_groups:
                    index_dict.setdefault(i[0], {'index_range': None})
                    index_dict[i[0]]['index_range'] = [i[0], i[-1]]
                    index_dict[i[0]]['cleaned_key'] = f"numeric_{i[0]}"

            if index_dict:
                if process:
                    print(video, index_dict)

                    new_final_results_df = self._generic_workflow(video, index_dict, output)

                    self.input_dict[video] = new_final_results_df
                    
                    new_final_results_df['is_numeric'] = pd.to_numeric(new_final_results_df['text'], errors='coerce')
                    new_final_results_df['is_numeric'] = np.where(new_final_results_df['is_numeric'].isna(), 0, 1)
                    new_grouped_indices = new_final_results_df[new_final_results_df['is_numeric'] == 1].index
                    new_consecutive_groups = np.split(new_grouped_indices, np.where(np.diff(new_grouped_indices) != 1)[0] + 1)

                    new_index_dict = {}

                    if list(new_consecutive_groups[0]):
                        for i in new_consecutive_groups:
                            new_index_dict.setdefault(i[0], {'index_range': None})
                            new_index_dict[i[0]]['index_range'] = [i[0], i[-1]]
                            new_index_dict[i[0]]['cleaned_key'] = f"numeric_{i[0]}"

                    print(video, new_index_dict)
                    
                    self.delete_index_dict_mp4(self.enhance_video_list)
                else:
                    print("Enhancements for numeric not processed.")
            else:
                print(f"No numeric are found.")
                if output:
                    subs = self.create_enhanced_subs_dict(self.input_dict[video])
                    whisper_transcription_enhance = self.init_whisper_transcription([video])
                    self.add_enhanced_subs_to_video(whisper_transcription_enhance, video, subs)

        return self.input_dict

    def _generic_workflow(self, video, index_dict, output):

        enhance_video_list = self.extract_mp4_clips(video, index_dict)
        whisper_transcription_enhance = self.init_whisper_transcription(enhance_video_list)
        enhance_result_dict = self.enhance_transcribe_to_df(whisper_transcription_enhance)
        final_result_df = self.create_final_result_dict(enhance_result_dict, index_dict, self.input_dict[video])
        subs = self.create_enhanced_subs_dict(final_result_df)
        if output:
            self.add_enhanced_subs_to_video(whisper_transcription_enhance, video, subs)
        return final_result_df
