# 🎮 Seed Hunter - AI 越狱挑战游戏
**Web3 世界的第一座 AI 安全实战靶场**

> AI + WEB3 已经成为超大趋势，但是123
> 你的 AI 设计真的安全吗？
> 这是一款结合 AI 安全与 Web3 的创新游戏。**只有挑战过 AI 安全，你才知道 AI 安全到底有多难！ 到底有多重要！**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Kite AI](https://img.shields.io/badge/Blockchain-Kite%20AI-purple.svg)
![React](https://img.shields.io/badge/Frontend-React-61dafb.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)

## 📺 Live Demo (30s 极速预览)
![alt text](Level3.gif)

![alt text](安全学习.gif)

![alt text](铸造NFT.gif)

![alt text](突破高难度贡献数据.gif)

![alt text](排行榜单.gif)


## 📖 项目简介

- Seed Hunter 助记词猎手是一款集Web3 AI安全挑战学习平台

- 你将会模拟一名Web3黑客，通过学习不同的AI安全破解方法和Web3历史上的真实案例，逐步了解Web3行业中AI安全的重要程度和常见漏洞

- 并最终向**手握助记词单词**的 AI 发起挑战，尝试破解 AI 手中的助记词。

- 成功攻破关卡后，玩家可以获得 「链上荣誉勋章」 NFT 奖励；攻破高难度关卡后，还可以将攻击数据贡献给 Kite AI 网络，获得「链上代币奖励」

### 核心玩法

1. **7 个难度递增的关卡** - 从简单的无防御到复杂的多层 AI + 黑名单防御
2. **NFT 成就系统** - 每个关卡都有独特的 NFT 奖励！ 每突破一个 AI 安全挑战，就会在区块链世界上永远的留下你的足迹。
3. **Kite AI 数据贡献** - Level 6-7 的攻击数据可以贡献给 AI 安全研究，帮助共建更加安全的Web3 + AI 世界
4. **安全学习** - 不知道怎么写提示词会绕过 AI ？ 随时查看
5. **以史为鉴** - 在挑战的过程中，了解历史上真实的 **九大惊天大劫案**,深入了解 AI 安全在 Web3 行业中的惨痛教训
6. **排行天梯** - 与链上好友一同挑战


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

##  关卡系统

| 关卡 | 难度 | 防御机制 | NFT 等级 |
|------|------|----------|----------|
| 1 | ⭐ | 无防御 | Bronze |
| 2 | ⭐ | 输出黑名单 | Bronze |
| 3 | ⭐⭐ | LLM 输出检测 | Silver |
| 4 | ⭐⭐ | LLM 双重检测 | Silver |
| 5 | ⭐⭐⭐ | 输入黑名单 | Gold |
| 6 | ⭐⭐⭐ | LLM 输入检测 + 数据贡献 | Gold |
| 7 | ⭐⭐⭐⭐ | 终极防御 + 数据贡献 | Platinum |


##  一些常见的 AI 安全破解木马：



##  区块链集成

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

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢
- ETH Panda & LXDAO
- Web3实习计划
- [Kite AI](https://gokite.ai) - 区块链基础设施
- [DeepSeek](https://deepseek.com) - LLM 服务
- [OpenZeppelin](https://openzeppelin.com) - 智能合约库
