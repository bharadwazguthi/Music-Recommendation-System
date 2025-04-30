import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

REDIRECT_URI = "https://music-rs.streamlit.app"

@st.cache_resource
def initialize_spotify():
    try:
        auth_manager = SpotifyOAuth(
            client_id="a991f60a350e4f3fa4b40d3f47059f75",
            client_secret="d5a01f68d36144a09a0383d30d640343",
            redirect_uri=REDIRECT_URI,
            scope="user-read-private"
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        st.error(f"Failed to initialize Spotify API: {e}")
        return None

@st.cache_data(ttl=3600)
def get_spotify_recommendations(song_name):
    spotify = initialize_spotify()
    if not spotify:
        return [], "Spotify API not initialized."
    
    try:
        results = spotify.search(q=song_name, type='track', limit=5)
        if not results['tracks']['items']:
            return [], "Song not found on Spotify."
        
        track = results['tracks']['items'][0]

        recommendations = spotify.recommendations(seed_tracks=[track['id']], limit=10)

        formatted_recommendations = [{
            'title': item.get('name', 'Unknown'),
            'artist': ', '.join([a.get('name', 'Unknown') for a in item.get('artists', [])]),
            'url': item.get('external_urls', {}).get('spotify', '#'),
            'thumbnail': item.get('album', {}).get('images', [{}])[0].get('url')
        } for item in recommendations.get('tracks', [])]

        return formatted_recommendations, None
    except Exception as e:
        return [], f"Error: {e}"
