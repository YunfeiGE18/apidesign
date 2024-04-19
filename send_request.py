import requests
import json
import collections

from vlib.configuration.useragent_config import user_agent

class ApiRequest(object):
    """

    The APIrequest class contains all the relevant data for a single request along with the relevant methods for generating the header, request body, etc.
    
    Attributes
    ----------
    url: str
    method: str
    proxy: dict
    header: dict
    request_body: json
    parameter: List[Paramter]
        A list of parameter associated with this request that could be added into header / query / request_body / etc.
    """

    @staticmethod
    def send_http_request(
        api_url,
        headers={},
        method="GET",
        request_body=None,
        proxies = {},
        cookie=None,
        is_redirect=True,
        timeout=10,
        verify=False,
        files=None,
        **kwargs
    ):
        
        Response = collections.namedtuple(
            "Response", ["code", "headers", "body"]
        )
        
        if not headers:
            headers = {}

        default_headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": ", ".join(("gzip", "deflate")),
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        default_headers.update(headers)

        response = requests.request(
            method,
            url=api_url,
            headers=default_headers,
            data=request_body,
            timeout=timeout,
            proxies=proxies,
            cookies=cookie,
            allow_redirects=is_redirect,
            verify=verify,
            files=files,
            **kwargs
        )
        response_code = response.status_code
        response_headers = dict(response.headers)
        response_body = response.content

        return Response(
            response_code,
            response_headers,
            response_body
        )