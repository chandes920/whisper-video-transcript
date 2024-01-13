from setuptools import setup, find_packages

setup(
    name='whisper_video_transcript',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'faster-whisper==0.10.0',
        'moviepy==1.0.3',
        'pandas==2.0.3',
        'numpy==1.24.3',
        'opencv-python==4.9.0.80',
        'googletrans==3.0.0'
    ],
)
