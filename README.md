🎵 Music Recommendation System

A web-based Music Recommendation System built with Streamlit, YouTube Music API, and Last.fm API.
It allows users to search for a song and get recommendations from YouTube Music and Spotify (via Last.fm), along with download options for CSV files.

🚀 Features

🎧 Search for any song and fetch recommendations.

🔴 YouTube Music Recommendations using ytmusicapi.

🟢 Spotify Recommendations using Last.fm API (with Spotify search links).

📂 Export recommendations as CSV files (per platform or combined).

🎨 Beautiful dark mode UI with custom CSS styling.

🖥️ Responsive layout – works on both desktop and mobile.

🛠️ Tech Stack

Streamlit
 – Web app framework

ytmusicapi
 – YouTube Music API wrapper

Last.fm API
 – For track similarity and Spotify links

Pandas
 – Data handling and CSV export

Requests
 – API requests

📂 Project Structure
├── app.py                # Main Streamlit app
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation

⚙️ Installation
1. Clone the Repository
git clone https://github.com/your-username/music-recommendation-system.git
cd music-recommendation-system

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows

3. Install Dependencies
pip install -r requirements.txt

4. Set Up Environment Variables

Create a .env file (or export directly in terminal):

LASTFM_API_KEY=your_lastfm_api_key_here


If not set, the app defaults to a demo API key (may have limits).

▶️ Running the App
streamlit run app.py
Open your browser at http://localhost:8501
 🎉


📥 CSV Export

YouTube Music Recommendations

Spotify Recommendations

All Recommendations (combined)

✅ Future Improvements

✅ Add authentication for personalized recommendations.

✅ Integrate Spotify Web API directly instead of Last.fm links.

✅ Add playlist creation on Spotify/YouTube.

✅ Improve recommendation algorithm (collaborative filtering / ML).

👨‍💻 Author

Developed by Guthi Bharadwaz ✨
