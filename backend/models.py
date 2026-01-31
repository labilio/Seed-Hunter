"""
# Seed Hunter Game Models - API 请求/响应数据模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============== Enums ==============

class GuardResult(str, Enum):
    PASSED = "passed"
    BLOCKED = "blocked"


# ============== Request Models ==============

class ChatRequest(BaseModel):
    """聊天请求 - The Brain 模块"""
    level: int = Field(..., ge=1, le=7, description="关卡编号 (1-7)")
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，用于保持对话上下文")


class SubmitPasswordRequest(BaseModel):
    """提交密码请求 - The Judge 模块"""
    level: int = Field(..., ge=1, le=7, description="关卡编号 (1-7)")
    password: str = Field(..., min_length=1, max_length=100, description="用户提交的密码猜测")
    wallet_address: str = Field(..., description="用户钱包地址，用于 NFT 铸造")


class NegotiateHintRequest(BaseModel):
    """讨价还价请求 - The Oracle 模块"""
    level: int = Field(..., ge=1, le=7, description="关卡编号 (1-7)")
    hint_index: int = Field(..., ge=0, description="提示索引 (0-based)")
    offered_price: float = Field(..., gt=0, description="用户出价 (USDC)")
    negotiation_message: Optional[str] = Field(None, description="讨价还价的对话内容")


class VerifyHintPaymentRequest(BaseModel):
    """验证提示支付请求 - The Oracle 模块"""
    level: int = Field(..., ge=1, le=7, description="关卡编号")
    hint_index: int = Field(..., ge=0, description="提示索引")
    tx_hash: str = Field(..., description="链上交易哈希")
    wallet_address: str = Field(..., description="支付者钱包地址")


# ============== Response Models ==============

class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    message: str = Field(..., description="AI 回复内容")
    blocked: bool = Field(False, description="是否被防护系统拦截")
    block_reason: Optional[str] = Field(None, description="拦截原因")
    session_id: str = Field(..., description="会话ID")


class SubmitPasswordResponse(BaseModel):
    """提交密码响应"""
    success: bool
    correct: bool = Field(..., description="密码是否正确")
    message: str
    mint_signature: Optional[str] = Field(None, description="NFT 铸造签名 (仅正确时返回)")
    nft_metadata: Optional[Dict[str, Any]] = Field(None, description="NFT 元数据")
    kite_contribution: Optional[Dict[str, Any]] = Field(None, description="Kite AI 数据贡献信息 (Level 6-7)")


class LevelInfoResponse(BaseModel):
    """关卡信息响应"""
    level: int
    difficulty: str
    input_guard: str
    output_guard: str
    hint_count: int
    hint_base_price: float
    nft_tier: str


class NegotiateHintResponse(BaseModel):
    """讨价还价响应"""
    success: bool
    accepted: bool = Field(..., description="AI 是否接受出价")
    counter_offer: Optional[float] = Field(None, description="AI 的还价")
    final_price: Optional[float] = Field(None, description="最终成交价格 (仅接受时)")
    ai_message: str = Field(..., description="AI 的讨价还价回复")
    payment_address: Optional[str] = Field(None, description="支付地址 (仅接受时)")


class HintResponse(BaseModel):
    """获取提示响应"""
    success: bool
    hint: Optional[str] = Field(None, description="提示内容")
    hint_index: int
    remaining_hints: int
    message: str


class GameStatusResponse(BaseModel):
    """游戏状态响应"""
    levels: List[LevelInfoResponse]
    total_levels: int = 7


# ============== Event Models (用于链上事件) ==============

class HintPaidEvent(BaseModel):
    """链上 HintPaid 事件"""
    payer: str
    level: int
    hint_index: int
    amount: int  # wei
    tx_hash: str
    block_number: int


# ============== Certificate Models (荣誉勋章) ==============

class ClaimCertificateRequest(BaseModel):
    """领取荣誉勋章请求"""
    wallet_address: str = Field(..., description="用户钱包地址")
    completed_levels: List[int] = Field(..., description="已完成的关卡列表")


class ClaimCertificateResponse(BaseModel):
    """领取荣誉勋章响应"""
    success: bool
    eligible: bool = Field(..., description="是否有资格领取勋章")
    message: str
    mint_signature: Optional[str] = Field(None, description="NFT 铸造签名")
    certificate_metadata: Optional[Dict[str, Any]] = Field(None, description="勋章元数据")
