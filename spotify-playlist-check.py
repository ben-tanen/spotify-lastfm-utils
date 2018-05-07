import os, sys, colorama
import spotipy
import spotipy.util as util

colorama.init()

apikeys = json.load(open("data/api-keys.json"))
os.environ["SPOTIPY_CLIENT_ID"]     = apikeys["spotipy-client-id"]
os.environ["SPOTIPY_CLIENT_SECRET"] = apikeys["spotipy-client-secret"]
os.environ["SPOTIPY_REDIRECT_URI"]  = apikeys["redirect-url"]

user_id   = '129874447'
token     = util.prompt_for_user_token(user_id)
sp        = spotipy.Spotify(auth = token)
playlists = sp.user_playlists(user = user_id)

if len(sys.argv) < 2:
    sys.exit('\033[31mERROR\033[0m - usage: python spotify-playlist-check.py "[query]"')

search_str = sys.argv[1]

# check if a song is in a particular playlist
def SongInPlaylist(user_id, playlist_id, track_name):
    playlist    = sp.user_playlist(user_id, playlist_id)
    tracks      = playlist['tracks']

    while tracks != None:
        for track in tracks['items']:
            if track_name.lower() in track['track']['name'].lower():
                print '>> "%s" found in playlist "%s"' % (track['track']['name'], playlist['name'])
        tracks = sp.next(tracks)

# loop through all playlists
while playlists != None:
    for playlist in playlists['items']:
        try:
            if playlist['owner']['id'] == user_id:
                SongInPlaylist(user_id, playlist['id'], search_str)
            else:
                print 'Not owned by user: %s' % playlist['name']
        except:
            print 'Playlist error: %s' % playlist['name']
        
    playlists = sp.next(playlists)