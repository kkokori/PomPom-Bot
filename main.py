import asyncio
from datetime import datetime, timedelta
import discord
import os
from threading import Timer
from dotenv import load_dotenv
load_dotenv()

# various valid time calls
seconds = ['s', 'sec', 'secs', 'second', 'seconds']
minutes = ['m', 'min', 'mins', 'minute', 'minutes']
hours = ['h', 'hr', 'hrs', 'hour', 'hours']
days = ['d', 'day', 'days']
months = ['M', 'mo', 'month', 'months']
years = ['y', 'yr', 'yrs', 'year', 'years']

client = discord.Client()
debug = False

commands = {
    "!help": "list commands",
    "!events": "list events",
    "!add": "<date> <time> <location> <description>",
}


@client.event
async def on_ready():
    await parse_reminder_list()
    print('Logged in at {0.user}'.format(client))


# convert date values to seconds
def to_seconds(num, t):
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
        return num * 31556952


async def remind(remindIn, reminderMsg, replyMsg, mentionReply, channel):
    def remove_date(date):
        print(date)
        with open("reminders.txt", "r") as file:
            lines = file.readlines()
            file.close()

        with open("reminders.txt", "w") as file:
            flag = False
            for line in lines:
                print(line.startswith(date))
                if flag:
                    flag = False
                elif not line.startswith(date):
                    file.write(line)
                else:
                    flag = True
            file.close()
        return

    print(remindIn)
    delta = remindIn - datetime.now()
    secondsToRemind = delta.total_seconds()
   
    await asyncio.sleep(secondsToRemind)
    await channel.send(reminderMsg, reference=replyMsg, mention_author=mentionReply)
    remove_date(remindIn.isoformat())


async def parse_reminder_list():
    with open("reminders.txt", "r") as file:
        lines = file.readlines()
        file.close()

    firstFlag = True
    for line in lines:
        # first line: date, reminderMsg p1
        if (firstFlag):
            firstFlag = False
            lineInfo = line.split("`~")
            remindDate = datetime.fromisoformat(lineInfo[0].strip())
            reminderMsg = lineInfo[1]
        else: # second line: remindMsg p2, replyMsg, mentionReply, origMsg
            firstFlag = True
            lineInfo = line.split("`~")
            reminderMsg += lineInfo[0]
            mentionReply = lineInfo[2]
            channel = await client.fetch_channel(lineInfo[3])             
            replyMsg = await channel.fetch_message(lineInfo[1])

            # reminder time already passed
            if remindDate < datetime.now(): 
                reminderMsg = "Uh oh. We might have missed a reminder for " + remindDate.strftime("%B %d, %Y at %I:%M %p") + ".\n" + lineInfo[0]

            asyncio.create_task(remind(remindDate, reminderMsg, replyMsg, mentionReply, channel))
    return



async def new_remind(message, pts):
    # parse command
    num = pts[1]  # number value
    denom = pts[2]  # time denomination

    if num.isnumeric() == False:
        await message.channel.send("Invalid number value. Ensure the second argument is a number.")
        return
    elif denom not in (seconds + minutes + hours + days + months + years):
        await message.channel.send("Invalid time format. Valid formats are:\n```seconds: " + str(seconds[0:]) + "\nminutes: " + str(minutes[0:]) + "\nhours: " + str(hours[0:]) + "\ndays: " + str(days[0:]) + "\nmonths: " + str(months[0:]) + "\nyears: " + str(years[0:]) + "```")
        return

    
    # get the seconds difference and find the date of reminding
    secondsTilRemind = to_seconds(int(num), denom)
    remindDate = datetime.now() + timedelta(seconds=secondsTilRemind)

    mentionUser = message.author.mention
    reminderMsg = "Reminding you, " + mentionUser + "."

    # check if there's a note
    reminderNote = "\n"
    if len(pts) > 3:
        reminderNote += "> " + (" ".join(pts[3:]))
    reminderMsg += reminderNote

    # confirmation of reminder
    await message.add_reaction('✅')

    # reply to remind message if the remind message is not replying to a different message
    replyMsg = message.reference if message.reference else message

    # do not mention user if the remind message is replying to a different message
    mentionReply = False if message.reference else True
    
    channel = message.channel
  
    # save the whole reminder
    def saveReminder():
        # remind date, remind note/msg, message to reply to, ping on/off, original message
        file = open("reminders.txt", "a")
        file.write(remindDate.isoformat() + "`~"+ str(reminderMsg) + "`~" +
                   str(replyMsg.id) + "`~" + str(mentionReply) + "`~" + str(channel.id) + "\n")
        file.close()
        return
    saveReminder()

    # set the remind
    await remind(remindDate, reminderMsg, replyMsg, mentionReply, channel)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    pts = message.content.split(" ")
    cmd = pts[0]
    channel = message.channel
    if debug:
        print(cmd)

    match cmd:
        case '!help':
            await channel.send("```!help - list commands\n\n!events - list event\n!add <date> <time> <location> <desc>\n\n!remind <#> <sec/min/hr/day/mo/yr>```")

        case '!remind':
            if len(pts) < 3:
                await channel.send("Invalid format. Use `!remind <#> <sec/min/hr/day/mo/yr> <optional message>`")
            await new_remind(message, pts)

        case '!add':
            date = pts[1]
            time = pts[2]
            place = pts[3]
            desc = pts[4:]

        case '!bojji':
            id = 0
            for e in message.guild.emojis:
                if e.name == "bojji":
                    id = e.id
                    break

            await channel.send("<:bojji:" + str(id) + ">")
        case _:
            print(message.content)
            if cmd.startswith('!'):
                await channel.send("Invalid command. `!help` for command list.")


is_prod = os.environ.get('IS_HEROKU', None)

# handle reading token when run locally vs on heroku
if is_prod:
    client.run(os.environ.get('TOKEN'))
else:
    client.run(os.getenv('TOKEN'))

# read in the old reminders and store/run them
