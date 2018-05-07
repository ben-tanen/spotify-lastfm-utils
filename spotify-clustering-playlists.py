import os, sys, json, requests, urllib.parse
import spotipy
import spotipy.util as util
import pandas as pd

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

### init API parameters for Spotify
apikeys = json.load(open("data/api-keys.json"))

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

### pull in audio features for saved songs
saved_tracks_audiofeat = pull_audio_features(track_ids = [track['track_id'] for track in saved_tracks])
saved_tracks_audiofeat_df = pd.DataFrame(saved_tracks_audiofeat).drop(['analysis_url', 'track_href', 'type', 'uri'], axis = 1)

### merge track info with audio features
merged = saved_tracks_df.merge(saved_tracks_audiofeat_df, how = 'left', left_on = 'track_id', right_on = 'id')

###############################################################################

### pull tracks from two test spotify playlists
test1_playlist_tracks    = pull_playlist_tracks(user_id = 'spotify', playlist_id = '37i9dQZF1DX3Ogo9pFvBkY') # ambient chill playlist
test1_playlist_tracks_df = pd.DataFrame(test1_playlist_tracks)
test1_playlist_tracks_df['playlist'] = 1
test2_playlist_tracks    = pull_playlist_tracks(user_id = 'spotify', playlist_id = '37i9dQZF1DX0pH2SQMRXnC') # hardstyle hits playlist
test2_playlist_tracks_df = pd.DataFrame(test2_playlist_tracks)
test2_playlist_tracks_df['playlist'] = 2

test_playlists_tracks_df = test1_playlist_tracks_df.append(test2_playlist_tracks_df)

### get audio features for songs
test_playlists_audiofeat    = pull_audio_features(track_ids = list(test_playlist_tracks_df['track_id']))
test_playlists_audiofeat_df = pd.DataFrame(test_playlists_audiofeat).drop(['analysis_url', 'track_href', 'type', 'uri'], axis = 1)

### merge track info with audio features
test_playlists_df = test_playlists_tracks_df.merge(test_playlists_audiofeat_df, how = 'left', left_on = 'track_id', right_on = 'id')

### try clustering on test playlists
from sklearn.cluster import KMeans

num_clusters = 2
kmeans = KMeans(n_clusters = num_clusters).fit(test_playlists_df.drop(['track_id', 'id', 'name', 'artists', 'duration_ms', 'playlist'], axis = 1))
test_playlists_df['cluster'] = pd.Series(kmeans.labels_) + 1

###############################################################################

### do pca analysis
from sklearn.decomposition import PCA

num_components = 5

pca = PCA(n_components = num_components)
pca.fit(merged.drop(['track_id', 'id', 'name', 'artists', 'duration_ms', 'cluster'], axis = 1, errors = 'ignore')) # TODO: should normalize data (set mean = 0, etc.)
# print(pca.components_)

### do kmeans analysis
from sklearn.cluster import KMeans

num_clusters = 200
kmeans = KMeans(n_clusters = num_clusters).fit(merged.drop(['track_id', 'id', 'name', 'artists', 'duration_ms', 'cluster'], axis = 1, errors = 'ignore'))
merged['cluster'] = pd.Series(kmeans.labels_)

###############################################################################

### make playlist from one cluster
playlist_name = 'k-means music'

# pull in all playlists
playlist_limit  = 50
playlist_offset = 0

playlists_obj = sp.user_playlists(user_id, limit = playlist_limit, offset = playlist_offset)
num_playlists = playlists_obj['total']
all_playlists = [ ]

while (playlist_offset < num_playlists):
    playlists_obj = sp.user_playlists(user_id, limit = playlist_limit, offset = playlist_offset)
    all_playlists += [{'name': playlist['name'], 'id': playlist['id']} for playlist in playlists_obj['items']]
    playlist_offset += playlist_limit

# check if playlist already exists
if (playlist_name not in [playlist['name'] for playlist in all_playlists]):
    playlist = sp.user_playlist_create(user = user_id, name = 'k-means music', public = True)
else:
    playlist_id = [playlist['id'] for playlist in all_playlists if playlist['name'] == playlist_name][0]
    playlist = sp.user_playlist(user = user_id, playlist_id = playlist_id)

# remove any existing tracks in playlist
while (playlist['tracks']['total'] > 0):
    sp.user_playlist_remove_all_occurrences_of_tracks(user_id, playlist['id'], tracks = [track['track']['id'] for track in playlist['tracks']['items']])
    playlist = sp.user_playlist(user = user_id, playlist_id = playlist_id)

# add tracks from cluster
cluster_ix = 50
sp.user_playlist_add_tracks(user_id, playlist_id = playlist['id'], tracks = list(merged.ix[merged['cluster'] == cluster_ix]['id']))



    