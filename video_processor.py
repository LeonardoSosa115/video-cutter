import subprocess


def cut_video(
    input_path,
    output_path,
    start,
    end,
    progress_callback=None
):
    duration = end - start

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),
        "-c", "copy",
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        line = line.strip()

        if line.startswith("out_time_ms="):
            value = line.split("=", 1)[1]

            try:
                processed_ms = int(value) / 1000

                progress = int(
                    (processed_ms / duration) * 100
                )

                progress = max(
                    0,
                    min(progress, 100)
                )

                if progress_callback:
                    progress_callback(progress)

            except ValueError:
                pass

    process.wait()

    if process.returncode != 0:
        raise RuntimeError(
            "FFmpeg no pudo procesar el video."
        )