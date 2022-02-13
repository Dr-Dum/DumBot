import os
import discord
import pandas as pd
import requests
import json
import gspread
import sys
import numpy as np
import time
from datetime import datetime
import logging
import replit
replit.clear()

'''
Logging info for troubleshooting
'''

now = datetime.now()

logging.basicConfig(filename="LogFiles/log {}.log".format(now),
level=logging.DEBUG, 
format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',datefmt='%H:%M:%S')
logging.info("___________NEW RUN STARTING___________")
logging.info("Code started at: {}".format(now))


'''
Keep bot alive indefinitely
'''

import keep_alive
keep_alive.awake("https://DumBot.drdum.repl.co", True,now=now)

'''
Connect dumbot to google sheet with the commands
'''

from oauth2client.service_account import ServiceAccountCredentials
pd.options.display.max_rows = 1000

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

auth_creds = json.loads(os.getenv("GoogleAuthJson"))

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_dict(auth_creds,scope)

# authorize the clientsheet 
client_ = gspread.authorize(creds)

# get the instance of the Spreadsheet
sheet = client_.open('BotCommands')

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)

# get all the records of the data
records_data = sheet_instance.get_all_records()

records_df = pd.DataFrame.from_dict(records_data)
# view the data
#print(records_df)

cmd_dict = {}

for index, row in records_df.iterrows():
  cmd_dict[row['Command']] =  row['Link']

troub_msg = cmd_dict['troublemsg']
del cmd_dict['troublemsg']
#print(cmd_dict)

#pull token
token = os.environ['DumBotKey']

#define api address for quotes
quote_repo = 'https://zenquotes.io/api/random'

#return quotes from API
def get_quote():
  response = requests.get(quote_repo)
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + ' - ' + json_data[0]['a']
  return (quote)

#Create instance of client (connection to discord)
client = discord.Client()

cmd_list = cmd_dict.keys()
df_cmd = pd.DataFrame({'Commands': cmd_list})
df_cmd_ = df_cmd.sort_values('Commands',ascending=True).reset_index(drop=True)
#troub_msg = df_cmd_.loc[df_cmd_['Commands'] == 'troublemsg']
#print(troub_msg) 
df_cmd_split = np.array_split(df_cmd_, 2)
df_cmd_split_1 = df_cmd_split[0]
df_cmd_split_2 = df_cmd_split[1]

other_cmds = {'**?gm**':'Send and inspirational message to the boys.','**?av**':'Return the avatar of all mentioned users. If no user is mentioned, it returns the author avatar','**?check_commands**':'Check the available dumbot database commands.','**?dumbot**':'Commands to check all possible DumBot commands','**?cmds**': 'check commands containing a string.','**?restart_dumbot**':'Restart dumbot after commands have been added.'}

other_cmds_ = []

admin_roles = {'PCM':608926975054315533,'Admin': 539133957136973834}

for item in other_cmds.keys():
  other_cmds_.append(item.strip('*'))

df_other_cmds = pd.DataFrame(other_cmds, index=['Misc Commands']).T
#print(df_other_cmds)

github_msg = "If you're interested in seeing the dumbot code, please feel free to check out the github page here: https://github.com/HerrDoktorDum/DumBot"

#Register event with callback
@client.event
#Call when bot is ready to be used
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

#Register event with callback
@client.event
#Send message if command sent
async def on_message(message):
  #check to make sure message is not from bot
  if message.author == client.user:
    return

  msg = message.content.lower()

  '''
  Check if command sent is valid
  '''
  if msg.startswith('?'):
    split_msg = msg.split('@')
    if msg in cmd_dict.keys():
      await message.channel.send(cmd_dict[msg])
    elif msg not in cmd_dict.keys() and msg not in other_cmds_ and set(msg) != set('?') and not msg.startswith('? ') and split_msg[0].split()[0] not in other_cmds_ and split_msg[0].split()[0] != '?reset_nick' and msg.split()[0] != '?cmds' and msg.split()[0] != '?cmdz' and msg.count("?") == 1:
      await message.channel.send('That command is invalid. Please refer to the  <#874182927905333289> channel for a list of possible commands.')
  

  '''
  Commands to check DB info or refresh commands
  '''
        
  if msg.startswith('?check_commands'):
    await message.channel.send('> **List of Database commands:**')
    await message.channel.send(df_cmd_split_1)
    await message.channel.send(df_cmd_split_2.to_string(header=False))

  if msg.startswith('?cmds '):
    find_cmds = msg.split()[1]
    #print(find_cmds)
    cmd_match = [s for s in cmd_dict.keys() if find_cmds in s]
    if len(cmd_match) == 0:
      await message.channel.send('Sorry, there are no commands containing that string.')
    else:
      await message.channel.send('{} commands were found that contain that string'.format(len(cmd_match)))
      await message.channel.send(cmd_match)

  if msg.startswith('?cmdz ') and str(message.author) == 'Dr Dum#3527':
    find_cmds = msg.split()[1]
    #print(find_cmds)
    cmd_match = [s for s in cmd_dict.keys() if find_cmds in s]
    for i in cmd_match:
      await message.channel.send(cmd_dict[i])
  elif msg.startswith('?cmdz ') and str(message.author) != 'Dr Dum#3527':
    await message.channel.send('You are not authorized to use that command.')

  if msg.startswith('?dumbot'):
    await message.channel.send('> **List of Database commands:**')
    await message.channel.send(df_cmd_split_1)
    #await message.channel.send(df_cmd_split_2)
    await message.channel.send(df_cmd_split_2.to_string(header=False))
    await message.channel.send('> **List of Misc. Commands:**')
    await message.channel.send(df_other_cmds)
    await message.channel.send(troub_msg)
    await message.channel.send(github_msg)
    
  if msg.startswith('?restart_dumbot'):
    await message.channel.send('Restarting to refresh command database...')
    time.sleep(5)
    await message.channel.send("Dumbot's database has been updated. It may take up to a minute for the commands to become available.")
    os.execl(sys.executable, sys.executable, *sys.argv)

  '''
  Extra commands
  '''

  if msg.startswith('?gm'):
    quote = get_quote()
    await message.channel.send(quote)

  if msg.startswith('?reset_nick') and str(message.author) == 'Dr Dum#3527':
    users_taged = message.mentions
    #print(users_taged[0].nick)
    await users_taged[0].edit(nick="DumBot")
    await message.channel.send('Dumbot Username Reset. Rbd is a fucking idiot.')

  if msg.startswith('?av'):
    users_taged = message.mentions
    if len(users_taged) == 0:
      await message.channel.send(message.author.avatar_url)
    elif len(users_taged) == 1:
      await message.channel.send(users_taged[0].avatar_url)
    elif len(users_taged) > 1:
      counter = 0
      for i in users_taged:
        await message.channel.send(users_taged[counter].avatar_url)
        counter += 1

try:
  client.run(token)
except:
  os.system("kill 1")
