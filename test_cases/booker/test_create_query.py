"""Restful-booker 接口测试，按目标服务约定检查结果。"""
from copy import deepcopy

import allure
import pytest

from common.yaml_util import get_case_ids, load_case_data

DATA = load_case_data("booking_cases.yaml")
pytestmark = [pytest.mark.integration, pytest.mark.regression]


@allure.feature("预订增删改查")
@pytest.mark.parametrize("case", DATA["create_cases"], ids=get_case_ids(DATA["create_cases"]))
def test_create_and_read(booker, booking_factory, case):
    booking_id, payload = booking_factory(case["overrides"])
    result = booker.get_booking(booking_id)
    assert result.status_code == 200
    assert result.json() == payload


def test_filter_returns_own_booking(booker, booking_factory):
    booking_id, payload = booking_factory()
    result = booker.list_bookings({"firstname": payload["firstname"], "lastname": payload["lastname"]})
    assert result.status_code == 200
    assert booking_id in [item["bookingid"] for item in result.json()]
