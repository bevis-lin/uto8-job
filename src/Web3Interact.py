import os
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(os.environ['Web3_HTTP_Provider']))
salesProviderAddress = os.environ['SalesProvider_Contract_Address']

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

f = open(FILE_DIR + '/abi/SalesProvider.json')
salesProviderProviderABI = json.load(f)
f.close()

piamonAddress = os.environ['Piamon_Contract_Address']

f = open(FILE_DIR + '/abi/Piamon.json')
piamonProviderABI = json.load(f)
f.close()

salesProviderContract_instance = w3.eth.contract(
    address=salesProviderAddress, abi=salesProviderProviderABI)

piamonContract_instance = w3.eth.contract(address=piamonAddress, abi=piamonProviderABI)

def getOwnerOfPiamon(tokenId):
  try:
    nftOwnerAddrress = piamonContract_instance.functions.ownerOf(tokenId).call()
    return nftOwnerAddrress
  except Exception as e:
    print(e)
    return None

      

