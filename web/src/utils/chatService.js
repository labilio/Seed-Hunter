/**
 * Chat Service - 调用后端 seedhunter_game API
 * 不再直连 LLM，而是通过后端统一处理
 */

// 后端 API 基础 URL（开发环境通过 Vite 代理，生产环境配置实际地址）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 会话 ID 管理（按关卡存储）
const sessionIds = {}

/**
 * 发送消息到后端 AI
 * @param {Object} params
 * @param {string} params.userMessage - 用户消息
 * @param {number} params.level - 关卡编号
 * @param {string} params.secretWord - 前端生成的密码（不再使用，后端管理密码）
 * @param {Array} params.history - 历史消息（不再使用，后端管理会话）
 */
export async function sendMessageToAI({ userMessage, level, secretWord, history = [] }) {
  const userPrompt = String(userMessage ?? '').trim()
  if (!userPrompt) return { text: '' }

  try {
    const response = await fetch(`${API_BASE_URL}/api/brain/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        level: level,
        message: userPrompt,
        session_id: sessionIds[level] || null,
      }),
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    
    // 保存会话 ID
    if (data.session_id) {
      sessionIds[level] = data.session_id
    }

    // 返回 AI 回复
    let text = data.message || ''
    
    // 如果被拦截，显示拦截消息
    if (data.blocked && data.block_reason) {
      text = data.message || '🙅 我不能告诉你这个信息。'
    }

    return { text, blocked: data.blocked, sessionId: data.session_id }
  } catch (error) {
    console.error('Chat API error:', error)
    throw error
  }
}

/**
 * 提交密码验证
 * @param {Object} params
 * @param {number} params.level - 关卡编号
 * @param {string} params.password - 用户提交的密码
 * @param {string} params.walletAddress - 钱包地址
 */
export async function submitPassword({ level, password, walletAddress }) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/judge/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        level: level,
        password: password,
        wallet_address: walletAddress || '0x0000000000000000000000000000000000000000',
      }),
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Submit password error:', error)
    throw error
  }
}

/**
 * 获取游戏状态
 */
export async function getGameStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/game/status`)
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Get game status error:', error)
    throw error
  }
}

/**
 * 清除会话
 * @param {number} level - 关卡编号
 */
export async function clearSession(level) {
  const sessionId = sessionIds[level]
  if (!sessionId) return

  try {
    await fetch(`${API_BASE_URL}/api/brain/session/${sessionId}`, {
      method: 'DELETE',
    })
    delete sessionIds[level]
  } catch (error) {
    console.error('Clear session error:', error)
  }
}

export async function sendChat({ message, level, secretWord }) {
  return sendMessageToAI({ userMessage: message, level, secretWord })
}

/**
 * 领取荣誉勋章
 * @param {Object} params
 * @param {string} params.walletAddress - 用户钱包地址
 * @param {Array<number>} params.completedLevels - 已完成的关卡列表
 */
export async function claimCertificate({ walletAddress, completedLevels }) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/certificate/claim`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wallet_address: walletAddress,
        completed_levels: completedLevels,
      }),
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Claim certificate error:', error)
    throw error
  }
}
