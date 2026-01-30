# Gandalf Game Smart Contracts

基于 Foundry 的智能合约项目，包含 NFT 成就系统和提示付费系统。

## 合约说明

### GandalfBreakerNFT.sol
- **功能**: 玩家通关后铸造成就 NFT
- **特性**:
  - ERC721 标准
  - 使用后端签名验证通关
  - 链上生成 SVG 图片
  - 防重放攻击 (nonce)
  - 按等级分 Tier: Bronze/Silver/Gold/Platinum

### HintPayment.sol
- **功能**: 玩家支付 USDC 购买提示
- **特性**:
  - 支持固定价格和议价价格
  - 使用后端签名验证议价
  - 支持批量查询购买状态

## 快速开始

### 1. 安装 Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 2. 安装依赖

```bash
cd contracts
forge install OpenZeppelin/openzeppelin-contracts --no-commit
```

### 3. 编译合约

```bash
forge build
```

### 4. 运行测试

```bash
forge test -vvv
```

### 5. 部署合约

创建 `.env` 文件：

```bash
DEPLOYER_PRIVATE_KEY=0x...
SIGNER_ADDRESS=0x...
TREASURY_ADDRESS=0x...
USDC_ADDRESS=0x...  # Arbitrum Sepolia: 0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc
ARBISCAN_API_KEY=your_api_key
```

部署到 Arbitrum Sepolia：

```bash
source .env
forge script script/Deploy.s.sol:DeployScript \
  --rpc-url $ARBITRUM_SEPOLIA_RPC_URL \
  --broadcast \
  --verify
```

## 网络配置

### Arbitrum Sepolia (测试网)
- Chain ID: 421614
- RPC: https://sepolia-rollup.arbitrum.io/rpc
- Explorer: https://sepolia.arbiscan.io
- USDC: `0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d`

### Arbitrum One (主网)
- Chain ID: 42161
- RPC: https://arb1.arbitrum.io/rpc
- Explorer: https://arbiscan.io
- USDC: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`

## 签名格式

### NFT 铸造签名

```solidity
bytes32 messageHash = keccak256(abi.encodePacked(
    userAddress,    // 接收者地址
    level,          // 关卡 (1-7)
    nonce,          // bytes32 唯一标识
    deadline,       // 过期时间戳
    contractAddress // NFT 合约地址
));
```

### 议价提示签名

```solidity
bytes32 messageHash = keccak256(abi.encodePacked(
    buyerAddress,      // 购买者地址
    level,             // 关卡
    hintIndex,         // 提示索引 (0-2)
    negotiatedPrice,   // 议价后的价格
    deadline,          // 过期时间戳
    contractAddress    // HintPayment 合约地址
));
```

## Gas 估算

| 操作 | 预估 Gas |
|------|----------|
| mintWithSignature | ~150,000 |
| payForHint | ~80,000 |
| payForHintWithNegotiatedPrice | ~90,000 |

## 安全说明

1. **签名者钱包**: 使用独立的热钱包，不要使用部署者钱包
2. **私钥管理**: 后端签名私钥应使用 KMS 或 HSM 管理
3. **Nonce 管理**: 确保每次签名使用唯一的 nonce
4. **时间限制**: 签名有效期建议设置为 1 小时
