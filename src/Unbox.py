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

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

f = open(FILE_DIR + '/abi/SalesProvider.json')
salesProviderABI = json.load(f)
f.close()

f = open(FILE_DIR + '/abi/Piamon.json')
piamonProviderABI = json.load(f)
f.close()

salesProviderContract_instnace = w3.eth.contract(address=salesProviderAddress, abi=salesProviderABI)
piamonContract_instance = w3.eth.contract(address=piamonAddress, abi=piamonProviderABI)

blindBoxId = int(os.environ['BlindBox_Id'])

while(True):

  print("BlindBoxId:"+str(blindBoxId)+", checking blindbox information...")

  #get BlindBox definition
  blindBox = salesProviderContract_instnace.functions.blindBoxes(blindBoxId).call()

  #check if already unboxed
  if blindBox[11] > 0:
    print("BlindBoxId:"+str(blindBoxId)+", already unboxed")
    sys.exit()

  #unboxing time
  print(blindBox[10])

  dt_object = datetime.fromtimestamp(blindBox[10])
  print("dt_object = ", dt_object)

  print(dt_object<datetime.now())

  isTimeToUnbox = dt_object<datetime.now()

  if not isTimeToUnbox:
    print("BlindBoxId:"+str(blindBoxId)+ ", unbox time is yet to come. Waiting for 60 seconds...")
    time.sleep(60)
    continue

  contract_owner_address = os.environ['Contract_Owner_Address']
  nonce = w3.eth.get_transaction_count(contract_owner_address)

  print("BlindBoxId:"+str(blindBoxId) + ", begin to unbox...")

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
  tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
  print(w3.toHex(w3.keccak(signed_txn.rawTransaction)))
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
  print(tx_receipt, file=sys.stdout)
  print(type(tx_receipt))

  if tx_receipt.status==1:
    print("BlindBoxId:"+str(blindBoxId)+", transaction complete.")
  else:
    print("BlindBoxId:"+str(blindBoxId)+", transaction failed.")

