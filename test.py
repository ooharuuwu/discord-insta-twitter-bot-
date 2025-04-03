import yt_dlp
import os

def download_twitter_video(tweet_url, output_dir='x'):
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'quiet': True
    }

    os.makedirs(output_dir, exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(tweet_url, download=True)
        return ydl.prepare_filename(info)

# Example
filepath = download_twitter_video('https://x.com/anime_twits/status/1906349105175015797')