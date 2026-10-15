"""Restful-booker 接口测试，按目标服务约定检查结果。"""
from copy import deepcopy

import allure
import pytest

from common.yaml_util import get_case_ids, load_case_data

DATA = load_case_data("booking_cases.yaml")
pytestmark = [pytest.mark.integration, pytest.mark.regression]


def test_deleted_booking_is_not_readable(booker, token, booking_factory):
    booking_id, _ = booking_factory()
    assert booker.delete_booking(booking_id, token).status_code == 201
    assert booker.get_booking(booking_id).status_code == 404
