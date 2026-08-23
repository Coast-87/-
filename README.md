# 校园跳蚤市场 - AI 智能发品平台

基于 FastAPI + Vue 3 的二手交易平台，集成 AI 多模态商品分析、自动估价、内容审核。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + SQLite + JWT
- **前端**: Vue 3 + Vite + Tailwind CSS
- **AI**: OpenAI 兼容协议（默认阿里云百炼 DashScope / qwen3.8-max）
- **审核**: 自定义敏感词引擎 + AI 多模态图片审核

## 快速启动

```powershell
cd outputs/mu/backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

cp .env.example .env

.\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --host 0.0.0.0
```

浏览器打开 http://localhost:8000

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin@12345 |
| 普通用户 | 自行注册 | >=8位，字母/数字/符号至少两类 |

## 功能

- 用户注册/登录（JWT 认证）
- AI 智能发品（上传图片自动生成标题/分类/成色/估价/文案）
- 联网行情估价
- 商品浏览/搜索/详情
- 个人中心（商品管理/删除/下架/标记已售）
- 管理员面板（用户管理/违规标记/放行）
- 敏感词过滤（文本+图片双重审核）
- 图片上传安全校验（魔数+AI 审核）

## 运行测试

```powershell
cd outputs/mu/backend
.\.venv\Scripts\python.exe test_auth.py
.\.venv\Scripts\python.exe test_validation.py
.\.venv\Scripts\python.exe test_moderation.py
.\.venv\Scripts\python.exe test_errors.py
.\.venv\Scripts\python.exe test_api.py
.\.venv\Scripts\python.exe test_ai.py
```

## 前端开发

```powershell
cd outputs/mu/frontend
pnpm install
pnpm dev
pnpm build
```
