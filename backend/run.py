#!/usr/bin/env python3
"""
Gandalf Game - 启动脚本
"""
import uvicorn
from gandalf_game.config import config

if __name__ == "__main__":
    print("🧙 Starting Gandalf Game Server...")
    print(f"   Host: {config.HOST}")
    print(f"   Port: {config.PORT}")
    print(f"   Debug: {config.DEBUG}")
    print(f"   LLM: {config.LLM_PROVIDER}/{config.LLM_MODEL}")
    print()
    print("📚 API Docs: http://localhost:8000/docs")
    print("🎮 Frontend: http://localhost:8000/")
    print()
    
    uvicorn.run(
        "gandalf_game.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
