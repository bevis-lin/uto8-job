from datetime import datetime
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
import sys
import helper.RabbitMQHelper as rabbit

w3 = Web3(Web3.HTTPProvider(os.environ['Web3_HTTP_Provider']))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
salesProviderAddress = os.environ['SalesProvider_Contract_Address']
piamonAddress = os.environ['Piamon_Contract_Address']
f = open('./abi/SalesProvider.json')
salesProviderABI = json.load(f)
f.close()

f = open('./abi/Piamon.json')
piamonProviderABI = json.load(f)
f.close()

salesProviderContract_instnace = w3.eth.contract(address=salesProviderAddress, abi=salesProviderABI)
piamonContract_instance = w3.eth.contract(address=piamonAddress, abi=piamonProviderABI)

#get BlindBox definition
blindBox = salesProviderContract_instnace.functions.blindBoxes(0).call()

#unboxing time
print(blindBox[10])

dt_object = datetime.fromtimestamp(blindBox[10])
print("dt_object = ", dt_object)

print(dt_object<datetime.now())

contract_owner_address = os.environ['Contract_Owner_Address']
nonce = w3.eth.get_transaction_count(contract_owner_address)

blindBoxId = int(os.environ['BlindBox_Id'])

#get blindbox total minted quantity from Piamon contract
totalMint = piamonContract_instance.functions.blindBoxTotalMint(blindBoxId).call()

print("BlindBox total minted quantity: " + str(totalMint))

#rabbit.QueueDeclare('chain.v1.unblind.piya')

#rabbit.QueueDeclare('hello')



for i in range(totalMint):
  message = {
    "wallet_address": "0x37100698B013ce6097453dEf91986EabA6570Ea2",
    "nft_id": str(i+1),
    "BlindBoxID": 0,
    "BlindBoxListID": str(i+1),
    "publish_time": str(datetime.now().timestamp())
  }
  print(json.dumps(message))
  rabbit.Publish('chain.v1.unblind.piya', json.dumps(message))
  #rabbit.Publish('hello', json.dumps(message))

sys.exit()

# Build a transaction that invokes SalesProvider contract's function called generateRandomNumber
salesprovider_txn = salesProviderContract_instnace.functions.getRandomNumberForBlindBox(blindBoxId).buildTransaction({
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
  #send queue



