# 校园跳蚤市场 — AI 智能发品平台

> 专为校园场景设计的二手交易平台。上传一张商品图，AI 自动识别物品、生成标题与文案、结合成色和联网行情给出估价。内置文本敏感词过滤 + 图片违规审核，管理员可对违规内容标记与放行。

## 技术架构

```
frontend (Vue 3 + Vite + Tailwind)     backend (FastAPI + SQLite)
       │                                       │
       │  SPA 静态文件由后端直托管               │
       │  /api/*  →  REST API                  │
       │  /uploads/*  →  静态文件               │
       │                                       │
       └───────────── uvicorn ─────────────────┘
                          │
                    ┌─────┴─────┐
                    │  SQLite   │  AI (DashScope)
                    │  (文件DB)  │  qwen3.8-max
                    └───────────┘
```

- **后端**：Python 3.14+ / FastAPI / SQLAlchemy / SQLite / JWT
- **前端**：Vue 3 / Vite / Tailwind CSS（构建产物 `dist/` 由后端直接托管，无需 Node 运行环境）
- **AI**：OpenAI 兼容协议，默认阿里云百炼 DashScope（`qwen3.8-max` 多模态），可替换为任意兼容服务
- **审核**：自定义敏感词引擎（归一化防绕过）+ AI 多模态图片违规审核

## 功能

### 买家端
- 首页瀑布流浏览全部在售商品
- 关键词搜索、分类筛选
- 商品详情页（大图、描述、估价参考、卖家信息）

### 卖家端
- AI 智能发品：上传商品图 → 自动识别 → 生成标题、分类、成色、估价区间、促销文案
- 发品前引导补充品牌/型号/购入价格，AI 估价更精准
- 联网行情估价（基于实时二手市场数据修正估价）
- 个人中心：在售 / 已售 / 已下架三栏管理，支持删除、下架、标记已售

### 管理员
- 全量商品列表，可下架 / 标记违规 / 放行恢复
- 违规商品列表与审核
- 用户管理：新增/删除账号、升降级管理员角色（含保护：不能降级自己、不能删除最后一名管理员）

### 安全
- 敏感词过滤：文本（标题/描述/标签/联系方式）命中敏感词直接拦截，支持归一化防绕过（空格/符号/全角/谐音变体均能命中）
- 图片审核：上传时魔数校验（防伪装）+ AI 多模态审核（色情/暴力/违禁品/敏感/诈骗/隐私证件 6 类），AI 不可用时降级为仅本地校验
- JWT 认证、SPA 路径穿越防护、状态取值校验

## 快速启动

```powershell
# 1. 进入后端目录
cd outputs/mu/backend

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# 3. 配置环境变量
copy .env.example .env
# 编辑 .env：至少填入 OPENAI_API_KEY（AI 发品必需），可选修改 JWT_SECRET

# 4. 启动（前端已预构建在 dist/，后端直接托管）
.\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --host 0.0.0.0
```

浏览器打开 **http://localhost:8000**。

> 首次启动自动创建 SQLite 数据库并初始化 admin 账号。

## 账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | `admin` | `admin@12345` | 首次启动自动创建，可通过 `.env` 的 `ADMIN_DEFAULT_PASSWORD` 修改默认值 |
| 普通用户 | 自行注册 | ≥8 位，字母/数字/符号至少两类 | — |

## 配置参考 (.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | AI 服务 API Key | 必填 |
| `OPENAI_API_BASE` | API 地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `AI_MODEL` | 模型名称 | `qwen3.8-max` |
| `AI_ENABLE_SEARCH` | 联网行情估价 | `true` |
| `IMAGE_MODERATION` | 图片审核模式：`ai` / `local` / `off` | `ai` |
| `JWT_SECRET` | JWT 签名密钥 | 随机生成 |
| `ADMIN_DEFAULT_PASSWORD` | 新建库时 admin 初始密码 | `admin@12345` |

## API 概览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户信息 |
| POST | `/api/auth/change-password` | 修改密码 |
| POST | `/api/auth/avatar` | 上传头像 |

### 商品
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/products` | 商品列表（支持 `?search=&category=&page=&page_size=`） |
| GET | `/api/products/{id}` | 商品详情 |
| POST | `/api/products` | 发布商品 |
| PUT | `/api/products/{id}` | 更新商品（属主） |
| DELETE | `/api/products/{id}` | 删除商品（属主/管理员，同步清理图片） |
| GET | `/api/my/products` | 我的商品 |

### AI
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/analyze` | 上传图片 → AI 分析（标题/分类/成色/估价/标签/文案） |

### 审核
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/moderation/check` | 文本预检（前端发布前即时反馈） |
| POST | `/api/upload` | 图片上传（含校验+审核） |

### 管理员
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/all` | 全部商品 |
| GET | `/api/admin/flagged` | 违规商品列表 |
| POST | `/api/admin/products/{id}/offline` | 下架商品 |
| POST | `/api/admin/products/{id}/flag` | 标记违规（强制下架） |
| POST | `/api/admin/products/{id}/unflag` | 放行恢复（自动上架） |
| DELETE | `/api/admin/products/{id}` | 管理员删除商品 |
| GET | `/api/admin/users` | 用户列表 |
| POST | `/api/admin/users` | 创建用户 |
| PUT | `/api/admin/users/{id}/role` | 修改角色 |
| DELETE | `/api/admin/users/{id}` | 删除用户及名下全部商品 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/{path}` | SPA 兜底路由（返回前端页面） |

## 运行测试

后端运行时执行：

```powershell
cd outputs/mu/backend

.\.venv\Scripts\python.exe test_auth.py         # 认证 + 商品CRUD + 敏感词拦截
.\.venv\Scripts\python.exe test_validation.py   # 注册字段校验
.\.venv\Scripts\python.exe test_moderation.py   # 内容审核（25 项：文本/变体/误伤/图片）
.\.venv\Scripts\python.exe test_errors.py       # 错误处理
.\.venv\Scripts\python.exe test_api.py          # 商品列表/搜索
.\.venv\Scripts\python.exe test_ai.py           # AI 分析（需 API Key）
```

## 前端开发

需要 Node.js 与 pnpm：

```powershell
cd outputs/mu/frontend
pnpm install
pnpm dev        # 开发模式 http://localhost:5173，/api 自动代理到 8000
pnpm build      # 构建到 dist/，后端会直接托管最新版本
```

## 项目结构

```
ni/
├── start.bat                    # 一键启动脚本
├── README.md
├── .gitignore
├── outputs/mu/
│   ├── MERGE_NOTES.md           # 合并与修复记录
│   ├── backend/
│   │   ├── main.py              # 入口：路由、中间件、静态托管
│   │   ├── models.py            # SQLAlchemy 模型（User / Product）
│   │   ├── schemas.py           # Pydantic 请求/响应模型
│   │   ├── auth.py              # JWT 认证与密码哈希
│   │   ├── database.py          # 数据库连接与会话
│   │   ├── ai_service.py        # AI 分析服务（OpenAI 兼容协议）
│   │   ├── image_moderation.py  # 图片违规审核
│   │   ├── sensitive_filter.py  # 敏感词过滤引擎
│   │   ├── seed.py              # 种子数据
│   │   ├── requirements.txt     # Python 依赖
│   │   ├── .env.example         # 环境变量模板
│   │   └── test_*.py            # 测试套件
│   └── frontend/
│       ├── src/
│       │   ├── views/           # 页面组件（Home/Publish/Detail/Profile/Login/Admin/Welcome）
│       │   ├── components/      # 复用组件（NavBar/ProductCard）
│       │   ├── api/             # API 请求封装
│       │   ├── router/          # Vue Router 配置
│       │   └── stores/          # Pinia 状态管理
│       └── dist/                # 构建产物（后端直接托管）
└── work/                        # 开发过程文件（不上传仓库）
    ├── scripts/                 # 运维脚本
    ├── tests/                   # 额外测试
    ├── patches/                 # 历史补丁
    ├── logs/                    # 运行日志
    ├── results/                 # 测试结果
    └── diagnostics/             # 诊断脚本
```

## 安全说明

- `.env` 文件**不提交仓库**，仓库提供 `.env.example` 模板
- 生产部署前务必修改 `JWT_SECRET` 为随机值（`python -c "import secrets; print(secrets.token_urlsafe(32))"`）
- 默认管理员密码 `admin@12345`，首次登录后请立即修改
- 图片上传仅允许 `.jpg/.jpeg/.png/.gif/.webp`，且校验文件头魔数防止伪装
- API 未知路径返回 404 JSON，SPA 路由经过路径穿越防护
- 违规商品被标记后卖家无法自行重新上架（需管理员放行）
