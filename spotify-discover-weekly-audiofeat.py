import os, sys, json, requests, urllib.parse
import spotipy
import spotipy.util as util
import pandas as pd
from datetime import date

###############################################################################

def pull_saved_tracks(limit = 50, offset = 0):
    saved_tracks = [ ]
    saved_tracks_obj = sp.current_user_saved_tracks(limit = limit, offset = offset)
    num_saved_tracks = saved_tracks_obj['total']
    while (offset < num_saved_tracks):
        saved_tracks_obj = sp.current_user_saved_tracks(limit = limit, offset = offset)
        for track_obj in saved_tracks_obj['items']:
            saved_tracks.append({
                'name': track_obj['track']['name'],
                'artists': ', '.join([artist['name'] for artist in track_obj['track']['artists']]),
                'track_id': track_obj['track']['id']
            })
        offset += limit
    return saved_tracks

def pull_playlist_tracks(user_id, playlist_id, limit = 100, offset = 0):
    playlist_tracks = [ ]
    playlist_obj = sp.user_playlist_tracks(user = user_id, playlist_id = playlist_id, limit = 100, offset = 0)
    num_playlist_tracks = playlist_obj['total']
    while (offset < num_playlist_tracks):
        playlist_obj = sp.user_playlist_tracks(user = user_id, playlist_id = playlist_id, limit = 100, offset = 0)
        for track_obj in playlist_obj['items']:
            playlist_tracks.append({
                'name': track_obj['track']['name'],
                'artists': ', '.join([artist['name'] for artist in track_obj['track']['artists']]),
                'track_id': track_obj['track']['id']
            })
        offset += limit
    return playlist_tracks

def pull_audio_features(track_ids):
    saved_tracks_audiofeat = [ ]
    for track_ix in range(0,len(track_ids),50):
        audio_feats = sp.audio_features(track_ids[track_ix:track_ix+50])
        saved_tracks_audiofeat += audio_feats
    return saved_tracks_audiofeat

###############################################################################

data_dir = "/Users/ben-tanen/Desktop/Projects/spotify-lastfm-utils/data/"

### init API parameters for Spotify
apikeys = json.load(open(data_dir + "api-keys.json"))

os.environ["SPOTIPY_CLIENT_ID"]     = apikeys["spotipy-client-id"]
os.environ["SPOTIPY_CLIENT_SECRET"] = apikeys["spotipy-client-secret"]
os.environ["SPOTIPY_REDIRECT_URI"]  = apikeys["redirect-url"]

user_id = '129874447'

###############################################################################

### sign into spotify
token = util.prompt_for_user_token(user_id, scope = 'user-library-read, playlist-modify-public, playlist-modify-private')
sp    = spotipy.Spotify(auth = token)

### pull in list of saved songs
saved_tracks    = pull_saved_tracks()
saved_tracks_df = pd.DataFrame(saved_tracks)
saved_tracks_df['source'] = "Saved"

### pull in list of discover weekly songs
dw_tracks    = pull_playlist_tracks(user_id = user_id, playlist_id = '6FoUsELdGgdNLhMuRsXp28')
dw_tracks_df = pd.DataFrame(dw_tracks)
dw_tracks_df['source'] = "Discover Weekly"

### stack tracklists
all_tracks_df = saved_tracks_df.append(dw_tracks_df)

### pull in audio features for saved songs
all_tracks_audiofeat = pull_audio_features(track_ids = list(all_tracks_df['track_id']))
all_tracks_audiofeat_df = pd.DataFrame(all_tracks_audiofeat).drop(['analysis_url', 'track_href', 'type', 'uri'], axis = 1)

### merge track info with audio features
all_tracks_full = all_tracks_df.merge(all_tracks_audiofeat_df, how = 'left', left_on = 'track_id', right_on = 'id')
all_tracks_full = all_tracks_full.drop_duplicates(['track_id', 'source'])

### output dataframe to csv
all_tracks_full.to_csv(data_dir + "saved-vs-discoverweekly-audiofeat-" + date.today().strftime('%d%b%Y') + ".csv")
    