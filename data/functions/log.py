import os
import datetime

ERROR = 0
INFO = 1
WARNING = 2

def log(methode:int,message:str):
    log_time_format = "%d.%m.%y %H:%M:%S:%f"
    time = datetime.datetime.now().strftime(log_time_format)[:-4]
    try:
        if not os.path.exists(os.path.join("data","logs")):
            os.mkdir(os.path.join("data","logs"))
        with open(os.path.join("data","logs","latest.log"),"w+") as f:
            if methode == ERROR:
                print(f"[{time}] \033[91m [Error]: \033[0m{message}")
                f.write(f"[{time}] [Error]: {message}")
            elif methode == INFO:
                print(f"[{time}] \033[94m[Info]: \033[0m{message}")
                f.write(f"[{time}] [Info]: {message}")
            else:
                print(f"[{time}] \033[92m[Info]: \033[0m{message}")
                f.write(f"[{time}] [Info]: {message}")
            f.close()
    except Exception as e:
        print(f"[{time}] \033[91m [Error] could not log: \033[0m{e}")