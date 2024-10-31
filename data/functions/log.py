import os
import datetime

ERROR = 0
INFO = 1
WARNING = 2
SHUTDOWN = 3

def log(method:int,message:str):
    log_time_format = "%d.%m.%y %H:%M:%S:%f"
    time = datetime.datetime.now().strftime(log_time_format)[:-4]
    try:
        if not os.path.exists(os.path.join("data","logs")):
            os.mkdir(os.path.join("data","logs"))
        with open(os.path.join("data","logs","latest.log"),"w+") as file:
            if method == ERROR:
                print(f"[{time}] \033[91m [Error]: \033[0m{message}")
                file.write(f"[{time}] [Error]: {message}")
            elif method == WARNING:
                print(f"[{time}] \033[94m[Warning]: \033[0m{message}")
                file.write(f"[{time}] [Warning]: {message}")
            elif method == SHUTDOWN:
                print(f"[{time}] \033[94m[Shutdown]: \033[0m{message}")
                file.write(f"[{time}] [Shutdown]: {message}")
            else:
                print(f"[{time}] \033[92m[Info]: \033[0m{message}")
                file.write(f"[{time}] [Info]: {message}")
            file.close()
    except Exception as e:
        print(f"[{time}] \033[91m [Error] could not log: \033[0m{e}")