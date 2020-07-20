# -*- coding: utf-8 -*-

import requests
import config


def get_play_list(url):
    result = requests.get(url, stream=True)
    result.encoding = 'utf-8'
    lines = result.iter_lines(decode_unicode=True)
    return lines


def converter(pl_lines):
    play_list = f'#EXTM3U x-tvg-url="{config.EPG_URL}"\n\n'
    prefix = ""
    channel_name = ""
    channel_group = ""
    if next(pl_lines) != '#EXTM3U':  # checking first line for existing of #EXTM3U
        return False

    for line in pl_lines:
        if line[:7] == "#EXTINF":
            parts = line.split(',')
            prefix = parts[0].strip(' \t\n')
            channel_name = parts[1].strip(' \t\n')
        elif line[:7] == "#EXTGRP":
            parts = line.split(':')
            channel_group = parts[1].strip(' \t\n')
        elif line[:4] == "http":
            link = line.strip(' \t\n')
            # channel_id = link.split("/")[5]
            play_list += f'{prefix} group-title="{channel_group}", tvg-name="{channel_name}", ' \
                         f'{channel_name}\n{link}\n\n'
            # play_list += f'{prefix} group-title="{channel_group}", tvg-id="{channel_id}", ' \
            #              f'tvg-logo="{config.LOGO_URL}{channel_id}.png",{channel_name}\n{link}\n\n'
        else:
            pass
    return play_list


def gen_file(play_list):
    with open('new_playlist.m3u8', 'w') as output_file:
        output_file.write(play_list)


if __name__ == '__main__':
    old_play_list = get_play_list(config.PL_URL)
    new_play_list = converter(old_play_list)
    if new_play_list:
        gen_file(new_play_list)
        print("new playlist is ready")
    else:
        print("Incorrect playlist format")
