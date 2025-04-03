import discord
import requests
import json
import re
import os
import glob
import instaloader
import yt_dlp
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI = os.getenv("GEMINI_API_KEY")


loader = instaloader.Instaloader(download_pictures=False,
                                 download_comments=False,
                                 download_geotags=False,
                                 download_video_thumbnails=False,
                                 save_metadata=False,
                                 post_metadata_txt_pattern="",
                                 compress_json=False)

# Enable message content intent
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages

# Create bot instance
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip()

    if content.startswith("https://www.instagram.com/"):
        await message.channel.send("📸 Downloading Instagram video...", delete_after=3)    
        video = downloadinsta(content)

        if video:
            await message.channel.send(file = discord.File(video))
            os.remove(video)
            
            try:
                def check(m):
                    return (
                        m.author.id == 760904896970096660 and
                        m.channel == message.channel
                    )

                reply = await bot.wait_for("message", timeout=15, check=check)
                await reply.delete()

            except asyncio.TimeoutError:
                pass  # No message received within 15 seconds, do nothing

        else:
            await message.channel.send("Failed to download video")
        return
    
    if content.startswith("https://x.com/"):

        video = downloadtwitter(content)

        if video:
            await message.channel.send(file = discord.File(video))
            os.remove(video)
        return


    if bot.user in message.mentions and not message.content.startswith("https://www.instagram.com/"):  
        prompt = re.sub(f"<@!?{bot.user.id}>", "", message.content).strip()

        if not prompt:  
            return
        
        try:
            response_text = get_gemini_response(prompt)  
            await message.reply(response_text, mention_author=True)
        
        except Exception as e:
            await message.reply("Meow... Something went wrong! 😿", mention_author=True)
            print(f"Error: {e}")

def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [{"text": f"Keep the answer under 30 words, reply in a cat-like manner with cat emojis, also give the cat an indian especially south indian personality: {prompt}"}]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"] 
    else:
        return "Meow... Something went wrong! 😿"


def downloadinsta(url):
    FOLDER = "insta"

    try:
        shortcode = url.split("/")[-2] 
        loader.download_post(instaloader.Post.from_shortcode(loader.context, shortcode), target= FOLDER)

        video_files = glob.glob(FOLDER + "/*.mp4")
        if video_files:
            latest_video = max(video_files, key=os.path.getctime)
            return latest_video  

    except Exception as e:
        print(f"Download Error: {e}")
        return None
    
def downloadtwitter(url):

    FOLDER = "x"
    os.makedirs(FOLDER, exist_ok=True)

    # yt-dlp options
    ydl_opts = {
        'outtmpl': f'{FOLDER}/%(id)s.%(ext)s',
        'quiet': True,
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)

            return video_path
    
    except Exception as e:
        print(f"Download Error: {e}")
        return None


bot.run(TOKEN)