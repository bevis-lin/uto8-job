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
    # print(Web3.toJSON(event))
    #{"args": {"from": "0x0000000000000000000000000000000000000000", "to": "0x37100698B013ce6097453dEf91986EabA6570Ea2", "tokenId": 10045005}, "event": "Transfer", "logIndex": 4, "transactionIndex": 1, "transactionHash": "0x161790cfedf06d7cfc008ff1aacb7e6b03d03e58180711252d9241a7d166af9c", "address": "0xb961027CF87dE6D5942027a04AecEC1c3a50E029", "blockHash": "0x39e79f6705b3a6fc7c6f66aefd176758b2acc8a74a864f26c194ac52e69a2cf3", "blockNumber": 26683317}
    resultJson = json.loads(Web3.toJSON(event))
    print(resultJson["args"])
    blindoxId = resultJson["args"]["blindboxId"]
    #get BlindBox definition
    blindBox = salesProviderContract_instance.functions.blindBoxes(blindoxId).call()

    #get blindbox total mint count from Piamon blindBoxTotalMint
    totalMint = piamonContract_instance.functions.blindBoxTotalMint(blindoxId).call()
    print("BlindBox total minted quantity: " + str(totalMint))

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
        #rabbit.Publish('hello', json.dumps(message))

#   x = int(str(resultJson["args"]["from"]), 16)
#   if x == 0:
#     print('New NFT minted,tokenId:', str(resultJson["args"]["tokenId"]))
#     message = {
#       "wallet_address": resultJson["args"]["to"],
#       "nft_id": str(resultJson["args"]["tokenId"]),
#       "publish_time": str(datetime.now().timestamp())
#     }
#     rabbit.Publish('chain.v1.mint.piya', json.dumps(message))


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
