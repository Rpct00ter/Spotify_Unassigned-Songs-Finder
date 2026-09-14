# Spotify Unassigned Songs Finder

## 1.) Fast Setup
Prepare the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install spotipy python-dotenv
```

Create `.env` file (requires a Spotify Developer app):

```env
SPOTIFY_CLIENT_ID=CLIENT_ID
SPOTIFY_CLIENT_SECRET=CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

Download `unassigned_songs_tracker.py`.

Run:

```bash
python3 unassigned_songs_tracker.py
```

The app connects to Spotify via Web API, finds liked songs that are not in any of your own non-collaborative playlists, and adds them to a new private playlist.


## 2.) Results
<img width="689" height="398" alt="image" src="https://github.com/user-attachments/assets/7f31204a-9258-45ff-b7f3-e7a70b2e62dd" />
<img width="689" height="149" alt="image" src="https://github.com/user-attachments/assets/8620f01a-51ca-424e-8323-6ff825e279aa" />


## 3.) Documentation
* https://developer.spotify.com/documentation/web-api
* https://developer.spotify.com/documentation/web-api/concepts/scopes
* https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks
* https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
* https://developer.spotify.com/documentation/web-api/reference/get-playlists-items
* https://developer.spotify.com/documentation/web-api/reference/create-playlist
* https://developer.spotify.com/documentation/web-api/reference/add-items-to-playlist
