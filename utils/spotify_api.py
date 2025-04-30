import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

# Replace these with your actual Spotify Client ID and Client Secret
CLIENT_ID = "01c5c4ec250f440e8a434c7cd6fb6dd9"
CLIENT_SECRET = "481ae17a6f8d43bb8d690a59c2640adb"

def initialize_spotify():
    try:
        # Use hardcoded credentials
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        st.error(f"Failed to initialize Spotify API: {e}")
        return None

@st.cache_data(ttl=3600)
def get_spotify_recommendations(song_name):
    sp = initialize_spotify()
    if not sp:
        return [], "Spotify API not initialized."

    try:
        # Search for the song by name
        search_results = sp.search(q=song_name, type='track', limit=1)
        if not search_results['tracks']['items']:
            return [], "Song not found on Spotify."

        track = search_results['tracks']['items'][0]
        track_id = track['id']
        artist_id = track['artists'][0]['id']
        st.write("✅ Found Track:", track['name'])
        st.write("🎯 Track ID:", track_id)
        st.write("🎤 Artist ID:", artist_id)

        # Try track-based recommendations
        try:
            recs = sp.recommendations(seed_tracks=[track_id], limit=10, market="US")
            st.success("✅ Track-based recommendations fetched.")
        except Exception as e1:
            st.warning("⚠️ Track-based failed, trying artist...")
            st.exception(e1)
            try:
                recs = sp.recommendations(seed_artists=[artist_id], limit=10, market="US")
                st.success("✅ Artist-based recommendations fetched.")
            except Exception as e2:
                st.warning("⚠️ Artist-based failed, trying genre...")
                st.exception(e2)
                try:
                    recs = sp.recommendations(seed_genres=["pop"], limit=10, market="US")
                    st.success("✅ Genre-based recommendations fetched.")
                except Exception as e3:
                    st.error("❌ All recommendation methods failed.")
                    st.exception(e3)
                    return [], f"Error: {e3}"

        if not recs['tracks']:
            return [], "No recommendations returned."

        recommendations = [{
            'title': t['name'],
            'artist': ', '.join([a['name'] for a in t['artists']]),
            'url': t['external_urls']['spotify'],
            'thumbnail': t['album']['images'][0]['url'] if t['album']['images'] else ''
        } for t in recs['tracks']]

        return recommendations, None

    except Exception as e:
        st.error("❌ Failed to fetch Spotify recommendations.")
        st.exception(e)
        return [], f"Error: {e}"
