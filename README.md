# whisper-video-transcript

## Features

- **Faster Whisper Integration:** Utilize faster-whisper for faster and more accurate transcription of long videos.
- **MoviePy Subtitle Integration:** Add subtitles to your videos using MoviePy
- **Main Classes:**
  - `OpenAIWhisperTranscription`: Class for initiating transcription using the OpenAI Whisper model.
  - `ResultEnhancement`: Class for enhancing transcription results, offering additional functionalities.

## Example Usage

```python
from transcribe import OpenAIWhisperTranscription

whisper_transcription = OpenAIWhisperTranscription(
    mp4_name="your_mp4_name.mp4"
)

result_dict = whisper_transcription.openai_transcribe_to_df()

subs_dict = whisper_transcription.create_subs_dict(result_dict)

whisper_transcription.add_subs_to_video(subs_dict)
```
