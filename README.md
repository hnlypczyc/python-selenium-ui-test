# UI Automation Framework

> Open source UI automation test framework by **NancyZhou**

一个基于 `Python + pytest + Selenium` 的 UI 自动化测试框架示例项目，当前以 `OrangeHRM` 作为演示系统，支持：

- 页面对象模型（POM）
- Excel 数据驱动
- Jenkins 集成
- 本地 HTML 报告
- 失败自动截图
- 多浏览器/远程执行扩展

## 项目标签

- Project Name: `UI Automation Framework`
- Author: `NancyZhou`
- Type: `Open Source`
- Tech Stack: `Python + pytest + Selenium + Excel + Jenkins + Allure`

这个项目可以作为个人 GitHub 开源模板项目使用，也可以作为后续新 UI 自动化项目的起始框架。

## 1. 本地执行命令

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

执行全部 UI 用例：

```powershell
python run.py --run-ui -q
```run

执行烟雾测试：

```powershell
python run.py --run-ui -m smoke -q
```

执行回归测试：

```powershell
python run.py --run-ui -m regression -q
```

执行报告截图演示用例：

```powershell
python run.py --run-ui -m report_demo -q
```

如果只想看 pytest 默认行为，也可以执行：

```powershell
python -m pytest --run-ui -q
```

但更推荐使用 `python run.py ...`，因为它会自动生成：

- `reports\<run_id>\report.html`
- `reports\<run_id>\junit.xml`
- `allure-results\<run_id>\`

## 2. 执行后产物位置

每次运行都会生成一个独立的 `run_id` 目录，常见产物如下：

- HTML 报告：`reports\<run_id>\report.html`
- JUnit 报告：`reports\<run_id>\junit.xml`
- 失败截图：`screenshots\<run_id>\`
- 运行日志：`logs\<run_id>\framework.log`
- Allure 原始结果：`allure-results\<run_id>\`

打开本地 HTML 报告：

```powershell
start .\reports\<run_id>\report.html
```

打开 Allure 报告：

```powershell
allure serve .\allure-results\<run_id>
```

如果希望先生成静态 Allure 报告目录，再手动查看，可执行：

```powershell
allure generate .\allure-results\<run_id> -o .\allure-report\<run_id> --clean
```

> ⚠️ **不要直接双击 `index.html` 打开**。浏览器在 `file://` 协议下会阻止 JS 加载数据文件，导致报告一直 loading 没有内容。
>
> 必须通过本地 HTTP 服务器访问，例如用 Python 在报告目录内启动：
>
> ```powershell
> python -m http.server 8088 --directory .\allure-report\<run_id>
> ```
>
> 然后在浏览器打开 `http://localhost:8088`。

或者用上面的allure serve方式打开

说明：

1. `allure-results\<run_id>\` 是 pytest 执行时生成的 Allure 原始结果目录。
2. `allure serve` 会临时启动一个本地服务并自动打开报告（推荐快速查看时使用）。
3. `allure generate` 会生成可落地保存的静态报告目录，但需配合本地 HTTP 服务器访问。
4. 当前框架已支持失败时把截图附加进 Allure 结果中。

## 3. 用例执行开始到结束的完整代码流程

下面以这条命令为例说明：

```powershell
python run.py --run-ui -m report_demo -q
```

这个命令会执行 `tests\reporting\test_tc99_report_fail_demo.py`，该用例会先登录系统，再故意失败，用于验证 HTML 报告中的截图展示。

### 第 1 步：进入 `run.py`

入口文件是项目根目录下的 `run.py`。

执行后会先进入：

```python
main()
```

这里做的事情有：

1. 解析命令行参数
2. 读取或生成本次执行的 `run_id`
3. 创建本次运行目录
4. 自动为 pytest 补充报告参数

`run.py` 会自动给 pytest 增加以下参数：

- `--html reports\<run_id>\report.html`
- `--self-contained-html`
- `--junitxml reports\<run_id>\junit.xml`
- `--alluredir allure-results\<run_id>\`

最后执行：

```python
pytest.main(pytest_args)
```

此时程序正式进入 pytest。

### 第 2 步：pytest 读取 `pytest.ini`

pytest 启动后，会读取项目根目录下的 `pytest.ini`。

当前关键配置包括：

- `testpaths = tests`
- `markers = ui / smoke / regression / data_driven / report_demo`

因此 pytest 会到 `tests` 目录下收集测试用例。

### 第 3 步：pytest 自动加载 `conftest.py`

pytest 在收集和执行测试前，会自动加载项目根目录下的 `conftest.py`。

这里是整个框架的统一入口，负责：

- 注册命令行参数
- 加载配置
- 创建浏览器 driver
- 控制 UI 用例是否执行
- 失败后截图
- 将截图嵌入 HTML 报告

### 第 4 步：执行 `pytest_addoption()`

在 `conftest.py` 中，`pytest_addoption()` 注册了自定义参数：

- `--env`
- `--browser`
- `--headless`
- `--remote-url`
- `--base-url`
- `--run-ui`
- `--run-id`

所以命令中的：

```powershell
--run-ui -m report_demo -q
```

会被 pytest 正确识别。

### 第 5 步：执行 `pytest_configure()`

pytest 完成初始化后，会执行：

```python
pytest_configure(config)
```

这里完成三件核心事情：

#### 5.1 创建运行目录

通过：

```python
create_runtime_paths(config.getoption("--run-id"))
```

生成本次运行的目录结构，例如：

- `reports\<run_id>\`
- `logs\<run_id>\`
- `screenshots\<run_id>\`
- `allure-results\<run_id>\`

#### 5.2 初始化日志

通过：

```python
configure_logging(runtime_paths.log_dir)
```

生成：

`logs\<run_id>\framework.log`

#### 5.3 加载配置文件

通过：

```python
load_settings(config.getoption("--env"))
```

读取并合并：

- `config\settings.yaml`
- `config\environments\demo.yaml`

最终得到当前运行需要的配置，比如：

- base_url
- 浏览器类型
- 默认账号密码
- 超时时间

### 第 6 步：收集测试并筛选

pytest 收集到测试后，会执行：

```python
pytest_collection_modifyitems(config, items)
```

当前逻辑是：

- 如果没有 `--run-ui`，所有 `@pytest.mark.ui` 用例会被跳过
- 如果有 `--run-ui`，UI 用例允许执行

因为当前命令里带了：

```powershell
--run-ui
```

所以 UI 用例会真正运行。

同时因为命令里有：

```powershell
-m report_demo
```

所以只会执行带 `@pytest.mark.report_demo` 的用例。

### 第 7 步：准备 fixture

以故障演示用例为例：

```python
def test_report_demo_intentional_failure(driver, settings, base_url):
```

pytest 看到这个函数依赖三个 fixture：

- `driver`
- `settings`
- `base_url`

所以会先创建这三个对象。

#### 7.1 `settings`

返回当前环境配置。

#### 7.2 `base_url`

返回被测系统地址：

`https://opensource-demo.orangehrmlive.com/web/index.php/auth/login`

#### 7.3 `driver`

`driver` fixture 会调用：

```python
create_driver(...)
```

对应文件：

`core\driver_factory.py`

这里会：

1. 读取浏览器类型
2. 读取 headless 参数
3. 构建浏览器启动配置
4. 创建 WebDriver
5. 设置超时

然后把这个浏览器实例传给测试函数。

注意 `driver` fixture 使用了 `yield`，所以：

- `yield` 前：创建浏览器
- `yield` 后：测试执行完成后自动 `driver.quit()`

### 第 8 步：执行测试函数

故障演示用例文件：

`tests\reporting\test_tc99_report_fail_demo.py`

核心代码：

```python
dashboard = LoginFlow(driver, settings, base_url).login_as_default_admin()
assert dashboard.is_loaded()
assert False
```

执行流程如下。

#### 8.1 进入 `LoginFlow`

文件：

`flows\login_flow.py`

这里会从配置中取默认账号：

- username: `Admin`
- password: `admin123`

然后调用页面对象执行登录。

#### 8.2 进入 `LoginPage`

文件：

`pages\login_page.py`

登录过程包括：

1. 打开登录页
2. 输入用户名
3. 输入密码
4. 点击登录按钮

#### 8.3 进入 `BasePage`

文件：

`core\base_page.py`

这里封装了：

- `open()`
- `type()`
- `click()`
- `wait_for_visible()`
- `wait_for_clickable()`

所以登录时不是直接裸操作元素，而是先等待元素出现，再输入和点击。

#### 8.4 进入 `DashboardPage`

登录成功后，会等待：

```python
//h6[normalize-space()='Dashboard']
```

当这个元素出现时，说明系统已经成功登录并进入首页。

### 第 9 步：故意触发失败

在故障演示用例中，前面的登录都成功以后，代码故意执行：

```python
assert False, "Intentional failure ..."
```

所以这条用例一定失败。

pytest 会把这次执行结果标记为 `failed`。

### 第 10 步：失败后自动截图

这是在 `conftest.py` 中通过下面这个 hook 实现的：

```python
pytest_runtest_makereport(item, call)
```

pytest 每执行完一条用例，都会调用这个 hook。

当前代码逻辑是：

```python
if report.when != "call" or report.passed:
    return
```

意思是：

- 只处理真正测试函数执行阶段
- 只处理失败场景

如果失败了，继续往下执行。

#### 10.1 获取当前 driver

```python
driver_instance = item.funcargs.get("driver")
```

这里拿到当前失败用例对应的浏览器实例。

#### 10.2 生成截图路径

```python
screenshot_path = runtime_paths.screenshot_dir / screenshot_name
```

最终截图会保存到：

`screenshots\<run_id>\`

#### 10.3 执行 Selenium 截图

```python
driver_instance.save_screenshot(str(screenshot_path))
```

这一步就是浏览器当前页面截图的真正实现。

### 第 11 步：把截图嵌入 HTML 报告

截图保存成 PNG 文件后，代码继续执行：

```python
html_plugin = item.config.pluginmanager.getplugin("html")
```

这里拿到 `pytest-html` 插件。

然后把刚保存的 PNG 文件复制到报告目录下的 `assets` 子目录：

```python
report_image_path = runtime_paths.report_assets_dir / screenshot_name
shutil.copy2(screenshot_path, report_image_path)
```

再把这个相对路径写进 HTML 报告附加信息中：

```python
image_relative_path = f"assets/{report_image_path.name}"
extras.append(html_plugin.extras.html(...))
report.extras = extras
```

这样做的结果是：

1. 磁盘上有截图文件
2. 报告目录下有一份专门给 HTML 报告使用的图片副本
3. HTML 报告里可直接显示截图，并可点击查看原图

所以打开 `report.html` 时，可以在失败用例详情里看到页面截图。

### 第 12 步：把截图附加到 Allure 结果

在失败截图保存后，如果启用了 `allure-pytest` 插件，还会执行：

```python
allure.attach.file(
    str(screenshot_path),
    name="failure-screenshot",
    attachment_type=allure.attachment_type.PNG,
)
```

这一步会把失败截图作为附件写入：

`allure-results\<run_id>\`

所以后续用 Allure 生成报告时，失败用例里也可以看到截图附件。

### 第 13 步：生成本地 HTML 报告

因为 `run.py` 自动给 pytest 传了：

```powershell
--html reports\<run_id>\report.html
--self-contained-html
```

所以 `pytest-html` 插件会在全部用例执行结束后生成一个单文件 HTML 报告：

`reports\<run_id>\report.html`

这个文件可以直接本地双击打开。

报告内容包括：

- 测试总数
- 通过/失败/跳过数量
- 每条用例执行状态
- 失败堆栈
- 失败截图

### 第 14 步：生成 Jenkins / Allure 所需产物

同一次运行中，还会额外生成：

#### 13.1 JUnit XML

`reports\<run_id>\junit.xml`

这个主要给 Jenkins 读取。

#### 13.2 Allure 原始结果

`allure-results\<run_id>\`

这个目录给 Allure 后续生成报告使用，其中也包含失败截图附件。

### 第 15 步：测试结束后关闭浏览器

测试函数执行结束后，pytest 会回到 `driver` fixture 的 `yield` 后半段：

```python
driver_instance.quit()
```

浏览器关闭，本次用例执行结束。

## 4. 一句话总结整个调用链

执行命令后，整体调用链可以概括为：

```text
run.py
  -> pytest.main(...)
    -> pytest.ini
    -> conftest.py
      -> pytest_addoption()
      -> pytest_configure()
      -> pytest_collection_modifyitems()
      -> fixture: settings / base_url / driver
    -> test_xxx.py
      -> flow
        -> page
          -> base_page
    -> pytest_runtest_makereport()
      -> save_screenshot()
      -> allure.attach.file(...)
      -> pytest-html extras.html(...)
    -> 生成 report.html / junit.xml / allure-results
    -> driver.quit()
```

## 5. 常用命令汇总

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

执行全部 UI 用例：

```powershell
python run.py --run-ui -q
```

执行烟雾测试：

```powershell
python run.py --run-ui -m smoke -q
```

执行回归测试：

```powershell
python run.py --run-ui -m regression -q
```

执行故障演示用例，验证报告截图：

```powershell
python run.py --run-ui -m report_demo -q
```

启动 Allure 临时报告：

```powershell
allure serve .\allure-results\<run_id>
```

生成本地静态 Allure 报告：

```powershell
allure generate .\allure-results\<run_id> -o .\allure-report\<run_id> --clean
```

> ⚠️ 静态报告必须通过 HTTP 服务器访问，不能直接双击 `index.html`（`file://` 协议下报告会一直 loading）：
>
> ```powershell
> python -m http.server 8088 --directory .\allure-report\<run_id>
> # 然后在浏览器打开 http://localhost:8088
> ```

打开最新报告后，可在失败用例详情中查看截图。

## 6. 项目目录结构说明

项目当前目录结构及职责如下：

```text
python-selenium-ui-test/
|-- ci/
|   |-- Jenkinsfile
|-- config/
|   |-- settings.yaml
|   |-- environments/
|       |-- demo.yaml
|       |-- test.yaml
|-- core/
|   |-- base_page.py
|   |-- config_loader.py
|   |-- driver_factory.py
|   |-- exceptions.py
|-- data/
|   |-- data_loader.py
|   |-- orangehrm/
|       |-- TC02_新增员工.xlsx
|       |-- TC03_登录失败.xlsx
|-- flows/
|   |-- employee_flow.py
|   |-- login_flow.py
|-- pages/
|   |-- dashboard_page.py
|   |-- login_page.py
|   |-- pim_page.py
|-- tests/
|   |-- data/
|   |-- employee/
|   |-- login/
|   |-- reporting/
|-- utils/
|   |-- assertion.py
|   |-- excel_reader.py
|   |-- file_manager.py
|   |-- logger.py
|   |-- paths.py
|-- conftest.py
|-- pytest.ini
|-- requirements.txt
|-- run.py
|-- README.md
```

### 6.1 `config`

配置层，负责维护：

- 全局执行配置
- 浏览器配置
- 环境地址配置
- 默认账号信息

### 6.2 `core`

框架核心层，负责：

- 读取配置
- 创建 WebDriver
- 页面基类封装
- 框架异常定义

### 6.3 `pages`

页面对象层，负责：

- 页面元素定位
- 单页面操作行为

例如：

- `login_page.py`：登录页
- `dashboard_page.py`：首页
- `pim_page.py`：员工管理页

### 6.4 `flows`

业务流程层，负责把多个页面串起来形成业务动作。

例如：

- `login_flow.py`：封装完整登录流程
- `employee_flow.py`：封装新增员工业务流程

### 6.5 `data`

数据驱动层，负责：

- Excel 数据文件存放
- case_name 与 Excel 文件匹配
- 读取可执行数据

### 6.6 `tests`

测试用例层，负责组织 pytest 测试。

- `login`：登录相关 UI 用例
- `employee`：员工管理相关 UI 用例
- `reporting`：报告功能验证测试
- `data`：测试数据加载与契约校验

目录按功能模块组织；实际执行哪些用例，主要依赖 marker（如 `smoke`、`regression`、`report_demo`）来筛选。

### 6.7 `utils`

工具层，负责：

- 路径处理
- 日志
- Excel 读取
- 断言辅助
- 目录创建

### 6.8 运行产物目录

运行过程中生成：

- `reports\`：HTML 报告与 JUnit XML
- `logs\`：日志
- `screenshots\`：失败截图
- `allure-results\`：Allure 原始结果

## 7. Jenkins 使用说明

项目已经提供了示例：

`ci\Jenkinsfile`

### 7.1 Jenkins 参数

当前 Jenkinsfile 支持以下参数：

- `ENV`：运行环境
- `BROWSER`：浏览器类型
- `HEADLESS`：是否无头
- `RUN_UI`：是否执行 UI 用例
- `MARKER`：pytest marker 表达式
- `WORKERS`：并发 worker 数量
- `REMOTE_URL`：远程 Selenium Grid 地址

### 7.2 Jenkins 执行命令

Jenkins 最终调用的是：

```powershell
python run.py --env ${ENV} --browser ${BROWSER} --headless ${HEADLESS} --run-ui -m ${MARKER} -n ${WORKERS} --run-id ${BUILD_NUMBER}
```

如果 `REMOTE_URL` 有值，则会额外带上：

```powershell
--remote-url ${REMOTE_URL}
```

### 7.3 Jenkins 归档内容

Jenkinsfile 会归档：

- `logs/**/*`
- `reports/**/*`
- `screenshots/**/*`
- `allure-results/**/*`

同时会读取：

```text
reports/**/*.xml
```

作为 JUnit 测试结果。

### 7.4 Jenkins 使用建议

建议在 Jenkins 中优先使用：

```powershell
python -m pip install -r requirements.txt
python run.py --run-ui -m smoke -q
```

如果做回归，可用：

```powershell
python run.py --run-ui -m regression -n 2 -q
```

## 8. 如何复制为新项目模板

当前项目就是一个可复用模板。后续如果要接新系统，建议按以下步骤复制。

### 8.1 复制项目目录

复制整个 `python-selenium-ui-test` 目录，改成你的新项目名。

### 8.2 修改配置

重点修改：

- `config\settings.yaml`
- `config\environments\*.yaml`

替换为新系统的：

- base_url
- 默认账号
- 浏览器/执行策略

### 8.3 新建页面对象

在 `pages\` 中新增目标系统页面对象，例如：

- 登录页
- 首页
- 列表页
- 详情页

### 8.4 新建业务流

在 `flows\` 中新增业务流程，例如：

- 登录
- 新增
- 查询
- 删除
- 审批

### 8.5 新建测试数据

在 `data\` 中放新的 Excel 文件，并保持：

- 一个测试脚本最多对应一个 Excel
- 文件名与 `case_name` 匹配

### 8.6 新建测试用例

在 `tests\` 下按功能模块新增用例，例如 `tests\login\`、`tests\employee\`，并给用例打合适的 marker。

### 8.7 验证模板是否生效

建议至少执行：

```powershell
python run.py --run-ui -m smoke -q
```

确认：

- 浏览器能正常打开
- 页面对象可用
- 报告可生成
- 截图可保存

## 9. 推荐实践

1. 测试脚本中不要直接写大量 Selenium 原生操作，优先走 page + flow。
2. 测试数据尽量放 Excel，不要硬编码在测试脚本里。
3. 新项目优先先打通一条最小闭环用例，再逐步扩展。
4. 平时开发优先跑 smoke，用 Jenkins 跑 regression。
5. 故障排查时优先查看：
   - `report.html`
   - `framework.log`
   - `screenshots\`

## 10. BasePage 常用方法示例

`core\base_page.py` 中已经封装了一批常用 Selenium 操作，页面对象中可以直接复用，尽量不要在测试脚本里重复写底层 Selenium 代码。

### 10.1 基础输入与点击

```python
from selenium.webdriver.common.by import By
from core.base_page import BasePage


class DemoPage(BasePage):
    USERNAME = (By.NAME, "username")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def login(self, username: str) -> None:
        self.type(self.USERNAME, username)
        self.click(self.LOGIN_BUTTON)
```

常用方法：

- `click(locator)`
- `js_click(locator)`
- `type(locator, value)`
- `clear(locator)`
- `send_keys(locator, *keys)`
- `text_of(locator)`
- `attribute_of(locator, attribute_name)`

### 10.2 下拉框选择

```python
ROLE_SELECT = (By.ID, "role")

self.select_by_text(ROLE_SELECT, "Admin")
self.select_by_value(ROLE_SELECT, "admin")
self.select_by_index(ROLE_SELECT, 1)

selected_text = self.selected_option_text(ROLE_SELECT)
```

适用于标准 HTML `select` 下拉框。

### 10.3 鼠标操作

```python
MENU = (By.CSS_SELECTOR, ".menu")
DOUBLE_CLICK_TARGET = (By.ID, "double-click-area")
RIGHT_CLICK_TARGET = (By.ID, "context-menu-area")

self.hover(MENU)
self.double_click(DOUBLE_CLICK_TARGET)
self.right_click(RIGHT_CLICK_TARGET)
```

### 10.4 拖拽操作

```python
SOURCE = (By.ID, "drag-source")
TARGET = (By.ID, "drop-target")
SLIDER = (By.ID, "slider")

self.drag_and_drop(SOURCE, TARGET)
self.drag_and_drop_by_offset(SLIDER, 200, 0)
```

### 10.5 滚动与 JavaScript

```python
SAVE_BUTTON = (By.ID, "save")

self.scroll_to_element(SAVE_BUTTON)
self.scroll_to_top()
self.scroll_to_bottom()
self.execute_js("window.localStorage.clear();")
self.js_click(SAVE_BUTTON)
```

### 10.6 frame / 窗口切换

```python
IFRAME = (By.TAG_NAME, "iframe")

self.switch_to_frame(IFRAME)
self.switch_to_default_content()

self.open_new_tab()
self.switch_to_window(-1)
```

说明：

- `switch_to_window(-1)` 表示切到最后一个窗口
- `switch_to_window(0)` 表示切回第一个窗口

### 10.7 浏览器控制

```python
self.refresh()
self.back()
self.forward()
```

### 10.8 回车和 ESC

```python
SEARCH_INPUT = (By.ID, "search")

self.type(SEARCH_INPUT, "OrangeHRM")
self.press_enter(SEARCH_INPUT)
self.press_escape(SEARCH_INPUT)
```

### 10.9 可见性与可点击判断

```python
SUBMIT_BUTTON = (By.ID, "submit")

if self.is_visible(SUBMIT_BUTTON):
    self.click(SUBMIT_BUTTON)

if self.is_clickable(SUBMIT_BUTTON):
    self.click(SUBMIT_BUTTON)
```

### 10.10 页面对象中的推荐写法

推荐在页面对象中封装业务动作，而不是在测试脚本中直接调用这些底层方法。

例如：

```python
class EmployeePage(BasePage):
    ADD_BUTTON = (By.XPATH, "//button[normalize-space()='Add']")
    FIRST_NAME = (By.NAME, "firstName")
    LAST_NAME = (By.NAME, "lastName")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def add_employee(self, first_name: str, last_name: str) -> None:
        self.click(self.ADD_BUTTON)
        self.type(self.FIRST_NAME, first_name)
        self.type(self.LAST_NAME, last_name)
        self.scroll_to_element(self.SAVE_BUTTON)
        self.click(self.SAVE_BUTTON)
```

推荐原则：

1. 测试脚本负责断言和流程编排。
2. 页面对象负责页面操作细节。
3. `BasePage` 负责可复用的底层 Selenium 能力。

## 11. Excel 数据模板说明

当前框架支持基于 Excel 的数据驱动测试。

数据驱动的核心规则是：

1. 一个测试脚本最多对应一个 Excel 文件
2. Excel 文件通过 `case_name` 与测试脚本匹配
3. 只有 `execute=Y/TRUE/1/YES/ON` 的数据行才会执行
4. 如果没有匹配到 Excel，或 Excel 中没有可执行数据，数据驱动用例会被跳过

### 11.1 文件命名规则

推荐做法：

- Python 测试文件使用英文命名，便于维护
- 在测试脚本内部声明中文/业务友好的 `case_name`
- Excel 文件名与 `case_name` 保持一致

例如：

```python
case_name = "TC02_新增员工"
```

对应 Excel 文件：

```text
data\orangehrm\TC02_新增员工.xlsx
```

### 11.2 当前匹配逻辑

框架会在 `data\data_loader.py` 中执行以下流程：

1. 先根据 `case_name` 查找同名 Excel 文件
2. 如果指定了 `app_name`，优先到 `data\<app_name>\` 下查找
3. 找到 Excel 后读取 `data` sheet
4. 只保留 `execute` 为真值的行；如果 Excel 里仍保留 `case_name` 列，则继续按它做兼容过滤
5. 转成 pytest 参数化数据

### 11.3 Excel 默认 Sheet 名

默认读取：

```text
data
```

如果你的 Excel Sheet 不叫 `data`，需要修改代码中的调用参数。

### 11.4 必填列

当前框架要求 Excel 至少包含以下字段：

- `execute`
- `data_id`
- `test_title`
- `expected_result`
- `checkpoints`

如果缺少这些列，框架会抛出 `DataFileFormatError`。

### 11.5 推荐字段模板

建议使用如下表头：

| execute | data_id | test_title | precondition | steps_data | username | password | first_name | middle_name | last_name | expected_error | expected_result | checkpoints | remark |
|---------|---------|------------|--------------|------------|----------|----------|------------|-------------|-----------|----------------|-----------------|------------|--------|

说明：

- `execute`：是否执行当前数据，常用值 `Y/N`
- `data_id`：数据编号，便于区分和追踪
- `test_title`：当前数据行标题
- `precondition`：前置条件，可选
- `steps_data`：JSON 字符串字段，可选，框架会尝试自动解析
- `username/password`：登录类数据
- `first_name/middle_name/last_name`：员工类数据
- `expected_error`：失败场景断言字段
- `expected_result`：预期结果描述
- `checkpoints`：验证点说明
- `remark`：备注

说明补充：

- Excel 文件名仍然需要与脚本中的 `case_name` 一致
- `case_name` 列现在是可选列；如果保留，框架会继续校验并过滤不匹配的行
- 对于不需要测试数据的用例，可以不创建 Excel 文件，也不需要调用 `build_case_params(...)`

### 11.6 示例数据

例如新增员工用例可以写成：

| execute | data_id | test_title | first_name | middle_name | last_name | expected_result | checkpoints | remark |
|---------|---------|------------|------------|-------------|-----------|-----------------|------------|--------|
| Y | EMP_001 | 新增普通员工 | Auto | UI | User | 成功保存员工并进入个人详情页 | 进入 Personal Details 页面 | sample row |
| N | EMP_002 | 跳过样例数据 | Skip | UI | User | 不执行 | execute=N 时应跳过 | disabled row |

例如登录失败用例可以写成：

| execute | data_id | test_title | username | password | expected_error | expected_result | checkpoints | remark |
|---------|---------|------------|----------|----------|----------------|-----------------|------------|--------|
| Y | LOGIN_001 | 错误密码登录 | Admin | bad-password | Invalid credentials | 页面提示 Invalid credentials | 错误信息展示正确 | negative sample |
| Y | LOGIN_002 | 错误用户名登录 | BadUser | admin123 | Invalid credentials | 页面提示 Invalid credentials | 错误信息展示正确 | negative sample |

### 11.7 `steps_data` 字段说明

如果某条测试数据比较复杂，不想把字段拆很多列，可以把输入参数放进 `steps_data`。

例如：

```json
{"employee_name": "Auto User", "job_title": "QA", "location": "Shanghai"}
```

框架在读取时，如果发现 `steps_data` 是 JSON 字符串，会自动解析成 Python 字典。

### 11.8 测试脚本中如何使用 Excel 数据

示例：

```python
import pytest

from data.data_loader import build_case_params


case_name = "TC02_新增员工"


@pytest.mark.parametrize("case_data", build_case_params(case_name, app_name="orangehrm"))
def test_add_employee(driver, settings, base_url, case_data):
    first_name = case_data["first_name"]
    last_name = case_data["last_name"]
```

这里的 `case_data` 就是 Excel 中当前这一行转换后的字典。

### 11.9 当没有 Excel 或没有可执行数据时会怎样

框架的处理逻辑如下：

#### 情况 1：没有找到对应 Excel

例如：

- 脚本里是 `case_name = "TC99_xxx"`
- `data\` 下没有 `TC99_xxx.xlsx`

结果：

- 数据驱动用例会被 `skip`
- 报告中会显示跳过原因

#### 情况 2：Excel 存在，但没有 `execute=Y` 的行

结果：

- 同样会 `skip`
- 报告中会显示跳过原因

#### 情况 3：Excel 缺少必填字段

结果：

- 会直接报错
- 用于提醒数据模板不合规

### 11.10 推荐维护方式

建议按以下方式维护 Excel 数据：

1. 每个业务用例一个 Excel 文件
2. 一行代表一组测试数据
3. `data_id` 保证唯一
4. 如果保留 `case_name` 列，确保它与脚本中的 `case_name` 保持一致
5. 不执行的数据使用 `execute=N`
6. 尽量不要随意修改表头命名

### 11.11 新增 Excel 数据文件的步骤

1. 在测试脚本中定义 `case_name`
2. 如果这是数据驱动用例，在 `data\<app_name>\` 下创建同名 Excel
3. Sheet 命名为 `data`
4. 按模板补齐必填列
5. 至少准备一条 `execute=Y` 的数据
6. 执行对应 pytest 用例验证
