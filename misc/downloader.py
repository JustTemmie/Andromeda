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
    download("https://www.youtube.com/playlist?list=PLYVt6sUD_amTtozqHuhl0uPs2oy34HQLm", "assets/music")