# laowang.vip 签到

独立运行的 Firefox 签到脚本。它读取本地持久浏览器登录态，打开当前的 `k_misign` 页面，完成站点显示的拼图滑块，提交后重新读取已签到状态。只有读到已签到才以退出码 `0` 结束；未确认时退出码为 `2`。

## 安装

需要 Node.js 22、可运行 Firefox 的桌面或 VNC 环境。

```bash
npm install
npx playwright install firefox
npm run login
```

首次登录在可见浏览器内完成一次。之后可用青龙或系统 Cron 执行 `npm run checkin`。脚本不会保存账号密码；浏览器会话位于默认的 `./data/browser`，请只保存在可信机器上，且不要提交到 Git。

如需指定已有代理和数据目录，可设置 `LAOWANG_PROXY=http://host:port`、`LAOWANG_DATA_DIR=/private/path`。没有代理时使用系统网络。运行结果写入数据目录中的 `result.json`，截图写入 `result.png`；运行日志可能包含签到天数和奖励信息，不应公开。

## 验证与限制

`node --check sign.cjs` 与 `node --check login.cjs` 可做语法检查。实际签到依赖账号已登录、目标站点可访问及其当前页面结构；脚本每次只提交一次，不把验证码通过或 HTTP 200 单独视为签到成功。若站点修改滑块或表单，请先检查结果文件及页面再调整选择器。

这是本站专用实现，不依赖 `qd-today/qd`。代码不包含个人 Cookie、代理地址或会话文件。
