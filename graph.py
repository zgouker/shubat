import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3,csv,os

con = sqlite3.connect("art_prod.db")
cursor = con.cursor()

command = "!graph Squashua zg53 Abbielizx3"
char_list = command.split(" ")[1:]
print(char_list)




char_list = command.split(" ")[1:]
# resp = cursor.execute(f"""SELECT character_name, SUBSTR(post_date,0,9), COUNT(*) FROM art_character
#                           LEFT JOIN art_messages
#                           ON art_messages.art_id=art_character.art_id
#                           LEFT JOIN characters
#                           ON art_character.character_id=characters.character_id
#                           WHERE channel_id = 915394280510619649
#                           GROUP BY character_name, SUBSTR(post_date,0,9)
#                           """)
# resp = cursor.execute(f"""SELECT channel_id, SUBSTR(post_date,0,9), COUNT(*) FROM art_messages
#                           GROUP BY channel_id, SUBSTR(post_date,0,9)
#                           """)

resp = cursor.execute(f"""SELECT poster, SUBSTR(post_date,0,9), COUNT(*) FROM art_character
                          LEFT JOIN art_messages
                          ON art_messages.art_id=art_character.art_id
                          LEFT JOIN characters
                          ON art_character.character_id=characters.character_id
                          WHERE channel_id = 915394280510619649
                          GROUP BY poster, SUBSTR(post_date,0,9)
                          """)
resp_list = resp.fetchall()

all_dates_by_char = {}
cumulative_count = {}
# date_count_by_char = {}
temp_date_set = [a for a in resp_list if a[1][2]=='-']
oldest_date = min([a[1] for a in temp_date_set])
newest_date = max([a[1] for a in temp_date_set])
print(oldest_date,)
for char in char_list:
    all_dates_by_char[char] = {}
    for item in [a for a in resp_list if str(a[0])==char]:
        all_dates_by_char[char][item[1]] = item[2]

    cumulative_count[char] = 0
    # date_count_by_char[char] = {}

# print(all_dates_by_char["ina"])

datelist = pd.date_range(datetime.strptime(oldest_date,"%y-%m-%d"),datetime.strptime(newest_date,"%y-%m-%d"))
# print(datelist)

df = pd.DataFrame(columns=(["date"] + char_list))

for date in datelist:
    for char in char_list:
        formatted_date = date.strftime("%y-%m-%d")
        if(formatted_date in all_dates_by_char[char]):
            cumulative_count[char] = cumulative_count[char] + all_dates_by_char[char][formatted_date]
            print(date, char, all_dates_by_char[char][formatted_date])
        else:
            print(date, char, 0)






        # print(formatted_date)
        # print(all_dates_by_char[char].keys())

        # print(date, char, all_dates_by_char[char][formatted_date])
        # date_count_by_char[char][formatted_date] = cumulative_count[char]
    df.loc[len(df.index)] = [date] + [cumulative_count[a] for a in cumulative_count.keys()]
# print(df)
plt.figure(figsize=(16,8), dpi=150)
for char in char_list:
    df.set_index('date')[char].plot(label=char)
plt.legend()
plt.savefig('out.png')

