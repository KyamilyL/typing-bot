import json
import os

from PIL import Image, ImageDraw, ImageFont

def load_words():
    with open("data/word.json", encoding="utf-8") as file:
        return json.load(file)
    
def create_image():
    for difficuly, list in load_words().items():
        for id, word in enumerate(list):
            image = Image.new("RGB", (1000, 200), (255, 255, 255))

            draw = ImageDraw.Draw(image)

            word_font = ImageFont.truetype(os.path.join("data/font/NotoSansJP-Regular.ttf") , 70)
            hira_font = ImageFont.truetype(os.path.join("data/font/NotoSansJP-Light.ttf") , 25)

            word_bbox = draw.textbbox((0, 0), word[0], font=word_font)
            word_x = (image.width - word_bbox[2] - word_bbox[0]) // 2
            draw.text((word_x, 70), word[0], font=word_font, fill=(0, 0, 0))

            hira_bbox = draw.textbbox((0, 0), word[1], font=hira_font)
            hira_x = (image.width - hira_bbox[2] - word_bbox[0]) // 2
            draw.text((hira_x, 50), word[1], font=hira_font, fill=(0, 0, 0))

            image.save(os.path.join(f"data/image/{difficuly}", f"{id}.png"))