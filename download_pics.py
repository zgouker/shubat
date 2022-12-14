import discord, traceback, configparser,time, utils,asyncio,sqlite3,pytz,requests
from datetime import timedelta, datetime
intents = discord.Intents(messages=True, guilds=True,message_content=True)
client = discord.Client(intents=intents)

channel_set = []
pause=False

@client.event
async def on_ready():
    global space_names
    print('Connected as: ' + client.user.name + "!")
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.now().replace(tzinfo=local_tz)

    print("Current time: " + now.strftime("%m/%d/%Y, %H:%M:%S"))
    cutoff = now - timedelta(weeks=1)
    print("Cutoff time: " + cutoff.strftime("%m/%d/%Y, %H:%M:%S"))
    print("Building stats...")
    for ch in channel_set:

        channel = client.get_channel(int(ch))
        async for message in channel.history(limit = None):
            created_at = message.created_at.replace(tzinfo=local_tz)
            if(created_at<cutoff):
                break
            try:
                f = open(f"download/{str(message.channel.id)}/{str(message.id)}.png",'wb')
                if(len(message.embeds)>0):
                    url=message.embeds[0].image.url
                else:
                    url=message.attachments[0].url
                f.write(requests.get(url).content)
                f.close()
                print(message.id)
            except Exception as e:
                print(str(e))

    print("done")
    exit()

print("Welcome to the bot!")
print("Loading settings...")
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    channel_set = config["bot"]["channels"].split(',')
    channel_set = [x.strip() for x in channel_set]
    token = config["bot"]["prod_token"]
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