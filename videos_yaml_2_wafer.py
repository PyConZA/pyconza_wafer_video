#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for setting video data from a videos.yaml file after uploading
    to the internet archive. """

# This code is fully of dubious assumptions and should be
# used with due caution (and undue caution if you feel like it)

from wafer_video import WaferApi, video_on_talk, YOUTUBE_VIDEO_DESC, ARCHIVE_VIDEO_DESC

import yaml
import re
from urllib import parse as urlparse

import requests
import click


TalkUrlRE = re.compile('^Talk.*https://.*za.pycon.org/talks/(.*)/$')
YoutubeRE = re.compile(r'\[([^]]*)\].mp4')


def read_video_yaml_file(video_file):
    with open(video_file) as f:
        data = yaml.safe_load(f)

    videos = []
    for candidate in data['videos']:
        # extraact Talk id from the description
        description = candidate['metadata']['description'].splitlines()
        talk_url = None
        for ll in description:
            talk_url = TalkUrlRE.match(ll)
            if talk_url:
                break
        if not talk_url:
            # Not a talk
            continue
        the_talk = candidate['metadata'].copy()
        the_talk['talk id'] = talk_url.groups()[0]
        the_talk['videos'] = []

        # Kludge together the youtube url from the yt download filename
        base_youtube = candidate['filename']
        yt_id = YoutubeRE.search(base_youtube)
        if not yt_id:
            continue
        youtube = {
            'desc': YOUTUBE_VIDEO_DESC,
            'url': f'https://www.youtube.com/watch?v={yt_id.groups()[0]}'
        }
        the_talk['videos'].append(youtube)
        # Create the archive.org url from the identifier
        archive = {
            'desc': ARCHIVE_VIDEO_DESC,
            'url': f'https://archive.org/details/{candidate["identifier"]}'
        }
        the_talk['videos'].append(archive)

        videos.append(the_talk)
    return videos


def wafer_talk_url(video):
    return {
      "url": video["url"],
      "description": video['desc'],
    }


@click.command()
@click.option('--wafer-url', help='Base Wafer URL.')
@click.option('--wafer-auth', help='Username:password.')
@click.argument('pyvideo-file')
def pyv2wafer(pyvideo_file, wafer_url, wafer_auth):
    wafer_api = WaferApi(wafer_url, wafer_auth)
    videos = read_video_yaml_file(pyvideo_file)
    for talk in videos:
        talk_id = talk['talk id']
        if talk_id is None:
            continue
        #wafer_talk = wafer_api.get_talk(talk_id)
        for video in talk["videos"]:
            if video["desc"] not in (YOUTUBE_VIDEO_DESC, ARCHIVE_VIDEO_DESC):
                continue
            print("Adding %s to talk %s ..." % (video["desc"], talk_id))
            print(video['url'])
            #if not video_on_talk(video, wafer_talk):
            #    print("Adding %s to talk %s ..." % (video["type"], talk_id))
            #    print(wafer_api.add_talk_url(talk_id, wafer_talk_url(video)))


if __name__ == "__main__":
    pyv2wafer()
