import streamlit as st
from utils.youtube_api import get_youtube_recommendations, initialize_ytmusic
from utils.spotify_api import get_spotify_recommendations, initialize_spotify
import pandas as pd
import streamlit.components.v1 as components
import time

# Page config
st.set_page_config(page_title="Music Recommendation System", page_icon="🎵", layout="wide")
with open("styles/custom_styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🎵 Music Recommendation System")

# Initialize APIs once
ytmusic = initialize_ytmusic()
spotify = initialize_spotify()

# Loading spinner
def custom_loading_spinner():
    spinner_html = """
    <div id="loading-spinner">
        <div class="music-note">🎵</div>
    </div>
    """
    components.html(spinner_html, height=150)

# UI
song_name = st.text_input("Enter a song name:")
platform_choice = st.radio("Choose Platform:", ["Both", "Spotify Only", "YouTube Music Only"])

# Buttons
search_button = st.button("Get Recommendations")
clear_button = st.button("Clear All")

if clear_button:
    st.session_state.clear()
    st.rerun()

combined_recommendations = []

if search_button and song_name:
    col1, col2 = st.columns(2)

    if platform_choice in ["Both", "YouTube Music Only"]:
        with col1:
            custom_loading_spinner()
            time.sleep(1)
            st.subheader("YouTube Music")
            youtube_recs, error = get_youtube_recommendations(song_name)
            if error:
                st.error(error)
            elif not youtube_recs:
                st.warning("No recommendations found.")
            else:
                for rec in youtube_recs:
                    st.markdown(f"""
                        <div class="song-card">
                            <img src="{rec['thumbnail']}" width="100%">
                            <div class="song-title">{rec['title']}</div>
                            <div class="artist-name">{rec['artist']}</div>
                            <a href="{rec['url']}" target="_blank" class="platform-btn youtube-btn">Listen on YouTube Music</a>
                        </div>
                    """, unsafe_allow_html=True)
                    rec['source'] = "YouTube Music"
                    combined_recommendations.append(rec)

    if platform_choice in ["Both", "Spotify Only"]:
        with col2:
            custom_loading_spinner()
            time.sleep(1)
            st.subheader("Spotify")
            spotify_recs, error = get_spotify_recommendations(song_name)
            if error:
                st.error(error)
            elif not spotify_recs:
                st.warning("No recommendations found.")
            else:
                for rec in spotify_recs:
                    st.markdown(f"""
                        <div class="song-card">
                            <img src="{rec['thumbnail']}" width="100%">
                            <div class="song-title">{rec['title']}</div>
                            <div class="artist-name">{rec['artist']}</div>
                            <a href="{rec['url']}" target="_blank" class="platform-btn spotify-btn">Listen on Spotify</a>
                        </div>
                    """, unsafe_allow_html=True)
                    rec['source'] = "Spotify"
                    combined_recommendations.append(rec)

    if combined_recommendations:
        df = pd.DataFrame(combined_recommendations)
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Recommendations as CSV",
            data=csv,
            file_name=f"{song_name}_recommendations.csv",
            mime='text/csv',
        )

# Footer
st.markdown("""
<div class="footer">
    Made with ❤️ using Streamlit, Spotify API, and YouTube Music API
</div>
""", unsafe_allow_html=True)
