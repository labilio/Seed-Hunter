#!/bin/bash

# ============================================================
# Seed Hunter - 一键启动脚本
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              🎮 Seed Hunter - AI 越狱挑战游戏              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/web"

# 检查目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ 后端目录不存在: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ 前端目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

# 函数：启动后端
start_backend() {
    echo -e "${YELLOW}🚀 启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}📦 创建虚拟环境...${NC}"
        python3 -m venv .venv
    fi
    
    # 激活虚拟环境并安装依赖
    source .venv/bin/activate
    
    # 检查是否需要安装依赖
    if [ ! -f ".venv/.installed" ]; then
        echo -e "${YELLOW}📦 安装后端依赖...${NC}"
        pip install -r requirements.txt -q
        touch .venv/.installed
    fi
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}⚠️  未找到 .env 文件，正在从 .env.example 复制...${NC}"
            cp .env.example .env
            echo -e "${RED}⚠️  请编辑 .env 文件并填写必要的 API 密钥！${NC}"
        else
            echo -e "${RED}❌ 未找到 .env 或 .env.example 文件${NC}"
            exit 1
        fi
    fi
    
    # 启动后端
    echo -e "${GREEN}✅ 后端启动中... (端口 8000)${NC}"
    cd "$BACKEND_DIR" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/seed_hunter_backend.pid
}

# 函数：启动前端
start_frontend() {
    echo -e "${YELLOW}🚀 启动前端服务...${NC}"
    cd "$FRONTEND_DIR"
    
    # 检查是否需要安装依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 安装前端依赖...${NC}"
        npm install
    fi
    
    # 启动前端
    echo -e "${GREEN}✅ 前端启动中... (端口 5173)${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/seed_hunter_frontend.pid
}

# 函数：停止所有服务
stop_all() {
    echo -e "${YELLOW}🛑 停止所有服务...${NC}"
    
    if [ -f /tmp/seed_hunter_backend.pid ]; then
        kill $(cat /tmp/seed_hunter_backend.pid) 2>/dev/null || true
        rm /tmp/seed_hunter_backend.pid
    fi
    
    if [ -f /tmp/seed_hunter_frontend.pid ]; then
        kill $(cat /tmp/seed_hunter_frontend.pid) 2>/dev/null || true
        rm /tmp/seed_hunter_frontend.pid
    fi
    
    # 清理可能残留的进程
    pkill -f "uvicorn gandalf_game" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
}

# 函数：显示状态
show_status() {
    echo -e "${BLUE}📊 服务状态:${NC}"
    
    if pgrep -f "uvicorn gandalf_game" > /dev/null; then
        echo -e "  后端: ${GREEN}运行中${NC} (http://localhost:8000)"
    else
        echo -e "  后端: ${RED}未运行${NC}"
    fi
    
    if pgrep -f "vite" > /dev/null; then
        echo -e "  前端: ${GREEN}运行中${NC} (http://localhost:5173)"
    else
        echo -e "  前端: ${RED}未运行${NC}"
    fi
}

# 函数：显示帮助
show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动所有服务 (默认)"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    查看服务状态"
    echo "  backend   仅启动后端"
    echo "  frontend  仅启动前端"
    echo "  help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 启动所有服务"
    echo "  $0 start        # 启动所有服务"
    echo "  $0 stop         # 停止所有服务"
}

# 主逻辑
case "${1:-start}" in
    start)
        stop_all
        start_backend
        sleep 2
        start_frontend
        echo ""
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                    🎉 启动成功！                          ║${NC}"
        echo -e "${GREEN}╠═══════════════════════════════════════════════════════════╣${NC}"
        echo -e "${GREEN}║  前端地址: http://localhost:5173                          ║${NC}"
        echo -e "${GREEN}║  后端地址: http://localhost:8000                          ║${NC}"
        echo -e "${GREEN}║  API 文档: http://localhost:8000/docs                     ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务，或运行 '$0 stop'${NC}"
        wait
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 1
        $0 start
        ;;
    status)
        show_status
        ;;
    backend)
        start_backend
        wait
        ;;
    frontend)
        start_frontend
        wait
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        show_help
        exit 1
        ;;
esac
