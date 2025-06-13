import streamlit as st
from ytmusicapi import YTMusic
import pandas as pd
import requests
import os
from urllib.parse import quote

# Initialize APIs
@st.cache_resource
def initialize_apis():
    try:
        ytmusic = YTMusic()
    except Exception as e:
        st.error(f"Failed to initialize YouTube Music API: {e}")
        ytmusic = None
    return ytmusic

# Last.fm API setup
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY') or '9e56e3c9932dbcf9e845a48e4906bcb1'
LASTFM_BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
    }
    .platform-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .song-card {
        background-color: rgba(30, 30, 30, 0.7);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        color: white;
    }
    .song-title {
        font-weight: bold;
        font-size: 1.1rem;
        color: white;
    }
    .artist-name {
        font-style: italic;
        color: #cccccc;
    }
    .platform-btn {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 20px;
        text-decoration: none;
        color: white !important;  /* Force white text */
        font-weight: bold;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    .platform-btn:visited {
        color: white !important;  /* Keep white after click */
    }
    .spotify-btn {
        background-color: #1DB954;
    }
    .spotify-btn:hover {
        background-color: #1ed760;
        transform: translateY(-2px);
    }
    .youtube-btn {
        background-color: #FF0000;
    }
    .youtube-btn:hover {
        background-color: #ff3333;
        transform: translateY(-2px);
    }
    .stRadio > div {
        display: flex;
        justify-content: center;
    }
    /* Dark mode styling */
    .main {
        background-color: #121212;
        color: white;
    }
    .stButton button {
        background-color: #1DB954;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 8px 16px;
        border: none;
    }
    .stButton button:hover {
        background-color: #1ed760;
        transform: translateY(-2px);
    }
    .stTextInput > div > div > input {
        background-color: #333333;
        color: white;
        border-radius: 8px;
    }
    .stRadio > div {
        background-color: rgba(30, 30, 30, 0.7);
        border-radius: 10px;
        padding: 10px;
    }
    .search-header {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .divider {
        border-top: 1px solid #444;
        margin: 15px 0;
    }
    .recommendation-columns {
        display: flex;
        gap: 20px;
    }
    .recommendation-column {
        flex: 1;
    }
    @media (max-width: 768px) {
        .recommendation-columns {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<div class="main-header">🎵 Music Recommendation System</div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
Discover new music based on your favorite songs! Get recommendations from YouTube Music and Spotify.
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = {
        'youtube': None,
        'lastfm': None
    }

# Initialize APIs
ytmusic = initialize_apis()

# Function to get YouTube Music recommendations
@st.cache_data(ttl=3600, show_spinner=False)
def get_youtube_recommendations(_ytmusic, song_name):
    try:
        search_results = _ytmusic.search(song_name, filter="songs", limit=1)
        if not search_results:
            return None, []
        
        video_id = search_results[0]['videoId']
        recommendations = _ytmusic.get_watch_playlist(videoId=video_id, limit=10)
        recommendations = recommendations.get('tracks', [])
        
        return search_results[0], recommendations
        
    except Exception as e:
        st.error(f"YouTube Music API error: {e}")
        return None, []

# Function to get Last.fm recommendations with Spotify links
@st.cache_data(ttl=3600)
def get_lastfm_recommendations(song_name):
    try:
        # First search for the track to get the correct name/artist
        search_params = {
            'method': 'track.search',
            'track': song_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': 1
        }
        search_response = requests.get(LASTFM_BASE_URL, params=search_params)
        search_data = search_response.json()
        
        if 'error' in search_data or not search_data.get('results', {}).get('trackmatches', {}).get('track'):
            return None
            
        track = search_data['results']['trackmatches']['track'][0]
        artist = track['artist']
        track_name = track['name']
        
        # Get similar tracks
        similar_params = {
            'method': 'track.getSimilar',
            'artist': artist,
            'track': track_name,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'limit': 5
        }
        similar_response = requests.get(LASTFM_BASE_URL, params=similar_params)
        similar_data = similar_response.json()
        
        if 'error' in similar_data or not similar_data.get('similartracks', {}).get('track'):
            return None
            
        tracks = similar_data['similartracks']['track']
        
        recommendations = []
        for track in tracks:
            # Create Spotify search link
            search_query = f"{track['name']} {track['artist']['name']}"
            spotify_url = f"https://open.spotify.com/search/{quote(search_query)}"
            
            recommendations.append({
                'title': track['name'],
                'artist': track['artist']['name'],
                'url': spotify_url,
                'platform': 'Spotify'
            })
        
        return recommendations
        
    except Exception as e:
        st.error(f"Error fetching Last.fm recommendations: {str(e)}")
        return None

# Function to display YouTube recommendations
def display_youtube_recommendations(original_song, recommendations):
    if not original_song:
        st.warning("No YouTube Music results found.")
        return
    
    st.markdown('<div class="search-header">🎧 You searched for:</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="song-card">
        <div class="song-title">{original_song.get('title', 'Unknown Title')}</div>
        <div class="artist-name">by {original_song.get('artists', [{'name': 'Unknown Artist'}])[0]['name']}</div>
    """, unsafe_allow_html=True)
    
    video_id = original_song.get('videoId', '')
    if video_id:
        st.markdown(f'<a href="https://music.youtube.com/watch?v={video_id}" class="platform-btn youtube-btn">Listen on YouTube Music</a>', unsafe_allow_html=True)
    
    st.markdown('<div class="platform-header">YouTube Music Recommendations</div>', unsafe_allow_html=True)
    
    yt_data = []
    
    if recommendations:
        for i, track in enumerate(recommendations[:10], 1):
            st.markdown(f"""
            <div class="song-card">
                <div class="song-title">{i}. {track.get('title', 'Unknown Title')}</div>
                <div class="artist-name">by {track.get('artists', [{'name': 'Unknown Artist'}])[0]['name']}</div>
            """, unsafe_allow_html=True)
            
            video_id = track.get('videoId', '')
            if video_id:
                st.markdown(f'<a href="https://music.youtube.com/watch?v={video_id}" class="platform-btn youtube-btn">Listen on YouTube Music</a>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            yt_data.append({
                'Title': track.get('title', 'Unknown'),
                'Artist': track.get('artists', [{'name': 'Unknown'}])[0]['name'],
                'Platform': 'YouTube Music',
                'URL': f"https://music.youtube.com/watch?v={video_id}" if video_id else ''
            })
        
        if yt_data:
            yt_df = pd.DataFrame(yt_data)
            csv = yt_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download YouTube Music Recommendations",
                data=csv,
                file_name="youtube_music_recommendations.csv",
                mime='text/csv'
            )
    else:
        st.info("No recommendations found from YouTube Music.")

# Function to display Last.fm recommendations
def display_lastfm_recommendations(recommendations):
    if not recommendations:
        st.warning("No Spotify recommendations found.")
        return
    
    st.markdown('<div class="platform-header">Spotify Recommendations </div>', unsafe_allow_html=True)
    
    lastfm_data = []
    
    for i, rec in enumerate(recommendations[:10], 1):
        st.markdown(f"""
        <div class="song-card">
            <div class="song-title">{i}. {rec['title']}</div>
            <div class="artist-name">by {rec['artist']}</div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<a href="{rec["url"]}" class="platform-btn spotify-btn">Listen on Spotify</a>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        lastfm_data.append({
            'Title': rec['title'],
            'Artist': rec['artist'],
            'Platform': 'Spotify',
            'URL': rec['url']
        })
    
    if lastfm_data:
        lastfm_df = pd.DataFrame(lastfm_data)
        csv = lastfm_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Spotify Recommendations",
            data=csv,
            file_name="spotify_recommendations.csv",
            mime='text/csv'
        )

# Main app
with st.form("recommendation_form"):
    st.markdown('<div class="search-header">Search for a song:</div>', unsafe_allow_html=True)
    song_name = st.text_input("", placeholder="e.g., Bohemian Rhapsody", label_visibility="collapsed")
    
    st.markdown('<div class="search-header" style="margin-top: 1rem;">Select platform(s):</div>', unsafe_allow_html=True)
    platform_options = ['Both', 'YouTube Music', 'Spotify']
    platform = st.radio("", platform_options, index=0, label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.form_submit_button("Get Recommendations")
    with col2:
        clear_button = st.form_submit_button("Clear All")

if clear_button:
    st.session_state.recommendations = {
        'youtube': None,
        'lastfm': None
    }
    st.rerun()

if submit_button and song_name:
    with st.spinner("Fetching recommendations..."):
        if platform in ['Both', 'YouTube Music'] and ytmusic:
            original_song, youtube_recs = get_youtube_recommendations(ytmusic, song_name)
            st.session_state.recommendations['youtube'] = (original_song, youtube_recs)
        
        if platform in ['Both', 'Spotify']:
            lastfm_recs = get_lastfm_recommendations(song_name)
            st.session_state.recommendations['lastfm'] = lastfm_recs

# Display recommendations
if st.session_state.recommendations['youtube'] is not None or st.session_state.recommendations['lastfm'] is not None:
    if platform == 'Both':
        # Display side by side for "Both" option
        st.markdown('<div class="recommendation-columns">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.recommendations['youtube']:
                original_song, youtube_recs = st.session_state.recommendations['youtube']
                display_youtube_recommendations(original_song, youtube_recs)
        
        with col2:
            if st.session_state.recommendations['lastfm']:
                display_lastfm_recommendations(st.session_state.recommendations['lastfm'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Single column display for individual platforms
        if platform == 'YouTube Music' and st.session_state.recommendations['youtube']:
            original_song, youtube_recs = st.session_state.recommendations['youtube']
            display_youtube_recommendations(original_song, youtube_recs)
        
        if platform == 'Spotify' and st.session_state.recommendations['lastfm']:
            display_lastfm_recommendations(st.session_state.recommendations['lastfm'])
    
    # Combined download option
    if (st.session_state.recommendations['youtube'] or st.session_state.recommendations['lastfm']):
        all_data = []
        if st.session_state.recommendations['youtube']:
            original_song, youtube_recs = st.session_state.recommendations['youtube']
            for track in youtube_recs[:10]:
                all_data.append({
                    'Title': track.get('title', 'Unknown'),
                    'Artist': track.get('artists', [{'name': 'Unknown'}])[0]['name'],
                    'Platform': 'YouTube Music',
                    'URL': f"https://music.youtube.com/watch?v={track.get('videoId', '')}" if track.get('videoId') else ''
                })
        
        if st.session_state.recommendations['lastfm']:
            for rec in st.session_state.recommendations['lastfm'][:10]:
                all_data.append({
                    'Title': rec['title'],
                    'Artist': rec['artist'],
                    'Platform': 'Spotify',
                    'URL': rec['url']
                })
        
        if all_data:
            combined_df = pd.DataFrame(all_data)
            csv = combined_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download All Recommendations",
                data=csv,
                file_name=f"all_recommendations_{song_name.replace(' ', '_')}.csv",
                mime='text/csv'
            )
