/**
 * Smart Contract Configuration
 * 智能合约配置和 ABI
 */

// 合约地址 (部署后更新)
export const CONTRACT_ADDRESSES = {
  // Kite AI Testnet (推荐)
  2368: {
    nft: '0x12bC0b071f294716E4E3cc64f3Da117519496B24',
    hintPayment: import.meta.env.VITE_HINT_CONTRACT_ADDRESS || '0x0000000000000000000000000000000000000000',
  },
  // Arbitrum Sepolia (备用)
  421614: {
    nft: import.meta.env.VITE_NFT_CONTRACT_ADDRESS || '0x0000000000000000000000000000000000000000',
    hintPayment: import.meta.env.VITE_HINT_CONTRACT_ADDRESS || '0x0000000000000000000000000000000000000000',
    usdc: '0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d',
  },
}

// Kite AI 网络配置
export const KITE_AI_NETWORK = {
  chainId: '0x940', // 2368 in hex
  chainName: 'KiteAI Testnet',
  rpcUrls: ['https://rpc-testnet.gokite.ai'],
  nativeCurrency: {
    name: 'KITE',
    symbol: 'KITE',
    decimals: 18,
  },
  blockExplorerUrls: ['https://testnet.kitescan.ai'],
}

// SeedHunterNFT ABI (简化版，只包含需要的函数)
export const NFT_ABI = [
  {
    name: 'mintWithSignature',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'level', type: 'uint256' },
      { name: 'signature', type: 'bytes' },
      { name: 'nonce', type: 'bytes32' },
      { name: 'deadline', type: 'uint256' },
    ],
    outputs: [],
  },
  {
    name: 'hasCompletedLevel',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'user', type: 'address' },
      { name: 'level', type: 'uint256' },
    ],
    outputs: [{ name: '', type: 'bool' }],
  },
  {
    name: 'getCompletedLevels',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'user', type: 'address' }],
    outputs: [{ name: '', type: 'bool[]' }],
  },
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'owner', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }],
  },
  {
    name: 'tokenOfOwnerByIndex',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'owner', type: 'address' },
      { name: 'index', type: 'uint256' },
    ],
    outputs: [{ name: '', type: 'uint256' }],
  },
  {
    name: 'tokenURI',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'tokenId', type: 'uint256' }],
    outputs: [{ name: '', type: 'string' }],
  },
  {
    name: 'tokenLevel',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'tokenId', type: 'uint256' }],
    outputs: [{ name: '', type: 'uint256' }],
  },
  // Events
  {
    name: 'LevelCompleted',
    type: 'event',
    inputs: [
      { name: 'user', type: 'address', indexed: true },
      { name: 'level', type: 'uint256', indexed: true },
      { name: 'tokenId', type: 'uint256', indexed: false },
    ],
  },
]

/**
 * 获取当前链的合约地址
 */
export function getContractAddresses(chainId) {
  const id = typeof chainId === 'string' ? parseInt(chainId, 16) : chainId
  return CONTRACT_ADDRESSES[id] || CONTRACT_ADDRESSES[421614]
}
