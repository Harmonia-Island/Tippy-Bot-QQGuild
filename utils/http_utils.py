from typing import Optional, Dict, Any
from utils.user_agent import get_user_agent
from .utils import get_local_proxy
from service.log import logger
import aiohttp


class AsyncAioHTTP:

    @classmethod
    async def get(
        cls,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        use_proxy: bool = False,
        proxy: Dict[str, str] = None,
        timeout: Optional[int] = 30,
        method: str = "json",
        **kwargs,
    ):
        """
        说明：
            Get
        参数：
            :param url: url
            :param params: params
            :param headers: 请求头
            :param cookies: cookies
            :param use_proxy: 使用默认代理
            :param proxy: 指定代理
            :param allow_redirects: allow_redirects
            :param timeout: 超时时间
        """
        if not headers:
            headers = get_user_agent()
        proxy = get_local_proxy() if use_proxy else None

        async with aiohttp.ClientSession(
                headers=headers,
                connector=aiohttp.TCPConnector(verify_ssl=False),
                timeout=timeout) as session:
            try:
                async with session.get(
                        url=url,
                        timeout=timeout,
                        cookies=cookies,
                        proxy=proxy,
                        params=params,
                ) as response:
                    if method == 'json':
                        return await response.json(content_type=None)
                    elif method == 'text':
                        return await response.text()
                    else:
                        return await response.read()
            except Exception as e:
                logger.warning(f"访问 url：{url} 发生错误 {type(e)}：{e}")
                return None

    @classmethod
    async def post(
        cls,
        url: str,
        *,
        data: Optional[Dict[str, str]] = None,
        content: Any = None,
        files: Any = None,
        use_proxy: bool = False,
        proxy: Dict[str, str] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        timeout: Optional[int] = 30,
        method: str = 'json',
        **kwargs,
    ):
        """
        说明：
            Post
        参数：
            :param url: url
            :param data: data
            :param content: content
            :param files: files
            :param use_proxy: 是否默认代理
            :param proxy: 指定代理
            :param json: json
            :param params: params
            :param headers: 请求头
            :param cookies: cookies
            :param allow_redirects: allow_redirects
            :param timeout: 超时时间
        """
        if not headers:
            headers = get_user_agent()
        proxy = get_local_proxy() if use_proxy else None

        async with aiohttp.ClientSession(
                headers=headers,
                connector=aiohttp.TCPConnector(verify_ssl=False),
                timeout=timeout) as session:
            try:
                async with session.post(url=url,
                                        timeout=timeout,
                                        cookies=cookies,
                                        json=json,
                                        params=params,
                                        data=data,
                                        proxy=proxy) as response:
                    if method == 'json':
                        return await response.json()
                    elif method == 'text':
                        return await response.text()
                    else:
                        return await response.read()
            except Exception:
                return None
