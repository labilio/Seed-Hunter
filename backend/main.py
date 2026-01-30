"""
Gandalf Game - FastAPI 主应用
提供 RESTful API 接口
"""
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from .config import config, LEVELS
from .models import (
    ChatRequest, ChatResponse,
    SubmitPasswordRequest, SubmitPasswordResponse,
    NegotiateHintRequest, NegotiateHintResponse,
    VerifyHintPaymentRequest, HintResponse,
    LevelInfoResponse, GameStatusResponse
)
from .brain import TheBrain
from .judge import TheJudge
from .oracle import TheOracle


# ============== 全局服务实例 ==============
brain: Optional[TheBrain] = None
judge: Optional[TheJudge] = None
oracle: Optional[TheOracle] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global brain, judge, oracle
    # 启动时初始化服务
    brain = TheBrain()
    judge = TheJudge()
    oracle = TheOracle()
    print("🧙 Gandalf Game services initialized!")
    yield
    # 关闭时清理
    print("🧙 Gandalf Game shutting down...")


# ============== FastAPI 应用 ==============
app = FastAPI(
    title="Gandalf Game API",
    description="""
    🧙 **Gandalf Game** - A Web3 AI Password Challenge
    
    Combine Gandalf-style prompt injection challenges with Web3 mechanics:
    - Chat with AI guardians protecting secrets
    - Submit passwords to earn NFT mint signatures  
    - Negotiate hint prices with The Oracle
    - Pay on-chain to unlock hints
    
    ## Modules
    - **The Brain**: LLM interaction with multi-level defenses
    - **The Judge**: Password verification & NFT signature generation
    - **The Oracle**: Hint negotiation & payment verification
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", tags=["System"])
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "gandalf-game"}


# ============== Game Status ==============

@app.get("/api/game/status", response_model=GameStatusResponse, tags=["Game"])
async def get_game_status():
    """
    获取游戏状态
    
    返回所有关卡的基本信息（不含密码）
    """
    levels = []
    for level_num, level_config in LEVELS.items():
        difficulty = "Easy" if level_num <= 2 else "Medium" if level_num <= 5 else "Hard"
        levels.append(LevelInfoResponse(
            level=level_num,
            difficulty=difficulty,
            input_guard=level_config.input_guard,
            output_guard=level_config.output_guard,
            hint_count=len(level_config.hints),
            hint_base_price=level_config.hint_base_price,
            nft_tier=level_config.nft_metadata.get("tier", "Unknown")
        ))
    
    return GameStatusResponse(levels=levels, total_levels=len(LEVELS))


@app.get("/api/game/level/{level}", response_model=LevelInfoResponse, tags=["Game"])
async def get_level_info(level: int):
    """
    获取指定关卡信息
    
    - **level**: 关卡编号 (1-7)
    """
    if level not in LEVELS:
        raise HTTPException(status_code=404, detail=f"Level {level} not found")
    
    level_config = LEVELS[level]
    difficulty = "Easy" if level <= 2 else "Medium" if level <= 5 else "Hard"
    
    return LevelInfoResponse(
        level=level,
        difficulty=difficulty,
        input_guard=level_config.input_guard,
        output_guard=level_config.output_guard,
        hint_count=len(level_config.hints),
        hint_base_price=level_config.hint_base_price,
        nft_tier=level_config.nft_metadata.get("tier", "Unknown")
    )


# ============== The Brain - LLM 交互 ==============

@app.post("/api/brain/chat", response_model=ChatResponse, tags=["The Brain"])
async def chat_with_gandalf(request: ChatRequest):
    """
    与 Gandalf 对话
    
    这是游戏的核心接口。用户尝试通过各种提示词诱导 AI 泄露密码。
    
    - **level**: 关卡编号 (1-7)，每个关卡有不同的防护机制
    - **message**: 用户消息
    - **session_id**: 可选，用于保持对话上下文
    
    ## 防护机制
    | Level | Input Guard | Output Guard |
    |-------|-------------|--------------|
    | 1 | None | None |
    | 2 | None (system prompt only) | None |
    | 3 | None | Password detection |
    | 4 | LLM check | LLM check |
    | 5 | Blacklist | None |
    | 6 | LLM check | None |
    | 7 | LLM + Blacklist | LLM + Blacklist |
    """
    if brain is None:
        raise HTTPException(status_code=503, detail="Brain service not initialized")
    
    return await brain.chat(
        level=request.level,
        message=request.message,
        session_id=request.session_id
    )


@app.delete("/api/brain/session/{session_id}", tags=["The Brain"])
async def clear_session(session_id: str):
    """
    清除对话会话
    
    - **session_id**: 要清除的会话ID
    """
    if brain is None:
        raise HTTPException(status_code=503, detail="Brain service not initialized")
    
    brain.clear_session(session_id)
    return {"success": True, "message": f"Session {session_id} cleared"}


# ============== The Judge - 答案验证 ==============

@app.post("/api/judge/submit", response_model=SubmitPasswordResponse, tags=["The Judge"])
async def submit_password(request: SubmitPasswordRequest):
    """
    提交密码猜测
    
    当用户认为已经获得了密码时，通过此接口提交验证。
    
    - **level**: 关卡编号
    - **password**: 用户猜测的密码
    - **wallet_address**: 用户钱包地址，用于生成 NFT 铸造签名
    
    ## 成功响应
    如果密码正确，返回:
    - `correct`: true
    - `mint_signature`: 用于链上铸造 NFT 的签名数据
    - `nft_metadata`: NFT 元数据
    """
    if judge is None:
        raise HTTPException(status_code=503, detail="Judge service not initialized")
    
    return await judge.submit_password(
        level=request.level,
        password=request.password,
        wallet_address=request.wallet_address
    )


# ============== The Oracle - 提示服务 ==============

@app.get("/api/oracle/hints/{level}", tags=["The Oracle"])
async def get_hints_info(level: int):
    """
    获取关卡提示信息
    
    返回该关卡的提示数量和价格信息（不包含提示内容）
    
    - **level**: 关卡编号
    """
    if oracle is None:
        raise HTTPException(status_code=503, detail="Oracle service not initialized")
    
    return oracle.get_level_hints_info(level)


@app.post("/api/oracle/negotiate", response_model=NegotiateHintResponse, tags=["The Oracle"])
async def negotiate_hint_price(request: NegotiateHintRequest):
    """
    与 Oracle 讨价还价
    
    用户可以尝试以更低的价格购买提示。AI 会根据出价决定接受、还价或拒绝。
    
    - **level**: 关卡编号
    - **hint_index**: 提示索引 (0-based)
    - **offered_price**: 用户出价 (USDC)
    - **negotiation_message**: 可选，讨价还价的对话内容
    
    ## 响应
    - `accepted`: AI 是否接受出价
    - `counter_offer`: AI 的还价（如果不接受）
    - `final_price`: 最终成交价（如果接受）
    - `payment_address`: 支付地址（如果接受）
    """
    if oracle is None:
        raise HTTPException(status_code=503, detail="Oracle service not initialized")
    
    # 临时使用固定钱包地址，实际应从请求中获取
    wallet = "0x0000000000000000000000000000000000000000"
    
    return await oracle.negotiate_hint_price(
        level=request.level,
        hint_index=request.hint_index,
        offered_price=request.offered_price,
        wallet_address=wallet,
        message=request.negotiation_message
    )


@app.post("/api/oracle/verify-payment", response_model=HintResponse, tags=["The Oracle"])
async def verify_hint_payment(request: VerifyHintPaymentRequest):
    """
    验证提示支付并解锁提示
    
    用户完成链上支付后，调用此接口验证交易并获取提示。
    
    - **level**: 关卡编号
    - **hint_index**: 提示索引
    - **tx_hash**: 链上交易哈希
    - **wallet_address**: 支付者钱包地址
    
    ## 注意
    当前为 Demo 版本，简化了链上验证逻辑。
    生产环境需要实际查询区块链验证交易。
    """
    if oracle is None:
        raise HTTPException(status_code=503, detail="Oracle service not initialized")
    
    return await oracle.verify_payment_and_unlock(
        level=request.level,
        hint_index=request.hint_index,
        tx_hash=request.tx_hash,
        wallet_address=request.wallet_address
    )


@app.get("/api/oracle/hint", response_model=HintResponse, tags=["The Oracle"])
async def get_unlocked_hint(
    level: int = Query(..., ge=1, le=7),
    hint_index: int = Query(..., ge=0),
    wallet_address: str = Query(...)
):
    """
    获取已解锁的提示
    
    - **level**: 关卡编号
    - **hint_index**: 提示索引
    - **wallet_address**: 钱包地址
    """
    if oracle is None:
        raise HTTPException(status_code=503, detail="Oracle service not initialized")
    
    return oracle.get_hint_if_unlocked(level, hint_index, wallet_address)


# ============== 静态文件服务 (前端) ==============

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")


@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_frontend():
    """服务前端页面"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>Gandalf Game API</h1><p>Visit /docs for API documentation</p>")


# 挂载静态文件目录
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ============== 运行入口 ==============

def run_server():
    """运行服务器"""
    import uvicorn
    uvicorn.run(
        "gandalf_game.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )


if __name__ == "__main__":
    run_server()
