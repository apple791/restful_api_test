# Restful-booker 酒店预订接口自动化测试

基于原 api_test_project 的 Python、Pytest、Requests、YAML 和 Allure 框架改造的个人学习项目。原项目保持不变。2026-10-15已将旧文章接口、httpbin、SQL、Selenium练习及无关工具备份到项目外，仅保留酒店预订接口测试所需内容。

## 本次改造

- 新增 BookerClient，沿用 common/request_util.py 的公共请求入口，支持 GET、POST、PUT、PATCH、DELETE。
- 使用 YAML 管理预订及鉴权场景，使用 Pytest 参数化组织用例。
- 完整流程：创建 → 查询 → 全量修改 → 查询 → 局部修改 → 查询 → 删除 → 再查询。
- 每条测试创建唯一姓名的记录，只操作自己的预订；通过 fixture 清理数据并验证删除结果。
- 缺失或错误 Token 时验证写操作被拒绝，并检查原数据保持不变。
- 复用 Allure 报告工具，记录响应附件并屏蔽认证响应。写操作不自动重试，避免重复创建。
- Booker 配置与旧 MySQL 配置隔离，运行新测试不要求数据库、浏览器或 MySQL 密码。

## 最新整理验证

2026-10-15：清理旧练习并拆分测试文件后，联网执行24 passed（13条真实接口用例、11条离线检查），33.47秒。详见docs/整理验证记录.md；本次报告reports/organized-live.html。

## 历史验证结果

2026-10-10，本地执行 `python -m pytest --live`：24 passed，33.71 秒。
其中 13 项真实公开接口用例、11 项离线客户端检查。没有据此计算业务覆盖率，也没有声称公司生产环境测试经验。

报告：reports/live-report.html
原始机器可读结果：reports/results.xml
Allure 原始结果：reports/allure-live-01/

这些文件为本次执行证据，之后运行结果可能因公开服务网络或共享数据重置而变化。检查失败时应保留实际结果，不把失败简单改成通过或跳过。

## 目录

```text
restful_api_test/
├── common/
│   ├── booker_client.py         # 新增的预订业务接口封装
│   ├── request_util.py          # 沿用的原始公共请求工具
│   └── yaml_util.py             # 沿用的 YAML 数据工具
├── config/restful_config.py     # 独立的 Booker 配置
├── data/booking_cases.yaml
├── test_cases/
│   ├── booker/                  # 创建查询、完整流程、鉴权、删除四类用例及清理夹具
│   └── unit/                    # 无需网络的客户端检查
├── docs/
│   ├── 学习路线.md
│   ├── 测试用例说明.md
│   └── 本次验证记录.md
├── reports/
├── conftest.py
├── pytest.ini
├── requirements.txt
└── .env.example
```

旧练习备份：D:/简历/制作过程/restful_api_test_整理前备份.zip。公共请求工具只保留当前使用的send_request入口；不再混入旧数据库、UI及文章接口工具。

booker下的文件：test_create_query.py（创建和查询）、test_lifecycle.py（完整流程）、test_auth.py（鉴权）、test_delete.py（删除）。配置仍在config/restful_config.py，测试数据仍在data/booking_cases.yaml，夹具仍在test_cases/booker/conftest.py。

## Windows PowerShell 运行

进入项目：

```powershell
cd D:\简历\restful_api_test
```

本机已建立独立 .venv，可直接执行。复制到其他电脑时应重新创建环境，不复制虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

默认运行：离线检查执行，13 项真实接口测试明确跳过，不会自动联网写入数据。

```powershell
.\.venv\Scripts\python.exe -m pytest
```

真实公开接口全量测试：

```powershell
.\.venv\Scripts\python.exe -m pytest --live --html=reports/live-report.html --self-contained-html
```

先只学习一组创建查询用例：

```powershell
.\.venv\Scripts\python.exe -m pytest --live test_cases/booker/test_create_query.py -k create_and_read -v
```

单独运行完整业务流程：

```powershell
.\.venv\Scripts\python.exe -m pytest --live -m smoke -v
```

生成 Allure 原始结果并查看（查看需要另行安装 Allure Commandline）：

```powershell
.\.venv\Scripts\python.exe -m pytest --live --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 环境配置

默认连接 https://restful-booker.herokuapp.com ，账号密码是该公开练习服务的示例 admin / password123。无需创建 .env 文件。

如使用自己的本地服务，在当前 PowerShell 中设置环境变量：

```powershell
$env:BOOKER_BASE_URL = 'http://localhost:3001'
$env:BOOKER_USERNAME = 'admin'
$env:BOOKER_PASSWORD = 'password123'
$env:BOOKER_TIMEOUT = '10'
```

.env.example 只提供变量说明，新模块不自动读取 .env。不应将真实凭据提交到仓库。

## 测试范围与限制

- 状态码按目标接口文档验证：创建预订为 200，删除为 201；错误账号密码返回 200 和 Bad credentials。
- 零价格用例是验证字段能否原值保存，并非定义真实酒店定价需求。
- 本次没有测试真实数据库落库、UI、并发或性能，也没有新增 Playwright。
- 公开服务可能重置，测试只使用自己创建的数据，不修改他人的预订。
- 写请求响应丢失时可能无法拿到新 ID，从而无法自动清理；不盲目重试创建请求。
- .github/workflows/tests.yml 提供离线检查，以及手动选择的真实接口执行；尚未上传和验证 GitHub Actions。

## 学习与简历

先阅读 docs/学习路线.md，再逐行运行一条用例。项目是在原学习框架上辅助改造的个人项目，只有你能独立解释、运行和修改的部分，才适合写作个人能力。可使用项目名“酒店预订系统接口自动化测试（个人项目）”，不写企业经验或虚构效率提升。

官方接口文档：https://restful-booker.herokuapp.com/apidoc/index.html
官方被测服务源码：https://github.com/mwinteringham/restful-booker
