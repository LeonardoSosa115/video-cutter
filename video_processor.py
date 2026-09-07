import subprocess


def cut_video(input_path, output_path, start, end):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-ss", start,
        "-to", end,
        "-c", "copy",
        output_path
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )