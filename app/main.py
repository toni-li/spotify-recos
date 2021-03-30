from flask import Flask, render_template, request, redirect, g
from urllib.parse import quote

# ------------------ refreshing authorization token ---------------------- #
AUTHORIZATION_HEADER = ""
# Client Keys
CLIENT_ID = "4300c682d48b480d96478da07107ca59"
CLIENT_SECRET = "5a034c056898492b966e34c01a995d28"

# Server-side Parameters
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

REDIRECT_URI = "https://spotify-recos.herokuapp.com/callback/q"

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "playlist-read-private",
    "client_id": CLIENT_ID
}

app = Flask(__name__)


def process(user_id, song):
    import requests
    import sys
    import spotipy
    import spotipy.util as util

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
        # print(query)

        response = requests.get(query,
                                headers={"Content-Type": "application/json",
                                         "Authorization": f"Bearer {token}"})
        json_response = response.json()
        # print(json_response)
        for i, j in enumerate(json_response['items']):
            #print(f"{i + 1}) \"{j['track']['uri']}")
            playlistURIs.append(j['track']['uri'])

    # print(playlistURIs)

    # ------------------ getting track information for song ---------------------- #
    song = song.split("/")
    songID = song[4]
    songID = songID.split("?")
    songID = songID[0]

    # print(songID)

    # PERFORM THE QUERY
    query = "https://api.spotify.com/v1/tracks/" + songID + "?market=US"

    response = requests.get(query,
                            headers={"Content-Type": "application/json",
                                     "Authorization": f"Bearer {token}"})
    json_response = response.json()
    # print(json_response['uri'])

    songURI = json_response['uri']

    # ------------------ checking to see if song URI is in any of the playlists ---------------------- #
    if songURI in playlistURIs:
        message = "The song was found in their library, better not recommend it :("
    else:
        message = "Recommend the song!"

    return(message)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login")
def auth():
    url_args = "&".join(["{}={}".format(key, quote(val))
                        for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format("https://accounts.spotify.com/authorize", url_args)
    return redirect(auth_url)


@app.route("/callback/q", methods=['GET', 'POST'])
def callback():
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


@app.route('/get_data', methods=['POST'])
def get_data():
    username = request.form['user-name']
    song = request.form['song']

    print("Spotify Username: " + username)
    print("URL of the song you want to recommend: " + song)

    message = process(username, song)

    return render_template('success.html', message=message)


# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
