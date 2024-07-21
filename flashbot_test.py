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

#Load accounts and keys
load_dotenv()
GASSER_WALLET: LocalAccount = Account.from_key(os.environ.get("ETH_TEST_WALLET"))
COMP_WALLET: LocalAccount = Account.from_key(os.environ.get("EMPTY_TEST_WALLET"))
FLASHBOT_SIGNER: LocalAccount = Account.from_key(os.environ.get("FLASHBOT_SIGNER"))

#connect to llamarpc and intiialize web3 instance
w3 = Web3(HTTPProvider(os.environ.get("ETH_TESTNET_RPC")))
print(f"Connected: {w3.isConnected()}")
gasprice = w3.eth.gas_price
print(gasprice)


#initialize flashbots instance
#w3.middleware_onion.add(construct_sign_and_send_raw_middleware(FLASHBOT_SIGNER))

flashbotsProvider = FlashbotProvider(
    w3,
    FLASHBOT_SIGNER,
    os.environ.get("TESTNET_FLASHBOT_RELAY"),
)

flashbot(
    w3, #this doesn't allow flashbotProvider
    FLASHBOT_SIGNER
)

print('Flashbot connected to goerli relay')


# response = requests.get("https://api-sepolia.etherscan.io/api?module=proxy&action=eth_gasPrice&apikey=")

# if response.status_code == 200:
#     data = response.json()
#     gas_price = data["result"]
#     print(f"Gas Price:{Web3.to_int(hexstr=gas_price)}")
# else:
#     print("Error:", response.status_code)



#prepare eth send tx from gasser to comp
nonce = w3.eth.get_transaction_count(GASSER_WALLET.address)
print(f"Nonce:{nonce}")
amount = 1000000000000000
signed_tx: SignTx = {
    "to": COMP_WALLET.address,
    "value": amount,
    "nonce": nonce,
    "maxFeePerGas": Web3.toWei(200, "gwei"),
    "maxPriorityFeePerGas": Web3.toWei(50, "gwei"),
    "gas": 21000,
    "chainId": 11155111,
     "type": 2
}
signed_transaction1 = GASSER_WALLET.sign_transaction(signed_tx)
print("Gas tx signed")



signed_tx2: SignTx = {
    "to": GASSER_WALLET.address,
    "value": 500000000000000,
    "nonce": nonce + 1,
    "maxFeePerGas": Web3.toWei(200, "gwei"),
    "maxPriorityFeePerGas": Web3.toWei(50, "gwei"),
    "gas": 21000,
    "chainId": 11155111,
     "type": 2
}

signed_transaction2 = COMP_WALLET.sign_transaction(signed_tx2)
print("Return tx signed")


# #prepare bundle
bundle = [

    {
        "signed_transaction": signed_transaction1.rawTransaction
    },
    
    {
        "signed_transaction": signed_transaction2.rawTransaction
    },
]


block = w3.eth.block_number

print(f"Simulating on block {block}")
        # simulate bundle on current block
try:
    w3.flashbots.simulate(bundle, block)
    print("Simulation successful.")
except Exception as e:
    print("Simulation error", e)
    

print(f"Sending bundle targeting block {block+1}")

# replacement_uuid = str(uuid4())
# print(f"replacementUuid {replacement_uuid}")
# send_result = w3.flashbots.send_bundle(
#             bundle,
#             target_block_number=block + 1,
#             opts={"replacementUuid": replacement_uuid},
# )

# print("bundleHash", w3.toHex(send_result.bundle_hash()))