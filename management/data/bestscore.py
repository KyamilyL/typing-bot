import json

def load_bestscores():
    with open("data/bestscore.json", "r") as file:
        return json.load(file)

def save_bestscores(data):
    try:
        with open("data/bestscore.json", "w") as file:
            json.dump(data, file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    
def get_bestscores(difficulty, userid):
    data = load_bestscores()
    if str(userid) not in data[difficulty]:
        data[difficulty][str(userid)] = 0
    save_bestscores(data)
    return data[difficulty][str(userid)]

def set_bestscore(difficulty, userid, score):
    data = load_bestscores()
    data[difficulty][str(userid)] = score
    save_bestscores(data)