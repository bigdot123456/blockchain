from shortuuid import uuid
import time
import json
import argparse

from nodes import BlockchainNode
from blockchain import Blockchain


"""
===========
 MAIN CODE
===========
"""

parser = argparse.ArgumentParser()
parser.add_argument('-n', type=str)
parser.add_argument('-p', type=int)
parser.add_argument('--file', type=str)

args = parser.parse_args()
node_id = uuid()

if __name__ == '__main__':
    # Load Blockchain File
    filename = args.file
    if filename:
        data = json.load(open(filename))
        blockchain = Blockchain(data['chain'])
    else:
        blockchain = Blockchain()

    node = BlockchainNode(
        name=args.n or f'node-{node_id}',
        port=args.p or 5000,
        blockchain=blockchain
    )

    try:
        print(f'Starting node-{node_id}')

        # Establish Connection
        while not node.ready:
            node.send('version', message=json.dumps({
                'height': len(node.blockchain.chain)
            }))
            time.sleep(1)

        # Sync up with the other nodes
        node.resolve_conflicts()
        while not node.synced:
            time.sleep(1)

        # Listen for new blocks being added
        while True:
            user_input = input('\nDo you want to add a transaction? (y/n) ')

            if user_input.lower == 'yes' or user_input.lower == 'y':
                recipient = input('Recipient: ')
                amount = input('Amount: ')

                node.blockchain.add_transaction(node.identifier, recipient, amount, '0')
            time.sleep(1)

    except (EOFError, KeyboardInterrupt):
        node.stop()

        # Save Blockchain to file
        with open(filename or 'blockchain.json', 'w') as outfile:
            json.dump({'chain': blockchain.chain}, outfile, indent=4)
