# Texas Edge PWA 升级方案

本文档说明如何把当前 Streamlit 版本的 Texas Edge 迁移为 `React + FastAPI + PWA` 架构，让用户可以通过手机浏览器访问，并支持“添加到手机桌面”的类 App 体验。

## 1. 当前版本资产盘点

当前 Streamlit 版本已经具备可复用的核心能力：

- `cards.py`：牌库、牌面格式化、防重复、阶段识别。
- `hand_evaluator.py`：5 到 7 张牌最佳牌型判断、A-5 顺子、kicker、多玩家比较。
- `poker_engine.py`：Monte Carlo 胜率模拟、未知对手发牌、胜/平/负统计。
- `preflop_rank.py`：起手牌 S/A/B/C/D 评级和解释。
- `styles.py`：当前 Streamlit 深色 UI 样式，可作为 PWA 视觉参考。
- `app.py`：交互流程原型，包括选牌、玩家人数、模拟次数、结果展示和历史记录。

升级时不建议重写扑克算法。第一阶段应保留 Python 核心模块，把 Streamlit UI 替换为：

- 后端：FastAPI，负责校验输入、调用现有算法、返回 JSON。
- 前端：React，负责移动端界面、牌面选择、结果仪表盘和本地历史。
- PWA：manifest、service worker、离线外壳缓存、桌面安装能力。

## 2. 目标架构

```text
texas-edge-pwa/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   └── equity_service.py
│   │   └── poker/
│   │       ├── cards.py
│   │       ├── hand_evaluator.py
│   │       ├── poker_engine.py
│   │       └── preflop_rank.py
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── public/
│   │   ├── manifest.webmanifest
│   │   ├── icons/
│   │   └── screenshots/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── texasEdgeApi.ts
│       ├── components/
│       │   ├── CardGrid.tsx
│       │   ├── CardSlot.tsx
│       │   ├── PlayerCountControl.tsx
│       │   ├── SimulationControl.tsx
│       │   ├── ResultDashboard.tsx
│       │   └── HistoryPanel.tsx
│       ├── hooks/
│       │   └── useLocalHistory.ts
│       ├── styles/
│       │   └── theme.css
│       └── types/
│           └── poker.ts
│
└── README.md
```

也可以先保留单仓库结构，在当前仓库新增 `backend/` 和 `frontend/`，等 PWA 稳定后再归档 Streamlit 版本到 `legacy_streamlit/`。

## 3. 后端迁移方案：FastAPI

### 3.1 依赖建议

`backend/requirements.txt`：

```txt
fastapi
uvicorn[standard]
pydantic
```

如需跨域分离部署，使用 FastAPI 内置的 `CORSMiddleware`，不需要额外依赖。

### 3.2 核心模块迁移

把当前文件移动或复制到后端算法目录：

```text
cards.py              -> backend/app/poker/cards.py
hand_evaluator.py     -> backend/app/poker/hand_evaluator.py
poker_engine.py       -> backend/app/poker/poker_engine.py
preflop_rank.py       -> backend/app/poker/preflop_rank.py
```

迁移后只调整 import 路径，例如：

```python
from app.poker.cards import stage_name
from app.poker.poker_engine import run_monte_carlo
```

不要在迁移第一阶段改变牌型算法和 Monte Carlo 逻辑，先保证结果与 Streamlit 版本一致。

### 3.3 API 设计

建议提供以下接口：

```text
GET  /api/health
GET  /api/cards
POST /api/equity
POST /api/preflop-grade
POST /api/hand-type
```

核心接口 `POST /api/equity` 请求：

```json
{
  "hero_cards": ["AS", "KS"],
  "board_cards": ["QS", "JS", "2D"],
  "player_count": 6,
  "simulations": 10000
}
```

响应：

```json
{
  "win_rate": 48.7,
  "tie_rate": 3.1,
  "lose_rate": 48.2,
  "stage": "Flop / 翻牌圈",
  "hero_hand_type": "同花听牌",
  "preflop_grade": "S",
  "preflop_combo": "AKs",
  "preflop_comment": "顶级起手牌，适合多数位置积极参与。",
  "simulations": 10000,
  "confidence": "稳定度较高"
}
```

### 3.4 后端校验规则

后端必须保留这些校验：

- Hero 手牌必须正好 2 张。
- 公共牌数量必须是 0、3、4、5。
- 不能重复选牌。
- 玩家人数必须是 2 到 10。
- 模拟次数只能使用允许值：1000、10000、50000。
- 剩余牌不足时返回 400 错误。

前端可以提前提示，但最终校验必须以后端为准。

### 3.5 性能优化路线

第一版 FastAPI 可以同步调用 `run_monte_carlo`。如果后续 50,000 次模拟在多人局下延迟明显，再升级为：

- 使用 `asyncio.to_thread()` 或线程池把模拟放到后台线程。
- 为 9 人、10 人局限制默认模拟次数。
- 引入任务接口：`POST /api/equity-jobs` 创建任务，`GET /api/equity-jobs/{id}` 查询进度。
- 对固定输入做短时缓存，但要清楚提示 Monte Carlo 结果是模拟估算。

## 4. 前端迁移方案：React

### 4.1 技术选型

推荐：

- 构建工具：Vite
- 框架：React + TypeScript
- 样式：CSS Modules 或普通 CSS，自定义主题变量即可
- 状态管理：React 内置 state + custom hooks，第一版不需要 Redux
- API 请求：`fetch`
- 本地历史：`localStorage`，后续可升级 IndexedDB

### 4.2 页面结构

React 首屏保持当前 Streamlit 版本的移动端流程：

1. 顶部品牌区：Texas Edge / 德州扑克胜率分析器。
2. Hero 手牌槽：两个大卡槽。
3. 公共牌槽：五个卡槽，并显示 Preflop / Flop / Turn / River。
4. 玩家人数控制：加减按钮、滑块、2/6/9/10 快捷按钮。
5. 模拟精度：1000 / 10000 / 50000。
6. 牌面选择网格：按花色和点数显示 52 张牌。
7. 计算按钮：固定在底部或接近底部的大按钮。
8. 结果仪表盘：WIN 最大，TIE/LOSE 和分析卡片在下方。
9. 最近记录：折叠面板，保存最近 10 条。

### 4.3 前端状态模型

```ts
type CardCode =
  | "AS" | "KS" | "QS" | "JS" | "TS"
  | string;

type AppState = {
  heroCards: [CardCode | null, CardCode | null];
  boardCards: [CardCode | null, CardCode | null, CardCode | null, CardCode | null, CardCode | null];
  activeSlot: {
    area: "hero" | "board";
    index: number;
  };
  playerCount: number;
  simulations: 1000 | 10000 | 50000;
  result: EquityResult | null;
  history: HistoryRecord[];
};
```

### 4.4 组件拆分

- `CardSlot`：显示单个卡槽，负责 active/highlight 状态。
- `CardGrid`：52 张牌按钮，负责禁用已占用牌。
- `PlayerCountControl`：玩家人数加减、滑块和快捷按钮。
- `SimulationControl`：模拟次数切换。
- `ResultDashboard`：胜率、平局率、失败率、阶段、牌型、评级。
- `HistoryPanel`：最近 10 条历史，使用 localStorage。
- `InstallPrompt`：PWA 安装提示。

### 4.5 与后端通信

前端只向后端提交紧凑牌码，不提交花色符号：

```ts
await fetch(`${API_BASE_URL}/api/equity`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    hero_cards: heroCards.filter(Boolean),
    board_cards: boardCards.filter(Boolean),
    player_count: playerCount,
    simulations
  })
});
```

## 5. PWA 能力设计

### 5.1 Manifest

`frontend/public/manifest.webmanifest`：

```json
{
  "name": "Texas Edge",
  "short_name": "Texas Edge",
  "description": "德州扑克胜率、牌型与起手牌分析工具",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#07110D",
  "theme_color": "#07110D",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### 5.2 Service Worker

第一版 PWA 建议缓存：

- HTML shell
- JS/CSS bundle
- 图标和截图
- 主题 CSS

不建议离线缓存胜率 API 结果作为默认行为，因为 Monte Carlo 结果与输入强相关，错误复用会造成误导。离线时应显示：

```text
当前离线，胜率计算需要网络连接。你仍可以查看最近记录。
```

### 5.3 可安装体验

移动端目标：

- Android Chrome：出现安装提示或浏览器菜单“添加到主屏幕”。
- iOS Safari：通过分享菜单“添加到主屏幕”。
- 安装后全屏或 standalone 打开。
- 使用安全 HTTPS 域名部署。

### 5.4 本地历史

Streamlit 版使用 `session_state`，PWA 版改为浏览器本地保存：

- 第一版：`localStorage` 保存最近 10 条。
- 第二版：IndexedDB 保存更多复盘记录。
- 后续可增加导出 JSON / CSV。

## 6. 部署方案

### 6.1 分离部署

推荐初期使用分离部署：

- 前端：Vercel、Netlify 或 Cloudflare Pages。
- 后端：Render、Railway、Fly.io 或 VPS。

优点：

- 前端 PWA 部署简单。
- 后端可以单独扩容。
- 后续可替换算法服务而不影响前端。

需要配置：

- 前端环境变量：`VITE_API_BASE_URL=https://你的后端域名`
- 后端 CORS：允许前端域名访问。

### 6.2 单体部署

也可以让 FastAPI 托管 React 构建后的静态文件：

```text
frontend build -> backend/app/static/
FastAPI serves /
FastAPI serves /api/*
```

优点：

- 只有一个部署服务。
- CORS 更简单。

缺点：

- 前后端发布耦合。
- PWA 静态资源缓存策略要更小心。

## 7. 迁移阶段计划

### 阶段 1：冻结 Streamlit 基线

目标：确保迁移前后结果一致。

- 给当前 Python 核心算法补最小测试。
- 固定一批样例牌局：
  - 皇家同花顺
  - A-5 顺子
  - 四条
  - 葫芦
  - 两对 kicker
  - 多人平局
- 记录 `AKs heads-up preflop` 等固定 seed 的模拟结果。

### 阶段 2：抽出后端服务

目标：保留算法，建立 FastAPI JSON 接口。

- 创建 `backend/`。
- 移入扑克算法模块。
- 新增 Pydantic 请求/响应模型。
- 新增 `/api/equity`。
- 用 pytest 验证接口和算法。

### 阶段 3：重建 React 移动端 UI

目标：React 完整复刻当前 Streamlit 功能。

- 建立 Vite + React + TypeScript 项目。
- 实现牌槽、牌面网格、玩家人数、模拟精度。
- 接入 `/api/equity`。
- 实现结果仪表盘。
- 实现最近 10 条历史。
- 保留当前深绿、金色、深色卡片视觉方向。

### 阶段 4：加入 PWA 能力

目标：手机可安装，弱网体验更稳。

- 添加 manifest。
- 添加图标：192、512、maskable icon。
- 添加 service worker。
- 缓存 App shell。
- 增加离线提示。
- 测试 Android Chrome 和 iOS Safari。

### 阶段 5：部署与灰度

目标：从 Streamlit 网址平滑过渡到 PWA 网址。

- 部署 FastAPI 后端。
- 部署 React 前端。
- 配置 HTTPS 和环境变量。
- 用手机访问并添加到桌面。
- 在 README 中保留 Streamlit 版本和 PWA 版本说明。

## 8. 测试清单

### 后端测试

- `POST /api/equity` 正常返回。
- 缺少两张手牌返回 400。
- 公共牌 1 或 2 张返回 400。
- 重复牌返回 400。
- 玩家人数小于 2 或大于 10 返回 400。
- 50,000 次模拟可完成并有 loading 支持。

### 前端测试

- 手机竖屏 375px 宽度不溢出。
- 52 张牌点击区域足够大。
- 已选牌高亮，重复牌禁用。
- 公共牌阶段自动显示。
- API 错误显示中文友好提示。
- 最近记录刷新页面后仍存在。

### PWA 测试

- Lighthouse PWA 检查通过主要项。
- Manifest 可识别。
- Service worker 注册成功。
- 首页可离线打开外壳。
- 离线时不误算胜率。
- Android 可添加到主屏幕。
- iOS Safari 可添加到主屏幕。

## 9. 风险与处理

| 风险 | 处理方式 |
| --- | --- |
| 多人局 50,000 次模拟响应慢 | 后端线程池、任务队列、进度查询、默认提示快速/标准模式 |
| 前后端结果不一致 | 算法模块只迁移 import，不重写逻辑，使用固定样例测试 |
| PWA 离线误导用户 | 离线只展示历史，不调用缓存的胜率计算结果 |
| 手机 UI 过密 | 保持单列主流程，牌面网格分花色分行 |
| iOS PWA 限制较多 | 明确提供 Safari 添加到主屏幕说明 |

## 10. 推荐开发顺序

1. 新建分支：

```bash
git checkout -b pwa-migration
```

2. 创建 `backend/`，迁移算法并暴露 FastAPI。
3. 创建 `frontend/`，先做无 PWA 的 React 页面。
4. 前后端联调，确保功能等价。
5. 增加 PWA manifest 和 service worker。
6. 部署测试环境。
7. 手机真机测试。
8. 合并到 `main`。

## 11. 第一版 PWA 验收标准

- 手机浏览器可直接打开网址。
- 可以添加到手机桌面。
- UI 功能覆盖当前 Streamlit 版本。
- 选择手牌、公共牌、玩家人数、模拟次数后可计算胜/平/负。
- 显示当前阶段、当前牌型、起手牌评级。
- 最近 10 条记录保存在本机浏览器。
- 核心算法结果与当前 Streamlit 版本一致。
- 无需登录、无需支付、无需数据库。

