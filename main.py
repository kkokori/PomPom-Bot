import discord
import asyncio
import os
from threading import Timer
from dotenv import load_dotenv
load_dotenv()


client = discord.Client()

commands = {
    "!help": "list commands",
    "!events": "list events",
    "!add": "<event-name>",
    }

@client.event
async def on_ready():
    print('Logged in at {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    pts = message.content.split(" ")
    cmd = pts[0]
    print(cmd)

    match cmd:
        case '!help':
            await message.channel.send("```!help - list commands\n\n!events - list event\n!add <event name> <date> <time> <location>\n\n!remind <#> <sec/min/hr/day/mo/yr>```")
        case '!remind':
            print(message.author)
            if len(pts) < 3:
                await message.channel.send("Invalid format. Use `!remind <#> <sec/min/hr/day/mo/yr> <optional message>`")
            
            num = pts[1] # number value
            denom = pts[2] # time denomination

            # various valid time calls
            seconds = ['s', 'sec', 'secs', 'second', 'seconds']
            minutes = ['m', 'min', 'mins', 'minute', 'minutes']
            hours = ['h', 'hr', 'hrs', 'hour', 'hours']
            days = ['d', 'day', 'days']
            months = ['M', 'mo', 'month', 'months']
            years = ['y', 'yr', 'yrs', 'year', 'years']

            # converting values to seconds for asyncio
            def toSeconds(num, t):
                if t in seconds:
                    return num
                elif t in minutes:
                    return num * 60
                elif t in hours:
                    return num * 3600
                elif t in days:
                    return num * 86400
                elif t in months:
                    return num * 2629800
                elif t in years:
                    return num * 31,556,952

            if num.isnumeric() == False:
                await message.channel.send("Invalid number value. Ensure the second argument is a number.")
            elif denom not in (seconds + minutes + hours + days + months + years):
                await message.channel.send("Invalid time format. Valid formats are:\n```seconds: " + str(seconds[0:]) + "\nminutes: " + str(minutes[0:]) + "\nhours: " + str(hours[0:]) + "\ndays: " + str(days[0:]) + "\nmonths: " + str(months[0:]) + "\nyears: "+ str(years[0:]) +"```")
            else: 
                remindIn = toSeconds(int(num), denom)
                mentionUser = message.author.mention
                reminderMsg = "Reminding you, " + mentionUser
            
                print(len(pts))
                if len(pts) > 3:
                    reminderMsg += ": " + (" ".join(pts[3:]))
                
                # reply to remigignd message if the remind message is not replying to a different message
                replyMsg = message.reference if message.reference else message
                # do not mention user if the remind message is replying to a different message
                mentionReply = False if message.reference else True
                
                await asyncio.sleep(remindIn)
                await message.channel.send(reminderMsg, reference=replyMsg, mention_author=mentionReply)
                
        case '!bojji':
            id = 0
            for e in message.guild.emojis:
                if e.name == "bojji":
                    id = e.id
                    break

            await message.channel.send("<:bojji:" + str(id) + ">")
        case _:
            print(message.content)
            if cmd.startswith('!'):
                await message.channel.send("Invalid command. `!help` for command list.")


client.run(os.getenv('TOKEN'))
