from datetime import datetime
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os

w3 = Web3(Web3.HTTPProvider(os.environ['Web3_HTTP_Provider']))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
address = os.environ['SalesProvider_Contract_Address']
f = open('./abi/SalesProvider.json')
abi = json.load(f)
f.close()

contract_instnace = w3.eth.contract(address=address, abi=abi)

blindBox = contract_instnace.functions.blindBoxes(0).call()

print(blindBox[10])

dt_object = datetime.fromtimestamp(blindBox[10])
print("dt_object = ", dt_object)

print(dt_object<datetime.now())

contract_owner_address = os.environ['Contract_Owner_Address']
nonce = w3.eth.get_transaction_count(contract_owner_address)

blindBoxId = int(os.environ['BlindBox_Id'])

# Build a transaction that invokes SalesProvider contract's function called generateRandomNumber
salesprovider_txn = contract_instnace.functions.getRandomNumberForBlindBox(blindBoxId).buildTransaction({
  'chainId': 80001,
  'gas': 10000000,
  'maxFeePerGas': w3.toWei('2', 'gwei'),
  'maxPriorityFeePerGas': w3.toWei('1', 'gwei'),
  'nonce': nonce,
})

private_key = os.environ['Contract_Owner_Key']
signed_txn = w3.eth.account.sign_transaction(salesprovider_txn, private_key=private_key)
print(signed_txn.hash)
w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print(w3.toHex(w3.keccak(signed_txn.rawTransaction)))

receipt = None

while receipt == None:
  try:
    receipt = w3.eth.get_transaction_receipt(w3.toHex(w3.keccak(signed_txn.rawTransaction)))
  except Exception as e:
    #<class 'web3.exceptions.TransactionNotFound'>
    print(type(e))
    print('Unknow error', e)
    time.sleep(3)

print(receipt)
if receipt.status==1:
  print('Transaction complete.')


