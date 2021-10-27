import discord
import queue
import threading
import sys
from common import client
from xml_strings import strs_dict, cmds_dict, help_str
import consts

music_queue = queue.Queue()
bot_voice_client = None
is_playing_done = threading.Event()


def playDone(err):
    global is_playing_done

    if err is not None:
        raise err

    is_playing_done.set()
    

def playWholeQueue():
    global music_queue
    global bot_voice_client
    global is_playing_done

    try:
        while True:
            url = music_queue.get(timeout=600)

            stream = discord.FFmpegOpusAudio(f"res/{url}.mp3")
            bot_voice_client.play(stream, after=playDone)
            
            is_playing_done.wait()
            is_playing_done.clear()
            music_queue.task_done()

    except queue.Empty:
        client.loop.create_task(bot_voice_client.disconnect())
        bot_voice_client = None
        return


async def playMusic(channel, url):
    global bot_voice_client
    global music_queue

    if bot_voice_client is None:
        bot_voice_client = await channel.connect()

        music_queue.put(url)
        threading.Thread(target=playWholeQueue).start()

        return strs_dict[consts.play_entering_channel] + channel.name

    if channel != bot_voice_client.channel:
        return strs_dict[consts.play_another_channel]

    music_queue.put(url)
    return strs_dict[consts.play_now_in_queue]