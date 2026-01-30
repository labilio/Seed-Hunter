// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title HintPayment
 * @notice Contract for paying USDC to unlock hints in Gandalf Game
 * @dev Supports fixed prices and negotiated prices via backend signature
 */
contract HintPayment is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // ============== Constants ==============
    uint256 public constant MAX_LEVEL = 7;
    uint256 public constant MAX_HINTS_PER_LEVEL = 3;
    uint256 public constant USDC_DECIMALS = 6;

    // ============== State Variables ==============
    IERC20 public immutable paymentToken; // USDC
    address public treasury;
    address public priceSigner; // Backend signer for negotiated prices
    
    // Base prices per level (in USDC with 6 decimals)
    // e.g., 1000 = 0.001 USDC
    mapping(uint256 => uint256[3]) public hintPrices;
    
    // User purchases: user => level => hint_index => purchased
    mapping(address => mapping(uint256 => mapping(uint256 => bool))) public purchases;
    
    // Used signatures (to prevent replay)
    mapping(bytes32 => bool) public usedSignatures;
    
    // Total collected fees
    uint256 public totalCollected;

    // ============== Events ==============
    event HintPurchased(
        address indexed buyer,
        uint256 indexed level,
        uint256 indexed hintIndex,
        uint256 amount
    );
    event HintPriceUpdated(uint256 level, uint256[3] prices);
    event TreasuryUpdated(address oldTreasury, address newTreasury);
    event PriceSignerUpdated(address oldSigner, address newSigner);
    event Withdrawn(address indexed to, uint256 amount);

    // ============== Errors ==============
    error InvalidLevel();
    error InvalidHintIndex();
    error AlreadyPurchased();
    error InvalidAmount();
    error InvalidSignature();
    error SignatureExpired();
    error SignatureAlreadyUsed();
    error ZeroAddress();
    error InsufficientBalance();

    // ============== Constructor ==============
    constructor(
        address _paymentToken,
        address _treasury,
        address _priceSigner
    ) Ownable(msg.sender) {
        if (_paymentToken == address(0)) revert ZeroAddress();
        if (_treasury == address(0)) revert ZeroAddress();
        if (_priceSigner == address(0)) revert ZeroAddress();
        
        paymentToken = IERC20(_paymentToken);
        treasury = _treasury;
        priceSigner = _priceSigner;
        
        // Initialize default prices (in micro-USDC, 6 decimals)
        // Level 1: 0.001, 0.0015, 0.002 USDC
        hintPrices[1] = [uint256(1000), 1500, 2000];
        // Level 2
        hintPrices[2] = [uint256(2000), 3000, 4000];
        // Level 3
        hintPrices[3] = [uint256(5000), 7500, 10000];
        // Level 4
        hintPrices[4] = [uint256(10000), 15000, 20000];
        // Level 5
        hintPrices[5] = [uint256(15000), 22500, 30000];
        // Level 6
        hintPrices[6] = [uint256(20000), 30000, 40000];
        // Level 7
        hintPrices[7] = [uint256(30000), 45000, 60000];
    }

    // ============== External Functions ==============

    /**
     * @notice Pay for a hint at the fixed price
     * @param level Level number (1-7)
     * @param hintIndex Hint index (0-2)
     */
    function payForHint(uint256 level, uint256 hintIndex) external nonReentrant {
        _validatePurchase(level, hintIndex);
        
        uint256 price = hintPrices[level][hintIndex];
        if (price == 0) revert InvalidAmount();
        
        _processPurchase(msg.sender, level, hintIndex, price);
    }

    /**
     * @notice Pay for a hint with a negotiated price (signed by backend)
     * @param level Level number (1-7)
     * @param hintIndex Hint index (0-2)
     * @param negotiatedPrice The negotiated price
     * @param deadline Signature expiration
     * @param signature Backend signature
     */
    function payForHintWithNegotiatedPrice(
        uint256 level,
        uint256 hintIndex,
        uint256 negotiatedPrice,
        uint256 deadline,
        bytes calldata signature
    ) external nonReentrant {
        _validatePurchase(level, hintIndex);
        
        // Check deadline
        if (block.timestamp > deadline) revert SignatureExpired();
        
        // Build message hash
        bytes32 messageHash = keccak256(abi.encodePacked(
            msg.sender,
            level,
            hintIndex,
            negotiatedPrice,
            deadline,
            address(this)
        ));
        
        // Check if signature was used
        if (usedSignatures[messageHash]) revert SignatureAlreadyUsed();
        
        // Verify signature
        bytes32 ethSignedHash = _toEthSignedMessageHash(messageHash);
        address recoveredSigner = _recover(ethSignedHash, signature);
        
        if (recoveredSigner != priceSigner) revert InvalidSignature();
        
        // Mark signature as used
        usedSignatures[messageHash] = true;
        
        _processPurchase(msg.sender, level, hintIndex, negotiatedPrice);
    }

    /**
     * @notice Check if user has purchased a hint
     */
    function hasPurchasedHint(
        address user,
        uint256 level,
        uint256 hintIndex
    ) external view returns (bool) {
        return purchases[user][level][hintIndex];
    }

    /**
     * @notice Get hint price for a level
     */
    function getHintPrice(uint256 level, uint256 hintIndex) external view returns (uint256) {
        if (level == 0 || level > MAX_LEVEL) revert InvalidLevel();
        if (hintIndex >= MAX_HINTS_PER_LEVEL) revert InvalidHintIndex();
        return hintPrices[level][hintIndex];
    }

    /**
     * @notice Get all hint prices for a level
     */
    function getLevelPrices(uint256 level) external view returns (uint256[3] memory) {
        if (level == 0 || level > MAX_LEVEL) revert InvalidLevel();
        return hintPrices[level];
    }

    /**
     * @notice Get user's purchase status for a level
     */
    function getUserPurchases(address user, uint256 level) external view returns (bool[3] memory) {
        bool[3] memory result;
        for (uint256 i = 0; i < MAX_HINTS_PER_LEVEL; i++) {
            result[i] = purchases[user][level][i];
        }
        return result;
    }

    // ============== Admin Functions ==============

    /**
     * @notice Update hint prices for a level
     */
    function setHintPrices(uint256 level, uint256[3] calldata prices) external onlyOwner {
        if (level == 0 || level > MAX_LEVEL) revert InvalidLevel();
        hintPrices[level] = prices;
        emit HintPriceUpdated(level, prices);
    }

    /**
     * @notice Update treasury address
     */
    function setTreasury(address newTreasury) external onlyOwner {
        if (newTreasury == address(0)) revert ZeroAddress();
        address oldTreasury = treasury;
        treasury = newTreasury;
        emit TreasuryUpdated(oldTreasury, newTreasury);
    }

    /**
     * @notice Update price signer
     */
    function setPriceSigner(address newSigner) external onlyOwner {
        if (newSigner == address(0)) revert ZeroAddress();
        address oldSigner = priceSigner;
        priceSigner = newSigner;
        emit PriceSignerUpdated(oldSigner, newSigner);
    }

    /**
     * @notice Withdraw collected fees to treasury
     */
    function withdraw() external onlyOwner nonReentrant {
        uint256 balance = paymentToken.balanceOf(address(this));
        if (balance == 0) revert InsufficientBalance();
        
        paymentToken.safeTransfer(treasury, balance);
        emit Withdrawn(treasury, balance);
    }

    // ============== Internal Functions ==============

    function _validatePurchase(uint256 level, uint256 hintIndex) internal view {
        if (level == 0 || level > MAX_LEVEL) revert InvalidLevel();
        if (hintIndex >= MAX_HINTS_PER_LEVEL) revert InvalidHintIndex();
        if (purchases[msg.sender][level][hintIndex]) revert AlreadyPurchased();
    }

    function _processPurchase(
        address buyer,
        uint256 level,
        uint256 hintIndex,
        uint256 amount
    ) internal {
        // Transfer payment
        paymentToken.safeTransferFrom(buyer, address(this), amount);
        
        // Record purchase
        purchases[buyer][level][hintIndex] = true;
        totalCollected += amount;
        
        emit HintPurchased(buyer, level, hintIndex, amount);
    }

    function _toEthSignedMessageHash(bytes32 hash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    }

    function _recover(bytes32 hash, bytes memory signature) internal pure returns (address) {
        if (signature.length != 65) return address(0);
        
        bytes32 r;
        bytes32 s;
        uint8 v;
        
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        
        if (v < 27) v += 27;
        if (v != 27 && v != 28) return address(0);
        
        return ecrecover(hash, v, r, s);
    }
}
