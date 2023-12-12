from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips
from pydub import AudioSegment
import noisereduce as nr
import numpy as np
from googletrans import Translator
import os
import shutil



def mp4_to_mp3(mp4, mp3):
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()


def mp3_duration(mp3):
    audio_clip = AudioFileClip(mp3)
    return audio_clip.duration

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


def adjust_volume(input_file, output_file, volume_factor):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Adjust the volume by the specified factor
    adjusted_audio = audio + volume_factor

    # Export the adjusted audio to a file
    adjusted_audio.export(output_file, format="mp3")


def clean_background_noise(input_file, output_file):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Convert the audio to a numpy array
    audio_array = audio.get_array_of_samples()

    # Perform background noise reduction
    reduced_audio = nr.reduce_noise(y=audio_array, sr=audio.frame_rate)

    # Create a new AudioSegment from the reduced audio numpy array
    cleaned_audio = audio._spawn(reduced_audio)

    # Export the cleaned audio to a file
    cleaned_audio.export(output_file, format="mp3")

def calculate_average_decibels(input_file, reference_level=0.0):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Convert the audio to a numpy array
    audio_array = np.array(audio.get_array_of_samples())

    # Calculate the RMS of the audio signal
    rms = np.sqrt(np.mean(np.square(audio_array)))

    # Convert RMS to decibels (dB)
    decibels = 20 * np.log10(rms) + reference_level

    return decibels


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
    final_clip.write_videofile(output_filename, codec="libx264")


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
