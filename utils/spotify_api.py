import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

@st.cache_resource
def initialize_spotify():
    try:
        # Directly use your credentials (remove all st.secrets references)
        client_id = "aed05b133c93407c85a371de0c1b3ec4"
        client_secret = "272d835ea2184f4196c2911f4ecb747a"
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
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
        artist_id = track['artists'][0]['id']

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
