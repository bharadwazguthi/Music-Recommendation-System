import streamlit as st
from ytmusicapi import YTMusic

@st.cache_resource
def initialize_ytmusic():
    try:
        return YTMusic()
    except Exception as e:
        st.error(f"Failed to initialize YouTube Music API: {e}")
        return None

@st.cache_data(ttl=3600)
def get_youtube_recommendations(song_name):
    ytmusic = initialize_ytmusic()
    if not ytmusic:
        return [], "YouTube Music API not initialized."
    
    try:
        search = ytmusic.search(song_name, filter="songs", limit=1)
        if not search:
            return [], "Song not found on YouTube Music."
        
        song = search[0]
        playlist = ytmusic.get_watch_playlist(videoId=song['videoId'])

        recommendations = [{
            'title': track.get('title', 'Unknown'),
            'artist': ', '.join([a.get('name', 'Unknown') for a in track.get('artists', [])]),
            'url': f"https://music.youtube.com/watch?v={track.get('videoId')}",
            'thumbnail': track.get('thumbnails', [{}])[-1].get('url')
        } for track in playlist.get('tracks', [])[:10]]

        return recommendations, None
    except Exception as e:
        return [], f"Error: {e}"
