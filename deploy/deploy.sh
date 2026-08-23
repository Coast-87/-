#!/bin/bash
set -e

# ==============================================
# 校园跳蚤市场 - 一键部署脚本 (Ubuntu 22.04/24.04)
# ==============================================

APP_DIR="/opt/flea-market"
DOMAIN="${1:-localhost}"

echo "=== 校园跳蚤市场 部署脚本 ==="
echo "目标域名/IP: $DOMAIN"
echo ""

# 1. 系统依赖
echo "[1/6] 安装系统依赖..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip nginx certbot python3-certbot-nginx

# 2. 创建目录
echo "[2/6] 创建应用目录..."
mkdir -p $APP_DIR

# 3. 复制项目文件（假设当前在项目根目录）
echo "[3/6] 复制项目文件..."
cp -r . $APP_DIR/
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# 4. Python 虚拟环境
echo "[4/6] 创建 Python 虚拟环境..."
cd $APP_DIR/outputs/mu/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 确保 uploads 目录存在且可写
mkdir -p uploads
chown -R www-data:www-data uploads

# 5. 配置环境变量（如果 .env 不存在则从模板创建）
if [ ! -f .env ]; then
    echo "[5/6] 创建 .env 文件..."
    cp .env.example .env
    echo ""
    echo "!!! 请编辑 $APP_DIR/outputs/mu/backend/.env 填入配置 !!!"
    echo "!!! 至少需要设置 OPENAI_API_KEY                    !!!"
    echo ""
fi

# 6. Nginx 配置
echo "[6/6] 配置 Nginx..."
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/flea-market
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/flea-market
ln -sf /etc/nginx/sites-available/flea-market /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 7. systemd 服务
echo ""
echo "=== 配置 systemd 服务 ==="
cp $APP_DIR/deploy/flea-market.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable flea-market
systemctl start flea-market

# 8. SSL 证书（如果有域名）
if [ "$DOMAIN" != "localhost" ]; then
    echo ""
    echo "=== 申请 SSL 证书 ==="
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || echo "SSL 证书申请失败，请手动执行: certbot --nginx -d $DOMAIN"
fi

echo ""
echo "=============================================="
echo "  部署完成！"
echo "  访问地址: http://$DOMAIN"
echo "=============================================="
echo ""
echo "常用命令:"
echo "  查看状态:   systemctl status flea-market"
echo "  查看日志:   journalctl -u flea-market -f"
echo "  重启服务:   systemctl restart flea-market"
echo "  修改配置后: systemctl daemon-reload && systemctl restart flea-market"
