from datetime import datetime
import json
import os
import sys
from web3 import Web3
import asyncio
import helper.RabbitMQHelper as rabbit

w3 = Web3(Web3.HTTPProvider(os.environ['Web3_HTTP_Provider']))
piamonAddress = os.environ['Piamon_Contract_Address']

# absolute path to this file
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# absolute path to this file's root directory
PARENT_DIR = os.path.join(FILE_DIR, os.pardir)

f = open(PARENT_DIR + '/abi/Piamon.json')
piamonProviderABI = json.load(f)
f.close()

piamonContract_instance = w3.eth.contract(
    address=piamonAddress, abi=piamonProviderABI)


def handle_event(event):
    # print(Web3.toJSON(event))
    #{"args": {"from": "0x0000000000000000000000000000000000000000", "to": "0x37100698B013ce6097453dEf91986EabA6570Ea2", "tokenId": 10045005}, "event": "Transfer", "logIndex": 4, "transactionIndex": 1, "transactionHash": "0x161790cfedf06d7cfc008ff1aacb7e6b03d03e58180711252d9241a7d166af9c", "address": "0xb961027CF87dE6D5942027a04AecEC1c3a50E029", "blockHash": "0x39e79f6705b3a6fc7c6f66aefd176758b2acc8a74a864f26c194ac52e69a2cf3", "blockNumber": 26683317}
    resultJson = json.loads(Web3.toJSON(event))
    print(resultJson["args"])
    x = int(str(resultJson["args"]["from"]), 16)
    if x == 0:
        print('New NFT minted,tokenId:', str(resultJson["args"]["tokenId"]))
        message = {
            "wallet_address": resultJson["args"]["to"],
            "nft_id": str(resultJson["args"]["tokenId"]),
            "publish_time": str(datetime.now().timestamp())
        }
        rabbit.Publish('chain.v1.mint.piya', json.dumps(message))


async def log_loop(event_filter, poll_interval):
    while True:
        for Transfer in event_filter.get_new_entries():
            handle_event(Transfer)
        await asyncio.sleep(poll_interval)


def main():
    event_filter = piamonContract_instance.events.Transfer.createFilter(
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
