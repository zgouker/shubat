import discord, traceback, configparser,time,pytz,sqlite3
from datetime import date, timedelta, datetime

intents = discord.Intents(messages=True, guilds=True,message_content=True)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    NUM_CHANNEL_TOP = 5
    NUM_POSTER_TOP = 5

    global spcae_names
    print('Connected as: ' + client.user.name + "!")
    local_tz = pytz.timezone('US/Eastern')
    now = datetime.now().replace(tzinfo=local_tz)
    print("Current time: " + now.strftime("%m/%d/%Y, %H:%M:%S"))
    cutoff = now - timedelta(weeks=1)
    print("Cutoff time: " + cutoff.strftime("%m/%d/%Y, %H:%M:%S"))
    cutoff_sql_string = cutoff.strftime('%y-%m-%d %H:%M:%S')
    print(cutoff_sql_string)
    print("Building stats...")

    for ch in channel_set:
        resp = cursor.execute(f"""SELECT poster,COUNT(*) 
                        FROM art_messages
                        WHERE channel_id={str(ch)}
                        AND post_date>'{cutoff_sql_string}'
                        GROUP BY poster
                        ORDER BY 2 DESC""")
        user_list = resp.fetchall()

        channel_name = client.get_channel(int(ch)).name


        resp = cursor.execute(f"""SELECT COUNT(*) 
                        FROM art_messages
                        WHERE channel_id={str(ch)}
                        AND post_date>'{cutoff_sql_string}'
                        """)
        total_count = resp.fetchone()[0]

        resp = cursor.execute(f"""SELECT COUNT(DISTINCT character_id)
                                        FROM art_character
                                        LEFT JOIN art_messages
                                        ON art_messages.art_id=art_character.art_id
                                        WHERE channel_id={str(ch)}
                                        AND post_date>'{cutoff_sql_string}'
                                        """)
        character_count = resp.fetchone()[0]                                        

        stringbuilder = f"Stats for #{channel_name}:\nTimeframe: {cutoff.strftime('%m/%d/%Y %H:%M')} EST - {now.strftime('%m/%d/%Y %H:%M')} EST\nTotal art pieces: {str(total_count)}\nTotal characters: {str(character_count)}\n"
        stringbuilder = stringbuilder + "Top Characters:\n"

        resp = cursor.execute(f"""SELECT character_name, COUNT(*)
                            FROM art_character
                            LEFT JOIN art_messages
                            ON art_messages.art_id=art_character.art_id
                            LEFT JOIN characters
                            ON art_character.character_id=characters.character_id
                            WHERE channel_id={ch}
                            AND post_date>'{cutoff_sql_string}'
                            GROUP BY character_name
                            ORDER BY 2 DESC
                            LIMIT {NUM_CHANNEL_TOP}
                            """)
        char_list = resp.fetchall()

        for count,char in enumerate(char_list):
            stringbuilder = stringbuilder + f"{count+1}. {char[0]} ({char[1]})\n"
        
        stringbuilder = stringbuilder + "\n\nTop by person:\n"

        for user in user_list:
            stringbuilder = stringbuilder + f"{user[0]} ({user[1]} total):\n"
            resp = cursor.execute(f"""SELECT character_name, poster, COUNT(*)
                                        FROM art_character
                                        LEFT JOIN art_messages
                                        ON art_messages.art_id=art_character.art_id
                                        LEFT JOIN characters
                                        ON art_character.character_id=characters.character_id
                                        WHERE poster='{user[0]}' 
                                        AND channel_id={str(ch)}
                                        AND post_date>'{cutoff_sql_string}'
                                        GROUP BY character_name, poster
                                        ORDER BY 3 DESC
                                        LIMIT 5
                                        """)
            char_list = resp.fetchall()
            for count,char in enumerate(char_list):
                stringbuilder = stringbuilder + f"{count+1}. {char[0]} ({char[2]})\n"
            stringbuilder = stringbuilder + "\n"
    
        print(stringbuilder)
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
    token = config["bot"]["prod_token"]
    stats_channel = int(config["bot"]["stats_channel"])
    space_names = config["bot"]["space_names"].split(',')
    print("Channels to watch: "+ str(channel_set))
    print("Settings loaded!")
    con = sqlite3.connect("art_prod.db")
    cursor = con.cursor()
except Exception as e:
    print("Error loading the settings! " + str(e))
    traceback.print_exc()
    exit()

print("Connecting to Discord...")
client.run(token)