from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware
from flashbots import flashbot
from flashbots import FlashbotProvider
from flashbots.types import SignTx
from eth_account import Account
from web3 import Web3, HTTPProvider, exceptions
import os
from uuid import uuid4
import requests
import math
import json
from web3.types import TxParams
from dotenv import load_dotenv
from web3.exceptions import TransactionNotFound
from web3morebundlers import bundler


def main():
    #Load accounts and keys
    load_dotenv()
    GASSER_WALLET: LocalAccount = Account.from_key(os.environ.get("ETH_GASSER_PRIVATE_KEY"))
    COMP_WALLET: LocalAccount = Account.from_key(os.environ.get("ETH_COMPROMISED_PRIVATE_KEY"))
    FLASHBOT_SIGNER: LocalAccount = Account.from_key(os.environ.get("FLASHBOT_SIGNER"))
    token_addres=Web3.to_checksum_address(os.environ.get("USDT_MAINNET"))
    safe=Web3.to_checksum_address(os.environ.get("ETH_SAFE_ADDRESS"))

    #connect to llamarpc and intiialize web3 instance
    w3 = Web3(HTTPProvider(os.environ.get("ETH_RPC")))
    print(f"Connected: {w3.isConnected()}")
    gasprice = w3.eth.gas_price
    print(gasprice)

    # BUNDLER_ENPOINTS: Final[list[str]] = [
    #     "https://relay.flashbots.net",
    #     "https://rpc.titanbuilder.xyz",
    #     "https://rpc.beaverbuild.org",
    #     "https://rsync-builder.xyz",
    #     "https://eth-builder.com",
    #     "https://builder.gmbit.co/rpc",
    #     "https://buildai.net",
    #     "https://rpc.payload.de",
    #     "https://rpc.nfactorial.xyz",
    # ]

    # bundler(
    #     w3=w3,
    #     signature_account=FLASHBOT_SIGNER,
    #     endpoint_uris=BUNDLER_ENPOINTS,
    #     flashbots_uri=("https://relay.flashbots.net"),
    # )




    # flashbotsProvider = FlashbotProvider(
    #     w3,
    #     FLASHBOT_SIGNER
    # )

    flashbot(
        w3, #this doesn't allow flashbotProvider
        FLASHBOT_SIGNER
    )

    print('Flashbot connected to mainnet relay')



    


    #prepare eth send tx from gasser to comp
    nonce = w3.eth.get_transaction_count(GASSER_WALLET.address)
    #print(f"Nonce:{nonce}")
    
    
    basefee=math.floor(gasprice*5/2)
    print(f"CurrentBase Fee : {gasprice}")
    print(f"Base Fee sent (x2.5) : {basefee}")   

    ethbalance = w3.eth.get_balance(GASSER_WALLET.address)
    glimit1=21000
    glimit2=80000
    
    maxPriorityFeePerGas1=0
    maxFeePerGas1=basefee+maxPriorityFeePerGas1
    priorityfee1=maxPriorityFeePerGas1*glimit1
    txfee1=maxFeePerGas1*glimit1

    
    
    
    txfee2=ethbalance-txfee1
    maxFeePerGas2=math.floor(txfee2/glimit2)
    maxPriorityFeePerGas2=maxFeePerGas2-basefee
    priorityfee2=maxPriorityFeePerGas2*glimit2
    
    

    print(f"Transfer Amount: {txfee2}")
    print(f"maxPriorityFeePerGas1: {maxPriorityFeePerGas1}")
    print(f"maxPriorityFeePerGas2: {maxPriorityFeePerGas2}")
    print(f"maxFeePerGas1: {maxFeePerGas1}")
    print(f"maxFeePerGas2: {maxFeePerGas2}")
    print(f"Total Transaction Fee for 2 tx: {txfee1+txfee2}")
    print(f"Total Miner Fee: {priorityfee2+priorityfee1}")
    
    signed_tx: SignTx = {
        "to": COMP_WALLET.address,
        "value": txfee2,
        "nonce": nonce,
        "maxFeePerGas": maxFeePerGas1,
        "maxPriorityFeePerGas": maxPriorityFeePerGas1,
        "gas": glimit1,
        "chainId": 1,
        "type": 2
    }
    signed_transaction1 = GASSER_WALLET.sign_transaction(signed_tx)
    print("Gas tx signed")


    # initialize usd contract
    abi = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_upgradedAddress","type":"address"}],"name":"deprecate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"deprecated","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_evilUser","type":"address"}],"name":"addBlackList","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"upgradedAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balances","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"maximumFee","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"unpause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_maker","type":"address"}],"name":"getBlackListStatus","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowed","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"paused","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"pause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"newBasisPoints","type":"uint256"},{"name":"newMaxFee","type":"uint256"}],"name":"setParams","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"issue","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"redeem","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"basisPointsRate","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"isBlackListed","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_clearedUser","type":"address"}],"name":"removeBlackList","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"MAX_UINT","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_blackListedUser","type":"address"}],"name":"destroyBlackFunds","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_initialSupply","type":"uint256"},{"name":"_name","type":"string"},{"name":"_symbol","type":"string"},{"name":"_decimals","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"amount","type":"uint256"}],"name":"Issue","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"amount","type":"uint256"}],"name":"Redeem","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"newAddress","type":"address"}],"name":"Deprecate","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"feeBasisPoints","type":"uint256"},{"indexed":false,"name":"maxFee","type":"uint256"}],"name":"Params","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_blackListedUser","type":"address"},{"indexed":false,"name":"_balance","type":"uint256"}],"name":"DestroyedBlackFunds","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_user","type":"address"}],"name":"AddedBlackList","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_user","type":"address"}],"name":"RemovedBlackList","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[],"name":"Pause","type":"event"},{"anonymous":false,"inputs":[],"name":"Unpause","type":"event"}]')
    usdtContract = w3.eth.contract(address=token_addres, abi=abi)
    

    #prepare usd transfer payload
    encoded1 = usdtContract.encodeABI(fn_name='transfer', args=[safe,usdtContract.functions.balanceOf(COMP_WALLET.address).call()])
    encoded_bytes_data1 = Web3.toBytes(hexstr=encoded1)
    print('Transfer ABI Encoded')
        

    nonce2ndtx = w3.eth.get_transaction_count(COMP_WALLET.address)
    #print(f"2nd tx Nonce:{nonce2ndtx}")
    #prepare bundle
    bundle = [

        {
            "signed_transaction": signed_transaction1.rawTransaction
        },
        
        {
            "signer": COMP_WALLET,
            "transaction": {"to": token_addres,
                            "value": Web3.toWei(0, "ether"),
                            "gas":glimit2,
                            "maxFeePerGas": maxFeePerGas2,
                            "maxPriorityFeePerGas": maxPriorityFeePerGas2,
                            "nonce": nonce2ndtx,
                            "chainId": 1,
                            "data": encoded_bytes_data1,
                            "type": 2
                            },
        }
    ]


    for i in range(10):

        block = w3.eth.block_number
        tgt_block=block+3
        print(f"Simulating on block {block}")
                # simulate bundle on current block
        try:
            w3.flashbots.simulate(bundle, block)
            print("Simulation successful.")
        except Exception as e:
            print("Simulation error", e)
            return
            

        print(f"Sending bundle targeting block {tgt_block}")

        replacement_uuid = str(uuid4())
        print(f"replacementUuid {replacement_uuid}")
        send_result = w3.flashbots.send_bundle(
                    bundle,
                    target_block_number=tgt_block,
                    opts={"replacementUuid": replacement_uuid},
        )

        print("bundleHash", w3.toHex(send_result.bundle_hash()))
        stats_v1 = w3.flashbots.get_bundle_stats(
                    w3.toHex(send_result.bundle_hash()), block
                )
        print("bundleStats v1", stats_v1)
                

        stats_v2 = w3.flashbots.get_bundle_stats_v2(w3.toHex(send_result.bundle_hash()), block)
        print("bundleStats v2", stats_v2)

        send_result.wait()
        try:
            receipts = send_result.receipts()
            print(f"\nBundle was mined in block {receipts[0].blockNumber}\a")
            break
        except TransactionNotFound:
            print(f"Bundle not found in block {tgt_block}")
            # essentially a no-op but it shows that the function works
            cancel_res = w3.flashbots.cancel_bundles(replacement_uuid)
            print(f"canceled {cancel_res}")

    print(f"Compromised account USDT balance: {usdtContract.functions.balanceOf(COMP_WALLET.address).call()}")

if __name__ == "__main__":
    main()
