from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips
import numpy as np
from googletrans import Translator
import os
import pickle
import shutil


def mp4_to_mp3(mp4, mp3):
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()


def mp3_duration(mp3):
    audio_clip = AudioFileClip(mp3)
    return audio_clip.duration

def mp4_duration(mp4):
    video_clip = VideoFileClip(mp4)
    return video_clip.duration

def split_mp3(input_file, start, end, output_file):
    # Load the MP3 audio clip
    audio_clip = AudioFileClip(input_file)

    # Split the audio clip into two parts
    part = audio_clip.subclip(start, end)

    # Write the two parts to separate MP3 files
    part.write_audiofile(output_file)

def split_mp4(input_file, start, end, output_file):
    # Load the video clip
    video_clip = VideoFileClip(input_file)

    # Split the video clip into two parts
    part = video_clip.subclip(start, end)

    # Write the two parts to separate video files
    part.write_videofile(output_file, codec='libx264', audio_codec="aac")


def translate_japanese_to_chinese(text):
    translator = Translator(service_urls=['translate.google.com'])
    try:
        translation = translator.translate(text, src='ja', dest='zh-cn')
        return translation.text
    except TypeError:
        return " "

def combine_outputs(file_path, video_filenames):
    # Load the video clips
    video_clips = [VideoFileClip(filename) for filename in video_filenames]
    # Concatenate the video clips
    final_clip = concatenate_videoclips(video_clips)
    # Set the output filename
    output_filename = f"{file_path}_output.mp4"

    # Save the final concatenated video
    final_clip.write_videofile(output_filename, temp_audiofile=f"temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")


def create_working_dir(folder_name, file_name):
    # Specify the folder name and file path
    folder_name = folder_name
    file_name = file_name

    # Create the folder
    os.makedirs(folder_name, exist_ok=True)

    # Move the file to the new folder
    shutil.move(file_name, os.path.join(folder_name, file_name))

def delete_working_files(file_path):

    # Specify the file path
    file_path = file_path

    # Check if the file exists
    if os.path.exists(file_path):
        # Remove the file
        os.remove(file_path)
        print(f"File '{file_path}' has been successfully deleted.")
    else:
        print(f"File '{file_path}' does not exist.")

def load_pkl(file_path):
    with open(file_path, 'rb') as f:
        object = pickle.load(f)
    return object

def write_pkl(object, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(object, f)