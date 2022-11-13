import discord, traceback, configparser,time, utils,asyncio,sqlite3,pytz
intents = discord.Intents(messages=True, guilds=True,message_content=True)
client = discord.Client(intents=intents)

channel_set = []
pause=False

def repost_embed(art_id):
    resp = cursor.execute(f"SELECT poster,message_id,server_id,channel_id FROM art_messages WHERE art_id='{art_id}';")
    fetchone = resp.fetchone()


    (poster,message_id,server_id,channel_id) = fetchone

    resp = cursor.execute(f"""SELECT character_name 
                                FROM art_character 
                                LEFT JOIN characters 
                                ON art_character.character_id=characters.character_id 
                                WHERE art_id='{art_id}';""")
    fetchall = resp.fetchall()
    post_char_list = [a[0] for a in fetchall]
    char_string = ", ".join(post_char_list)

    print(char_string)
    print((poster,message_id,server_id,channel_id))

    embed =  discord.Embed(title="🚨 Repost! 🚨",description=f"{poster} posted this ({char_string}) before. Check [here](https://discord.com/channels/{server_id}/{channel_id}/{message_id}) for the original. This message will delete in one minute.",color=0x0366fc)
    embed.set_image(url="https://cdn.discordapp.com/attachments/994668648742531182/1030958839366950952/Shubat.gif")
    return embed

async def set_status(client):
    global resp,cursor
    resp = cursor.execute(f"SELECT COUNT(*) FROM art_messages")
    count = resp.fetchone()[0]
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(count) + " art pieces"))

def get_char_id(character_name):
    global con, cursor
    #check for character
    resp = cursor.execute(f"SELECT character_id FROM characters WHERE character_name='{character_name}';")
    fetchone = resp.fetchone()
    if(fetchone is None):
        #add it if not already
        resp = cursor.execute(f"INSERT INTO characters (character_name) VALUES ('{character_name}');")
        con.commit()
        resp = cursor.execute(f"SELECT character_id FROM characters WHERE character_name='{character_name}';")
        char_id = resp.fetchone()[0]
    else:
        char_id=fetchone[0]
    
    return char_id

def add_art(art_id,message):
    global con, cursor, space_names
    local_tz = pytz.timezone('US/Eastern')
    created_at = message.created_at.replace(tzinfo=local_tz)
    poster = message.author.name
    splitter = message.content.replace(",","").replace("\n"," ").split(" ")
    splitter = [s.lower() for s in splitter if ("http" not in s and s != "" and s != "||")]

    for spaced_name in space_names:
        segments = spaced_name.split(" ")
        if(all(segment in splitter for segment in segments)):
            splitter = [s for s in splitter if s not in segments]
            splitter.append("".join(segments))

    try:
        command = f"""INSERT INTO art_messages (art_id,message_id,server_id,channel_id,poster,post_date)
                        VALUES (
                            '{art_id}',
                            {message.id},
                            {message.guild.id},
                            {message.channel.id},
                            '{poster}',
                            '{created_at}')
                            """
        cursor.execute(command)
        print(f"{art_id} added")
    except Exception as e:
        print(f"couldnt insert\n{str(e)}")

    for character in splitter:

        #check if in db
        
        print(character)
        character_id = get_char_id(character)
        # print(character_id)

        try:
            cursor.execute(f"""INSERT INTO art_character (art_id, character_id)
                                    VALUES ('{art_id}',{character_id})""")
        except Exception as e:
            print(f"couldnt insert\n{str(e)}")
        con.commit();
    
async def repost_detect(art_id,message):
    global cursor,con
    #check if in db

    resp = cursor.execute(f"SELECT message_id,channel_id,server_id FROM art_messages WHERE art_id='{art_id}';")
    response_post = resp.fetchone();

    if(response_post is None):
        add_art(art_id,message)
    else:
        print("repost")
        msg = await message.channel.send(embed=repost_embed(art_id))
        await asyncio.sleep(5)
        await message.delete()
        await asyncio.sleep(60)
        await msg.delete()

    await set_status(client)
    

    # if(art_id in art_dict):
    #     #repost
    #     msg = await message.channel.send(embed=repost_embed(art_id))
    #     time.sleep(5)
    #     await message.delete()
    #     time.sleep(60)
        
    #     await msg.delete()
    # else:
    #     #add it
    #     art_dict[art_id] = (utils.build_url(message),message.created_at)

        # f = open(str(message.id)+'.png','wb')
@client.event
async def on_ready():
    print('Connected as: ' + client.user.name + "!")
    await set_status(client)

@client.event
async def on_message_delete(message):
    art_id="dummy_id"
    if("twitter.com" in message.content):
        art_id = utils.pull_twitter_id(message)
    if("pixiv" in message.content):
        art_id = utils.pull_pixiv_id(message)
    resp = cursor.execute(f"SELECT message_id FROM art_messages WHERE art_id='{art_id}';")
    fetchone = resp.fetchone()
    if(fetchone is not None):
        if(message.id==fetchone[0]):
            resp = cursor.execute(f"DELETE FROM art_messages WHERE art_id='{art_id}';")
            con.commit()
            resp = cursor.execute(f"DELETE FROM art_character WHERE art_id='{art_id}';")

            await set_status(client)
    


@client.event
async def on_message(message):
    global pause
    if(str(message.channel.id) in channel_set and not pause):
        if(not pause):
            if("twitter.com" in message.content):
                art_id = utils.pull_twitter_id(message)
                await repost_detect(art_id,message)
            if("pixiv" in message.content):
                art_id = utils.pull_pixiv_id(message)
                await repost_detect(art_id,message)
        if(message.content=="!pause"):
            print("pause")
        

print("Welcome to the bot!")
print("Loading settings...")
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    channel_set = config["bot"]["channels"].split(',')
    channel_set = [x.strip() for x in channel_set]
    token = config["bot"]["prod_token"]
    space_names = config["bot"]["space_names"].split(',')
    print("Channels to watch: "+ str(channel_set))
    print("Settings loaded!")
    print("Connecting to db...")
    con = sqlite3.connect("art_prod.db")
    cursor = con.cursor()
    print("Connected to db!")


except Exception as e:
    print("Error loading the settings! " + str(e))
    traceback.print_exc()
    exit()

print("Connecting to Discord...")
client.run(token)