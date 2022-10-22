import discord, traceback, configparser,time,pytz
from datetime import date, timedelta, datetime

intents = discord.Intents(messages=True, guilds=True,message_content=True)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    global spcae_names
    print('Connected as: ' + client.user.name + "!")
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.now().replace(tzinfo=local_tz)

    print("Current time: " + now.strftime("%m/%d/%Y, %H:%M:%S"))
    cutoff = now - timedelta(days=7)
    print("Cutoff time: " + cutoff.strftime("%m/%d/%Y, %H:%M:%S"))
    print("Building stats...")

    for ch in channel_set:

        char_list = []
        user_dict = {}
        char_dict = {}
        total_count = 0

        channel = client.get_channel(int(ch))
        async for message in channel.history(limit = None):
            created_at = message.created_at.replace(tzinfo=local_tz)
            if(created_at<cutoff):
                break

            poster = message.author.name
            if("twitter.com" in message.content) or ("pixiv.net" in message.content):
                total_count = total_count + 1
                splitter = message.content.replace(",","").replace("\n"," ").split(" ")
                splitter = [s.lower() for s in splitter if ("http" not in s and s != "" and s != "||")]

                for spaced_name in space_names:
                    segments = spaced_name.split(" ")
                    if(all(segment in splitter for segment in segments)):
                        splitter = [s for s in splitter if s not in segments]
                        splitter.append("".join(segments))

                if not (poster in user_dict.keys()):
                    user_dict[poster] = {}
                
                for character in splitter:
                    if not(character in user_dict[poster]):
                        user_dict[poster][character] = 0

                    if not(character in char_list):
                        char_list.append(character)
                        char_dict[character] = 0

                    user_dict[poster][character] = user_dict[poster][character] + 1
                    char_dict[character] = char_dict[character] + 1

        channel_name = client.get_channel(int(ch)).name
        stringbuilder = "Stats for #" + channel_name + ":\n" + "Timeframe: " + cutoff.strftime("%m/%d/%Y %H:%M") + "EST -" + now.strftime("%m/%d/%Y %H:%M") + "EST\nTotal art pieces: " + str(total_count) + "\n" + "Total characters: " + str(len(char_list)) + "\n"

        sorted_char_tuples = sorted(char_dict.items(), key=lambda item: item[1], reverse=True)

        user_counts = {}
        for user in user_dict.keys():
            user_sum = 0
            for char in user_dict[user].keys():
                user_sum = user_sum + user_dict[user][char]
            user_counts[user] = user_sum

        sorted_user_tuples = sorted(user_counts.items(), key=lambda item: item[1], reverse=True)

        top_num = min(len(char_list),5)
        stringbuilder = stringbuilder + "Top Characters:\n"
        for i in range(0,top_num):
            stringbuilder = stringbuilder + (str(i+1) + ". " + sorted_char_tuples[i][0] + " (" + str(sorted_char_tuples[i][1]) + ")\n")

        stringbuilder = stringbuilder + "\n\nTop by person:"
        for utuple in sorted_user_tuples:

            stringbuilder = stringbuilder + ("\n" + utuple[0] + " (" + str(utuple[1]) + " total):\n")
            sorted_user_char_tuples = sorted(user_dict[utuple[0]].items(), key=lambda item: item[1], reverse=True)
            top_num = min(len(sorted_user_char_tuples),5)
            for i in range(0,top_num):
                stringbuilder = stringbuilder + (str(i+1) + ". " + sorted_user_char_tuples[i][0] + " (" + str(sorted_user_char_tuples[i][1]) + ")\n")
        
        await client.get_channel(stats_channel).send(stringbuilder)

    print("done")
    exit()

print("Welcome to the bot!")
print("Loading settings...")
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    channel_set = config["bot"]["channels"].split(',')
    channel_set = [x.strip() for x in channel_set]
    token = config["bot"]["token"]
    stats_channel = int(config["bot"]["stats_channel"])
    space_names = config["bot"]["space_names"].split(',')
    print("Channels to watch: "+ str(channel_set))
    print("Settings loaded!")
except Exception as e:
    print("Error loading the settings! " + str(e))
    traceback.print_exc()
    exit()

print("Connecting to Discord...")
client.run(token)