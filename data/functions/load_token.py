import os
from data.functions.log import *

def load_token():
    try:
        with open(os.path.join("data","token"),"r") as f:
            token = f.readline(71)
            f.close()
            return token
    except Exception as e:
        log(ERROR,f"Cannot load token: {e}")
        raise Exception