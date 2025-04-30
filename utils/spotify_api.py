import requests

# Spotify API credentials (replace these with your own credentials)
CLIENT_ID = '01c5c4ec250f440e8a434c7cd6fb6dd9'  # Replace with your Spotify Client ID
CLIENT_SECRET = '481ae17a6f8d43bb8d690a59c2640adb'  # Replace with your Spotify Client Secret

# Get Spotify Access Token
def get_access_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    auth_response = requests.post(auth_url, data=auth_data)
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

# Fetch recommendations from Spotify
def get_spotify_recommendations(song_name):
    token = get_access_token()
    search_url = f"https://api.spotify.com/v1/search?q={song_name}&type=track&limit=1"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }

    search_response = requests.get(search_url, headers=headers)
    search_data = search_response.json()
    
    if search_data['tracks']['items']:
        track_id = search_data['tracks']['items'][0]['id']
        
        # Get recommendations based on the track ID
        recommendations_url = f"https://api.spotify.com/v1/recommendations?seed_tracks={track_id}&limit=10"
        recs_response = requests.get(recommendations_url, headers=headers)
        recs_data = recs_response.json()
        
        recommendations = [{
            'title': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'url': track['external_urls']['spotify'],
            'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else ''
        } for track in recs_data['tracks']]
        
        return recommendations, None
    else:
        return [], "Song not found on Spotify."
