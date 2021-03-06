import sys
import json
import time
import urllib
import logging
import spotipy
import spotipy.util as util
from datetime import datetime

def scrape_song():
	current_time = datetime.utcnow().strftime("%m-%d-%H:%M:00")
	url = "http://www.siriusxm.com/metadata/pdt/en-us/json/channels/altnation/timestamp/" + current_time
	response = urllib.urlopen(url);
	data = json.loads(response.read())

	try:
		artist = data["channelMetadataResponse"]["metaData"]["currentEvent"]["artists"]["name"]
		song = data["channelMetadataResponse"]["metaData"]["currentEvent"]["song"]["name"]

		search_spotify(artist, song)
	except Exception as err:
		logger.debug("Error parsing response: %s", err)
		return

def search_spotify(artist, song):
	results = spotify.search(artist + " - " + song, type='track', limit=1)

	if len(results["tracks"]["items"]) == 0:
		logger.debug("Couldn't find: %s - %s", artist, song)
		return

	for track in results['tracks']['items']:
		add_to_playlist(track["id"])
		logger.info("%s - %s (%s)", artist, song, track["id"])

def add_to_playlist(track_id):
	results = spotify.user_playlist_tracks(username, playlist_id)

	for result in results['items']:
		if result['track']['id'] == track_id:
			logger.debug("Track already exists: %s", track_id)
			return

	track_ids = [track_id]
	spotify.user_playlist_add_tracks(username, playlist_id, track_ids)

def setup_logger():
    formatter = logging.Formatter('%(asctime)s: %(message)s')

    handler = logging.FileHandler('siriusxmToSpotify.log')
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

    return logger

if len(sys.argv) == 3:
    username = sys.argv[1]
    playlist_id = sys.argv[2]
else:
    print "Usage: %s username playlist_id" % (sys.argv[0],)
    sys.exit()

scope = 'playlist-modify-public'
token = util.prompt_for_user_token(username, scope)

if not token:
	print "Can't get token for", username
	sys.exit()

logger = setup_logger()

while True:
	token = util.prompt_for_user_token(username, scope)
	spotify = spotipy.Spotify(auth=token)
	scrape_song()
	time.sleep(180)