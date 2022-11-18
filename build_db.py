import discord, traceback, configparser,time,pytz,sqlite3, utils
from datetime import date, timedelta, datetime

intents = discord.Intents(messages=True, guilds=True,message_content=True)
client = discord.Client(intents=intents)

def get_char_id(character_name):
    global con,cursor

    resp = cursor.execute(f"SELECT character_id FROM characters WHERE character_name='{character_name}';")
    fetchone = resp.fetchone()
    if(fetchone is None):
        resp = cursor.execute(f"INSERT INTO characters (character_name) VALUES ('{character_name}');")
        con.commit()
        resp = cursor.execute(f"SELECT character_id FROM characters WHERE character_name='{character_name}';")
        char_id = resp.fetchone()[0]
    else:
        char_id=fetchone[0]
    return char_id


@client.event
async def on_ready():
    global space_names,con,cursor
    print('Connected as: ' + client.user.name + "!")
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.now().replace(tzinfo=local_tz)

    print("Current time: " + now.strftime("%m/%d/%Y, %H:%M:%S"))
    cutoff = now - timedelta(weeks=52)
    print("Cutoff time: " + cutoff.strftime("%m/%d/%Y, %H:%M:%S"))
    print("Building stats...")

    for ch in channel_set:
        channel = client.get_channel(int(ch))
        async for message in channel.history(limit = None):
            created_at = message.created_at.replace(tzinfo=local_tz)
            if(created_at<cutoff):
                break

            poster = message.author.name
            if("twitter.com" in message.content) or ("pixiv.net" in message.content):
                if("twitter.com" in message.content):
                    art_id = utils.pull_twitter_id(message)
                if("pixiv.net" in message.content):
                    art_id = utils.pull_pixiv_id(message)                
                splitter = message.content.replace(",","").replace("\n"," ").split(" ")
                splitter = [s.lower() for s in splitter if ("http" not in s and s != "" and s != "||")]

                for spaced_name in space_names:
                    segments = spaced_name.split(" ")
                    if(all(segment in splitter for segment in segments)):
                        splitter = [s for s in splitter if s not in segments]
                        splitter.append("".join(segments))
                
                # print(art_id)
                try:
                    resp = cursor.execute(f"SELECT message_id,channel_id,server_id,post_date FROM art_messages WHERE art_id='{art_id}';")
                    response_post = resp.fetchone();

                    if(response_post is None):
                        pass
                    else:

                        print(f"old: {response_post[3]}\nnew: {created_at}")
                        old_time = datetime.strptime(response_post[3],"%y-%m-%d %H:%M:%S").replace(tzinfo=local_tz)
                        if(created_at<old_time):
                            cursor.execute(f"DELETE FROM art_messages WHERE art_id='{art_id}';")
                            cursor.execute(f"DELETE FROM art_character WHERE art_id='{art_id}';")
                            print(art_id)

                    command = f"""INSERT INTO art_messages (art_id,message_id,server_id,channel_id,poster,post_date)
                                    VALUES (
                                        '{art_id}',
                                        {message.id},
                                        {message.guild.id},
                                        {message.channel.id},
                                        '{poster}',
                                        '{created_at.strftime("%y-%m-%d %H:%M:%S")}')
                                        """
                    cursor.execute(command)
                except Exception as e:
                    print(f"couldnt insert\n{str(e)}")
                

                for character in splitter:

                    #check if in db
                    
                    # print(character)
                    character_id = get_char_id(character)
                    # print(character_id)
                    try:
                        cursor.execute(f"""INSERT INTO art_character (art_id, character_id)
                                                VALUES ('{art_id}',{character_id})""")
                    except Exception as e:
                        print(f"couldnt insert\n{str(e)}")
                    con.commit();
                print(created_at)
    con.commit();
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
    # stats_channel = int(config["bot"]["stats_channel"])
    space_names = config["bot"]["space_names"].split(',')
    print("Channels to watch: "+ str(channel_set))
    print("Settings loaded!")
    print("Connecting to db...")
    con = sqlite3.connect("art.db")
    cursor = con.cursor()
    print("Connected to db!")

except Exception as e:
    print("Error loading the settings! " + str(e))
    traceback.print_exc()
    exit()

print("Connecting to Discord...")
client.run(token)