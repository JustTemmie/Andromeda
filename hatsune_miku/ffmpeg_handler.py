from ffmpeg import FFmpeg


async def apply_ffmpeg_audio_filter(input_file, output_file, codec, map, filter):
    if codec == map == filter == None:
        ffmpeg = (
            FFmpeg("/usr/bin/ffmpeg")
            .option("y")
            .input(input_file)
            .output(output_file)
        )
    else:
        ffmpeg = (
            FFmpeg("/usr/bin/ffmpeg")
            .option("y")
            .input(input_file)
            .output(output_file,
                codec,
                map=map,
                filter=filter
            )
        )

    try:
        ffmpeg.execute()
        return True
    except Exception as e:
        print(f"ffmpeg failed to convert {input_file}\n{e.message}, {e.arguments}")
        return False

def get_duration(file):
    return float(
        FFmpeg("/usr/bin/ffprobe")
        .input(
            file,
            show_entries="format=duration",
            of="compact=p=0:nk=1",
            loglevel="error"
        )
        .execute()
        .strip()
    )