# nonebot-plugin-remake

适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的人生重开模拟器

这垃圾人生一秒也不想待了？立即重开！


### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_remake
```

- 使用 pip

```
pip install nonebot_plugin_remake
```


### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

#### `remake_send_forword_msg`
 - 类型：`bool`
 - 默认：`False`
 - 说明：是否以合并转发消息的形式发送（仅对于 OneBot V11 适配器有效，且需要 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) `v1.0.0-rc2` 以上版本）


### 使用

#### 触发方式：

**以下命令需要加[命令前缀](https://nonebot.dev/docs/appendices/config#command-start-和-command-separator) (默认为`/`)，可自行设置为空**

```
@机器人 remake/liferestart/人生重开/人生重来
```


#### 示例：

<div align="left">
  <img src="https://s2.loli.net/2023/08/02/25YjUFKwvnWisNr.jpg" width="400" />
  <img src="https://s2.loli.net/2023/08/02/b4L7WvnAyHeYUPZ.jpg" width="400" />
</div>


### 特别感谢

- [VickScarlet/lifeRestart](https://github.com/VickScarlet/lifeRestart) やり直すんだ。そして、次はうまくやる。

- [cc004/lifeRestart-py](https://github.com/cc004/lifeRestart-py) lifeRestart game in python

- [DaiShengSheng/lifeRestart_bot](https://github.com/DaiShengSheng/lifeRestart_bot) 适用于HoshinoBot下的人生重来模拟器插件
