# -*- coding: utf-8 -*-
"""
@File    :  core.py
@Time    :  2022/2/15 17:05:11
@Author  :  Zrq
@Version :  V1.0
@Contact :  ceshi17777813307@163.com
@Desc    :  核心文件
"""
import requests
import logging
from requests.models import Response

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(
            self,
            proxies: dict = None,
            cookies: dict = None,
            timeout: int = 15
    ):
        self.proxies = proxies
        self.cookies = cookies
        self.timeout = timeout
        self.requests_args = {
            'timeout': timeout,
            'proxies': proxies,
            'cookies': cookies
        }

    def post(self, url, **kwargs) -> Response:
        requests_args = dict(**self.requests_args)
        requests_args.update(kwargs)
        return requests.post(url, **requests_args)

    def get(self, url, **kwargs) -> Response:
        requests_args = dict(**self.requests_args)
        requests_args.update(kwargs)
        return requests.get(url, **requests_args)

    def put(self, url, **kwargs) -> Response:
        requests_args = dict(**self.requests_args)
        requests_args.update(kwargs)
        return requests.put(url, **requests_args)

    def delete(self, url, **kwargs) -> Response:
        requests_args = dict(**self.requests_args)
        requests_args.update(kwargs)
        return requests.delete(url, **requests_args)
