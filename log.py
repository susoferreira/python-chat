from datetime import datetime
LOG_FILE=""
    

def log(*msg):
    global LOG_FILE
    if LOG_FILE =="":
        raise Exception("Log: no logfile set, use log.LOG_FILE to set it")
    out = open(LOG_FILE,"a")
    print(datetime.now() ,msg,file=out)