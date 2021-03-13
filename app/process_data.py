# resources
# https://developer.spotify.com/console/get-playlists/
# https://developer.spotify.com/console/get-playlist-tracks/
# https://developer.spotify.com/console/get-track/

import sys
import spotipy
import spotipy.util as util

scope = 'playlist-read-private, playlist-read-collaborative'

util.prompt_for_user_token("toni1li131",scope,client_id='4300c682d48b480d96478da07107ca59',client_secret='5a034c056898492b966e34c01a995d28',redirect_uri='https://oauth.pstmn.io/v1/browser-callback')


def process(user_id, song):
    import requests

    # SETTINGS
    # refreshing token
    token = util.prompt_for_user_token("toni1li131", scope)
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




        


