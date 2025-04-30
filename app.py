import streamlit as st
import pandas as pd
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from io import StringIO

# ---------- SETUP ----------
st.set_page_config(page_title="Music Recommender", layout="wide")
st.title("🎵 Music Recommendation App")

# ---------- API CLIENTS ----------
# Replace with your actual credentials
SPOTIFY_CLIENT_ID = "01c5c4ec250f440e8a434c7cd6fb6dd9"
SPOTIFY_CLIENT_SECRET = "481ae17a6f8d43bb8d690a59c2640adb"

@st.cache_resource
def init_spotify():
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    return spotipy.Spotify(auth_manager=auth_manager)

@st.cache_resource
def init_ytmusic():
    return YTMusic()

sp = init_spotify()
yt = init_ytmusic()

# ---------- FUNCTIONS ----------
@st.cache_data(show_spinner=False)
def get_spotify_recommendations(song_name):
    results = sp.search(q=song_name, type='track', limit=1)
    if not results['tracks']['items']:
        return []
    track_id = results['tracks']['items'][0]['id']
    recommendations = sp.recommendations(seed_tracks=[track_id], limit=10)
    return [
        {
            "title": track['name'],
            "artist": ", ".join([a['name'] for a in track['artists']]),
            "album": track['album']['name'],
            "thumbnail": track['album']['images'][0]['url'] if track['album']['images'] else None,
            "url": track['external_urls']['spotify']
        }
        for track in recommendations['tracks']
    ]

@st.cache_data(show_spinner=False)
def get_ytmusic_recommendations(song_name):
    search_results = yt.search(song_name, filter="songs", limit=1)
    if not search_results:
        return []
    song = search_results[0]
    watch_playlist_id = song.get('videoId')
    if not watch_playlist_id:
        return []
    suggestions = yt.get_watch_playlist(watch_playlist_id)
    return [
        {
            "title": t['title'],
            "artist": ", ".join([a['name'] for a in t.get('artists', [])]),
            "album": t.get('album', {}).get('name', ''),
            "thumbnail": t['thumbnails'][-1]['url'] if t.get('thumbnails') else None,
            "url": f"https://music.youtube.com/watch?v={t['videoId']}"
        }
        for t in suggestions.get('tracks', [])[:10]
    ]

# ---------- UI ELEMENTS ----------
st.write("Enter a song name to get recommendations from Spotify and YouTube Music.")
song_input = st.text_input("Song Name", placeholder="Type a song name...")
platform = st.radio("Choose platform(s) for recommendations:", ["Both", "Spotify", "YouTube Music"], horizontal=True)

col1, col2 = st.columns([1, 1])
get_recs = st.button("Get Recommendations")
clear_output = st.button("Clear All")

if clear_output:
    st.experimental_rerun()

if get_recs and song_input:
    spotify_recs, ytmusic_recs = [], []

    if platform in ["Both", "Spotify"]:
        try:
            spotify_recs = get_spotify_recommendations(song_input)
        except Exception as e:
            st.error(f"Spotify error: {e}")

    if platform in ["Both", "YouTube Music"]:
        try:
            ytmusic_recs = get_ytmusic_recommendations(song_input)
        except Exception as e:
            st.error(f"YouTube Music error: {e}")

    def display_results(recs, col, title):
        if recs:
            col.subheader(title)
            for track in recs:
                with col.container():
                    col.image(track['thumbnail'], width=80)
                    col.markdown(f"**{track['title']}**")
                    col.markdown(f"*{track['artist']}* — {track['album']}")
                    col.markdown(f"[Listen here]({track['url']})\n")
        else:
            col.warning(f"No recommendations found on {title}.")

    if platform in ["Both", "Spotify"]:
        display_results(spotify_recs, col1, "Spotify Recommendations")
    if platform in ["Both", "YouTube Music"]:
        display_results(ytmusic_recs, col2, "YouTube Music Recommendations")

    # Combine results for CSV export
    all_recs = []
    if spotify_recs:
        for track in spotify_recs:
            track['source'] = "Spotify"
            all_recs.append(track)
    if ytmusic_recs:
        for track in ytmusic_recs:
            track['source'] = "YouTube Music"
            all_recs.append(track)

    if all_recs:
        df = pd.DataFrame(all_recs)
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name="music_recommendations.csv", mime="text/csv")
else:
    st.info("Enter a song name and click 'Get Recommendations'.")
