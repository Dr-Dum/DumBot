import os
import discord
import pandas as pd
import requests
import json
import gspread
import sys
import time

import keep_alive
keep_alive.keep_alive()
from oauth2client.service_account import ServiceAccountCredentials
pd.options.display.max_rows = 999

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('botcommandsapi.json', scope)

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
#print(df_cmd_)

other_cmds_ = ['?gm','?check_commands','?dumbot','?restart_dumbot']

other_cmds = {'**?gm**':'Send and inspirational message to the boys.','**?check_commands**':'Check the available dumbot commands.','**?dumbot**':'Commands to check all possible DumBot commands','**?restart_dumbot**':'Restart dumbot after commands have been added.'}

df_other_cmds = pd.DataFrame(other_cmds, index=['Misc Commands']).T
#print(df_other_cmds)

cmd_update_msg = '> **Please dm @Dr Dum#3527 if you have any commands you would like added.**'

status_msg = "> **Additionally if you think dumbot has gone down, please dm Dr Dum. You can see its current status at this url: https://stats.uptimerobot.com/JKrx3tBq8j/788943864 **"

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
  if msg.startswith('?'):
    if msg in cmd_dict.keys():
      await message.channel.send(cmd_dict[msg])
    elif msg not in cmd_dict.keys() and msg not in other_cmds_:
      await message.channel.send('That command is invalid. Please refer to the  <#874182927905333289> channel for a list of possible commands.')

  if msg.startswith('?gm'):
    quote = get_quote()
    await message.channel.send(quote)

  if msg.startswith('?check_commands'):
    await message.channel.send('> **List of Database commands:**')
    await message.channel.send(df_cmd_)

  if msg.startswith('?dumbot'):
    await message.channel.send('> **List of Database commands:**')
    await message.channel.send(df_cmd_)
    await message.channel.send('> **List of Misc. Commands:**')
    await message.channel.send(df_other_cmds)
    await message.channel.send(cmd_dict['troublemsg'])

  if msg.startswith('?restart_dumbot'):
    await message.channel.send('Restarting to refresh command database...')
    time.sleep(5)
    await message.channel.send("Dumbot's database has been updated. It may take up to a minute for the commands to become available.")
    os.execl(sys.executable, sys.executable, *sys.argv)
client.run(token)






