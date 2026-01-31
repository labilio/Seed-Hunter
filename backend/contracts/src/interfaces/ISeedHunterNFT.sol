// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ISeedHunterNFT
 * @notice Interface for SeedHunterNFT contract
 */
interface ISeedHunterNFT {
    /// @notice Mint NFT with backend signature
    function mintWithSignature(
        uint256 level,
        bytes calldata signature,
        bytes32 nonce,
        uint256 deadline
    ) external;
    
    /// @notice Check if user has completed a level
    function hasCompletedLevel(address user, uint256 level) external view returns (bool);
    
    /// @notice Get all completed levels for a user
    function getCompletedLevels(address user) external view returns (bool[] memory);
    
    /// @notice Get signer address
    function signer() external view returns (address);
    
    /// @notice Update signer (owner only)
    function setSigner(address newSigner) external;
    
    /// @notice Get tier name for a level
    function getTier(uint256 level) external pure returns (string memory);
    
    // Events
    event LevelCompleted(address indexed user, uint256 indexed level, uint256 tokenId);
    event SignerUpdated(address indexed oldSigner, address indexed newSigner);
}
