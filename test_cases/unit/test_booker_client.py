"""无需联网：检查请求映射、响应校验和报告脱敏。"""
import importlib.util
import json
from unittest.mock import Mock

import pytest
import requests

pytestmark = pytest.mark.unit
spec = importlib.util.find_spec("common.booker_client")
if spec:
    from common.booker_client import BookerClient, sanitize
else:
    BookerClient = None
    sanitize = None


def response(code=200, data=None):
    result = requests.Response()
    result.status_code = code
    result._content = json.dumps(data if data is not None else {}).encode()
    result.url = "http://localhost/booking"
    return result


def client_with_response(result):
    assert BookerClient is not None, "缺少 Restful-booker 业务客户端"
    session = Mock(spec=requests.Session)
    session.request.return_value = result
    return BookerClient("http://localhost/", session=session), session


@pytest.mark.parametrize("method,args,verb,path,payload,headers", [
    ("list_bookings", (), "GET", "/booking", None, None),
    ("get_booking", (12,), "GET", "/booking/12", None, None),
    ("create_booking", ({"firstname": "Test"},), "POST", "/booking", {"firstname": "Test"}, None),
    ("update_booking", (12, {"firstname": "New"}, "sample-token"), "PUT", "/booking/12", {"firstname": "New"}, {"Cookie": "token=sample-token"}),
    ("patch_booking", (12, {"firstname": "New"}, "sample-token"), "PATCH", "/booking/12", {"firstname": "New"}, {"Cookie": "token=sample-token"}),
    ("delete_booking", (12, "sample-token"), "DELETE", "/booking/12", None, {"Cookie": "token=sample-token"}),
])
def test_request_mapping(method, args, verb, path, payload, headers):
    client, session = client_with_response(response())
    getattr(client, method)(*args)
    session.request.assert_called_once()
    actual = session.request.call_args.kwargs
    assert actual["method"] == verb
    assert actual["url"] == "http://localhost" + path
    assert actual["json"] == payload
    assert actual["timeout"] > 0
    assert actual["headers"]["Accept"] == "application/json"
    if headers:
        assert actual["headers"]["Cookie"] == headers["Cookie"]


def test_authentication_extracts_token():
    client, session = client_with_response(response(data={"token": "sample-token"}))
    assert client.authenticate("user", "secret") == "sample-token"
    assert session.request.call_args.kwargs["json"] == {"username": "user", "password": "secret"}


def test_invalid_authentication_does_not_leak_password():
    client, _ = client_with_response(response(data={"reason": "Bad credentials"}))
    with pytest.raises(ValueError, match="未返回有效 Token") as caught:
        client.authenticate("user", "secret")
    assert "secret" not in str(caught.value)


def test_create_is_not_retried_on_timeout():
    client, session = client_with_response(response())
    session.request.side_effect = requests.Timeout("timeout")
    with pytest.raises(RuntimeError, match="请求失败"):
        client.create_booking({"firstname": "Test"})
    assert session.request.call_count == 1


def test_nested_report_data_redacts_secrets():
    assert sanitize is not None, "缺少报告脱敏函数"
    assert sanitize({"password": "secret", "nested": [{"token": "abc", "firstname": "Test"}]}) == {
        "password": "***", "nested": [{"token": "***", "firstname": "Test"}]
    }


def test_close_releases_session():
    client, session = client_with_response(response())
    client.close()
    session.close.assert_called_once()
