#!/bin/bash
# Seed Hunter 一键部署脚本 (Linux)
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

echo "========================================="
echo "  Seed Hunter 一键部署脚本"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
PROJECT_DIR="/opt/Seed-Hunter"
BACKEND_PORT=8000
FRONTEND_PORT=80

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}请使用 root 用户运行此脚本${NC}"
  echo "使用: sudo ./deploy.sh"
  exit 1
fi

echo -e "${YELLOW}[1/7] 更新系统包...${NC}"
apt update -y

echo -e "${YELLOW}[2/7] 安装依赖...${NC}"
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl

echo -e "${YELLOW}[3/7] 克隆项目...${NC}"
if [ -d "$PROJECT_DIR" ]; then
  echo "项目目录已存在，更新代码..."
  cd $PROJECT_DIR
  git pull
else
  git clone https://github.com/labilio/Seed-Hunter.git $PROJECT_DIR
  cd $PROJECT_DIR
fi

echo -e "${YELLOW}[4/7] 部署后端...${NC}"
cd $PROJECT_DIR/backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
  echo -e "${RED}请配置 .env 文件！${NC}"
  echo "复制示例配置:"
  cat > .env << 'EOF'
# LLM 配置
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
DEEPSEEK_API_KEY=你的API密钥

# 区块链配置
SIGNER_PRIVATE_KEY=你的私钥
NFT_CONTRACT_ADDRESS=0x12bC0b071f294716E4E3cc64f3Da117519496B24
CHAIN_RPC_URL=https://rpc-testnet.gokite.ai
CHAIN_ID=2368
EOF
  echo -e "${YELLOW}请编辑 $PROJECT_DIR/backend/.env 配置环境变量${NC}"
fi

# 创建 systemd 服务
cat > /etc/systemd/system/seedhunter-backend.service << EOF
[Unit]
Description=Seed Hunter Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/backend/.venv/bin"
ExecStart=$PROJECT_DIR/backend/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable seedhunter-backend
systemctl restart seedhunter-backend

echo -e "${YELLOW}[5/7] 部署前端...${NC}"
cd $PROJECT_DIR/web

# 获取服务器公网 IP
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "localhost")

# 配置 API 地址
echo "VITE_API_BASE_URL=http://$PUBLIC_IP:$BACKEND_PORT" > .env.production

npm install
npm run build

echo -e "${YELLOW}[6/7] 配置 Nginx...${NC}"
cat > /etc/nginx/sites-available/seedhunter << EOF
server {
    listen 80;
    server_name _;
    root $PROJECT_DIR/web/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

ln -sf /etc/nginx/sites-available/seedhunter /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo -e "${YELLOW}[7/7] 配置防火墙...${NC}"
ufw allow 80/tcp || true
ufw allow $BACKEND_PORT/tcp || true

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "前端地址: ${GREEN}http://$PUBLIC_IP${NC}"
echo -e "后端地址: ${GREEN}http://$PUBLIC_IP:$BACKEND_PORT${NC}"
echo -e "API 文档: ${GREEN}http://$PUBLIC_IP:$BACKEND_PORT/docs${NC}"
echo ""
echo -e "${YELLOW}重要: 请编辑 $PROJECT_DIR/backend/.env 配置环境变量${NC}"
echo -e "${YELLOW}然后运行: systemctl restart seedhunter-backend${NC}"
echo ""
echo "查看后端日志: journalctl -u seedhunter-backend -f"
