// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

/**
 * @title GandalfBreakerNFT
 * @notice NFT contract for Gandalf Game achievements
 * @dev Players mint NFTs by submitting signatures from the backend after solving levels
 */
contract GandalfBreakerNFT is ERC721Enumerable, Ownable {
    using ECDSA for bytes32;
    using Strings for uint256;

    // ============== Constants ==============
    uint256 public constant MAX_LEVEL = 7;
    
    // ============== State Variables ==============
    address public signer;
    uint256 private _tokenIdCounter;
    string public baseURI;
    
    // Mapping: user => level => completed
    mapping(address => mapping(uint256 => bool)) public completedLevels;
    
    // Mapping: tokenId => level
    mapping(uint256 => uint256) public tokenLevel;
    
    // Mapping: tokenId => completion timestamp
    mapping(uint256 => uint256) public tokenCompletedAt;
    
    // Used nonces to prevent replay attacks
    mapping(bytes32 => bool) public usedNonces;

    // ============== Events ==============
    event LevelCompleted(address indexed user, uint256 indexed level, uint256 tokenId);
    event SignerUpdated(address indexed oldSigner, address indexed newSigner);
    event BaseURIUpdated(string newBaseURI);

    // ============== Errors ==============
    error InvalidLevel();
    error AlreadyCompleted();
    error InvalidSignature();
    error SignatureExpired();
    error NonceAlreadyUsed();
    error ZeroAddress();

    // ============== Constructor ==============
    constructor(
        address _signer,
        string memory _baseURI
    ) ERC721("Seed Hunter", "SEED") Ownable(msg.sender) {
        if (_signer == address(0)) revert ZeroAddress();
        signer = _signer;
        baseURI = _baseURI;
    }

    // ============== External Functions ==============

    /**
     * @notice Mint NFT with backend signature
     * @param level The level completed (1-7)
     * @param signature Backend signature
     * @param nonce Unique nonce to prevent replay
     * @param deadline Signature expiration timestamp
     */
    function mintWithSignature(
        uint256 level,
        bytes calldata signature,
        bytes32 nonce,
        uint256 deadline
    ) external {
        // Validate level
        if (level == 0 || level > MAX_LEVEL) revert InvalidLevel();
        
        // Check if already completed
        if (completedLevels[msg.sender][level]) revert AlreadyCompleted();
        
        // Check deadline
        if (block.timestamp > deadline) revert SignatureExpired();
        
        // Check nonce
        if (usedNonces[nonce]) revert NonceAlreadyUsed();
        
        // Verify signature
        bytes32 messageHash = keccak256(abi.encodePacked(
            msg.sender,
            level,
            nonce,
            deadline,
            address(this)
        ));
        bytes32 ethSignedHash = MessageHashUtils.toEthSignedMessageHash(messageHash);
        address recoveredSigner = ECDSA.recover(ethSignedHash, signature);
        
        if (recoveredSigner != signer) revert InvalidSignature();
        
        // Mark nonce as used
        usedNonces[nonce] = true;
        
        // Mark level as completed
        completedLevels[msg.sender][level] = true;
        
        // Mint NFT
        uint256 tokenId = _tokenIdCounter++;
        tokenLevel[tokenId] = level;
        tokenCompletedAt[tokenId] = block.timestamp;
        
        _safeMint(msg.sender, tokenId);
        
        emit LevelCompleted(msg.sender, level, tokenId);
    }

    /**
     * @notice Check if user has completed a specific level
     */
    function hasCompletedLevel(address user, uint256 level) external view returns (bool) {
        return completedLevels[user][level];
    }

    /**
     * @notice Get all completed levels for a user
     */
    function getCompletedLevels(address user) external view returns (bool[] memory) {
        bool[] memory levels = new bool[](MAX_LEVEL);
        for (uint256 i = 1; i <= MAX_LEVEL; i++) {
            levels[i - 1] = completedLevels[user][i];
        }
        return levels;
    }

    /**
     * @notice Get tier name based on level
     */
    function getTier(uint256 level) public pure returns (string memory) {
        if (level <= 2) return "Bronze";
        if (level <= 4) return "Silver";
        if (level <= 6) return "Gold";
        return "Platinum";
    }

    /**
     * @notice Generate on-chain metadata
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        
        uint256 level = tokenLevel[tokenId];
        string memory tier = getTier(level);
        uint256 completedAt = tokenCompletedAt[tokenId];
        
        string memory json = string(abi.encodePacked(
            '{"name":"Seed Hunter - Level ', level.toString(), '",',
            '"description":"Achievement NFT for breaking Gandalf defenses at Level ', level.toString(), '",',
            '"attributes":[',
            '{"trait_type":"Level","value":', level.toString(), '},',
            '{"trait_type":"Tier","value":"', tier, '"},',
            '{"trait_type":"Completed At","display_type":"date","value":', completedAt.toString(), '}',
            '],',
            '"image":"', _generateSVG(level, tier), '"}'
        ));
        
        return string(abi.encodePacked(
            "data:application/json;base64,",
            Base64.encode(bytes(json))
        ));
    }

    // ============== Admin Functions ==============

    /**
     * @notice Update the signer address
     */
    function setSigner(address newSigner) external onlyOwner {
        if (newSigner == address(0)) revert ZeroAddress();
        address oldSigner = signer;
        signer = newSigner;
        emit SignerUpdated(oldSigner, newSigner);
    }

    /**
     * @notice Update base URI
     */
    function setBaseURI(string memory newBaseURI) external onlyOwner {
        baseURI = newBaseURI;
        emit BaseURIUpdated(newBaseURI);
    }

    // ============== Internal Functions ==============

    function _generateSVG(uint256 level, string memory tier) internal pure returns (string memory) {
        string memory color;
        if (keccak256(bytes(tier)) == keccak256(bytes("Bronze"))) {
            color = "#CD7F32";
        } else if (keccak256(bytes(tier)) == keccak256(bytes("Silver"))) {
            color = "#C0C0C0";
        } else if (keccak256(bytes(tier)) == keccak256(bytes("Gold"))) {
            color = "#FFD700";
        } else {
            color = "#E5E4E2";
        }
        
        string memory svg = string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">',
            '<rect width="400" height="400" fill="#1a1a2e"/>',
            '<circle cx="200" cy="150" r="80" fill="', color, '" opacity="0.8"/>',
            '<text x="200" y="160" font-size="48" fill="#fff" text-anchor="middle" font-family="Arial">&#129668;</text>',
            '<text x="200" y="280" font-size="24" fill="#fff" text-anchor="middle" font-family="Arial">Level ', level.toString(), '</text>',
            '<text x="200" y="320" font-size="18" fill="', color, '" text-anchor="middle" font-family="Arial">', tier, '</text>',
            '<text x="200" y="370" font-size="14" fill="#888" text-anchor="middle" font-family="Arial">Seed Hunter</text>',
            '</svg>'
        ));
        
        return string(abi.encodePacked(
            "data:image/svg+xml;base64,",
            Base64.encode(bytes(svg))
        ));
    }
}
