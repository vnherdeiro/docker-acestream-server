#!/usr/bin/env python

import hashlib
import json
import re
import signal
import subprocess
import sys
import time
import urllib.request as urllib2
import click

DEFAULT_SERVER_HOSTNAME = '127.0.0.1'
DEFAULT_SERVER_PORT = 6878
SERVER_POLL_TIME = 2
SERVER_STATUS_STREAM_ACTIVE = 'dl'


def exit_error(message):
	sys.stderr.write('Error: {0}\n'.format(message))
	sys.exit(1)

class WatchSigint(object):
	_sent = None

	def __init__(self):
		if (WatchSigint._sent is None):
			# install handler
			WatchSigint._sent = False
			signal.signal(signal.SIGINT,self._handler)

	def _handler(self,signal,frame):
		# Ctrl-C (SIGINT) sent to process
		WatchSigint._sent = True

	def sent(self):
		return WatchSigint._sent


def api_request(uri):
	response = urllib2.urlopen(uri)
	return json.loads(response.read()).get('response',{})

def start_stream(server_hostname,server_port,stream_pid):
	# build stream UID from PID
	stream_uid = hashlib.sha1(stream_pid.encode('utf-8')).hexdigest()

	# call API to commence stream
	response = api_request('http://{0}:{1}/ace/getstream?format=json&sid={2}&id={3}'.format(
		server_hostname,
		server_port,
		stream_uid,
		stream_pid
	))

	# return statistics API endpoint and HTTP video stream URLs
	return (
		response['stat_url'],
		response['playback_url']
	)

def stream_stats_message(response):
	return 'Peers: {0} // Down: {1}KB // Up: {2}KB'.format(
		response.get('peers',0),
		response.get('speed_down',0),
		response.get('speed_up',0)
	)

def await_playback(watch_sigint,statistics_url):
	while (True):
		response = api_request(statistics_url)

		if (response.get('status') == SERVER_STATUS_STREAM_ACTIVE):
			# stream is ready
			print('Ready!\n')
			return True

		if (watch_sigint.sent()):
			# user sent SIGINT, exit now
			print('\nExit!')
			return False

		# pause and check again
		print('Waiting... [{0}]'.format(stream_stats_message(response)))
		time.sleep(SERVER_POLL_TIME)

def execute_media_player(media_player_bin,playback_url):
	subprocess.Popen(
		media_player_bin.split() + [playback_url],
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE
	)

def stream_progress(watch_sigint,statistics_url):
	print('')
	while (True):
		print('Streaming... [{0}]'.format(
			stream_stats_message(api_request(statistics_url))
		))

		if (watch_sigint.sent()):
			# user sent SIGINT, exit now
			print('\nExit!')
			return

		time.sleep(SERVER_POLL_TIME)

@click.command()
@click.argument('stream_pid')
@click.option('--media_player_bin', default='/Applications/VLC.app/Contents/MacOS/VLC',)
@click.option('--progress_follow', default=True,)
@click.option('--server_hostname', default=DEFAULT_SERVER_HOSTNAME,)
@click.option('--server_port', default=DEFAULT_SERVER_PORT,)
def main(stream_pid, media_player_bin, progress_follow, server_hostname, server_port):

	# create Ctrl-C watcher
	watch_sigint = WatchSigint()

	# trimming prefix
	PREFIX ='acestream://' 
	if stream_pid.startswith(PREFIX):
		stream_pid = stream_pid[len(PREFIX):]
	print('Connecting to program ID [{0}]'.format(stream_pid))
	statistics_url,playback_url = start_stream(server_hostname,server_port,stream_pid)

	print('Awaiting successful connection to stream')
	if (not await_playback(watch_sigint,statistics_url)):
		# exit early
		return

	print('Playback available at [{0}]'.format(playback_url))
	if (media_player_bin is not None):
		print('Starting media player...')
		execute_media_player(media_player_bin,playback_url)

	if (progress_follow):
		stream_progress(watch_sigint,statistics_url)


if (__name__ == '__main__'):
	main()
