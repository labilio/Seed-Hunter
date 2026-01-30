// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/GandalfBreakerNFT.sol";
import "../src/HintPayment.sol";

/**
 * @title DeployScript
 * @notice Deploy Gandalf Game contracts
 * 
 * Usage:
 * forge script script/Deploy.s.sol:DeployScript --rpc-url $RPC_URL --broadcast --verify
 */
contract DeployScript is Script {
    function run() external {
        // Load environment variables
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address signer = vm.envAddress("SIGNER_ADDRESS");
        address treasury = vm.envAddress("TREASURY_ADDRESS");
        address usdcAddress = vm.envAddress("USDC_ADDRESS");
        
        vm.startBroadcast(deployerPrivateKey);

        // Deploy NFT contract
        GandalfBreakerNFT nft = new GandalfBreakerNFT(
            signer,
            "" // Base URI can be set later
        );
        console.log("GandalfBreakerNFT deployed at:", address(nft));

        // Deploy HintPayment contract
        HintPayment hintPayment = new HintPayment(
            usdcAddress,
            treasury,
            signer
        );
        console.log("HintPayment deployed at:", address(hintPayment));

        vm.stopBroadcast();

        // Output deployment info
        console.log("\n=== Deployment Summary ===");
        console.log("NFT Contract:", address(nft));
        console.log("HintPayment Contract:", address(hintPayment));
        console.log("Signer:", signer);
        console.log("Treasury:", treasury);
        console.log("USDC:", usdcAddress);
    }
}

/**
 * @title DeployNFTOnly
 * @notice Deploy only the NFT contract
 */
contract DeployNFTOnly is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address signer = vm.envAddress("SIGNER_ADDRESS");
        
        vm.startBroadcast(deployerPrivateKey);

        GandalfBreakerNFT nft = new GandalfBreakerNFT(signer, "");
        console.log("GandalfBreakerNFT deployed at:", address(nft));

        vm.stopBroadcast();
    }
}
