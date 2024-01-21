from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def top_consecutive_occurrences(series, threshold=5):
    count_dict = {}

    current_count = 0
    current_value = None
    start_index = None

    for idx, value in enumerate(series):
        if value == current_value:
            current_count += 1
            
        else:
            current_value = value
            current_count = 1
            start_index = idx

        if current_count >= threshold:
            count_dict.setdefault(current_value, {'count': 0, 'index_range': None})
            count_dict[current_value]['count'] = max(count_dict[current_value]['count'], current_count)
            count_dict[current_value]['index_range'] = [start_index, idx]
            count_dict[current_value]['cleaned_key'] = f"consecutive_{start_index}"

    return count_dict

def extract_video_clip(start_time, end_time, input_path, output_path):
    video = VideoFileClip(input_path).subclip(start_time, end_time)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")

def extract_mp4_clips(video_file_path, index_dict, result_df):
    enhance_video_list = []
    for i in index_dict:
        min_timestamp = result_df.iloc[index_dict[i]["index_range"][0]:index_dict[i]["index_range"][1]+1]['start'].min()
        max_timestamp = result_df.iloc[index_dict[i]["index_range"][0]:index_dict[i]["index_range"][1]+1]['end'].max()
        enhance_video_path = f'output_clip_{index_dict[i]["cleaned_key"]}.mp4'
        extract_video_clip(min_timestamp, max_timestamp, video_file_path, enhance_video_path)
        enhance_video_list.append(enhance_video_path)
    return enhance_video_list

def update_timestamp_enhance_result(enhance_result_dict, count_dict, result_df):
    for i in count_dict:
        min_timestamp = result_df.iloc[count_dict[i]["index_range"][0]:count_dict[i]["index_range"][1]+1]['start'].min()
        enhance_result_dict[f"output_clip_{count_dict[i]['cleaned_key']}.mp4"]['start'] = enhance_result_dict[f"output_clip_{count_dict[i]['cleaned_key']}.mp4"]['start'] + min_timestamp
        enhance_result_dict[f"output_clip_{count_dict[i]['cleaned_key']}.mp4"]['end'] = enhance_result_dict[f"output_clip_{count_dict[i]['cleaned_key']}.mp4"]['end'] + min_timestamp
    return enhance_result_dict

def drop_enhancement_original_index(count_dict, result_df):
    dropped_result_df = result_df.copy()
    
    for i in count_dict:
        min_index = count_dict[i]["index_range"][0]
        max_index = count_dict[i]["index_range"][1]+1
        mask = ~dropped_result_df.index.isin(range(min_index, max_index))
        dropped_result_df = dropped_result_df[mask]
    return dropped_result_df

def delete_working_files(video_list):
    for video in video_list:
        os.remove(video)
        print(f"File '{video}' has been successfully deleted.")
