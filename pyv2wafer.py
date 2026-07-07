#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for uploading pyvideo JSON files to Wafer. """

import json
import re
from urllib import parse as urlparse

import requests
import click

YOUTUBE_TYPE = "host"  # wat
ARCHIVE_TYPE = "archive"


class WaferApi(object):
    def __init__(self, wafer_url, wafer_auth):
        self._wafer_url = wafer_url
        user, _, password = wafer_auth.partition(':')
        self._wafer_auth = (user, password)

    def _api_url(self, *parts):
        path = "/".join(parts)
        if not path.endswith("/"):
            path += "/"
        return urlparse.urljoin(self._wafer_url, path)

    def _talk_url(self, talk_id):
        return self._api_url('talks', 'api', 'talks', str(talk_id))

    def _talk_urls_url(self, talk_id):
        return self._api_url('talks', 'api', 'talks', str(talk_id), 'urls')

    def get_talk(self, talk_id):
        response = requests.get(self._talk_url(talk_id))
        return response.json()

    def add_talk_url(self, talk_id, url_data):
        response = requests.post(
            self._talk_urls_url(talk_id), auth=self._wafer_auth,
            json=url_data)
        return response.json()


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
        YOUTUBE_TYPE: "Video (youtube.com)",
        ARCHIVE_TYPE: "Video (archive.org)"
    }.get(video["type"], None)


def wafer_talk_url(video):
    return {
      "url": video["url"],
      "description": wafer_desc(video),
    }


def video_on_talk(video, talk):
    desc = wafer_desc(video)
    if desc is None:
        return False
    return any(url["description"] == desc for url in talk["urls"])


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
            if not video_on_talk(video, wafer_talk):
                print("Adding %s to talk %s ..." % (video["type"], talk_id))
                print(wafer_api.add_talk_url(talk_id, wafer_talk_url(video)))


if __name__ == "__main__":
    pyv2wafer()
