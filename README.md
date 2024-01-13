# whisper-video-transcript

## Features

- **Faster Whisper Integration:** Utilize faster-whisper for faster and more accurate transcription of long videos.
- **MoviePy Subtitle Integration:** Add subtitles to your videos using MoviePy
- **Main Classes:**
  - `OpenAIWhisperTranscription`: Class for initiating transcription using the OpenAI Whisper model.
  - `ResultEnhancement`: Class for enhancing transcription results, offering additional functionalities.

## Example Usage for Transcription

```python
from whisper_video_transcript.transcribe.openai_whisper_transcription import OpenAIWhisperTranscription

whisper_transcription = OpenAIWhisperTranscription(
    mp4_name="your_mp4_name.mp4"
)

result_dict = whisper_transcription.openai_transcribe_to_df()

subs_dict = whisper_transcription.create_subs_dict(result_dict)

whisper_transcription.add_subs_to_video(subs_dict)
```

## Example Usage for Result Enhancement

```python
from whisper_video_transcript.result_enhancement.result_enhancement import ResultEnhancement

for video in whisper_transcription.video_list:
    result_enhancement = ResultEnhancement(result_dict[video])
    enhanced_dict = result_enhancement.consecutive_text_workflow(video, consecutive_text_threshold=1, process=True, output=False)

    result_enhancement.duration_workflow(video, enhanced_dict, duration_threshold=4, process=True, output=True)
```