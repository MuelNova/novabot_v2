

<div align="center">
  <a href="https://bot.novanoir.dev"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NovaBot2"></p>
</div>


<div align="center">

# novabot2

_✨ 来自NovaBot二代目✨_

<a href="LICENSE">
    <img src="https://img.shields.io/github/license/Nova-Noir/novabot_v2.svg" alt="license">
</a>
<img src="https://img.shields.io/badge/nonebot2-2.0.0b2-blue.svg" alt="nonebot2">
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

基于[nonebot2](https://github.com/nonebot/nonebot2)和[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)开发的QQ群机器人

## 📖 介绍

因为一直用别人的BOT不好魔改所以就写了自己的BOT啦, 我是比较想叫它`Skadi Bot`嘛,但是想了想还是叫做`Nova Bot`啦


## 💿 安装

<details>
<summary>从 github 安装</summary>
打开命令行, 输入以下命令克隆此储存库

    git clone https://github.com/Nova-Noir/novabot_v2.git

正在更新...

</details>

## ⚙️ 配置

在项目的`.env`文件中添加下表中的必填配置

| 配置项  | 必填 | 默认值 |   说明   |
| :-----: | :--: | :----: | :------: |
| 配置项1 |  是  |   无   | 配置说明 |
| 配置项2 |  否  |   无   | 配置说明 |

## 🎉 使用
### Service_Manager
[`plugins.service_manager`](novabot/plugins/service_manager)

基础插件。提供整个Bot的插件管理系统。功能灵感来源于[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)(~~用习惯了~~)

采用修改`matcher`的`Rule`的方式, 使`matcher`功能增强, 可复用。(~~性能就不提了~~)

> 之前写的那个非藕合的过于复杂, 且对所有`matcher`均有效而无法进行精细化自定义, 也无法对定时任务做管理, 于是重写了这个。

#### 插件调用方式

```python
from nonebot.plugin import require

service = require("service_manager").Service

cmd = on_*(...)
service(plugin_name, cmd, ...)
```

一个可能的例子:

```python
from nonebot.plugin import require

service = require("service_manager").Service

cmd = on_command("abc")
cmd = service("abc", cmd, cd=20, cd_reply="HI!")

cmd1 = on_command("abd")
cmd1 = service("abd", cmd1, visible=False, limit=3, limit_reply="Another Hi!")

cmd2 = on_command("abe")
cmd2 = service("abee", cmd2, enable_on_default=False) # plugin_name: abee

notice_test = on_notice()
notice_test = service("notice_test", notice_test)
```

##### `Service` 类

由**删除线**标注的内容为未开发完成, 可能存在不兼容更新

| 参数                  | 类型            | 可省略 | 说明                                                | 默认值 |
| --------------------- | --------------- | ------ | --------------------------------------------------- | ------ |
| **plugin_name**       | `str`           | 否     | 插件名称                                            |        |
| **matcher**           | `Type[Matcher]` | 否     | 所要包裹的`Matcher`实例                             |        |
| **~~use_priv~~**      | `int`           | 是     | 插件使用权限, 未开发, 可使用`permission`代替        | 0      |
| **manage_priv**       | `int`           | 是     | 插件管理权限, 未开发                                | 0      |
| **enable_on_default** | `bool`          | 是     | 是否默认启用                                        | True   |
| **visible**           | `bool`          | 是     | 是否在`帮助` / `lssv`中可见                         | True   |
| **~~help_~~**         | `str`           | 是     | 帮助文档                                            | None   |
| **bundle**            | `str`           | 是     | 插件分类                                            | "默认" |
| **cd**                | `int`           | 是     | 插件调用CD, 针对个人, 单位为`秒`                    | 0      |
| **limit**             | `int`           | 是     | 插件日调用次数限制, 针对个人, 0为无限制, 单位为`次` | 0      |
| **cd_reply**          | `str`           | 是     | 插件CD中回复, 空为不回复                            | ""     |
| **limit_reply**       | `str`           | 是     | 插件日调用次数上限回复, 空为不回复                  | ""     |

#### 指令表
|    指令     | 别名                     | 参数           |              权限              | 需要@ | 范围 |                             说明                             |
| :---------: | ------------------------ | -------------- | :----------------------------: | :---: | :--: | :----------------------------------------------------------: |
|  **lssv**   | `服务列表` \| `功能列表`  | `show_all`     | 群管理员 \| 群主 \| 超级管理员 |  否   | 群聊 | 列出服务列表, 参数可为任意值, 存在则将同时显示`visible=False`的服务 |
| **enable**  | `启用` \| `打开` \| `开启` | `service_name` | 群管理员 \| 群主 \| 超级管理员 |  否   | 群聊 | 启用`service_name`插件. 可使用空格(" ")分隔多个`service_name`, 可使用关键字`all`或`全部`开启所有服务 |
| **disable** | `禁用` \| `关闭`          | `service_name` | 群管理员 \| 群主 \| 超级管理员 |  否   | 群聊 | 禁用`service_name`插件. 可使用空格(" ")分隔多个`service_name`, 可使用关键字`all`或`全部`开启所有服务 |
