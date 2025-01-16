import requests
import os
import time
import tweepy
import logging
from imageModifier import imageModifier
from PIL import Image, ImageDraw, ImageFont

image = Image.open("bgv2.jpg")
im = imageModifier(image)

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
# Clés et jetons d'authentification (assurez-vous de les sécuriser correctement)
consumer_key = 'iO1i4E8skesRVo1zTSrTk4s3v'
consumer_secret = 'lvvi2fld4oeJQjBUdMzbEbv0ZTfjfhp39E6C8Uagfk0zyErl6d'
access_token = '1713642445332746240-r8gtiNogPuj8LF6OpPbg81BN0MVsLG'
access_token_secret = 'NN6FW9ikxK7iWRmbkWI8H33DJepHUbN7qzAe3gf8sNB2l'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAHUiqgEAAAAAE3JwnxzpeNuroHEVcpv0fvlrVLY%3D4tSYC3Ic59dRXq4XUNmNWoqik1u0GU7S0iE4TzOJIeLAg25NxS'

# Initialisation du client Twitter
client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

class OsuApiHelper:
    def __init__(self, client_id, client_secret, mode, twitter_client):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.obtenir_token()
        self.mode = mode
        self.previous_pp = {}
        self.twitter_client = twitter_client

    def obtenir_token(self):
        try:
            token_url = 'https://osu.ppy.sh/oauth/token'
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
                'scope': 'public'
            }
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'obtention du token: {e}")
            return None

    def recuperer_top_joueurs(self, limite):
        try:
            rankings_url = f'https://osu.ppy.sh/api/v2/rankings/{self.mode}/performance'
            if self.token:
                headers = {'Authorization': f'Bearer {self.token}'}
                params = {'limit': limite}
                response = requests.get(rankings_url, headers=headers, params=params)
                response.raise_for_status()
                top_players = response.json().get('ranking', [])
                return top_players[:2]
            else:
                logger.error("Token non disponible.")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des classements: {e}")
            return []

    def infos_joueur(self, joueurs):
        if len(joueurs) == 2:
            joueur1 = joueurs[0]
            joueur2 = joueurs[1]

            pseudo1 = joueur1['user']['username']
            pp1 = joueur1['pp']            

            acc1 = round(joueur1['hit_accuracy'],2)
            previous_pp1 = self.previous_pp.get(pseudo1)

            pseudo2 = joueur2['user']['username']
            pp2 = joueur2['pp']
            acc2 = round(joueur2['hit_accuracy'],2)
            previous_pp2 = self.previous_pp.get(pseudo2)

            if previous_pp1 != pp1 or previous_pp2 != pp2:

                image_1 = im.saveImageByLink(joueur1['user']['avatar_url'], 1)
                image_2 = im.saveImageByLink(joueur2['user']['avatar_url'], 2)

                if not os.path.exists(image_1) or not os.path.exists(image_2):
                    logger.error("Les images des avatars ne sont pas accessibles.")
                    return

                pp_difference = round(pp1 - pp2, 2)
                
                im.ajoutImage(Image.open(image_1), 1, image)
                im.ajoutImage(Image.open(image_2), 2, image)
                
                font = ImageFont.truetype("Aller_Bd.ttf", size=80)
                font_pp = ImageFont.truetype("Aller_Bd.ttf", size=50)
                
                im.getDraw().text((500, 250), f"{pp1} pp", fill=(255, 255, 255), font=font_pp)
                im.getDraw().text((380, 900), f"{pp2} pp", fill=(255, 255, 255), font=font_pp)
                im.getDraw().text((500, 100), f"{pseudo1}", fill=(255, 255, 255), font=font)
                im.getDraw().text((380, 750), f"{pseudo2}", fill=(255, 255, 255), font=font)
                im.getDraw().text((500, 350), f"{acc1}%", fill=(255, 255, 255), font=font_pp)
                im.getDraw().text((380, 1000), f"{acc2}%", fill=(255, 255, 255), font=font_pp)
                
                print("test")
                if previous_pp1 is not None and previous_pp2 is not None:
                    im.whichFill(pp_difference,int(previous_pp1)-int(previous_pp2), image)
                else:
                    im.whichFill(pp_difference,0, image)
                image.save("result.png")
                image.show()

                message = f'Difference between {pseudo1} and {pseudo2} is {pp_difference} pp.'
                logger.info(message)
                self.tweeter(message)
                self.previous_pp[pseudo1] = pp1
                self.previous_pp[pseudo2] = pp2 

    def tweeter(self, message):
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            message_with_timestamp = f"{message} ({timestamp})"
            media = api.media_upload("result.png")
            media_id = media.media_id
            self.twitter_client.create_tweet(text=message_with_timestamp, media_ids=[media_id])
            logger.info("Tweet envoyé avec succès")
        except tweepy.TwitterServerError as e:
            logger.error(f"Erreur lors de l'envoi du tweet: {e}")

    def tweeterr(self,message):
        return 

    def surveiller_changements(self, intervalle, iterations):

        for _ in range(iterations):
            try:
                joueurs = self.recuperer_top_joueurs(2)
                self.infos_joueur(joueurs)
                time.sleep(intervalle)
            except Exception as e:
                logger.error(f"Erreur dans la boucle de surveillance: {e}")
                time.sleep(intervalle)  # Pause avant de réessayer

osu_helper = OsuApiHelper(
    client_id=31119,
    client_secret='uoG3VN9xzlVdW8b6PPEjgk1ohVnZt1hXMqAn5wku',
    mode='osu',
    twitter_client=client
)

osu_helper.surveiller_changements(intervalle=60, iterations=9999)
