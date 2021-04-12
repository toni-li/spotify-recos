# tutorial: https://github.com/drshrey/spotify-flask-auth-example
import os
import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.

def process(user_id, song, token):
    import requests
    import sys
    import spotipy
    import spotipy.util as util

   # scope = 'playlist-read-private, playlist-read-collaborative'

    #util.prompt_for_user_token("toni1li131",scope,client_id='4300c682d48b480d96478da07107ca59',client_secret='5a034c056898492b966e34c01a995d28',redirect_uri='https://oauth.pstmn.io/v1/browser-callback')

    # SETTINGS
    # refreshing token
    #token = util.prompt_for_user_token("toni1li131", scope)
    #print(token)
    #user_id = "toni1li131"

    # ------------------ getting list of playlists from user ---------------------- #
    # PERFORM THE QUERY
    query = "https://api.spotify.com/v1/users/" + user_id + "/playlists"
    # print(query)

    response = requests.get(query,
                            headers={"Content-Type": "application/json",
                                        "Authorization": f"Bearer {token}"})
    json_response = response.json()

    playlists = []
    for i, j in enumerate(json_response['items']):
        #print(f"{i + 1}) \"{j['name']}\" at {j['href']}")
        playlists.append(j['href'])


    # print('Public Playlists:')
    # print(playlists)

    #test = ["https://api.spotify.com/v1/playlists/1Am6znV9CWkrdUwpAAPpK6"]
    # ------------------ getting list of songs in the playlist(s) ---------------------- #
    playlistURIs = []
    for i in playlists:
        # PERFORM THE QUERY
        query = i + "/tracks?offset=0&market=US"
        #print(query)

        response = requests.get(query,
                            headers={"Content-Type": "application/json",
                                        "Authorization": f"Bearer {token}"})
        json_response = response.json()
        #print(json_response)
        for i, j in enumerate(json_response['items']):
            #print(f"{i + 1}) \"{j['track']['uri']}")
            playlistURIs.append(j['track']['uri'])

    #print(playlistURIs)


    # ------------------ getting track information for song ---------------------- #
    song = song.split("/")
    songID = song[4]
    songID = songID.split("?")
    songID = songID[0]
    
    #print(songID)

    # PERFORM THE QUERY
    query = "https://api.spotify.com/v1/tracks/" + songID + "?market=US"

    response = requests.get(query,
                        headers={"Content-Type": "application/json",
                                    "Authorization": f"Bearer {token}"})
    json_response = response.json()
    #print(json_response['uri'])

    songURI = json_response['uri']

    # ------------------ checking to see if song URI is in any of the playlists ---------------------- #
    if songURI in playlistURIs:
        message = "The song was found in their library, better not recommend it :("
    else:
        message = "Recommend the song!"


    return(message)



app = Flask(__name__)

#  Client Keys
CLIENT_ID = "4300c682d48b480d96478da07107ca59"
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
# print("Client Secret: " + str(CLIENT_SECRET))

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "https://spotify-recos.herokuapp.com"
#CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
#REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
REDIRECT_URI = "https://spotify-recos.herokuapp.com/callback/q" 
SCOPE = "playlist-read-private playlist-read-collaborative"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback/q", methods=['GET','POST'])
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    print(response_data)
    global access_token
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}


    return render_template("web-app.html")

@app.route('/get_data', methods=['POST'])
def get_data():
    username = request.form['user-name']
    song = request.form['song']

    print("Spotify Username: " + username)
    print("URL of the song you want to recommend: " + song)

    message = process(username, song, access_token)

    return render_template('success.html', message=message)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)