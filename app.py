import streamlit as st
import pandas as pd
import time
import streamlit.components.v1 as components
from spotify_api import get_spotify_recommendations

# Page config
st.set_page_config(page_title="Spotify Music Recommender", page_icon="🎵", layout="wide")
st.title("🎵 Spotify Music Recommendation System")

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

# Buttons
search_button = st.button("Get Spotify Recommendations")
clear_button = st.button("Clear All")

if clear_button:
    st.session_state.clear()
    st.rerun()

if search_button and song_name:
    custom_loading_spinner()
    time.sleep(1)
    st.subheader("🎧 Spotify Recommendations")

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

        # Download button
        df = pd.DataFrame(spotify_recs)
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Recommendations as CSV",
            data=csv,
            file_name=f"{song_name}_spotify_recommendations.csv",
            mime='text/csv',
        )

# Footer
st.markdown("""
<div class="footer">
    Made with ❤️ using Streamlit and Spotify API
</div>
""", unsafe_allow_html=True)
