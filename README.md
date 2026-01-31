# 🎮 Seed Hunter - AI 越狱挑战游戏

> AI + WEB3 已经成为超大趋势，但是
> 你的 AI 设计真的安全吗？
> 这是一款结合 AI 安全与 Web3 的创新游戏。只有挑战过 AI 安全，你才知道 AI 安全在 Web3 行业是多重要的一个事情！

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Kite AI](https://img.shields.io/badge/Blockchain-Kite%20AI-purple.svg)
![React](https://img.shields.io/badge/Frontend-React-61dafb.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)

## 📖 项目简介

Seed Hunter 是一款 AI 越狱挑战游戏。玩家需要通过各种 Prompt 注入技巧，突破 AI 的防御，获取被守护的"助记词"。成功攻破关卡后，玩家可以获得 NFT 奖励，高难度关卡还可以将攻击数据贡献给 Kite AI 网络，获得额外奖励。

### 核心玩法

1. **7 个难度递增的关卡** - 从简单的无防御到复杂的多层 AI + 黑名单防御
2. **NFT 成就系统** - 每个关卡都有独特的 NFT 奖励
3. **Kite AI 数据贡献** - Level 6-7 的攻击数据可以贡献给 AI 安全研究

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 一键启动

```bash
# 克隆项目
git clone https://github.com/labilio/Seed-Hunter.git
cd Seed-Hunter

# 启动所有服务
./start.sh
```

### 手动启动

**后端:**
```bash
cd spoon-starter
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填写 API 密钥
uvicorn seedhunter_game.main:app --reload --port 8000
```

**前端:**
```bash
cd Seed-Hunter/web
npm install
npm run dev
```

### 访问地址

- 🎮 **游戏前端**: http://localhost:5173
- 📡 **后端 API**: http://localhost:8000
- 📚 **API 文档**: http://localhost:8000/docs

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# LLM API 配置 (必填)
DEEPSEEK_API_KEY=your_api_key_here

# 区块链配置 (NFT 铸造需要)
SIGNER_PRIVATE_KEY=your_private_key
CHAIN_RPC_URL=https://rpc-testnet.gokite.ai
CHAIN_ID=2368

# NFT 合约地址
NFT_CONTRACT_ADDRESS=0x12bC0b071f294716E4E3cc64f3Da117519496B24
```

## 🎯 关卡系统

| 关卡 | 难度 | 防御机制 | NFT 等级 |
|------|------|----------|----------|
| 1 | ⭐ | 无防御 | Bronze |
| 2 | ⭐ | 输出黑名单 | Bronze |
| 3 | ⭐⭐ | LLM 输出检测 | Silver |
| 4 | ⭐⭐ | LLM 双重检测 | Silver |
| 5 | ⭐⭐⭐ | 输入黑名单 | Gold |
| 6 | ⭐⭐⭐ | LLM 输入检测 + 数据贡献 | Gold |
| 7 | ⭐⭐⭐⭐ | 终极防御 + 数据贡献 | Platinum |


## 🎯 一些常见的 AI 安全破解木马：



## 🔗 区块链集成

### Kite AI 测试网

- **网络名称**: KiteAI Testnet
- **RPC URL**: https://rpc-testnet.gokite.ai
- **Chain ID**: 2368
- **浏览器**: https://testnet.kitescan.ai
- **水龙头**: https://faucet.gokite.ai

### NFT 合约

- **合约地址**: `0x12bC0b071f294716E4E3cc64f3Da117519496B24`
- **标准**: ERC721
- **特性**: 链上 SVG 生成、签名验证铸造

## 📁 项目结构

```
spooooon/
├── start.sh                 # 一键启动脚本
├── README.md                # 项目说明
├── spoon-starter/           # 后端项目
│   ├── seedhunter_game/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── brain.py         # AI 对话处理
│   │   ├── judge.py         # 密码验证 + NFT 签名
│   │   ├── oracle.py        # 提示购买系统
│   │   ├── config.py        # 关卡配置
│   │   ├── kite_contributor.py  # Kite AI 数据贡献
│   │   └── contracts/       # Solidity 智能合约
│   ├── .env.example
│   └── requirements.txt
└── Seed-Hunter/             # 前端项目
    └── web/
        ├── src/
        │   ├── App.jsx      # 主组件
        │   └── utils/
        └── package.json
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **DeepSeek** - LLM 对话引擎
- **Web3.py** - 区块链交互
- **eth-account** - 签名生成

### 前端
- **React** - UI 框架
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **ethers.js** - Web3 交互

### 区块链
- **Solidity** - 智能合约语言
- **Foundry** - 合约开发框架
- **Kite AI** - Layer 1 区块链

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Kite AI](https://gokite.ai) - 区块链基础设施
- [DeepSeek](https://deepseek.com) - LLM 服务
- [OpenZeppelin](https://openzeppelin.com) - 智能合约库
