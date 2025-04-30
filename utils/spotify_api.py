import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

@st.cache_resource
def initialize_spotify():
    try:
        st.write("🔍 Checking Spotify secrets...")
        st.write("Client ID:", st.secrets["spotify"].get("client_id", "❌ Not found"))
        st.write("Client Secret:", "●●●●●●●●")  # Hide actual secret

        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        st.success("✅ Spotify API initialized successfully!")
        return spotipy.Spotify(auth_manager=auth_manager)
    except KeyError as e:
        st.error(f"❌ Missing key in secrets: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Failed to initialize Spotify API: {e}")
        return None

@st.cache_data(ttl=3600)
def get_spotify_recommendations(song_name):
    sp = initialize_spotify()
    if not sp:
        return [], "Spotify API not initialized."

    try:
        search_results = sp.search(q=song_name, type='track', limit=1)
        if not search_results['tracks']['items']:
            return [], "Song not found on Spotify."

        track = search_results['tracks']['items'][0]
        track_id = track['id']

        recs = sp.recommendations(seed_tracks=[track_id], limit=10)

        recommendations = [{
            'title': t['name'],
            'artist': ', '.join([a['name'] for a in t['artists']]),
            'url': t['external_urls']['spotify'],
            'thumbnail': t['album']['images'][0]['url'] if t['album']['images'] else ''
        } for t in recs['tracks']]

        return recommendations, None
    except Exception as e:
        return [], f"Error: {e}"
