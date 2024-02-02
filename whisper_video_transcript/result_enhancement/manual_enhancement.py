import logging
import math
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
os.environ["IMAGEMAGICK_BINARY"] = "/opt/homebrew/bin/convert"

from moviepy.editor import TextClip, VideoFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import numpy as np
import pandas as pd
import pickle

from whisper_video_transcript.transcribe.openai_whisper_transcription import OpenAIWhisperTranscription

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

class ManualEnhancer:
    def __init__(
        self,
        result_dict = None,
        enhanced_dict = None
    ):
        self.input_dict = result_dict if result_dict is not None else enhanced_dict

    def init_whisper_transcription(self, video_list):
        whisper_transcription = OpenAIWhisperTranscription(enhance_video_list=video_list)
        return whisper_transcription

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

    def csv_workflow(self):
        for video in self.input_dict:
            self.input_dict[video] = pd.read_csv(f'{video[:-4]}.csv',  index_col=0)
            subs = self.create_enhanced_subs_dict(self.input_dict[video])
            whisper_transcription_enhance = self.init_whisper_transcription([video])
            self.add_enhanced_subs_to_video(whisper_transcription_enhance, video, subs)