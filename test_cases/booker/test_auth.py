"""Restful-booker 接口测试，按目标服务约定检查结果。"""
from copy import deepcopy

import allure
import pytest

from common.yaml_util import get_case_ids, load_case_data

DATA = load_case_data("booking_cases.yaml")
pytestmark = [pytest.mark.integration, pytest.mark.regression]


@pytest.mark.negative
@allure.feature("写操作权限")
@pytest.mark.parametrize("operation", ["update_booking", "patch_booking", "delete_booking"])
@pytest.mark.parametrize("case", DATA["unauthorized_cases"], ids=get_case_ids(DATA["unauthorized_cases"]))
def test_unauthorized_write_does_not_change_booking(booker, booking_factory, operation, case):
    booking_id, payload = booking_factory()
    if operation == "delete_booking":
        result = booker.delete_booking(booking_id, case["token"])
    else:
        update = deepcopy(payload) if operation == "update_booking" else {}
        update["lastname"] = "Unauthorized"
        result = getattr(booker, operation)(booking_id, update, case["token"])
    assert result.status_code == 403
    current = booker.get_booking(booking_id)
    assert current.status_code == 200
    assert current.json() == payload, "被拒绝的写操作不应改变已有数据"


@pytest.mark.negative
def test_wrong_credentials(booker):
    result = booker.request("POST", "/auth", {"username": "invalid-user", "password": "invalid-password"})
    assert result.status_code == 200
    assert result.json().get("reason") == "Bad credentials"
    assert "token" not in result.json()
