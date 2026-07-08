"""Common helpers for wafer api video uploading"""

YOUTUBE_VIDEO_DESC = "Video (youtube.com)",
ARCHIVE_VIDEO_DESC = "Video (archive.org)"


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


def video_on_talk(desc, talk):
    if desc is None:
        return False
    return any(url["description"] == desc for url in talk["urls"])

