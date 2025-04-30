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
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY') or '75005e0fb82d7a25e27a654fa0809266'
LASTFM_BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

# App title and description
st.title('🎵 Music Recommendation Explorer')
st.markdown("""
Discover new music based on your favorite songs! Get recommendations from YouTube Music and Spotify (via Last.fm).
""")

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
    
    st.markdown("### 🎧 You searched for:")
    st.markdown(f"**{original_song.get('title', 'Unknown Title')}** by **{original_song.get('artists', [{'name': 'Unknown Artist'}])[0]['name']}**")
    video_id = original_song.get('videoId', '')
    if video_id:
        st.markdown(f"[Listen on YouTube Music](https://music.youtube.com/watch?v={video_id})")
    
    st.markdown("### YouTube Music Recommendations")
    
    yt_data = []
    
    if recommendations:
        for i, track in enumerate(recommendations[:10], 1):
            st.markdown(f"{i}. **{track.get('title', 'Unknown Title')}** by {track.get('artists', [{'name': 'Unknown Artist'}])[0]['name']}")
            video_id = track.get('videoId', '')
            if video_id:
                st.markdown(f"[Listen on YouTube Music](https://music.youtube.com/watch?v={video_id})")
            st.divider()
            
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
    
    st.markdown("### Spotify Recommendations (via Last.fm)")
    
    lastfm_data = []
    
    for i, rec in enumerate(recommendations[:10], 1):
        st.markdown(f"{i}. **{rec['title']}** by {rec['artist']}")
        st.markdown(f"[Listen on Spotify]({rec['url']})")
        st.divider()
        
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
    song_name = st.text_input("Enter a song name:", placeholder="e.g., Bohemian Rhapsody")
    
    platform_options = ['Both', 'YouTube Music', 'Spotify']
    platform = st.radio("Select platform(s):", platform_options, index=0)
    
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
    if platform in ['Both', 'YouTube Music'] and st.session_state.recommendations['youtube']:
        original_song, youtube_recs = st.session_state.recommendations['youtube']
        display_youtube_recommendations(original_song, youtube_recs)
    
    if platform in ['Both', 'Spotify'] and st.session_state.recommendations['lastfm']:
        display_lastfm_recommendations(st.session_state.recommendations['lastfm'])
    
    # Combined download option
    if platform == 'Both' and (st.session_state.recommendations['youtube'] or st.session_state.recommendations['lastfm']):
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
