import subprocess


def cut_video(
    input_path,
    output_path,
    start,
    end,
    mode="fast",
    progress_callback=None
):
    duration = end - start

    if duration <= 0:
        raise ValueError(
            "La duración del recorte debe ser mayor que 0."
        )

    if mode == "fast":
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

    elif mode == "precise":
        command = [
            "ffmpeg",
            "-y",

            "-ss", str(start),
            "-i", input_path,

            "-t", str(duration),

            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",

            "-c:a", "aac",
            "-b:a", "192k",

            "-movflags", "+faststart",
            "-avoid_negative_ts", "make_zero",

            "-progress", "pipe:1",
            "-nostats",

            output_path
        ]

    else:
        raise ValueError(
            f"Modo de recorte desconocido: {mode}"
        )

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    while True:
        line = process.stdout.readline()

        if not line:
            break

        line = line.strip()

        print("FFMPEG:", line)

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

    if progress_callback:
        progress_callback(100)