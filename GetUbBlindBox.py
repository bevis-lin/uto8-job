from datetime import datetime
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

w3 = Web3(Web3.HTTPProvider('https://polygon-mumbai.g.alchemy.com/v2/bcOXIBl9qePs2evjcvhuuSbZ12xi3h3e'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
address = '0x1bCa940a67Dab327284b8f1903873bEf9e479355'
f = open('./abi/SalesProvider.json')
abi = json.load(f)
f.close()

contract_instnace = w3.eth.contract(address=address, abi=abi)

#print(contract_instnace.functions.checkIsSaleOpen(0).call())

#print(contract_instnace.functions.getBlindBoxInfo(0).call())

#print(contract_instnace.functions.blindBoxes.length.call())

#blindBox = contract_instnace.functions.blindBoxes(1).call()
#print(blindBox)


blindBox = contract_instnace.functions.blindBoxes(0).call()

print(blindBox[10])

dt_object = datetime.fromtimestamp(blindBox[10])
print("dt_object = ", dt_object)

print(dt_object<datetime.now())

nonce = w3.eth.get_transaction_count('0x37100698B013ce6097453dEf91986EabA6570Ea2')

# Build a transaction that invokes SalesProvider contract's function called generateRandomNumber
salesprovider_txn = contract_instnace.functions.getRandomNumberForBlindBox(0).buildTransaction({
  'chainId': 80001,
  'gas': 10000000,
  'maxFeePerGas': w3.toWei('2', 'gwei'),
  'maxPriorityFeePerGas': w3.toWei('1', 'gwei'),
  'nonce': nonce,
})

private_key = 'e61290e879f2937226b46788b22a19b1e0ea6642fff7507808bf768f60e4101e'
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
  print('Transaction completed.')


