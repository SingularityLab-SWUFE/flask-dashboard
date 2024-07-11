# Dashboard

基于 Python Flask 框架的*轻量化*计分板/排行榜系统.

希望实现的是一个自动评分系统的服务端 server, 类似 UCB 的 [ok](https://okpy.github.io/documentation/index.html), 但在功能上会简化许多, 提供一些 API 供客户端调用.

## 动机

暑期授课, 想让交互性更强(而不是单方面的讲解知识), 希望看到参与课程同学的进度(例如确实完成了布置的作业), 让体验感更强.

不需要做的像课程实验那样严格, 我们希望的是: **哪怕是抄作业, 也抄一遍, 交一下!** :) 这就是这个项目最大的意义.

## 通用 API

### 注册

`/api/register/`

需要传入的参数:

- `username`: String, 用户名
- `password`: String, 密码
- `email`: String, 邮箱, 唯一标识符

### 登录

`/api/login/`

需要传入的参数:

- `email`: String, 邮箱
- `password`: String, 密码

返回一条 token 字符串, 作为用户凭证.

## 管理员级 API

### 创建 Lab

`/api/lab/`

权限: 需要提供 `access_token`

需要传入的参数:

- `name`: String, 实验名称
- `description`: String, 实验描述
- `deadline`: String, 截止日期. 格式: `YYYY-MM-DD HH:MM:SS +0800`

## 用户级 API

### 创建提交

`/api/submission/`

权限: 需要提供 `access_token`

需要传入的参数:

- `lab_id`: String, 实验 ID

本次单元测试运行的结果同样会作为输入提交.

## 客户端使用

在每次的实验中, 都需要提供一个 judge 的脚本

`python3 judge --submit <access_token>` 提交本次实验
