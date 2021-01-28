# Include standard modules
import sys, argparse
import requests
import string
import musicbrainzngs
import numpy as np
import matplotlib.pyplot as plt

LYRICSAPIROOT = "https://api.lyrics.ovh/v1/"

####################################
#  Class to contain artist info    #
####################################

class Artist:

	artist_id = None
	tracks = None

	def __init__(self, artist):
		self.artist = artist
		self.artist_id = self.set_artist_id(artist)

		result = musicbrainzngs.get_artist_by_id(self.artist_id)

		# The api seems to return a near miss if it can't find the correct artist
		# which causes problems further on, so, check the name of the artist with the
		# returned id and make sure they match
		
		if result:
			if result['artist']['name'] != artist:
				raise Exception

		if self.artist_id:
			self.albums = self.set_albums(self.artist_id)
		else:
			raise Exception

		if self.albums:
			self.tracks = self.set_tracklists(self.artist, self.albums)
		else:
			raise Exception

	def get_tracklists(self):
		return self.tracks

	def set_artist_id(self, artist):
		# The artists seem to be ranked from the most to the least familiar, so limit 1
		# returns the most popular artist by that name
		result = musicbrainzngs.search_artists(artist=artist, limit=1)

		if len(result['artist-list']) != 0:
			return result['artist-list'][0]['id']
		else:
			return None

	def set_albums(self, artist_id):
		albums = []

		result = musicbrainzngs.get_artist_by_id(artist_id, includes=["release-groups"],
															release_type=["album"])

		for r in result["artist"]["release-group-list"]:
			if r["type"] == "Album":
				albums.append(r["title"])

		return albums

	def set_tracklists(self, artist, albums):
		tracklist = []

		for album in albums:
			result = musicbrainzngs.search_releases(artist=artist, release=album, limit=1)
			album_id = result["release-list"][0]["id"]

			tracks = musicbrainzngs.get_release_by_id(album_id, includes=["recordings"])

			if 'status' in tracks['release']:
				if tracks['release']['status'] == 'Official':
					for x in range(len(tracks['release']['medium-list'])):
						for y in range(len(tracks['release']['medium-list'][x]['track-list'])):
							tracklist.append(tracks['release']['medium-list'][x]['track-list'][y]['recording']['title'])

		# To remove duplicates (compilation albums etc...) convert to a set and back to a list
		return list(set(tracklist))

####################################
#  Handle command line parameters  #
####################################

def fn_handle_args():
   # Initiate the parser
	parser = argparse.ArgumentParser()
	parser.add_argument("-a", "--all", help="Display all metrics about the artist",	action="store_true")
	parser.add_argument("-p", "--plot", help="Plot chart of word length distribution", action="store_true")
	parser.add_argument("artist", nargs='+', help="List of artists")

	# Read arguments from the command line
	args = parser.parse_args()

	return args

####################################
#  Gather lyrics from lyrics.ovh   #
####################################

def fn_get_tracklist_lyrics(artist, track):
	l = []

	try:
		response = requests.get(LYRICSAPIROOT + artist + '/' + track)
		response.raise_for_status()

	except Exception as err:
		print(f'Cannot open lyrics for {artist}: {track}')
	else:
		if response.status_code == 200:
			lyrics = response.json()['lyrics']
			l = [len(item) for item in lyrics.split()]

	return l

####################################
#  Plot graph of lyrics/length     #
####################################

def fn_statistics(lenlist, tracklistct, doall=False):
	a = np.array(lenlist)
	d = {}

	d['mean'] = np.mean(a)

	if doall:
		d['std'] = np.std(a)
		d['var'] = np.var(a)

		d['mini'] = np.amin(a)
		d['maxi'] = np.amax(a)
		d['med'] = np.median(a)
		csum = np.cumsum(a)
		d['csum'] = csum[-1]

		d['songs'] = tracklistct
		d['words'] = np.count_nonzero(a > 0)

		d['unique'], d['counts'] = np.unique(a, return_counts=True)

	return d

####################################
#  Plot graph of lyrics/length     #
####################################

def fn_plot(artists, stats):

	for a in range(len(artists)):
		plt.plot(stats[a]['unique'], stats[a]['counts'])

	plt.legend(artists, loc='upper right'
		)
	plt.xlabel("Word Length")
	plt.ylabel("Count")
	plt.title(f"Lyric length distribution")

	plt.show()

#########################################################################################
#                                                                                       #
#      M A I N  R O U T I N E                                                           #                                                                                 */
#                                                                                       #
#########################################################################################

if __name__ == "__main__":
	args = fn_handle_args()

	musicbrainzngs.set_useragent(
    	"python-musicbrainzngs-example",
    	"0.1",
    	"https://github.com/alastair/python-musicbrainzngs/",
	)

	artistlist = []
	tracklist = []
	lenlist = []

	# Wanted to use threads here but ran out of time
	for a in range(len(args.artist)):
		print(f"Processing '{args.artist[a]}' ...")
		try:
			artistlist.append(Artist(args.artist[a]))
		except:
			print(f"No details found for artist '{args.artist[a]}' - aborting")
			sys.exit()

		tracklist.append(artistlist[a].get_tracklists())

		l = []
		for track in tracklist[a]:
			l.extend(fn_get_tracklist_lyrics(args.artist[a], track))

		lenlist.append(l)

	# Now do statistical analysis
	stats = []

	for a in range(len(args.artist)):
		stats.append(fn_statistics(lenlist[a], len(tracklist[a]), args.all))

		
		print(f"'{args.artist[a]}' songs have the following statistics:")

		# We always want the mean
		print(f"-> Average lyric word size: {stats[a]['mean']:.4f}")

		# Other stats are available ...
		if args.all:
			print(f"-> Variance:                {stats[a]['var']:.4f}")
			print(f"-> Standard deviation:      {stats[a]['std']:.4f}")
			print(f"-> Minimum word length:     {stats[a]['mini']}")
			print(f"-> Maximum word length:     {stats[a]['maxi']}")
			print(f"-> Median:                  {stats[a]['med']}")
			print(f"-> # of unique tracks:      {stats[a]['songs']}")
			print(f"-> # of words in lyrics:    {stats[a]['words']}")
			print(f"-> Total # of characters:   {stats[a]['csum']}")

		print("\n")

	# Plot count/length for all musicicans
	if args.all and args.plot:
		fn_plot(args.artist, stats)
