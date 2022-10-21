import discord, traceback, configparser,time
intents = discord.Intents(messages=True, guilds=True,message_content=True)
client = discord.Client(intents=intents)

channel_set = []
art_dict = {}
repost_count = 0
pause=False
def build_url(message):
    return "https://discord.com/channels/"+str(message.guild.id)+"/"+str(message.channel.id)+"/"+str(message.id)

async def set_status(client):
    global art_dict
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(len(art_dict)) + " art pieces"))

def repost_embed(art_id):
    global art_dict
    embed =  discord.Embed(title="🚨 Repost! 🚨",description="Check [here](" + art_dict[art_id][0]+") for the original. This message will delete in one minute.",color=0x0366fc)
    embed.set_image(url="https://cdn.discordapp.com/attachments/994668648742531182/1030958839366950952/Shubat.gif")
    return embed

def pull_twitter_id(message):
    message_content = message.content
    id_start = message_content.find("status/")
    cur_substr = message_content[id_start+7:]
    cur_substr = cur_substr.split("?")[0]
    cur_substr = cur_substr.split("/")[0]
    cur_substr = "t" + cur_substr + "-" + str(message.channel.id)
    return cur_substr

def pull_pixiv_id(message):
    message_content = message.content
    id_start = message_content.find("artworks/")
    cur_substr = message_content[id_start+9:]
    cur_substr = cur_substr.split("?")[0]
    cur_substr = cur_substr.split("/")[0]
    cur_substr = "p" + cur_substr + "-" + str(message.channel.id)
    return cur_substr

async def repost_detect(art_id,message):
    print("b")
    if(art_id in art_dict):
        #repost
        msg = await message.channel.send(embed=repost_embed(art_id))
        time.sleep(5)
        await message.delete()
        time.sleep(60)
        
        await msg.delete()
    else:
        #add it
        art_dict[art_id] = (build_url(message),message.created_at)

        # f = open(str(message.id)+'.png','wb')
        # f.write(requests.get(message.embeds[0].image.url).content)
        # f.close()
        # await message.channel.send(content=message.content,file=discord.File(str(message.id)+'.png'))

def build_dict(art_id,message):
    global repost_count
    if(art_id in art_dict):
        repost_count = repost_count + 1
        if(art_dict[art_id][1] > message.created_at):
            art_dict[art_id] = (build_url(message),message.created_at,message.channel)

    else:
        art_dict[art_id] = (build_url(message),message.created_at) 
        if(len(art_dict)%200==0):
            print("Current art count: " + str(len(art_dict)))

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="(loading...)"))
    global repost_count
    print('Connected as: ' + client.user.name + "!")
    print('Building art post list...')
    for ch in channel_set:
        channel = client.get_channel(int(ch))
        async for message in channel.history(limit = None):
            if("twitter.com" in message.content):
                art_id = pull_twitter_id(message)
                build_dict(art_id,message)
            if("pixiv.net" in message.content):
                art_id = pull_pixiv_id(message)
                build_dict(art_id,message)           
    print("total reposts: "+str(repost_count))
    print("Finished building art post list!")
    print("Ready to go!")
    await set_status(client)

@client.event
async def on_message_delete(message):
    msgurl = build_url(message)
    art_id="dummy_key"
    if("twitter.com" in message.content):
        art_id = pull_twitter_id(message)
    if("pixiv" in message.content):
        art_id = pull_pixiv_id(message)
    
    if(art_id in art_dict.keys()):
        print(msgurl)
        print(art_dict[art_id][0])
        if(art_dict[art_id][0] == msgurl):
            del art_dict[art_id]
    await set_status(client)
    


@client.event
async def on_message(message):
    global channel_set, art_dict,pause
    print("hello")
    try:
        if(str(message.channel.id) in channel_set):
            print("a")
            print(message)
            if(not pause):
                if("twitter.com" in message.content):
                    print("c")
                    art_id = pull_twitter_id(message)
                    await repost_detect(art_id,message)
                    await set_status(client)
                if("pixiv" in message.content):
                    art_id = pull_pixiv_id(message)
                    await repost_detect(art_id,message)
                    await set_status(client)
            print(message.content)
            if(message.content=="!pause"):
                pause = True
                pmsg = await message.channel.send("stopping repost detection for 60 seconds. This message will delete when unpaused.")
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="(paused)"))
                time.sleep(60)
                await pmsg.delete()
                pause=False
                await set_status(client)

    except Exception as e:
        # await message.channel.send("Error: "+str(e)+"\nA stack trace has been printed to console.")
        traceback.print_exc()


print("Welcome to the bot!")
print("Loading settings...")
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    channel_set = config["bot"]["channels"].split(',')
    channel_set = [x.strip() for x in channel_set]
    token = config["bot"]["token"]
    print("Channels to watch: "+ str(channel_set))
    print("Settings loaded!")


except Exception as e:
    print("Error loading the settings! " + str(e))
    traceback.print_exc()
    exit()

print("Connecting to Discord...")
client.run(token)