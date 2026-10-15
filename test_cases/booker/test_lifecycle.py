"""Restful-booker 接口测试，按目标服务约定检查结果。"""
from copy import deepcopy

import allure
import pytest

from common.yaml_util import get_case_ids, load_case_data

DATA = load_case_data("booking_cases.yaml")
pytestmark = [pytest.mark.integration, pytest.mark.regression]


@pytest.mark.smoke
@allure.feature("预订完整业务流程")
def test_booking_lifecycle(booker, token, booking_factory):
    booking_id, payload = booking_factory()
    assert booker.get_booking(booking_id).json() == payload
    updated = deepcopy(payload)
    updated.update(totalprice=360, depositpaid=False, additionalneeds="Dinner")
    result = booker.update_booking(booking_id, updated, token)
    assert result.status_code == 200
    assert result.json() == updated
    current = booker.get_booking(booking_id)
    assert current.status_code == 200
    assert current.json() == updated
    result = booker.patch_booking(booking_id, {"lastname": "Updated"}, token)
    assert result.status_code == 200
    updated["lastname"] = "Updated"
    current = booker.get_booking(booking_id)
    assert current.status_code == 200
    assert current.json() == updated, "PATCH 应只修改指定字段"
    assert booker.delete_booking(booking_id, token).status_code == 201
    assert booker.get_booking(booking_id).status_code == 404
