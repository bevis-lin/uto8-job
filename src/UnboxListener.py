from datetime import datetime
import json
import os
import sys
from web3 import Web3
import asyncio
import helper.RabbitMQHelper as rabbit

w3 = Web3(Web3.HTTPProvider(os.environ['Web3_HTTP_Provider']))
salesProviderAddress = os.environ['SalesProvider_Contract_Address']

f = open('./abi/SalesProvider.json')
salesProviderProviderABI = json.load(f)
f.close()

piamonAddress = os.environ['Piamon_Contract_Address']

f = open('./abi/Piamon.json')
piamonProviderABI = json.load(f)
f.close()

salesProviderContract_instance = w3.eth.contract(
    address=salesProviderAddress, abi=salesProviderProviderABI)

piamonContract_instance = w3.eth.contract(address=piamonAddress, abi=piamonProviderABI)


def handle_event(event):
    resultJson = json.loads(Web3.toJSON(event))
    print(resultJson["args"])
    blindoxId = resultJson["args"]["blindboxId"]
    #get BlindBox definition
    blindBox = salesProviderContract_instance.functions.blindBoxes(blindoxId).call()

    #get blindbox total mint count from Piamon blindBoxTotalMint
    totalMint = piamonContract_instance.functions.blindBoxTotalMint(blindoxId).call()
    print("BlindBox total minted quantity: " + str(totalMint))

    #rabbit.QueueDeclare('chain.v1.unblind.piya')

    for i in range(totalMint):
        #compose nftId
        nftId = i + blindBox[2]
        nftOwnerAddrress = piamonContract_instance.functions.ownerOf(nftId).call()
        message = {
            "wallet_address": nftOwnerAddrress,
            "nft_id": str(nftId),
            "BlindBoxID": str(nftId)[:6],
            "BlindBoxListID": str(nftId),
            "publish_time": str(datetime.now().timestamp())
        }
        print(json.dumps(message))
        rabbit.Publish('chain.v1.unblind.piya', json.dumps(message))
       

async def log_loop(event_filter, poll_interval):
    while True:
        for Transfer in event_filter.get_new_entries():
            handle_event(Transfer)
        await asyncio.sleep(poll_interval)


def main():
    event_filter = salesProviderContract_instance.events.UnboxLog.createFilter(
        fromBlock='latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
        # log_loop(block_filter, 2),
        # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()
