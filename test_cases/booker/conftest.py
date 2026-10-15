from copy import deepcopy
from uuid import uuid4

import pytest

from common.booker_client import BookerClient
from common.yaml_util import load_case_data
from config.restful_config import BASE_URL, PASSWORD, TIMEOUT, USERNAME


@pytest.fixture(autouse=True)
def require_live(request):
    if not request.config.getoption("--live"):
        pytest.skip("真实接口测试需显式传入 --live；默认仅运行离线测试")


@pytest.fixture
def booker():
    client = BookerClient(BASE_URL, TIMEOUT)
    yield client
    client.close()


@pytest.fixture
def token(booker):
    return booker.authenticate(USERNAME, PASSWORD)


@pytest.fixture
def booking_factory(booker, token):
    """每条测试只操作自己创建的记录，失败时也尝试清理。"""
    created = []

    def create(overrides=None):
        payload = deepcopy(load_case_data("booking_cases.yaml")["base_booking"])
        payload["firstname"] = "Practice_" + uuid4().hex[:12]
        if overrides:
            payload.update(overrides)
        result = booker.create_booking(payload)
        assert result.status_code == 200, f"创建预订失败：{result.status_code}"
        data = result.json()
        assert isinstance(data.get("bookingid"), int), "响应缺少有效 bookingid"
        booking_id = data["bookingid"]
        created.append(booking_id)
        assert data["booking"] == payload, "创建响应与提交数据不一致"
        return booking_id, payload

    yield create

    failures = []
    for booking_id in created:
        try:
            current = booker.get_booking(booking_id)
            if current.status_code == 404:
                continue
            assert current.status_code == 200, f"清理前查询失败 {current.status_code}"
            result = booker.delete_booking(booking_id, token)
            assert result.status_code == 201, f"清理删除失败 {result.status_code}"
            assert booker.get_booking(booking_id).status_code == 404, "删除后预订仍存在"
        except Exception as exc:
            failures.append(f"bookingid={booking_id}: {exc}")
    if failures:
        pytest.fail("测试数据清理失败：" + "; ".join(failures))
