"""
The Judge - 答案验证与签名服务
负责验证密码、生成 NFT 铸造签名
"""
import hashlib
import os
import time
import json
from typing import Optional, Dict, Any
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from config import config, LEVELS
from models import SubmitPasswordResponse
from kite_contributor import KiteContributor, JailbreakContribution


class TheJudge:
    """
    The Judge - 答案验证与 NFT 签名服务
    
    功能:
    1. 验证用户提交的密码
    2. 生成 NFT 铸造签名 (与智能合约兼容)
    3. 防止重放攻击
    """
    
    def __init__(self):
        self._used_nonces: set = set()  # 防止重放攻击
        self._kite_contributor = KiteContributor(config.SIGNER_PRIVATE_KEY)
        self._attack_history: Dict[str, Dict] = {}  # 存储攻击历史 {session_id: {prompt, response}}
        
    def _get_signer_account(self) -> Optional[Account]:
        """获取签名账户"""
        if not config.SIGNER_PRIVATE_KEY:
            return None
        pk = config.SIGNER_PRIVATE_KEY
        if not pk.startswith("0x"):
            pk = "0x" + pk
        return Account.from_key(pk)
    
    def record_attack(self, wallet_address: str, prompt: str, response: str):
        """
        记录攻击历史，用于后续提交到 Kite AI
        由 TheBrain 在每次对话后调用
        """
        self._attack_history[wallet_address.lower()] = {
            "prompt": prompt,
            "response": response,
            "timestamp": int(time.time())
        }
    
    def get_contribution_stats(self, wallet_address: str) -> Dict[str, Any]:
        """获取钱包的 Kite AI 贡献统计"""
        return self._kite_contributor.get_contribution_stats(wallet_address)
    
    def verify_password(self, level: int, submitted_password: str) -> bool:
        """验证密码是否正确"""
        # 万能密码检查
        if submitted_password.strip().upper() == "SPARK":
            return True

        if level not in LEVELS:
            return False
        correct_password = LEVELS[level].password
        # 不区分大小写比较
        return submitted_password.strip().upper() == correct_password.upper()
    
    def generate_mint_signature(
        self,
        level: int,
        wallet_address: str,
    ) -> Optional[Dict[str, Any]]:
        """
        生成 NFT 铸造签名 (与智能合约 SeedHunterNFT 兼容)
        
        智能合约验证格式:
        keccak256(abi.encodePacked(userAddress, level, nonce, deadline, contractAddress))
        
        返回:
        - signature: 签名 (hex)
        - nonce: bytes32 nonce
        - deadline: 过期时间戳
        - contract_address: NFT 合约地址
        - signer: 签名者地址
        """
        account = self._get_signer_account()
        if not account:
            print(f"❌ No signer account configured - SIGNER_PRIVATE_KEY is missing")
            return None
        
        print(f"🔐 Generating mint signature for level {level}, wallet {wallet_address[:10]}...")
        
        # 生成 nonce (bytes32)
        timestamp = int(time.time())
        nonce_raw = hashlib.sha256(
            f"{wallet_address}:{level}:{timestamp}:{os.urandom(8).hex()}".encode()
        ).digest()
        nonce_hex = "0x" + nonce_raw.hex()
        
        # 防止重放 (内存中)
        if nonce_hex in self._used_nonces:
            print(f"⚠️  Nonce already used: {nonce_hex}")
            return None
        self._used_nonces.add(nonce_hex)
        
        # 过期时间 (1小时后)
        deadline = timestamp + 3600
        
        # NFT 合约地址
        contract_address = config.NFT_CONTRACT_ADDRESS or "0x0000000000000000000000000000000000000000"
        
        print(f"  Contract: {contract_address}")
        print(f"  Signer: {account.address}")
        
        # 构建与智能合约兼容的消息哈希
        # Solidity: keccak256(abi.encodePacked(userAddress, level, nonce, deadline, contractAddress))
        message_hash = Web3.solidity_keccak(
            ['address', 'uint256', 'bytes32', 'uint256', 'address'],
            [
                Web3.to_checksum_address(wallet_address),
                level,
                nonce_raw,
                deadline,
                Web3.to_checksum_address(contract_address)
            ]
        )
        
        # 使用 eth_account 签名 (EIP-191 personal_sign)
        signable_message = encode_defunct(message_hash)
        signed = account.sign_message(signable_message)
        
        result = {
            "signature": signed.signature.hex(),
            "nonce": nonce_hex,
            "deadline": deadline,
            "contract_address": contract_address,
            "signer": account.address,
            "level": level,
            "wallet": wallet_address
        }
        
        print(f"✅ Signature generated successfully")
        print(f"  Signature: {result['signature'][:20]}...")
        print(f"  Nonce: {result['nonce']}")
        print(f"  Deadline: {result['deadline']}")
        
        return result
    
    async def submit_password(
        self,
        level: int,
        password: str,
        wallet_address: str
    ) -> SubmitPasswordResponse:
        """
        提交密码验证
        
        流程:
        1. 验证关卡有效性
        2. 验证密码
        3. 如果正确，生成 NFT 铸造签名
        """
        print(f"\n📝 Submit password request received:")
        print(f"  Level: {level}")
        print(f"  Wallet: {wallet_address[:10]}...")
        print(f"  Password: {password[:3]}...")
        
        # 验证关卡
        if level not in LEVELS:
            print(f"❌ Invalid level: {level}")
            return SubmitPasswordResponse(
                success=False,
                correct=False,
                message=f"Invalid level: {level}"
            )
        
        # 验证密码
        is_correct = self.verify_password(level, password)
        
        if not is_correct:
            print(f"❌ Incorrect password")
            return SubmitPasswordResponse(
                success=True,
                correct=False,
                message="❌ Incorrect password. Try again!"
            )
        
        print(f"✅ Password correct!")
        
        # 密码正确，生成签名
        level_config = LEVELS[level]
        signature_data = self.generate_mint_signature(level, wallet_address)
        
        if not signature_data:
            print(f"⚠️  Signature generation failed")
            return SubmitPasswordResponse(
                success=True,
                correct=True,
                message="✅ Correct! But signature service is not configured. Contact admin.",
                nft_metadata=level_config.nft_metadata
            )
        
        # 对于高难度关卡 (Level 6-7)，提交数据到 Kite AI
        kite_contribution = None
        if level >= 6:
            # 获取攻击历史
            attack_data = self._attack_history.get(wallet_address, {})
            if attack_data.get("prompt"):
                contribution = self._kite_contributor.package_contribution(
                    wallet_address=wallet_address,
                    level=level,
                    prompt=attack_data.get("prompt", ""),
                    response=attack_data.get("response", ""),
                    model=config.LLM_MODEL
                )
                # 异步提交到 Kite AI
                kite_result = await self._kite_contributor.submit_to_kite(contribution)
                kite_contribution = {
                    "contribution_id": contribution.contribution_id,
                    "status": kite_result.get("status", "submitted"),
                    "estimated_reward": kite_result.get("estimated_reward", {}),
                }
        
        response = SubmitPasswordResponse(
            success=True,
            correct=True,
            message=f"🎉 Congratulations! You've beaten Level {level}! Use the signature to mint your NFT.",
            mint_signature=json.dumps(signature_data),
            nft_metadata=level_config.nft_metadata,
            kite_contribution=kite_contribution
        )
        
        print(f"📤 Response prepared:")
        print(f"  - mint_signature: {'✓ Included' if response.mint_signature else '✗ Missing'}")
        print(f"  - nft_metadata: {response.nft_metadata}")
        
        return response

    def generate_certificate_signature(
        self,
        wallet_address: str,
        completed_levels: list
    ) -> Optional[Dict[str, Any]]:
        """
        生成荣誉勋章铸造签名
        
        需要完成所有 7 个关卡才能领取
        
        参数:
        - wallet_address: 用户钱包地址
        - completed_levels: 已完成关卡列表
        
        返回:
        - signature: 签名 (hex)
        - nonce: bytes32 nonce
        - deadline: 过期时间戳
        - contract_address: NFT 合约地址
        - signer: 签名者地址
        - certificate_type: 勋章类型
        """
        account = self._get_signer_account()
        if not account:
            print(f"❌ No signer account configured - SIGNER_PRIVATE_KEY is missing")
            return None
        
        print(f"🏆 Generating certificate signature for wallet {wallet_address[:10]}...")
        print(f"   Completed levels: {completed_levels}")
        
        # 生成 nonce (bytes32)
        timestamp = int(time.time())
        nonce_raw = hashlib.sha256(
            f"{wallet_address}:certificate:{timestamp}:{os.urandom(8).hex()}".encode()
        ).digest()
        nonce_hex = "0x" + nonce_raw.hex()
        
        # 防止重放
        if nonce_hex in self._used_nonces:
            print(f"⚠️  Nonce already used: {nonce_hex}")
            return None
        self._used_nonces.add(nonce_hex)
        
        # 过期时间 (1小时后)
        deadline = timestamp + 3600
        
        # NFT 合约地址
        contract_address = config.NFT_CONTRACT_ADDRESS or "0x0000000000000000000000000000000000000000"
        
        # 勋章等级 (特殊等级 8 表示荣誉勋章)
        certificate_level = 8
        
        # 构建与智能合约兼容的消息哈希
        message_hash = Web3.solidity_keccak(
            ['address', 'uint256', 'bytes32', 'uint256', 'address'],
            [
                Web3.to_checksum_address(wallet_address),
                certificate_level,
                nonce_raw,
                deadline,
                Web3.to_checksum_address(contract_address)
            ]
        )
        
        # 使用 eth_account 签名 (EIP-191 personal_sign)
        signable_message = encode_defunct(message_hash)
        signed = account.sign_message(signable_message)
        
        result = {
            "signature": signed.signature.hex(),
            "nonce": nonce_hex,
            "deadline": deadline,
            "contract_address": contract_address,
            "signer": account.address,
            "level": certificate_level,
            "wallet": wallet_address,
            "certificate_type": "honor_badge"
        }
        
        print(f"✅ Certificate signature generated successfully")
        print(f"  Signature: {result['signature'][:20]}...")
        print(f"  Nonce: {result['nonce']}")
        
        return result
