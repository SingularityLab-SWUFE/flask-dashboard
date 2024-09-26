# Dashboard

基于 Python Flask 框架的*轻量化*计分板/排行榜系统.

希望实现的是一个自动评分系统的服务端 server, 类似 UCB 的 [ok](https://okpy.github.io/documentation/index.html), 但在功能上会简化许多, 提供一些 API 供客户端调用.

不希望借助其它 flask 相关的插件.

## 动机

暑期授课, 想让交互性更强(而不是单方面的讲解知识), 希望看到参与课程同学的进度(例如确实完成了布置的作业), 让体验感更强.

不需要做的像课程实验那样严格, 我们希望的是: **哪怕是抄作业, 也抄一遍, 交一下!** :) 这就是这个项目最大的意义.

## 客户端使用

在每次的实验中, 都需要提供一个 json 的实验配置文件, 同时包含一个 `client` 文件作为 CLI 客户端.

- `--local` 选项可以让 judge 脚本在本地运行, 方便调试, 不上传至远端服务器.
- `--show-token` 登录后显示 token.

## 简易 Web 界面

利用 flask 模板简单编写的 web 页面:

- `index` 主页
- `rank/{assignment_id}` 榜单
- `upload` 上传测试用例, 需要输入管理员 token
- `assignment` 创建实验

## 通用 API

### 注册

`POST /api/register/`

需要传入的参数:

- `username`: String, 用户名
- `password`: String, 密码
- `email`: String, 邮箱, 唯一标识符

### 登录

`POST /api/login/`

需要传入的参数:

- `email`: String, 邮箱
- `password`: String, 密码

返回一条 token 字符串, 作为用户凭证.

- 这条 token 数据作为 API 请求的凭证, 不设置 TTL. 使用时作为用户机密.
- 推荐单次登录后将 dashboard-api-token 作为本地环境变量.

### 查询榜单

`GET /api/scoreboard/`

query 参数:

- `assignment_id`: String, 实验 ID

返回该 Lab 下的榜单. 榜单上成绩按分数高低排名. 同分数的按时间提交先后排名.

未分页. 单次查询返回全部数据.

### 验证 md5

## 管理员级 API

### 创建 Assignment

`POST /api/assignment/`

权限: 需要提供 `access_token`

需要传入的参数:

- `name`: String, 实验名称
- `description`: String, 实验描述
- `max_score`: Integer, 最大分数
- `deadline`: String, 截止日期. 格式: `YYYY-MM-DD HH:MM:SS+0800`
  - 默认 1 周的 DDL

### 添加测试用例

`POST /api/testcase/`

权限: 需要提供 `access_token`

需要提供的参数:

- `testcases`: files, 测试用例文件(可多个)
- `assignment_id`: int, 实验 ID

## 用户级 API

### 创建提交

`/api/submission/`

权限: 需要提供 `access_token`

需要传入的参数:

- `assignment_id`: String, 实验 ID

本次单元测试运行的结果经过客户端解析后, 同样作为输入提交:

- `score`: Integer, 本次单元测试得到的分数

该接口主要由客户端调用, 上传本次单元测试的运行结果.

## 闲话

这个项目很多地方都是 poorly-designed, 例如一个操作可能要高频请求某一接口, 有佬帮忙重构代码感激不尽.
