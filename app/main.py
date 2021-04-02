import os
from flask import Flask, render_template, redirect, g, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import requests
from urllib.parse import quote


AUTHORIZATION_HEADER = ""
#  Client Keys
CLIENT_ID = "4300c682d48b480d96478da07107ca59"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")


# Server-side Parameters
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

REDIRECT_URI = "https://spotify-recos.herokuapp.com/callback/q"
#REDIRECT_URI = "http://127.0.0.1:5000/callback/q"

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "playlist-read-private playlist-read-collaborative",
    "client_id": CLIENT_ID
}

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login")
def auth():

    url_args = "&".join(["{}={}".format(key, quote(val))
                        for key, val in auth_query_parameters.items()])
    auth_url = "https://accounts.spotify.com/authorize?client_id=4300c682d48b480d96478da07107ca59&response_type=code&redirect_uri=https%3A%2F%2Fspotify-recos.herokuapp.com%2Fcallback&scope=playlist-read-private%20playlist-read-collaborative"
    return redirect(auth_url)


@app.route('/<path:text>', methods=['GET', 'POST'])
def all_routes(text):
    print(text)
    if text.startswith('https://spotify-recos.herokuapp.com/callback'):
        auth_token = request.args['code']
        code_payload = {
            "grant_type": "authorization_code",
            "code": str(auth_token),
            "redirect_uri": REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
        post_request = requests.post(
            "https://accounts.spotify.com/api/token", data=code_payload)

        response_data = json.loads(post_request.text)
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        token_type = response_data["token_type"]
        expires_in = response_data["expires_in"]

        global AUTHORIZATION_HEADER    # Needed to modify global copy of globvar
        AUTHORIZATION_HEADER = {"Authorization": "Bearer {}".format(access_token)}

        return render_template("web-app.html")
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
