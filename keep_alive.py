from flask import Flask
from threading import Thread
import random
import time
import requests
import logging

'''logging.basicConfig(filename="serverlog.log",
level=logging.INFO, 
format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',datefmt='%H:%M:%S')'''

app = Flask('')
@app.route('/')
def home():
    return "Dumbot is online."

def run():
  app.run(host='0.0.0.0',port=random.randint(2000,9000)) 

def ping(target, debug):
    while(True):
      logserv = logging.getLogger("log") 
      r = requests.get(target)
      stat_code = r.status_code
      if(debug == True):
        #print("Status Code: " + str(stat_code))
        logserv.info("Status code: {}".format(str(stat_code)))
      time.sleep(random.randint(180,300)) #alternate ping time between 3 and 5 minutes

def awake(target, debug=False):  
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.logger.disabled = True  
    t = Thread(target=run)
    r = Thread(target=ping, args=(target,debug,))
    t.start()
    r.start()