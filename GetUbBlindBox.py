from datetime import datetime
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

print(contract_instnace.functions.blindBoxes.length.call())

blindBox = contract_instnace.functions.blindBoxes(0).call()

print(blindBox[10])

dt_object = datetime.fromtimestamp(blindBox[10])
print("dt_object = ", dt_object)

print(dt_object<datetime.now())
