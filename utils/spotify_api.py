import requests
import json

CLIENT_ID = '01c5c4ec250f440e8a434c7cd6fb6dd9'  # Replace with your Spotify Client ID
CLIENT_SECRET = '481ae17a6f8d43bb8d690a59c2640adb'  # Replace with your Spotify Client Secret

# Function to get the Spotify API access token
def get_spotify_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(CLIENT_ID, CLIENT_SECRET)}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        access_token = response.json()['access_token']
        return access_token
    else:
        raise Exception(f"Error fetching access token from Spotify: {response.status_code} - {response.text}")

# Function to get Spotify recommendations based on song name
def get_spotify_recommendations(song_name):
    try:
        # Get access token
        access_token = get_spotify_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        # Search for the track based on the song name
        search_url = "https://api.spotify.com/v1/search"
        search_params = {
            "q": song_name,
            "type": "track",
            "limit": 1
        }

        search_response = requests.get(search_url, headers=headers, params=search_params)
        
        # Check if the response was successful
        if search_response.status_code == 200:
            try:
                search_data = search_response.json()
                if search_data['tracks']['items']:
                    track = search_data['tracks']['items'][0]
                    track_id = track['id']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    track_url = track['external_urls']['spotify']
                    track_thumbnail = track['album']['images'][0]['url']

                    # Get recommendations based on the track
                    recs_url = "https://api.spotify.com/v1/recommendations"
                    recs_params = {
                        "limit": 10,
                        "seed_tracks": track_id
                    }
                    recs_response = requests.get(recs_url, headers=headers, params=recs_params)
                    
                    if recs_response.status_code == 200:
                        recs_data = recs_response.json()
                        recommendations = []
                        for item in recs_data['tracks']:
                            recommendations.append({
                                'title': item['name'],
                                'artist': item['artists'][0]['name'],
                                'url': item['external_urls']['spotify'],
                                'thumbnail': item['album']['images'][0]['url']
                            })
                        return recommendations, None
                    else:
                        return [], f"Error fetching recommendations from Spotify: {recs_response.status_code} - {recs_response.text}"
                else:
                    return [], "Song not found."
            except json.JSONDecodeError as e:
                return [], f"Error decoding response JSON: {str(e)}"
        else:
            return [], f"Error: Unable to search for the song. Status code {search_response.status_code} - {search_response.text}"
    
    except requests.exceptions.RequestException as e:
        return [], f"Request Error: {str(e)}"
