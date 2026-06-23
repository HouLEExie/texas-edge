# Texas Edge

德州扑克胜率分析器。第一版使用 Python + Streamlit 开发，面向手机浏览器竖屏使用，适合学习、复盘、训练和牌力分析。

本项目不包含真钱游戏、线上平台实时辅助、登录、支付或数据库功能。

## 功能说明

- 支持 Texas Hold'em 德州扑克规则。
- 支持 2 到 10 名玩家，包括 Heads-up、6-Max、Full Ring、10-Max。
- 支持选择 Hero 两张手牌。
- 支持选择 0、3、4、5 张公共牌，并自动识别 Preflop、Flop、Turn、River。
- 防止重复选牌，同一张牌不能同时出现在手牌和公共牌中。
- 默认对手手牌未知，由程序从剩余牌堆随机生成。
- 使用 Monte Carlo 模拟输出胜率 WIN、平局 TIE、失败 LOSE。
- 支持快速 1,000 次、标准 10,000 次、精准 50,000 次模拟。
- 河牌圈已有 5 张公共牌时直接比较完整牌局。
- 完整支持牌型判断：皇家同花顺、同花顺、四条、葫芦、同花、顺子、三条、两对、一对、高牌。
- 正确处理 A-2-3-4-5 顺子和同牌型 kicker 比较。
- 支持多人比较和平局判断。
- 显示当前 Hero 最佳牌型或听牌提示。
- 提供起手牌 S / A / B / C / D 评级和说明。
- 使用 Streamlit session_state 保存最近 10 次计算结果。
- 深色牌桌风格、玻璃拟态卡片、大号胜率数字和手机端布局适配。

## 项目结构

```text
texas-edge/
├── app.py
├── cards.py
├── hand_evaluator.py
├── poker_engine.py
├── preflop_rank.py
├── styles.py
├── requirements.txt
└── README.md
```

## Windows 本地运行

1. 安装 Python 3.11 或以上。
2. 打开 PowerShell，进入项目目录：

```powershell
cd C:\Users\WAYNE\Documents\Codex\2026-06-23\files-mentioned-by-the-user-texas\texas-edge
```

3. 安装依赖：

```powershell
pip install -r requirements.txt
```

4. 启动应用：

```powershell
streamlit run app.py
```

5. 电脑浏览器打开 Streamlit 输出的本地地址，通常是：

```text
http://localhost:8501
```

6. 手机如需访问同一局域网内电脑服务，请让手机和电脑连接同一个 Wi-Fi，并使用电脑局域网 IP 地址访问。例如：

```text
http://192.168.1.100:8501
```

如果无法访问，请检查 Windows 防火墙是否允许 Python 或 Streamlit 监听局域网端口。

## 部署到 Streamlit Community Cloud

1. 创建 GitHub 仓库。
2. 上传 `texas-edge` 项目代码。
3. 打开 Streamlit Community Cloud。
4. 连接 GitHub 账号。
5. 选择对应仓库和分支。
6. 入口文件选择 `app.py`。
7. 部署完成后会得到一个公开网址。
8. 手机浏览器打开该网址即可使用。

## 使用方式

1. 点击手牌槽位，选择 Hero 的两张手牌。
2. 点击公共牌槽位，按需选择 0、3、4 或 5 张公共牌。
3. 选择玩家人数，范围为 2 到 10 人。
4. 选择模拟精度：快速、标准或精准。
5. 点击“计算胜率”。
6. 查看 WIN、TIE、LOSE、当前阶段、当前牌型、起手牌评级和稳定度。
7. 最近 10 次计算会显示在页面底部“最近记录”中。

## 输入校验

- 未选择两张手牌时不能计算。
- 公共牌数量为 1 或 2 张时不能计算。
- 同一张牌不能重复选择。
- 玩家人数必须在 2 到 10 人之间。
- 剩余牌数量不足时会提示错误。
- 计算异常会显示友好提示，不会把底层错误直接暴露给用户。

## 后续升级方向

- 升级为 React + FastAPI + PWA 手机 App 版本。
- 支持添加到手机桌面。
- 支持自定义对手手牌范围。
- 支持已知对手手牌输入。
- 添加 Outs 计算。
- 添加补牌概率计算。
- 添加训练模式。
- 添加复盘模式。
- 本地历史记录持久化。
- 起手牌矩阵。
- 多主题切换。
