import json
from static import DB

def get_classify():
    classify = DB.hgetall("classify")
    for cn in classify:
        context = classify[cn]
        print(json.loads(context))
        
    
def download(files, toclients):
    pass
if __name__ == "__main__":
    get_classify()