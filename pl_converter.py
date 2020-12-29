# -*- coding: utf-8 -*-
"""Main module."""
from typing import Union

import requests
import toml

config = toml.load('config.toml')


def get_play_list(url):
    """Get playlist from URL.

    Args:
        url: playlist url

    Returns:
        lines: generator object of a playlist lines
    """
    playlist = requests.get(url, stream=True)
    playlist.encoding = 'utf-8'
    return playlist.iter_lines(decode_unicode=True)


def playlist_converter(playlist_lines) -> Union[str, bool]:
    """Convert playlist to the format that Kodi supports.

    Args:
        playlist_lines: generator object of a playlist lines

    Returns:
        playlist: Converted playlist
    """
    playlist = '#EXTM3U x-tvg-url="{0}"\n'.format(config['epg']['url'])
    prefix = ''
    channel_name = ''
    channel_group = ''
    if next(playlist_lines) != '#EXTM3U':
        return False

    for line in playlist_lines:
        if line[:7] == '#EXTINF':
            parts = line.split(',')
            prefix = parts[0].strip()
            channel_name = parts[1].strip()
        elif line[:7] == '#EXTGRP':
            parts = line.split(':')
            channel_group = parts[1].strip()
        elif line[:4] == 'http':
            url = line.strip()
            playlist += '{0} group-title="{1}", tvg-name="{2}" {3}\n{4}\n'.format(
                prefix,
                channel_group,
                channel_name,
                channel_name,
                url,
                )
    return playlist


def generate_file(playlist: str):
    """Generate new playlist file.

    Args:
        playlist: Playlist
    """
    with open('new_playlist.m3u8', 'w') as output_file:
        output_file.write(playlist)


if __name__ == '__main__':
    old_play_list = get_play_list(config['playlist']['url'])
    new_play_list = playlist_converter(old_play_list)
    if new_play_list:
        generate_file(new_play_list)
