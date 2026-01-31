"""
Kite AI Data Contributor
负责将高质量的越狱 Prompt 数据提交到 Kite AI 网络
"""
import hashlib
import time
import json
import aiohttp
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from eth_account import Account
from eth_account.messages import encode_defunct


@dataclass
class JailbreakContribution:
    """越狱数据贡献结构"""
    wallet_address: str      # 贡献者钱包
    level: int               # 攻破的关卡
    prompt: str              # 越狱 Prompt
    response: str            # AI 的响应
    model: str               # 被攻破的模型
    timestamp: int           # 时间戳
    contribution_id: str     # 唯一贡献 ID
    signature: str           # 后端签名（防伪造）
    

class KiteContributor:
    """
    Kite AI 数据贡献者
    
    功能:
    1. 打包越狱数据
    2. 生成贡献签名
    3. 提交到 Kite AI 网络
    """
    
    # Kite AI 测试网 API (假设的端点，实际需要查阅 Kite AI 文档)
    KITE_API_BASE = "https://api-testnet.gokite.ai"
    
    def __init__(self, signer_private_key: Optional[str] = None):
        self._signer_key = signer_private_key
        self._contributions: list = []  # 本地存储贡献记录
        
    def _get_signer_account(self) -> Optional[Account]:
        """获取签名账户"""
        if not self._signer_key:
            return None
        pk = self._signer_key
        if not pk.startswith("0x"):
            pk = "0x" + pk
        return Account.from_key(pk)
    
    def _generate_contribution_id(
        self, 
        wallet: str, 
        level: int, 
        prompt: str, 
        timestamp: int
    ) -> str:
        """生成唯一的贡献 ID"""
        data = f"{wallet}:{level}:{prompt[:50]}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def _sign_contribution(self, contribution: JailbreakContribution) -> str:
        """对贡献数据签名"""
        account = self._get_signer_account()
        if not account:
            return ""
        
        # 创建签名消息
        message_data = {
            "id": contribution.contribution_id,
            "wallet": contribution.wallet_address,
            "level": contribution.level,
            "timestamp": contribution.timestamp,
        }
        message_str = json.dumps(message_data, sort_keys=True)
        signable = encode_defunct(text=message_str)
        signed = account.sign_message(signable)
        
        return signed.signature.hex()
    
    def package_contribution(
        self,
        wallet_address: str,
        level: int,
        prompt: str,
        response: str,
        model: str = "deepseek-chat"
    ) -> JailbreakContribution:
        """
        打包越狱数据为贡献结构
        
        只有 Level 6-7 的数据才有足够价值被记录
        """
        timestamp = int(time.time())
        contribution_id = self._generate_contribution_id(
            wallet_address, level, prompt, timestamp
        )
        
        contribution = JailbreakContribution(
            wallet_address=wallet_address.lower(),
            level=level,
            prompt=prompt,
            response=response,
            model=model,
            timestamp=timestamp,
            contribution_id=contribution_id,
            signature=""  # 先创建，后签名
        )
        
        # 签名
        contribution.signature = self._sign_contribution(contribution)
        
        # 本地记录
        self._contributions.append(contribution)
        
        return contribution
    
    async def submit_to_kite(
        self, 
        contribution: JailbreakContribution
    ) -> Dict[str, Any]:
        """
        提交贡献到 Kite AI 网络
        
        注意: 这是一个模拟实现，实际需要对接 Kite AI 的真实 API
        """
        # 准备提交数据
        payload = {
            "type": "ai_security_data",
            "category": "jailbreak_prompt",
            "data": {
                "contributor": contribution.wallet_address,
                "level": contribution.level,
                "prompt_hash": hashlib.sha256(contribution.prompt.encode()).hexdigest(),
                "model": contribution.model,
                "timestamp": contribution.timestamp,
                "signature": contribution.signature,
            },
            "metadata": {
                "source": "seedhunter_game",
                "version": "1.0",
                "contribution_id": contribution.contribution_id,
            }
        }
        
        # 尝试提交到 Kite AI
        # 注意: 实际 API 端点需要查阅 Kite AI 官方文档
        try:
            async with aiohttp.ClientSession() as session:
                # 这里使用模拟端点，实际需要替换为真实 API
                # async with session.post(
                #     f"{self.KITE_API_BASE}/v1/contributions",
                #     json=payload,
                #     headers={"Content-Type": "application/json"}
                # ) as resp:
                #     result = await resp.json()
                #     return result
                
                # 模拟返回
                return {
                    "success": True,
                    "contribution_id": contribution.contribution_id,
                    "status": "pending_verification",
                    "estimated_reward": self._estimate_reward(contribution.level),
                    "message": "Contribution submitted successfully. Pending PoAI verification."
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "contribution_id": contribution.contribution_id,
            }
    
    def _estimate_reward(self, level: int) -> Dict[str, Any]:
        """估算贡献奖励"""
        # 根据难度等级估算奖励
        base_reward = {
            6: {"kite_points": 10, "estimated_kite": "0.001"},
            7: {"kite_points": 50, "estimated_kite": "0.005"},
        }
        return base_reward.get(level, {"kite_points": 0, "estimated_kite": "0"})
    
    def get_contribution_stats(self, wallet_address: str) -> Dict[str, Any]:
        """获取钱包的贡献统计"""
        wallet = wallet_address.lower()
        contributions = [c for c in self._contributions if c.wallet_address == wallet]
        
        return {
            "total_contributions": len(contributions),
            "levels_contributed": list(set(c.level for c in contributions)),
            "total_estimated_points": sum(
                self._estimate_reward(c.level).get("kite_points", 0) 
                for c in contributions
            ),
        }
    
    def get_all_contributions(self) -> list:
        """获取所有贡献记录（用于调试）"""
        return [asdict(c) for c in self._contributions]
