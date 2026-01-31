"""
The Brain - LLM 交互模块
负责与大模型交互
"""
import os
import re
import uuid
from typing import Dict, List, Optional, Tuple
from openai import AsyncOpenAI
from .config import config, LEVELS, LevelConfig
from .models import ChatResponse


class SimpleLLM:
    """简单的 LLM 封装，支持多种 provider"""
    
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
            # Default to OpenAI
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = config.LLM_MODEL or "gpt-4o-mini"
    
    async def aask(self, prompt: str, system_msg: str = None, history: List[Dict] = None) -> str:
        """异步调用 LLM"""
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024
        )
        return response.choices[0].message.content


class ConversationMemory:
    """简单的会话记忆管理"""
    
    def __init__(self):
        self._sessions: Dict[str, List[Dict]] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Tuple[str, List[Dict]]:
        if session_id and session_id in self._sessions:
            return session_id, self._sessions[session_id]
        new_id = session_id or str(uuid.uuid4())
        self._sessions[new_id] = []
        return new_id, self._sessions[new_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id in self._sessions:
            self._sessions[session_id].append({"role": role, "content": content})
    
    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


class TheBrain:
    """
    The Brain - LLM 交互核心模块
    
    功能:
    1. 管理每个关卡的 System Prompt
    2. 处理用户对话
    """
    
    def __init__(self):
        self.llm = SimpleLLM()
        self.memory = ConversationMemory()
    
    def get_level_config(self, level: int) -> LevelConfig:
        """获取关卡配置"""
        if level not in LEVELS:
            raise ValueError(f"Invalid level: {level}")
        return LEVELS[level]
    
    async def chat(self, level: int, message: str, session_id: Optional[str] = None) -> ChatResponse:
        """
        处理用户聊天请求
        
        流程:
        1. 发送给 LLM
        2. 返回响应
        """
        try:
            level_config = self.get_level_config(level)
        except ValueError as e:
            return ChatResponse(
                success=False,
                message=str(e),
                blocked=True,
                block_reason="Invalid level",
                session_id=session_id or ""
            )
        
        # 获取或创建会话
        session_id, history = self.memory.get_or_create_session(session_id)
        
        # Step 1: 构建消息并发送给 LLM
        messages = history.copy()
        messages.append({"role": "user", "content": message})
        
        try:
            ai_response = await self.llm.aask(
                message,
                system_msg=level_config.system_prompt,
                history=history
            )
        except Exception as e:
            return ChatResponse(
                success=False,
                message=f"LLM error: {str(e)}",
                blocked=False,
                session_id=session_id
            )
        
        # Step 2: 保存对话历史并返回
        self.memory.add_message(session_id, "user", message)
        self.memory.add_message(session_id, "assistant", ai_response)
        
        return ChatResponse(
            success=True,
            message=ai_response,
            blocked=False,
            session_id=session_id
        )
    
    def clear_session(self, session_id: str):
        """清除会话"""
        self.memory.clear_session(session_id)
