import os
from flashbots import flashbot
from flashbots import FlashbotProvider
from eth_account import Account
from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from web3.types import TxParams
import json
import math
from web3.middleware import construct_sign_and_send_raw_middleware
from flashbots.types import SignTx
from eth_account import Account
from web3 import Web3, HTTPProvider, exceptions
import requests




def get_gas_price():
    gas_api = "https://ethgasstation.info/json/ethgasAPI.json"
    response = requests.get(gas_api).json()

    gas_multiplier = 3
    gas_price_gwei = math.floor(response["fastest"] / 10 * gas_multiplier)
    gas_price = w3.toWei(gas_price_gwei, "gwei")
    return gas_price


def main():
    
    w3 = Web3(HTTPProvider(os.environ.get("ETH_RPC")))
    print(f"Connected: {w3.isConnected()}")
    COMP_WALLET: LocalAccount = Account.from_key(os.environ.get("ETH_COMPROMISED_PRIVATE_KEY"))
    GASSER_WALLET: LocalAccount = Account.from_key(os.environ.get("ETH_GASSER_PRIVATE_KEY"))
    FLASHBOT_SIGNER: LocalAccount = Account.from_key(os.environ.get("FLASHBOT_SIGNER"))
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(FLASHBOT_SIGNER))


    abi_file="abi.json"
    with open('abi.json') as abi_file:
        contract_abi = json.load(abi_file)

    flashbotsProvider = FlashbotProvider(
        w3,
        authSigner,
    'https://relay-goerli.flashbots.net/',
)
    

    flashbot(w3, signer, os.environ.get("PROVIDER_URL"))

    nonce = w3.eth.get_transaction_count(sender.address)
    gas_price = get_gas_price()

    contract = w3.eth.contract(address=os.environ.get("USDT_MAINNET"), abi=contract_abi)

    #gas send tx    
    
    #usdt rescue tx
    token_amount=contract.funcitons.balanceOf(w3.eth.account.from_key(os.environ.get("ETH_COMPROMISED_PRIVATE_KEY")))
    contract.
    transaction = contract.functions.transfer.encodeABI(os.environ.get("safe_wallet"), token_amount).build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': 2000000,  # Adjust the gas limit as needed
        'gasPrice': gas_price,  # Adjust the gas price as needed or use w3.eth.generate_gas_price()
        'nonce': nonce,
    })

    gas_estimate = math.floor(w3.eth.estimate_gas(tx))
    tx["gas"] = gas_estimate

    gas_in_gwei = int(gas_price / 10**9)

    signed_tx = COMP_WALLET.sign_transaction(tx)

    bundle = [
            {"signed_transaction": signed_tx.rawTransaction},
            # you can include other transactions in the bundle
            # in the order that you want them in the block
        ]

    block_number = w3.eth.block_number

    print("SIMULATING TRANSACTION...")
    try:
        simulation = w3.flashbots.simulate(bundle, block_number + 1)
    except Exception as e:
        print("Error in simulation", e)
        return

    print(f'bundleHash: {simulation["bundleHash"]}')
    print(f'coinbaseDiff: {simulation["coinbaseDiff"]}')
    print(f'totalGasUsed: {simulation["totalGasUsed"]}')


    print("SENDING bundles to flashbots")
    for i in range(1, 3):
            w3.flashbots.send_bundle(bundle, target_block_number=block_number + i)

    print(f"broadcast started at block {block_number}")

        # target 3 future blocks
        # if we dont see confirmation in those blocks, assume the mint wasn't mined
    while True:
        try:
            w3.eth.wait_for_transaction_receipt(signed_tx.hash, timeout=1, poll_latency=0.1)
            break

        except exceptions.TimeExhausted:
            print(f"Block: {w3.eth.block_number}")
            if w3.eth.block_number > (block_number + 3):
                print("ERROR: transaction was not mined so you didn't mint a thing")
                exit(1)

    print(f"transaction confirmed at block {w3.eth.block_number}")

if __name__ == "__main__":
    main()
