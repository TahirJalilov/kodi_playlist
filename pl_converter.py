# -*- coding: utf-8 -*-

import os
import sys
import logging
import requests
import config

os.chdir(sys.path[0])  # set current directory as working for cron job

logging.basicConfig(level=logging.INFO, filename='errors.log', format='%(asctime)s : %(message)s')


def get_play_list(url):
    result = requests.get(url, stream=True)
    result.encoding = 'utf-8'
    lines = result.iter_lines(decode_unicode=True)
    return lines


def converter(pl_lines):
    play_list = f'#EXTM3U x-tvg-url="{config.EPG}"\n\n'
    prefix = ''
    chanel_name = ''
    chanel_group = ''
    if next(pl_lines) != '#EXTM3U':  # checking first line for existing of #EXTM3U
        return False

    for line in pl_lines:
        if line[:7] == '#EXTINF':
            parts = line.split(',')
            prefix = parts[0].strip(' \t\n')
            chanel_name = parts[1].strip(' \t\n')
        elif line[:7] == '#EXTGRP':
            parts = line.split(':')
            chanel_group = parts[1].strip(' \t\n')
            # play_list += f'{prefix} tvg-name="{chanel_name}", group-title="{chanel_group}", {chanel_name}\n'
        elif line[:4] == "http":
            link = line.strip(' \t\n')
            play_list += f'{prefix} tvg-name="{chanel_name}", group-title="{chanel_group}", {chanel_name}\n{link}\n\n'
        else:
            pass
    return play_list


def gen_file(play_list):
    with open('new_playlist.m3u8', 'w') as output_file:
        output_file.write(play_list)


if __name__ == '__main__':
    old_play_list = get_play_list(config.URL)
    new_play_list = converter(old_play_list)
    if new_play_list:
        gen_file(new_play_list)
    else:
        logging.info("Incorrect playlist format")
