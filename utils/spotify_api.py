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
        # Search track
        search_results = sp.search(q=song_name, type='track', limit=1)
        if not search_results['tracks']['items']:
            return [], "Song not found on Spotify."

        track = search_results['tracks']['items'][0]
        track_id = track['id']
        artist_id = track['artists'][0]['id']
        st.write("✅ Found Track:", track['name'])
        st.write("🎯 Track ID:", track_id)
        st.write("🎤 Artist ID:", artist_id)

        # Try seed_tracks
        try:
            recs = sp.recommendations(seed_tracks=[track_id], limit=10)
            st.success("✅ Track-based recommendations fetched.")
        except Exception as e1:
            st.warning("⚠️ Track-based failed, trying artist...")
            st.exception(e1)
            try:
                recs = sp.recommendations(seed_artists=[artist_id], limit=10)
                st.success("✅ Artist-based recommendations fetched.")
            except Exception as e2:
                st.warning("⚠️ Artist-based failed, trying genre...")
                st.exception(e2)
                try:
                    recs = sp.recommendations(seed_genres=["pop"], limit=10)
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
