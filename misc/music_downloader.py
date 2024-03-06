import argparse
import yt_dlp

def download(URL, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([URL])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download audio from YouTube using yt-dlp.")
    parser.add_argument("url", help="URL of the YouTube video or playlist")
    parser.add_argument("output_dir", help="Output directory to save the downloaded audio files")

    args = parser.parse_args()

    download(args.url, args.output_dir)