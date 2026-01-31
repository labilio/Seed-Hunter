"""
The Oracle - 提示监听与讨价还价模块
负责监听链上支付事件、发放提示、与用户讨价还价
"""
import asyncio
import json
import os
from typing import Dict, Optional, List, Any
from openai import AsyncOpenAI
from config import config, LEVELS
from models import (
    NegotiateHintResponse,
    HintResponse,
    HintPaidEvent
)


class SimpleLLM:
    """简单的 LLM 封装"""
    
    def __init__(self):
        provider = config.LLM_PROVIDER.lower()
        
        if provider == "deepseek":
            self.client = AsyncOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            self.model = config.LLM_MODEL or "deepseek-chat"
        elif provider == "openrouter":
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = config.LLM_MODEL or "openai/gpt-4o-mini"
        else:
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = config.LLM_MODEL or "gpt-4o-mini"
    
    async def aask(self, prompt: str, system_msg: str = None) -> str:
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=512
        )
        return response.choices[0].message.content


class NegotiationSession:
    """讨价还价会话"""
    def __init__(self, level: int, hint_index: int, base_price: float):
        self.level = level
        self.hint_index = hint_index
        self.base_price = base_price
        self.min_price = base_price * (1 - config.MAX_HINT_DISCOUNT)
        self.current_offer: Optional[float] = None
        self.rounds: int = 0
        self.accepted: bool = False
        self.final_price: Optional[float] = None


class TheOracle:
    """
    The Oracle - 提示服务与讨价还价模块
    
    功能:
    1. 管理提示的解锁状态
    2. 与用户进行讨价还价
    3. 监听链上支付事件
    4. 验证支付后发放提示
    """
    
    def __init__(self):
        self.llm = SimpleLLM()
        # 已解锁的提示: {(level, hint_index, wallet_address): True}
        self._unlocked_hints: Dict[tuple, bool] = {}
        # 进行中的讨价还价: {session_key: NegotiationSession}
        self._negotiations: Dict[str, NegotiationSession] = {}
        # 待验证的支付: {tx_hash: HintPaidEvent}
        self._pending_payments: Dict[str, Dict] = {}
    
    def _get_negotiation_key(self, level: int, hint_index: int, wallet: str) -> str:
        return f"{level}:{hint_index}:{wallet.lower()}"
    
    def get_hint_price(self, level: int, hint_index: int) -> float:
        """获取提示的基础价格"""
        if level not in LEVELS:
            return 0.0
        level_config = LEVELS[level]
        # 后面的提示更贵
        return level_config.hint_base_price * (1 + hint_index * 0.5)
    
    def get_hint_count(self, level: int) -> int:
        """获取关卡的提示数量"""
        if level not in LEVELS:
            return 0
        return len(LEVELS[level].hints)
    
    async def negotiate_hint_price(
        self,
        level: int,
        hint_index: int,
        offered_price: float,
        wallet_address: str,
        message: Optional[str] = None
    ) -> NegotiateHintResponse:
        """
        与用户讨价还价
        
        AI 会根据出价和对话内容决定是否接受
        """
        if level not in LEVELS:
            return NegotiateHintResponse(
                success=False,
                accepted=False,
                ai_message="Invalid level."
            )
        
        level_config = LEVELS[level]
        if hint_index >= len(level_config.hints):
            return NegotiateHintResponse(
                success=False,
                accepted=False,
                ai_message="Invalid hint index."
            )
        
        base_price = self.get_hint_price(level, hint_index)
        min_price = max(base_price * (1 - config.MAX_HINT_DISCOUNT), config.MIN_HINT_PRICE)
        
        # 获取或创建讨价还价会话
        session_key = self._get_negotiation_key(level, hint_index, wallet_address)
        if session_key not in self._negotiations:
            self._negotiations[session_key] = NegotiationSession(
                level=level,
                hint_index=hint_index,
                base_price=base_price
            )
        
        session = self._negotiations[session_key]
        session.rounds += 1
        session.current_offer = offered_price
        
        # 如果出价高于或等于基础价格，直接接受
        if offered_price >= base_price:
            session.accepted = True
            session.final_price = offered_price
            return NegotiateHintResponse(
                success=True,
                accepted=True,
                final_price=offered_price,
                ai_message=f"Deal! Pay {offered_price} USDC to unlock the hint.",
                payment_address=config.HINT_CONTRACT_ADDRESS or "0x_CONTRACT_ADDRESS_HERE"
            )
        
        # 如果出价低于最低价，拒绝
        if offered_price < min_price:
            counter = round(min_price + (base_price - min_price) * 0.3, 4)
            return NegotiateHintResponse(
                success=True,
                accepted=False,
                counter_offer=counter,
                ai_message=f"That's too low! I can't go below {min_price} USDC. How about {counter} USDC?"
            )
        
        # 中间价格，用 LLM 决定
        negotiation_prompt = f"""You are a shrewd merchant selling hints for a puzzle game.

Base price: {base_price} USDC
Minimum acceptable: {min_price} USDC
Customer's offer: {offered_price} USDC
Negotiation round: {session.rounds}
Customer's message: "{message or 'No message'}"

Decide whether to:
1. ACCEPT the offer (if it's reasonable or customer is persuasive)
2. COUNTER with a lower price (between their offer and base price)
3. REJECT and insist on a higher price

Respond in JSON format:
{{"decision": "ACCEPT/COUNTER/REJECT", "price": <number or null>, "message": "<your response to customer>"}}

Be playful and in-character as a mysterious oracle. Maximum 2 sentences."""

        try:
            response = await self.llm.aask(negotiation_prompt)
            # 解析 JSON 响应
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                decision = result.get("decision", "REJECT").upper()
                price = result.get("price")
                ai_msg = result.get("message", "Let me think about it...")
                
                if decision == "ACCEPT":
                    session.accepted = True
                    session.final_price = offered_price
                    return NegotiateHintResponse(
                        success=True,
                        accepted=True,
                        final_price=offered_price,
                        ai_message=ai_msg,
                        payment_address=config.HINT_CONTRACT_ADDRESS or "0x_CONTRACT_ADDRESS_HERE"
                    )
                elif decision == "COUNTER" and price:
                    return NegotiateHintResponse(
                        success=True,
                        accepted=False,
                        counter_offer=float(price),
                        ai_message=ai_msg
                    )
                else:
                    return NegotiateHintResponse(
                        success=True,
                        accepted=False,
                        counter_offer=base_price,
                        ai_message=ai_msg
                    )
        except Exception as e:
            # LLM 解析失败，使用简单逻辑
            pass
        
        # 默认还价
        counter = round((offered_price + base_price) / 2, 4)
        return NegotiateHintResponse(
            success=True,
            accepted=False,
            counter_offer=counter,
            ai_message=f"Hmm, how about we meet in the middle at {counter} USDC?"
        )
    
    async def verify_payment_and_unlock(
        self,
        level: int,
        hint_index: int,
        tx_hash: str,
        wallet_address: str
    ) -> HintResponse:
        """
        验证链上支付并解锁提示
        
        注意: 实际生产环境需要真正验证链上交易
        这里简化处理，模拟验证成功
        """
        if level not in LEVELS:
            return HintResponse(
                success=False,
                hint_index=hint_index,
                remaining_hints=0,
                message="Invalid level."
            )
        
        level_config = LEVELS[level]
        if hint_index >= len(level_config.hints):
            return HintResponse(
                success=False,
                hint_index=hint_index,
                remaining_hints=0,
                message="Invalid hint index."
            )
        
        # TODO: 实际验证链上交易
        # 这里模拟验证成功
        # 实际应该:
        # 1. 查询链上交易
        # 2. 验证交易目标是 HINT_CONTRACT_ADDRESS
        # 3. 验证交易金额
        # 4. 验证交易发送者是 wallet_address
        
        # 标记提示为已解锁
        unlock_key = (level, hint_index, wallet_address.lower())
        self._unlocked_hints[unlock_key] = True
        
        hint_text = level_config.hints[hint_index]
        remaining = len(level_config.hints) - hint_index - 1
        
        return HintResponse(
            success=True,
            hint=hint_text,
            hint_index=hint_index,
            remaining_hints=remaining,
            message="Payment verified! Here's your hint."
        )
    
    def get_hint_if_unlocked(
        self,
        level: int,
        hint_index: int,
        wallet_address: str
    ) -> HintResponse:
        """获取已解锁的提示"""
        unlock_key = (level, hint_index, wallet_address.lower())
        
        if level not in LEVELS:
            return HintResponse(
                success=False,
                hint_index=hint_index,
                remaining_hints=0,
                message="Invalid level."
            )
        
        level_config = LEVELS[level]
        
        if unlock_key not in self._unlocked_hints:
            return HintResponse(
                success=False,
                hint_index=hint_index,
                remaining_hints=len(level_config.hints) - hint_index,
                message="Hint not unlocked. Please pay first."
            )
        
        hint_text = level_config.hints[hint_index]
        remaining = len(level_config.hints) - hint_index - 1
        
        return HintResponse(
            success=True,
            hint=hint_text,
            hint_index=hint_index,
            remaining_hints=remaining,
            message="Here's your hint."
        )
    
    def get_level_hints_info(self, level: int) -> Dict[str, Any]:
        """获取关卡的提示信息"""
        if level not in LEVELS:
            return {"error": "Invalid level"}
        
        level_config = LEVELS[level]
        hints_info = []
        for i in range(len(level_config.hints)):
            hints_info.append({
                "index": i,
                "price": self.get_hint_price(level, i),
                "negotiable": True
            })
        
        return {
            "level": level,
            "total_hints": len(level_config.hints),
            "hints": hints_info
        }
