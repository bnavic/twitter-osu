from PIL import Image, ImageDraw, ImageFont
import requests

class imageModifier:
    def __init__(self, image):
        self.image = image
        self.draw = ImageDraw.Draw(image)


    def getDraw(self):
        return self.draw
    @staticmethod
    def ajoutImage(img, idx, image):
        image_size_1 = (350, 350)
        img = img.resize(image_size_1)

        mask = Image.new("L", image_size_1, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle((0, 0, image_size_1[0], image_size_1[1]),radius=20, fill=255)

        image_rajout = Image.new("RGBA", image_size_1)
        image_rajout.paste(img, (0, 0), mask)

        if idx == 1:
            position = (75, 100)
        else:
            position = (780, 750)

        # Coller sur le fond principal
        image.paste(image_rajout, position, mask)



    @staticmethod
    def whichFill(diff,previous_diff, image):
        # Détermine la couleur de remplissage en fonction de la différence
        if diff > 0:
            fill = (220, 255, 186)  # Vert
        else:
            fill = (255, 112, 102)  # Rouge

        # Afficher le message de différence
        real_diff = diff - previous_diff
        message = f"{diff} pp(+{real_diff})"
        font = ImageFont.truetype("Aller_Bd.ttf", size=60)

        draw = ImageDraw.Draw(image)
        draw.text((image.width // 2 - 280, image.height // 2 - 40), message, fill=fill, font=font)

    @staticmethod
    def saveImageByLink(link, idx):
        # Récupérer l'image à partir d'un lien et la sauvegarder
        image = Image.open(requests.get(link, stream=True).raw)
        image.save(f"{idx}.png")
        return f"{idx}.png"
