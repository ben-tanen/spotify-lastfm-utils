import os, sys, json, requests, urllib.parse
import spotipy
import spotipy.util as util

###############################################################################

def is_track_in_playlist(track, artist, playlist):
    for added_track in playlist:
        if track.lower() in added_track['name'].lower():
            if artist.lower() in added_track['artists'].lower():
                return True
    return False

def pull_playlist_tracks(user_id, playlist_id, limit = 100, offset = 0):
    playlist_tracks = [ ]
    playlist_obj = sp.user_playlist_tracks(user = user_id, playlist_id = playlist_id, limit = 100, offset = 0)
    num_playlist_tracks = playlist_obj['total']
    while (offset < num_playlist_tracks):
        playlist_obj = sp.user_playlist_tracks(user = user_id, playlist_id = playlist_id, limit = 100, offset = offset)
        for track_obj in playlist_obj['items']:
            playlist_tracks.append({
                'name': track_obj['track']['name'],
                'artists': ', '.join([artist['name'] for artist in track_obj['track']['artists']]),
                'track_id': track_obj['track']['id']
            })
        offset += limit
    return playlist_tracks

###############################################################################

# load in api keys
apikeys = json.load(open("/Users/ben-tanen/Desktop/Projects/spotify-lastfm-utils/data/api-keys.json"))

# init API parameters for Last.FM
lastfm_parameters = {
    "user": "ben-tanen",
    "method": "user.gettoptracks",
    "format": "json",
    "api_key": apikeys["lastfm-api-key"],
    "period": "1month",
    "limit": 50
}

# init API parameters for Spotify
os.environ["SPOTIPY_CLIENT_ID"]     = apikeys["spotipy-client-id"]
os.environ["SPOTIPY_CLIENT_SECRET"] = apikeys["spotipy-client-secret"]
os.environ["SPOTIPY_REDIRECT_URI"]  = apikeys["redirect-url"]

user_id     = '129874447'
playlist_id = '1adKv7j4ZnpwiEv70a2msj'

###############################################################################

# Get top tracks from Last.FM API
try:
    url = "http://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode(lastfm_parameters)
    response = requests.get(url)
except:
    print('ERROR: Failed to make connection')
    sys.exit(1)

if response.status_code != 200:
    print("ERROR: Status = %d" % response.status_code)
    sys.exit(1)

top_tracks = json.loads(response.content.decode('utf-8'))['toptracks']['track']

if len(top_tracks) == 0:
    print("ERROR: No tracks available")
    sys.exit(1)

###############################################################################

# get download playlist tracks
token           = util.prompt_for_user_token(user_id, 'playlist-read-private')
sp              = spotipy.Spotify(auth = token)
playlist        = pull_playlist_tracks(user_id, playlist_id)

for track in top_tracks:
    # check if track already in playlist
    # if not, tell IFTTT to add track to download playlist
    if not is_track_in_playlist(track['name'], track['artist']['name'], playlist):
        print('   ADDING: "%s" by %s' % (track['name'], track['artist']['name']))
        requests.post('https://maker.ifttt.com/trigger/specify_top_song/with/key/%s' % apikeys['ifttt-key'], data = {
            'value1': track['name'],
            'value2': track['artist']['name']
        })
    else:
        print('DUPLICATE: "%s" by %s' % (track['name'], track['artist']['name']))
    