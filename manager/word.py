import json
import os

from PIL import Image, ImageDraw, ImageFont

def load_words():
    with open("data/word.json", encoding="utf-8") as file:
        return json.load(file)

def create_image():
    os.makedirs(f"data/image", exist_ok=True)
    for difficulty, list in load_words().items():
        os.makedirs(f"data/image/{difficulty}", exist_ok=True)
        for id, word in enumerate(list):
            if os.path.exists(f"data/image/{difficulty}/{id}.png"):
                continue

            word_font = ImageFont.truetype(os.path.join("data/font/NotoSansJP-Regular.ttf"), 100)
            hira_font = ImageFont.truetype(os.path.join("data/font/NotoSansJP-Light.ttf"), 50)

            temp_image = Image.new("RGB", (1, 1))
            temp_draw = ImageDraw.Draw(temp_image)
            width = temp_draw.textbbox((0, 0), word[0], font=word_font)[2] + 150

            image = Image.new("RGB", (width, 300), (255, 255, 255))
            draw = ImageDraw.Draw(image)

            word_bbox = draw.textbbox((0, 0), word[0], font=word_font)
            word_x = (image.width - word_bbox[2] - word_bbox[0]) // 2
            word_y = (image.height - word_bbox[3] - word_bbox[1]) // 2
            draw.text((word_x, word_y), word[0], font=word_font, fill=(0, 0, 0))

            hira_bbox = draw.textbbox((0, 0), word[1], font=hira_font)
            hira_x = (image.width - hira_bbox[2] - hira_bbox[0]) // 2
            hira_y = ((image.height - hira_bbox[3] - hira_bbox[1]) // 2) - 80
            draw.text((hira_x, hira_y), word[1], font=hira_font, fill=(0, 0, 0))

            image.save(os.path.join(f"data/image/{difficulty}/{id}.png"))

            print(f"CreateImage: data/image/{difficulty}/{id}.png")