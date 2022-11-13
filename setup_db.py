import sqlite3,csv,os

#initialize db and cursor
os.remove("art_prod.db")
con = sqlite3.connect("art_prod.db")
cursor = con.cursor()

#create tables
cursor.execute("""CREATE TABLE art_messages (
                    art_id TEXT PRIMARY KEY , 
                    message_id INTEGER,
                    server_id INTEGER,
                    channel_id INTEGER,
                    poster STRING,
                    post_date DATE);""")
cursor.execute("""CREATE TABLE characters (
                    character_id INTEGER PRIMARY KEY,
                    character_name TEXT);""")
cursor.execute("""CREATE TABLE art_character (
                    art_id TEXT,
                    character_id INTEGER,
                    PRIMARY KEY (art_id, character_id));""")
# cursor.execute("""CREATE TABLE websites (
#                     site_id INTEGER PRIMARY KEY,
#                     site_name TEXT);""")

#populate sites from csv
# with open("db_scripts/sites.csv","r") as csvfile:
#     for line in csv.DictReader(csvfile):
#         cursor.execute(f"""INSERT INTO websites (site_id,site_name) 
#                            VALUES ({line["site_id"]},'{line["site_name"]}');""")



resp = cursor.execute("SELECT name from sqlite_master")

resp = cursor.execute(f"SELECT character_id FROM characters WHERE character_name='a';")

con.commit()
print(resp.fetchall())
