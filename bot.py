from discord.ext import commands, tasks
import discord
import tweepy
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv('.env')
id = 1522443992847335425


consumer_key = os.environ["Key"]
consumer_secret = os.environ["Secret"]
bearer = os.environ["Bearer"]
access_token = os.environ['Token']
access_token_secret = os.environ['TokenSecret']

prefix = "%"
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Loads server data
dataFile = open('data/data.json')
server_data = json.load(dataFile)

# Writes the current server data to the data json
def write_data():
   with open('data/data.json', 'w') as out:
      json.dump(server_data, out)

print(server_data)

client = tweepy.Client(bearer_token = bearer, consumer_key = consumer_key, consumer_secret=consumer_secret, access_token= access_token, access_token_secret=access_token_secret)

# Gets tweet links and returns in list 
def get_tweet_links(num_tweets):
    global id
    tweet_list = client.get_users_tweets(id = id, tweet_fields = ['created_at', 'text', 'id', 'attachments', 'author_id', 'entities'], media_fields = ['url'], expansions=['attachments.media_keys', 'author_id']).data
    if num_tweets > 10:
       num_tweets = 10
    links = []
    for i in range(num_tweets):
       link = tweet_list[i].id
       links.append("https://twitter.com/twitter/status/{}".format(link))
    return links


# Get tweet ids and returns in list
def get_tweet_ids(num_tweets):
    global id
    tweet_list = client.get_users_tweets(id = id, tweet_fields = ['created_at', 'text', 'id', 'attachments', 'author_id', 'entities'], media_fields = ['url'], expansions=['attachments.media_keys', 'author_id']).data
    if num_tweets > 10:
       num_tweets = 10
    ids = []
    for i in range(num_tweets):
       currid = tweet_list[i].id
       ids.append(currid)
    return ids

# Initializing code

# tweet cache to store current tweets and check for updates

tweet_cache = get_tweet_ids(10)

def update_tweets():
    global tweet_cache
    current_tweets = get_tweet_ids(10)
    # Same tweets, so no new updates
    if current_tweets[0] == tweet_cache[0]:
        return []
    new_tweets = []
    for i in range(len(current_tweets)):
        # Found the old "most current" tweet in cache so no more difference 
        if current_tweets[i] == tweet_cache[0]:
            break
        new_tweets.append("https://twitter.com/twitter/status/{}".format(current_tweets[i]))
    tweet_cache = current_tweets
    return new_tweets
      

# Bot Code
@bot.event
async def on_guild_join(guild):
    currId = guild.id
    server_data[currId] = {'updateFood': False,
                             'channelToUpdate': 0,
                             'hoursToCheck': 0}
    write_data()
    
@bot.event
async def on_ready():
    update.start()
    await bot.change_presence(status=discord.Status.online,activity=discord.Activity(name=prefix, type=discord.ActivityType.listening))

@bot.command()
async def hello(ctx):
  await ctx.channel.send('Hello, ' + ctx.author.display_name + "!")

@bot.command()
async def check_config(ctx):
   currConfig = server_data[str(ctx.guild.id)]
   await ctx.channel.send(
      "Configs for server with name: {} \nTo Check for food updates: {} \nChannel ID of food updates: {}\nHours to check for updates: {} \nIf you want to set up auto-check for free food updates, use the **start_update** command."
      .format(ctx.guild.name, currConfig['updateFood'], currConfig['channelToUpdate'], currConfig['hoursToCheck'])
   )

@bot.command()
async def recent(ctx):
   tweet_link = get_tweet_links(1)
   await ctx.channel.send(tweet_link[0])

@bot.command()
async def food(ctx, num = None):
    if num is None:
      num = 1
    num = int(num)
    if num > 10:
        num = 10
        await ctx.channel.send("Maximum number of food requests is 10, defaulting to 10.")
    tweet_links = get_tweet_links(num)
    for i in tweet_links:
        await ctx.channel.send(i)

@bot.command()
async def start_update(ctx):
   server_data[str(ctx.guild.id)]['updateFood'] = True
   server_data[str(ctx.guild.id)]['hoursToCheck'] = 3
   write_data()
   await ctx.channel.send("Updates for free food have started.\nRemember to set up which channel you want updates using **channel_set** command, and how many hours you want it to check with **hours_set**.\nCurrent hours to check are default set to 3.")
   
@bot.command()
async def stop_update(ctx):
   server_data[str(ctx.guild.id)]['updateFood'] = False
   server_data[str(ctx.guild.id)]['hoursToCheck'] = 0
   write_data()
   await ctx.channel.send("Updates for free food have been stopped. To restart, use **start_update** command.")

@bot.command()
async def channel_set(ctx):
   channel_id = ctx.channel.id
   server_data[str(ctx.guild.id)]['channelToUpdate'] = channel_id
   write_data()
   await ctx.channel.send("This channel has been chosen for updating free food events. ID: {}".format(channel_id))

@bot.command()
async def channel_erase(ctx):
   server_data[str(ctx.guild.id)]['channelToUpdate'] = 0
   write_data()
   await ctx.channel.send("Channel to update free food events has been unselected.\nYou won't receive any new free food event updates until you reset a new channel with **channel_set**.")

#@bot.command()
#async def remove(ctx):
#   tweet_cache.remove(tweet_cache[0])

@tasks.loop(hours=1)
async def update():
    serverIDs = list(server_data.keys())
    for i in serverIDs:
        toUpdate = server_data[i]['updateFood']
        channelID = int(server_data[i]['channelToUpdate'])
        timeToUpdate = int(server_data[i]['hoursToCheck'])
        if channelID == 0:
           continue
        if toUpdate == False:
           continue
        if timeToUpdate == 0:
           continue
        channel = bot.get_channel(channelID)
        currHr = datetime.now().hour
        if currHr % timeToUpdate == 0:
            new_tweets = update_tweets()
            if new_tweets is None or len(new_tweets) == 0:
                continue
            for link in new_tweets:
               await channel.send(link)
            

password = os.environ['discordPassword']
bot.run(password)