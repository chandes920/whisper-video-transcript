import subprocess

def download(url, mp4_name, res='res:720'):
    output_template = f'{mp4_name}'

    command = [
        'yt-dlp',
        '-S', res,
        '-o', output_template,
        url
    ]

    # Run the command using subprocess
    subprocess.run(command)
