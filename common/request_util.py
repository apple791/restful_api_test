"""统一HTTP请求入口，写操作不自动重试。"""
import requests


def send_request(
        method,
        url,
        params=None,
        payload=None,
        headers=None,
        session=None,
        timeout=5,
):

    try:
        if session is None:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=payload,
                headers=headers,
                timeout=timeout
            )
        else:
            response = session.request(
                method=method,
                url=url,
                params=params,
                json=payload,
                headers=headers,
                timeout=timeout
            )

        return response

    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None
