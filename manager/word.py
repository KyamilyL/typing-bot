import json

def load_words():
    with open("data/word.json", encoding="utf-8") as file:
        return json.load(file)