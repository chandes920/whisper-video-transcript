import logging
import math
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
os.environ["IMAGEMAGICK_BINARY"] = "/opt/homebrew/bin/convert"

from faster_whisper import WhisperModel
from moviepy.editor import TextClip, VideoFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import pandas as pd
import pickle

from transcribe import OpenAIWhisperTranscription

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

from result_enhancement_utils import (
    top_consecutive_occurrences,
    extract_mp4_each_consecutive_text,
    update_timestamp_enhance_result,
    drop_enhancement_original_index
)


class ResultEnhancement:
    def __init__(
        self,
        result_dict
    ):
        self.result_dict = result_dict

    def create_count_dict_consecutive_occurrences(self, threshold=5):
        count_dict = top_consecutive_occurrences(self.result_dict['text'], threshold)
        return count_dict
    
    def extract_mp4_each_consecutive_text(self, video_file_path, count_dict):
        enhance_video_list = extract_mp4_each_consecutive_text(video_file_path, count_dict, self.result_dict)
        self.enhance_video_list = enhance_video_list
        return self.enhance_video_list
    
    def init_whisper_transcription(self, video_list):
        whisper_transcription = OpenAIWhisperTranscription(video_list=video_list)
        return whisper_transcription
    
    def enhance_transcribe_to_df(self, whisper_transcription):
        enhance_result_dict = whisper_transcription.openai_transcribe_to_df()
        return enhance_result_dict

    def create_final_result_dict(self, enhance_result_dict, count_dict, result_dict):
        updated_timestamp_enhance_result_dict = update_timestamp_enhance_result(enhance_result_dict, count_dict, result_dict)
        dropped_result_df = drop_enhancement_original_index(count_dict, result_dict)
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
