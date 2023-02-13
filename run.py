import requests
import json
import m3u8
import sys

from subprocess import Popen, PIPE


DEFAULT_CHANNEL = 'zilioner'
CLIENT_ID = 'kimne78kx3ncx6brgo4mv6wki5h1ko'


def get_access_token(channel):
    query = 'query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!) {  streamPlaybackAccessToken(channelName: $login, params: {platform: "web", playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isLive) {    value    signature    __typename  }  videoPlaybackAccessToken(id: $vodID, params: {platform: "web", playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isVod) {    value    signature    __typename  }}'

    data = {
        'isLive': True,
        'login': channel,
        'isVod': False,
        'vodID': '',
        'playerType': 'site'
    }

    url = 'https://gql.twitch.tv/gql'

    r = requests.post(url, headers={'Client-ID': CLIENT_ID}, json={'operationName': 'PlaybackAccessToken_Template', 'query': query, 'variables': data})

    r.raise_for_status()
    body = r.json()

    return body['data']['streamPlaybackAccessToken']


def get_playlist(channel, access_token):
    url = f"https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8?client_id={CLIENT_ID}&token={access_token['value']}&sig={access_token['signature']}&allow_source=true"

    r = requests.get(url)
    r.raise_for_status()

    res = {}

    for playlist in m3u8.loads(r.text).playlists:
        res[playlist.stream_info.video] = playlist.uri

    return res


def run_movist(url):
    scpt = f"""tell application "Movist Pro"
       activate
       open location "{url}"
       activate
    end tell
"""

    p = Popen(['osascript'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.communicate(scpt.encode('utf-8'))


if __name__ == '__main__':
    try:
       channel = sys.argv[1]
    except IndexError:
       channel = DEFAULT_CHANNEL

    if not channel:
        channel = DEFAULT_CHANNEL

    access_token = get_access_token(channel)
    playlist = get_playlist(channel, access_token)
    run_movist(playlist['720p60'])

