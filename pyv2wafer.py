#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for uploading pyvideo JSON files to Wafer. """

from wafer_video import WaferApi, video_on_talk, YOUTUBE_VIDEO_DESC, ARCHIVE_VIDEO_DESC

import json
import re

import click

YOUTUBE_TYPE = "host"  # wat
ARCHIVE_TYPE = "archive"


def read_pyvideo_file(pyvideo_file):
    with open(pyvideo_file) as f:
        return json.loads(f.read())


def find_talk_id(data):
    urls = [v["url"] for v in data["videos"] if v["type"] == "conf"]
    pattern = re.compile(r"^.*/talks/(?P<id>\d+)-.*/$")
    matches = [pattern.match(u) for u in urls]
    ids = [m.group('id') for m in matches if m]
    if len(ids) == 1:
        return ids[0]
    return None


def wafer_desc(video):
    return {
        YOUTUBE_TYPE: YOUTUBE_VIDEO_DESC,
        ARCHIVE_TYPE: ARCHIVE_VIDEO_DESC,
    }.get(video["type"], None)


def wafer_talk_url(video):
    return {
      "url": video["url"],
      "description": wafer_desc(video),
    }


@click.command()
@click.option('--wafer-url', help='Base Wafer URL.')
@click.option('--wafer-auth', help='Username:password.')
@click.argument('pyvideo-files', nargs=-1)
def pyv2wafer(pyvideo_files, wafer_url, wafer_auth):
    wafer_api = WaferApi(wafer_url, wafer_auth)
    for pyvideo_file in pyvideo_files:
        pyvideo_talk = read_pyvideo_file(pyvideo_file)
        talk_id = find_talk_id(pyvideo_talk)
        if talk_id is None:
            continue
        wafer_talk = wafer_api.get_talk(talk_id)
        for video in pyvideo_talk["videos"]:
            if video["type"] not in (YOUTUBE_TYPE, ARCHIVE_TYPE):
                continue
            if not video_on_talk(wafer_desc(video), wafer_talk):
                print("Adding %s to talk %s ..." % (video["type"], talk_id))
                print(wafer_api.add_talk_url(talk_id, wafer_talk_url(video)))


if __name__ == "__main__":
    pyv2wafer()
