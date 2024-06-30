import spotipy
from spotipy.oauth2 import SpotifyOAuth

username = ''
clientID = ''
clientSecret = ''
redirect_uri = 'http://localhost:8888/callback'

def spotify_authenicate(client_id, client_secret, redirect_uri, username):
    scope = "user-read-currently-playing user-modify-playback-state"
    auth_manager = SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, username=username)
    return spotipy.Spotify(auth_manager = auth_manager)

spotify = spotify_authenicate(clientID, clientSecret, redirect_uri, username)

def get_current_playing_info():
    global spotify
    current_track = spotify.current_user_playing_track()
    if current_track is None:
        return None
    
    artist_name = current_track['item']['artists'][0]['name']
    album_name = current_track['item']['album']['name']
    track_title = current_track['item']['name']

    return {
        "artist": artist_name,
        "album": album_name,
        "title": track_title
    }


def start_music():
    global spotify
    try:
        spotify.start_playback()
    except spotipy.SpotifyException as e:
        return f"Error in starting playback: {str(e)}"
    
def stop_music():
    global spotify
    try:
        spotify.pause_playback()
    except spotipy.SpotifyException as e:
        return f"Error in starting playback: {str(e)}"
    
def skip_to_next():
    global spotify
    try:
        spotify.next_track()
    except spotipy.SpotifyException as e:
        return f"Error in starting playback: {str(e)}"
    
def skip_to_previous():
    global spotify
    try:
        spotify.previous_track()
    except spotipy.SpotifyException as e:
        return f"Error in starting playback: {str(e)}"
    
