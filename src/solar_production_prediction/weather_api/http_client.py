import http
import json
import typing
import urllib.error
import urllib.request

from lxml import etree
import tenacity
import tenacity.wait


def is_expected_to_be_transient(exc: typing.Any) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        try:
            return http.HTTPStatus(int(exc.code)) in (
                http.HTTPStatus.TOO_MANY_REQUESTS,
                http.HTTPStatus.SERVICE_UNAVAILABLE,
            )
        except ValueError:
            return False

    # Must come after the isinstance check of HTTPError,
    # which is a subclass of URLError
    if isinstance(exc, urllib.error.URLError):
        # DNS error, probably transient
        return "Temporary failure in name resolution" in str(exc.reason)

    return False


def default_retry_wait(_exc: BaseException | None) -> float:
    return 1.0


class HttpClient:
    def get_json(
        self,
        url: str,
        retry_wait: typing.Callable[[BaseException | None], float] = default_retry_wait,
    ) -> typing.Any:
        for attempt in tenacity.Retrying(
            retry=tenacity.retry_if_exception(is_expected_to_be_transient),
            stop=tenacity.stop_after_attempt(3),
            wait=self._wait(retry_wait),
        ):
            with attempt:
                request = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(request) as response:
                    response_body = response.read()
                    response_parsed = json.loads(response_body.decode("utf-8"))
                    return response_parsed

    @tenacity.retry(retry=tenacity.retry_if_exception(is_expected_to_be_transient))
    def get_xml(self, url: str) -> etree.ElementBase:
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request) as response:
            response_body = response.read()
            root: etree.ElementBase = etree.fromstring(response_body)
            return root

    def _wait(
        self, waiter: typing.Callable[[BaseException | None], float]
    ) -> tenacity.wait.wait_base:
        class Waiter(tenacity.wait.wait_base):
            def __call__(self, retry_state: tenacity.RetryCallState) -> float:
                outcome = retry_state.outcome
                if outcome is None:
                    return waiter(None)
                return waiter(outcome.exception())

        return Waiter()
