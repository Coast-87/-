# 部署指南 — 方案一：云服务器

## 前提条件

- 一台云服务器（阿里云/腾讯云轻量应用服务器，2C2G 即可）
- 操作系统：Ubuntu 22.04 或 24.04
- 已开放端口：80（HTTP）、443（HTTPS）、22（SSH）
- （可选）一个已备案域名，解析到服务器 IP

## 快速部署

### 1. 上传项目到服务器

```bash
# 在本地执行，将项目打包上传
cd ni
git archive --format=tar.gz -o flea-market.tar.gz main
scp flea-market.tar.gz root@你的服务器IP:/opt/
```

### 2. 在服务器上解压并部署

```bash
ssh root@你的服务器IP

cd /opt
tar -xzf flea-market.tar.gz
mv ni flea-market   # 如果解压出来是 ni 目录

# 运行一键部署脚本
cd /opt/flea-market
chmod +x deploy/deploy.sh
bash deploy/deploy.sh 你的域名或IP
```

### 3. 配置环境变量

```bash
vim /opt/flea-market/outputs/mu/backend/.env
# 至少填入：OPENAI_API_KEY=你的Key
# 修改：JWT_SECRET=一个随机字符串
```

### 4. 重启服务

```bash
systemctl restart flea-market
systemctl status flea-market
```

## 手动部署（分步操作）

如果一键脚本出问题，可以按以下步骤手动操作：

### 安装依赖

```bash
apt update
apt install -y python3 python3-venv python3-pip nginx
```

### 放置项目

```bash
mkdir -p /opt/flea-market
# 将项目文件复制到 /opt/flea-market/
# 确保目录结构为 /opt/flea-market/outputs/mu/backend/...
```

### 创建虚拟环境

```bash
cd /opt/flea-market/outputs/mu/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p uploads
```

### 配置 .env

```bash
cp .env.example .env
vim .env  # 修改配置
```

### 配置 Nginx

```bash
cp /opt/flea-market/deploy/nginx.conf /etc/nginx/sites-available/flea-market
# 编辑配置文件，将 your-domain.com 替换为实际域名或 IP
sed -i 's/your-domain.com/你的域名或IP/g' /etc/nginx/sites-available/flea-market
ln -s /etc/nginx/sites-available/flea-market /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

### 配置 systemd 服务

```bash
cp /opt/flea-market/deploy/flea-market.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable flea-market
systemctl start flea-market
```

### 申请 SSL 证书（需要域名）

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d 你的域名
```

## 日常运维

```bash
# 查看服务状态
systemctl status flea-market

# 查看实时日志
journalctl -u flea-market -f

# 查看最近 100 行日志
journalctl -u flea-market -n 100

# 重启服务
systemctl restart flea-market

# 更新代码后重启
cd /opt/flea-market
git pull
systemctl restart flea-market

# 备份数据库
cp /opt/flea-market/outputs/mu/backend/flea_market.db /backup/flea_market_$(date +%Y%m%d).db
```

## 安全加固清单

- [ ] 修改 `.env` 中 `JWT_SECRET` 为随机值
- [ ] 修改 `.env` 中 `ADMIN_DEFAULT_PASSWORD`（如果数据库已存在则需登录后手动修改 admin 密码）
- [ ] 配置云服务器安全组：仅开放 80/443/22 端口
- [ ] 配置防火墙：`ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 22/tcp && ufw enable`
- [ ] 如果不需要 AI 图片审核，设置 `IMAGE_MODERATION=local` 降低 API 调用成本
- [ ] 定期备份 `/opt/flea-market/outputs/mu/backend/flea_market.db` 和 `uploads/` 目录
- [ ] 配置日志轮转（`/etc/logrotate.d/`）防止磁盘占满
