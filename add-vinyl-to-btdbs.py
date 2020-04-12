import os, sys, json, requests, urllib.parse
import spotipy
import spotipy.util as util

###############################################################################

def clean_utf8(str, char = " "):
    return "".join([i if ord(i) < 128 else char for i in str])

def init_spotify(user_id = '129874447'):
    # init API parameters for Spotify
    os.environ["SPOTIPY_CLIENT_ID"]     = apikeys["spotipy-client-id"]
    os.environ["SPOTIPY_CLIENT_SECRET"] = apikeys["spotipy-client-secret"]
    os.environ["SPOTIPY_REDIRECT_URI"]  = apikeys["redirect-url"]
    
    token = util.prompt_for_user_token(user_id, '')
    sp    = spotipy.Spotify(auth = token)
    
    return(sp)

def parse_album_info(album_obj):
    album = album_obj['name']
    artists = ", ".join([artist['name'] for artist in album_obj['artists']])
    cover_url = album_obj['images'][1 if len(album_obj['images']) > 1 else 0]['url']
    release_date = album_obj['release_date']
    return("%s | %s | %s | %s" % (album, artists, release_date, cover_url))

###############################################################################

# load in api keys
apikeys = json.load(open("data/api-keys.json"))

# determine if using Spotify for data or manual entry
print("\n1. Get album information from Spotify")
print("2. Manually enter album information\n")
entry_type = input("How would you like to enter the album? ")
print()

# searching via spotify
if entry_type == "1":
    # init spotify 
    sp = init_spotify()
    
    # search for query and report results
    query = input("Spotify query? ")
    results = sp.search(q = query, type = "album")
    items = results['albums']['items']
    print("\nFound %d results for query..." % len(items))
    for ix in range(0, len(items)):
        print("%3d: %s" % (ix + 1, parse_album_info(items[ix])))
        
    # ask user to select result (if any)
    print("\nAre any of these the albums you're looking for?")
    print("If so, enter the result number. If not, enter anything else.")
    result_ix = input("Correct album? ")
    
    # if user entered something out of range, exit
    if not result_ix.isdigit() or int(result_ix) - 1 >= len(items) or int(result_ix) - 1 < 0:
        print("\nQuitting...")
        sys.exit(0)
        
    # otherwise, parse information from album
    album_obj = items[int(result_ix) - 1]
    album_str = album_obj['name']
    artist_str = ", ".join([artist['name'] for artist in album_obj['artists']])
    cover_url = album_obj['images'][1 if len(album_obj['images']) > 1 else 0]['url']
    
# manually entering information
elif entry_type == "2":
    album_str = input("Album name? ")
    artist_str = input("Album artist? ")
    cover_url = input("Album art url? ")
    
else:
    print("Invalid selection, quitting...")
    sys.exit(0)
    
# using information, make addition to bt-db
requests.post("http://bt-dbs.herokuapp.com/addVinylRecord",
              data = {
                  'password': apikeys['bt-dbs-pw'],
                  'album': album_str,
                  "artist": artist_str,
                  "cover_url": cover_url
              })
    

