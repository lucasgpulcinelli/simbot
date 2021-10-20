#!/usr/bin/env python3

#TODO: do not assume message has content (can generate error)

#external imports
import random
import discord

#local files imports
import quotes
import consts
from xml_strings import strs_dict, cmds_dict, help_str


#returns True if the command is the string corresponding to the xml_name
#made to simplify many if cases
def cmd_is(cmd, xml_name):
    return cmd == cmds_dict[xml_name][consts.help_fmt_xml[0]]


#processes the message with these arguments
def process_command(message, args):

    #is the string for the random command?
    if cmd_is(args[1], consts.cmd_random_xml):
        return random.choice(quotes.quotes)
        
    #for the play command?
    if cmd_is(args[1], consts.cmd_play_xml):
        voiceState = message.author.voice

        #is the person not in a voice channel?
        if voiceState is None:
            return strs_dict[consts.play_no_voice_xml]
        #did they not provide an URL?
        if len(args) < 3:
            return strs_dict[consts.play_no_url_xml]
        
        #playMusic(voiceState.channel, args[2])
        raise NotImplementedError("playMusic needs to be implemented yet!")

    #and so on
    if cmd_is(args[1], consts.cmd_help_xml):
        return help_str
        
    #if we did not return yet, there is no command!
    return strs_dict[consts.no_cmd_xml]


#the client itself
client = discord.Client()

@client.event
async def on_ready():
    print(strs_dict[consts.ready_msg_xml])

@client.event
async def on_message(message):
    try:
        #we don't want to process something we ourselves posted!
        if message.author == client.user:
            return

        args = message.content.split()

        #is this message directed to us?
        if args[0] != strs_dict[consts.bot_cmd_xml]:
            return

        response = process_command(message, args)
        
    except Exception as e:
        response = strs_dict[consts.fatal_error_xml] + f"`{e}`" 

    if response is not None:
        await message.channel.send(response, reference=message)
        

#getting the token
fp = open(consts.token_file)
token = fp.read()
fp.close()

if __name__ == "__main__":
    #running the bot!
    client.run(token)
