import discord
import queue
import threading
import subprocess
import time
import youtube_dl

from common import client
from xml_strings import strs_dict
import consts

music_queue = queue.Queue()
bot_voice_client = None
is_playing_done = threading.Event()


def playDone(err):
    global is_playing_done

    if err is not None:
        raise err

    is_playing_done.set()
    

def playWholeQueue(tchannel):
    global music_queue
    global bot_voice_client
    global is_playing_done

    try:
        while True:
            title, url = music_queue.get(timeout=10)

            audio = discord.FFmpegPCMAudio(url)
            client.loop.create_task(tchannel.send(strs_dict[consts.play_now_playing] + title))
            time.sleep(2)
            bot_voice_client.play(audio, after=playDone)
            
            is_playing_done.wait()
            is_playing_done.clear()
            music_queue.task_done()

    except queue.Empty:
        client.loop.create_task(bot_voice_client.disconnect())
        bot_voice_client = None
        return

def add_url_to_queue(yturl):
    ydl = youtube_dl.YoutubeDL({"format":"bestaudio/best", "cachedir":False, "playlistend":2})
    info = ydl.extract_info(yturl, download=False)

    if "entries" in info.keys(): #playlist
        music_queue.put((info["entries"][0]["title"], info["entries"][0]["url"]))
        
        ydl = youtube_dl.YoutubeDL({"format":"bestaudio/best", "cachedir":False, "playliststart":2})
        info = ydl.extract_info(yturl, download=False)
        for song in info["entries"]:
            music_queue.put((song["title"], song["url"]))

    elif "formats" in info.keys(): #single music
        music_queue.put((info["title"], info["formats"][0]["url"]))


async def playMusic(tchannel, vchannel, url):
    global bot_voice_client
    global music_queue

    if bot_voice_client is None:
        bot_voice_client = await vchannel.connect()

        threading.Thread(target=add_url_to_queue, args=(url,)).start()
        threading.Thread(target=playWholeQueue, args=(tchannel,)).start()

        return strs_dict[consts.play_entering_channel] + vchannel.name

    if vchannel != bot_voice_client.channel:
        return strs_dict[consts.play_another_channel]

    threading.Thread(target=add_url_to_queue, args=(url,)).start()
    return strs_dict[consts.play_now_in_queue]