/**
 * NFT Minting Service
 * 处理链上 NFT 铸造
 */

import { NFT_ABI, getContractAddresses } from './contractConfig.js'

/**
 * 调用智能合约铸造 NFT
 * @param {Object} params
 * @param {Object} params.signatureData - 后端返回的签名数据
 * @param {Object} params.provider - MetaMask provider (window.ethereum)
 * @param {string} params.chainId - 当前链 ID
 */
export async function mintNFT({ signatureData, provider, chainId }) {
  if (!provider) {
    throw new Error('请先连接钱包')
  }

  if (!signatureData) {
    throw new Error('缺少签名数据')
  }

  // 解析签名数据
  const { signature, nonce, deadline, level, contract_address } = signatureData

  // 获取合约地址
  const addresses = getContractAddresses(chainId)
  const nftAddress = contract_address || addresses.nft

  if (!nftAddress || nftAddress === '0x0000000000000000000000000000000000000000') {
    throw new Error('NFT 合约地址未配置，请联系管理员')
  }

  // 构建合约调用数据
  const iface = new ethers.Interface(NFT_ABI)
  const data = iface.encodeFunctionData('mintWithSignature', [
    level,
    signature,
    nonce,
    deadline,
  ])

  // 发送交易
  const accounts = await provider.request({ method: 'eth_accounts' })
  if (!accounts || accounts.length === 0) {
    throw new Error('请先连接钱包')
  }

  const txParams = {
    from: accounts[0],
    to: nftAddress,
    data: data,
  }

  // 估算 gas
  try {
    const gasEstimate = await provider.request({
      method: 'eth_estimateGas',
      params: [txParams],
    })
    txParams.gas = gasEstimate
  } catch (e) {
    console.warn('Gas estimation failed, using default:', e)
    txParams.gas = '0x30000' // 200000
  }

  // 发送交易
  const txHash = await provider.request({
    method: 'eth_sendTransaction',
    params: [txParams],
  })

  return {
    txHash,
    nftAddress,
    level,
  }
}

/**
 * 等待交易确认
 * @param {string} txHash - 交易哈希
 * @param {Object} provider - MetaMask provider
 * @param {number} confirmations - 确认数 (默认 1)
 */
export async function waitForTransaction(txHash, provider, confirmations = 1) {
  let receipt = null
  let attempts = 0
  const maxAttempts = 60 // 最多等待 60 秒

  while (!receipt && attempts < maxAttempts) {
    try {
      receipt = await provider.request({
        method: 'eth_getTransactionReceipt',
        params: [txHash],
      })
    } catch (e) {
      // 忽略错误，继续轮询
    }

    if (!receipt) {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      attempts++
    }
  }

  if (!receipt) {
    throw new Error('交易确认超时')
  }

  if (receipt.status === '0x0') {
    throw new Error('交易失败')
  }

  return receipt
}

/**
 * 检查用户是否已完成某关卡
 * @param {string} userAddress - 用户地址
 * @param {number} level - 关卡
 * @param {Object} provider - MetaMask provider
 * @param {string} chainId - 当前链 ID
 */
export async function hasCompletedLevel(userAddress, level, provider, chainId) {
  const addresses = getContractAddresses(chainId)
  const nftAddress = addresses.nft

  if (!nftAddress || nftAddress === '0x0000000000000000000000000000000000000000') {
    return false
  }

  const iface = new ethers.Interface(NFT_ABI)
  const data = iface.encodeFunctionData('hasCompletedLevel', [userAddress, level])

  try {
    const result = await provider.request({
      method: 'eth_call',
      params: [{ to: nftAddress, data }, 'latest'],
    })

    const decoded = iface.decodeFunctionResult('hasCompletedLevel', result)
    return decoded[0]
  } catch (e) {
    console.error('Check completed level failed:', e)
    return false
  }
}

/**
 * 获取用户的 NFT 数量
 * @param {string} userAddress - 用户地址
 * @param {Object} provider - MetaMask provider
 * @param {string} chainId - 当前链 ID
 */
export async function getNFTBalance(userAddress, provider, chainId) {
  const addresses = getContractAddresses(chainId)
  const nftAddress = addresses.nft

  if (!nftAddress || nftAddress === '0x0000000000000000000000000000000000000000') {
    return 0
  }

  const iface = new ethers.Interface(NFT_ABI)
  const data = iface.encodeFunctionData('balanceOf', [userAddress])

  try {
    const result = await provider.request({
      method: 'eth_call',
      params: [{ to: nftAddress, data }, 'latest'],
    })

    const decoded = iface.decodeFunctionResult('balanceOf', result)
    return Number(decoded[0])
  } catch (e) {
    console.error('Get NFT balance failed:', e)
    return 0
  }
}
