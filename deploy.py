from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

    # Compile
    install_solc("0.6.0")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "metadata",
                            "evn.bytecode",
                            "evm.bytecode.sourceMap",
                        ]
                    }
                }
            },
        },
        solc_version="0.6.0",
    )


with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Bytecode
# ABI

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  # localhost
# chain_id = 1337
# my_address = "0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0"
# private_key = os.getenv("PRIVATE_KEY")
w3 = Web3(
    Web3.HTTPProvider("https://goerli.infura.io/v3/94d154647a9947908ec0d78c41db9289")
)
chain_id = 5
my_address = "0x64FEa566cf0e7CB20A5eFb0b58a13Be69946cCB9"  # metaMask
private_key = os.getenv("PRIVATE_KEY_MT")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Nonce
nonce = w3.eth.getTransactionCount(my_address)
# 1. Build the transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# 2. Sign transaction
signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=private_key
)
# 3. Send transaction
transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
print("Waiting for transaction to finish...")
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(transaction_receipt.contractAddress)

# Working with deployed contracts
simple_storage = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)

# Call -> Simula una llamada para obtener un valor
print(simple_storage.functions.retrieve().call())

# Transact -> Ejecuta una llamada real, tiene un coste de gas
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_transaction = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
print("Updating stored value")
transaction_store_hash = w3.eth.send_raw_transaction(
    signed_store_transaction.rawTransaction
)
transaction_store_receipt = w3.eth.wait_for_transaction_receipt(transaction_store_hash)
print(simple_storage.functions.retrieve().call())


# ganache --deterministic
