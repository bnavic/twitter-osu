import requests
import os
import time
import tweepy
import tweepy.errors

consumer_key = os.getenv('API_key')
consumer_secret = os.getenv('API_secret')
bearer_token= os.getenv('bearer_token')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

client = tweepy.Client(bearer_token,consumer_key,consumer_secret,access_token,access_token_secret)
auth = tweepy.OAuth1UserHandler(consumer_key,consumer_secret, access_token, access_token_secret)
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
        token_url = 'https://osu.ppy.sh/oauth/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'public'
        }
        response = requests.post(token_url, data=data)
        return response.json().get('access_token')

    def recuperer_top_joueurs(self, limite):
        rankings_url = f'https://osu.ppy.sh/api/v2/rankings/{self.mode}/performance'
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            params = {'limit': limite}
            response = requests.get(rankings_url, headers=headers, params=params)
            if response.status_code == 200:
                top_players = response.json().get('ranking', [])
                return top_players[:2]
            else:
                print(f"Erreur lors de la récupération des classements: {response.status_code}")
                return []

    def infos_joueur(self, joueurs):
        for joueur in joueurs:
            pseudo = joueur['user']['username']
            pp = joueur['pp']
            global_rank = joueur['global_rank']
            previous_pp = self.previous_pp.get(pseudo)

            if previous_pp is not None and previous_pp != pp:
                pp_difference = pp - previous_pp
                message = f"{pseudo} a changé de pp: Ancien pp {previous_pp}, Nouveau pp {pp}, Différence: {pp_difference:.2f} pp"
                print(message)
                self.tweeter(message)

            self.previous_pp[pseudo] = pp
            print(pseudo, pp, global_rank)

    def tweeter(self, message):
        try:
            self.twitter_client.create_tweet(text=message)
            print("Tweet envoyé avec succès")
        except tweepy.TwitterServerError as e:
            print(f"Erreur lors de l'envoi du tweet: {e}")

    def surveiller_changements(self, intervalle, iterations):
        self.tweeter("Le bot Osu est lancé et commence à surveiller les changements de pp.")
        
        for _ in range(iterations):
            joueurs = self.recuperer_top_joueurs(2)
            self.infos_joueur(joueurs)
            time.sleep(intervalle)



std = OsuApiHelper(os.getenv('osu_api'),os.getenv('osu_api_secret'), 'osu', client)

std.surveiller_changements(intervalle=60, iterations=10)