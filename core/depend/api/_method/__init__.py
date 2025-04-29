import json
from lib.database import Redis

database = Redis()

def get_classify():
    classify = database.hgetall("classify")
    for cn in classify:
        context = classify[cn]
        print(json.loads(context))
        

if __name__ == "__main__":
    get_classify()