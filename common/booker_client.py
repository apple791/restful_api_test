"""酒店预订业务接口；沿用原项目的公共请求封装。"""
import json

import allure
import requests

from common.request_util import send_request


def sanitize(value):
    if isinstance(value, dict):
        return {key: "***" if key.lower() in {"password", "token", "cookie", "authorization"}
                else sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


class BookerClient:
    def __init__(self, base_url, timeout=10, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()

    def close(self):
        self.session.close()

    def request(self, method, path, payload=None, token=None, params=None):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if token is not None:
            headers["Cookie"] = f"token={token}"
        # 不自动重试写操作，避免超时后重复创建预订。
        with allure.step(f"{method} {path}"):
            response = send_request(method, self.base_url + path, payload=payload,
                                    params=params, headers=headers, session=self.session,
                                    timeout=self.timeout)
            if response is None:
                raise RuntimeError(f"请求失败：{method} {path}，请检查网络和服务状态")
            try:
                body = sanitize(response.json())
            except ValueError:
                body = response.text
            # 不附加请求头和密码；鉴权接口不保存原始响应，避免 Token 泄露。
            if path == "/auth":
                body = {"status_code": response.status_code, "auth_response": "redacted"}
            allure.attach(json.dumps({"status_code": response.status_code, "body": body},
                                     ensure_ascii=False, indent=2), "响应",
                          allure.attachment_type.JSON)
            return response

    def authenticate(self, username, password):
        result = self.request("POST", "/auth", {"username": username, "password": password})
        result.raise_for_status()
        token = result.json().get("token")
        if not isinstance(token, str) or not token:
            raise ValueError("鉴权接口未返回有效 Token")
        return token

    def list_bookings(self, params=None):
        return self.request("GET", "/booking", params=params)

    def get_booking(self, booking_id):
        return self.request("GET", f"/booking/{booking_id}")

    def create_booking(self, payload):
        return self.request("POST", "/booking", payload)

    def update_booking(self, booking_id, payload, token=None):
        return self.request("PUT", f"/booking/{booking_id}", payload, token)

    def patch_booking(self, booking_id, payload, token=None):
        return self.request("PATCH", f"/booking/{booking_id}", payload, token)

    def delete_booking(self, booking_id, token=None):
        return self.request("DELETE", f"/booking/{booking_id}", token=token)
