import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pygame
import sys
import time
import subprocess
import os

# Spotify API credentials
CLIENT_ID = '0ca0a12c12d74ab5ba99b278c8d78713'
CLIENT_SECRET = 'd6601dec5adf4068b88d51bd11e03dc1'
REDIRECT_URI = 'http://localhost:8888/callback'

scope = "user-read-playback-state,user-modify-playback-state,playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))
# Test authorization
# user = sp.current_user()
# print(user['display_name'])

pygame.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Spotify Music Player")

# Set up fonts
font = pygame.font.Font(None, 36)

# Load a placeholder image
placeholder = pygame.Surface((150, 150))
placeholder.fill((255, 0, 0))

# Button dimensions and positions
button_width = 100
button_height = 50
button_y = 400

play_button = pygame.Rect(100, button_y, button_width, button_height)
pause_button = pygame.Rect(200, button_y, button_width, button_height)
next_button = pygame.Rect(300, button_y, button_width, button_height)
prev_button = pygame.Rect(0, button_y, button_width, button_height)

# Main loop flag
running = True

def get_devices():
    return sp.devices()['devices']

def get_active_device():
    devices = get_devices()
    for device in devices:
        if device['is_active']:
            return device['id']
    return None

def start_playback_on_default_device():
    devices = get_devices()
    if devices:
        default_device = devices[0]['id']  # Choose the first available device
        sp.transfer_playback(device_id=default_device, force_play=True)
        time.sleep(1)  # Give Spotify some time to start playback

def open_spotify_app():
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", "-a", "Spotify"])
        elif sys.platform == "win32":  # Windows
            os.system("start spotify")
        time.sleep(5)  # Give Spotify some time to open
        return True
    except Exception as e:
        print(f"Failed to open Spotify app: {e}")
        return False

def ensure_active_device():
    device_id = get_active_device()
    if device_id is None:
        start_playback_on_default_device()
        device_id = get_active_device()
    if device_id is None:
        open_spotify_app()
        time.sleep(5)  # Give Spotify some time to connect
        start_playback_on_default_device()
        device_id = get_active_device()
    if device_id is None:
        print("No active Spotify device found. Please open the Spotify app on your computer.")
        return False
    return True

def play_song(song_uri):
    device_id = get_active_device()
    if device_id is None:
        start_playback_on_default_device()
        device_id = get_active_device()
    if device_id:
        sp.start_playback(device_id=device_id, uris=[song_uri])

def pause_song():
    device_id = get_active_device()
    if device_id:
        sp.pause_playback(device_id=device_id)

def next_song():
    device_id = get_active_device()
    if device_id:
        sp.next_track(device_id=device_id)

def prev_song():
    device_id = get_active_device()
    if device_id:
        sp.previous_track(device_id=device_id)

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    return results['items']

# Your Spotify playlist ID
playlist_id = '2JRXnerNyzSs7W7eOpYvU3'
tracks = get_playlist_tracks(playlist_id)
track_index = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not ensure_active_device():
                continue

            if play_button.collidepoint(event.pos):
                play_song(tracks[track_index]['track']['uri'])
            elif pause_button.collidepoint(event.pos):
                pause_song()
            elif next_button.collidepoint(event.pos):
                track_index = (track_index + 1) % len(tracks)
                play_song(tracks[track_index]['track']['uri'])
            elif prev_button.collidepoint(event.pos):
                track_index = (track_index - 1) % len(tracks)
                play_song(tracks[track_index]['track']['uri'])

    screen.fill((0, 0, 0))

    # Display the current track
    track_name = tracks[track_index]['track']['name']
    track_artist = tracks[track_index]['track']['artists'][0]['name']
    text = font.render(f"{track_name} by {track_artist}", True, (255, 255, 255))
    screen.blit(text, (50, 50))

    # Display placeholder image
    screen.blit(placeholder, (175, 100))

    # Draw buttons
    pygame.draw.rect(screen, (0, 255, 0), play_button)  # Green
    pygame.draw.rect(screen, (255, 0, 0), pause_button)  # Red
    pygame.draw.rect(screen, (0, 0, 255), next_button)  # Blue
    pygame.draw.rect(screen, (255, 255, 0), prev_button)  # Yellow

    # Button labels
    play_text = font.render("Play", True, (0, 0, 0))
    pause_text = font.render("Pause", True, (0, 0, 0))
    next_text = font.render("Next", True, (0, 0, 0))
    prev_text = font.render("Prev", True, (0, 0, 0))

    screen.blit(play_text, (play_button.x + 20, play_button.y + 10))
    screen.blit(pause_text, (pause_button.x + 10, pause_button.y + 10))
    screen.blit(next_text, (next_button.x + 20, next_button.y + 10))
    screen.blit(prev_text, (prev_button.x + 20, prev_button.y + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()