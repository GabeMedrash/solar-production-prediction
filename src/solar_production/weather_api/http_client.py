import http
import typing
import urllib.error
import urllib.request

from lxml import etree
import tenacity


def is_expected_to_be_transient(exc: typing.Any) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        try:
            return http.HTTPStatus(int(exc.code)) in (
                http.HTTPStatus.TOO_MANY_REQUESTS,
                http.HTTPStatus.SERVICE_UNAVAILABLE,
            )
        except ValueError:
            return False

    return False


class HttpClient:
    @staticmethod
    @tenacity.retry(retry=tenacity.retry_if_result(is_expected_to_be_transient))
    def get_xml(url: str) -> etree.ElementBase:
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request) as response:
            response_body = response.read()
            root: etree.ElementBase = etree.fromstring(response_body)
            return root
