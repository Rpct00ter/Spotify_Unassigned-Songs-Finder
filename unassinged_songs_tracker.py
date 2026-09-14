import os
import time
from datetime import datetime
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException


load_dotenv()


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    raise RuntimeError("Missing Spotify configuration. ")


# Spotify permissions
SCOPE = " ".join([
    "user-library-read",
    "playlist-read-private",
    "playlist-modify-private",
])


# Spotify client
def create_spotify_client():
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            open_browser=True,
            cache_path=".spotify_cache",
        )
    )


# Santa Lil Helpers
def spotify_request(function, *args, **kwargs):
    """
    Execute a Spotify API request.

    Automatically retries when Spotify responds with
    HTTP 429 (rate limit).
    """

    while True:
        try:
            return function(*args, **kwargs)

        except SpotifyException as error:

            if error.http_status == 429:

                retry_after = 5

                if error.headers:
                    retry_after = int(
                        error.headers.get(
                            "Retry-After",
                            5
                        )
                    )

                print(
                    f"Rate limit reached. "
                    f"Waiting {retry_after} seconds..."
                )

                time.sleep(retry_after)

            else:
                raise


def get_current_user(sp):
    return spotify_request(
        sp.current_user
    )


# Me Liked Songs
def get_liked_tracks(sp):
    """
    Return all liked tracks.

    Result:
        {
            "spotify_track_id": {
                "id": "...",
                "uri": "...",
                "name": "...",
                ...
            }
        }
    """

    tracks = {}

    results = spotify_request(
        sp.current_user_saved_tracks,
        limit=50,
    )

    while results:

        for item in results["items"]:

            track = item.get("track")

            if not track:
                continue

            track_id = track.get("id")

            if not track_id:
                continue

            tracks[track_id] = track

        if not results.get("next"):
            break

        results = spotify_request(
            sp.next,
            results,
        )

    return tracks


# Me Playlists

def get_my_playlists(sp, user_id):
    playlists = []

    results = spotify_request(
        sp.current_user_playlists,
        limit=50,
    )

    while results:

        for playlist in results["items"]:

            if not playlist:
                continue

            owner = playlist.get("owner") or {}
            owner_id = owner.get("id")

            is_my_playlist = (
                owner_id == user_id
            )

            is_collaborative = (
                playlist.get("collaborative", False)
            )

            if is_my_playlist and not is_collaborative:
                playlists.append(playlist)

        if not results.get("next"):
            break

        results = spotify_request(
            sp.next,
            results,
        )

    return playlists


def get_playlist_track_ids(sp, playlist_id):
    track_ids = set()

    results = spotify_request(
        sp.playlist_items,
        playlist_id,
        limit=100,
        fields="items(item(id,type)),next",
    )

    while results:

        for item in results.get("items", []):

            track = item.get("item")

            if not track:
                continue

            # Playlists may contain different item types.
            if track.get("type") != "track":
                continue

            track_id = track.get("id")

            if track_id:
                track_ids.add(track_id)

        if not results.get("next"):
            break

        results = spotify_request(
            sp.next,
            results,
        )

    return track_ids


# Create playlist

def create_not_sorted_playlist(sp):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    playlist_name = f"Not Sorted {timestamp}"

    data = {
        "name": playlist_name,
        "public": False,
        "collaborative": False,
        "description": (
            "Liked homeless songs"
        ),
    }
    playlist = spotify_request(
        sp._post,
        "me/playlists",
        payload=data,
    )
    return playlist

def add_tracks_to_playlist(sp, playlist_id, tracks):
#(MAX 100 songs per upload)
    uris = [
        track["uri"]
        for track in tracks
        if track.get("uri")
    ]

    for start in range(0, len(uris), 100):

        batch = uris[start:start + 100]

        spotify_request(
            sp.playlist_add_items,
            playlist_id,
            batch,
        )


# Main

def main():

    print("Connecting to Spotify...")

    sp = create_spotify_client()

    print("Getting current user...")

    user = get_current_user(sp)

    user_id = user["id"]

    print(
        f"Logged in as: "
        f"{user.get('display_name') or user_id}"
    )

# Liked Songs
    print("Reading liked songs...")

    liked_tracks = get_liked_tracks(sp)

    print(
        f"Liked songs: {len(liked_tracks)}"
    )


# Playlists
    print("Reading me playlists...")

    my_playlists = get_my_playlists(
        sp,
        user_id,
    )

    print(
        f"Me playlists: "
        f"{len(my_playlists)}"
    )

# Collect tracks from playlists
    playlist_track_ids = set()

    for index, playlist in enumerate(
        my_playlists,
        start=1,
    ):

        playlist_name = playlist.get(
            "name",
            "Unnamed playlist",
        )

        print(
            f"[{index}/{len(my_playlists)}] "
            f"Reading: {playlist_name}"
        )

        track_ids = get_playlist_track_ids(
            sp,
            playlist["id"],
        )

        playlist_track_ids.update(
            track_ids
        )

    print(
        f"Unique tracks found in my playlists: "
        f"{len(playlist_track_ids)}"
    )

# Find unsorted tracks
    unsorted_tracks = [
        track
        for track_id, track in liked_tracks.items()
        if track_id not in playlist_track_ids
    ]

    print(
        f"Unsorted liked songs: "
        f"{len(unsorted_tracks)}"
    )

# Nothing to do
    if not unsorted_tracks:

        print("Everything is already sorted.")
        print("Finished")

        return
# Create playlist
    print("Creating Not Sorted playlist...")

    new_playlist = create_not_sorted_playlist(sp)

    print(
        f"Created: {new_playlist['name']}"
    )

# Add tracks
    print(
        f"Adding {len(unsorted_tracks)} tracks..."
        )

    add_tracks_to_playlist(
        sp,
        new_playlist["id"],
        unsorted_tracks,
    )

# Finito
    print("Finished")


if __name__ == "__main__":
    main()






