"""项目级命令行选项。业务 fixture 位于 test_cases/booker。"""


def pytest_addoption(parser):
    parser.addoption("--live", action="store_true", help="执行真实酒店预订服务测试")
