import configparser

def build_url(message):
    return "https://discord.com/channels/"+str(message.guild.id)+"/"+str(message.channel.id)+"/"+str(message.id)

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
    if("artworks" in message_content):
        id_start = message_content.find("artworks/")
        cur_substr = message_content[id_start+9:]
        cur_substr = cur_substr.split("?")[0]
        cur_substr = cur_substr.split("/")[0]
    elif("member_illust" in message_content):
        id_start = message_content.find("id=")
        cur_substr = message_content[id_start+3:]
        cur_substr = cur_substr.split("?")[0]
        cur_substr = cur_substr.split("/")[0]        
    cur_substr = "p" + cur_substr + "-" + str(message.channel.id)
    return cur_substr