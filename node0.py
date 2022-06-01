# Creating a decentralized BLOCKCHAIN and verifying the transactions included using ZERO-KNOWLEDGE PROOF

# importing libraries

# to obtain the timestamp
import datetime
from operator import truediv
import random

# importing flask for creating the web app
from flask import Flask, jsonify, request
import json
from numpy import MAY_SHARE_BOUNDS

import requests

# to calculate hash using SHA256 function
import hashlib

# to make connections between nodes
from uuid import uuid4
from urllib.parse import urlparse


# create Blockchain blueprint
class Blockchain:

    # initializing the genesis block and setting the initial values
    def __init__(self):
        self.var1=5000
        self.p=11
        self.g=2
        self.x=10
        self.y=10
        self.r=10
        self.h=10
        self.b=0
        self.s=10
        self.l=10
        self.val=10
        self.chain = []
        self.my_block_indices = []
        self.transactions_pool = []
        self.create_block(prev_hash='0')
        self.nodes = set()
        


    # creating a new block before mining by storing appropriate values
    def create_block(self, prev_hash):

        # storing all the available transactions to the block before mining
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': 1,
                 'prev_hash': prev_hash,
                 'transactions': self.transactions_pool}

        self.my_block_indices.append(len(self.chain)) 
        print("adding in port=",self.var1,",index= ",len(self.chain))

        # emptying the transaction pool after adding to the block
        self.transactions_pool = []
        if len(self.chain) == 0:
            self.chain.append(block)
        return block

    # get the last block from the blockchain
    def fetch_previous_block(self):
        return self.chain[-1]

    # retrieve complete information of the block as requested by the user using block id
    def get_block(self, block_index):
        block = []
        if block_index > len(self.chain):
            return block
        block.append(self.chain[block_index - 1])
        return block

    # retrieve timestamp of the block as requested by the user using block id
    def get_timestamp(self, block_index):
        if block_index > len(self.chain):
            return -1
        return self.chain[block_index - 1]['timestamp']

    # generating proof of work by finding a valid nonce
    # a valid nonce is a nonce value which when added to the block provides a hash with 4 leading 0s (0000)
    def proof_of_work(self, block):
        nonce = 1
        check = False
        while check is False:
            block['nonce'] = nonce
            encoded_block = json.dumps(block, sort_keys=True).encode()
            cur_hash = hashlib.sha256(encoded_block).hexdigest()
            if cur_hash[:4] == '0000':
                check = True
            else:
                nonce += 1
        self.x=nonce
        self.y=pow(self.g,self.x,self.p)
        return [block, cur_hash]

    # finding the hash of a block by giving a complete block as a parameter
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # checking the validity of a chain by traversing through the chain
    # the prev_hash value for the current block should be equal to the hash value of the previous block
    # checking if the hash value of all the blocks has 4 leading zeros except the genesis block
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(previous_block):
                return False
            encoded_block = json.dumps(block, sort_keys=True).encode()
            cur_hash = hashlib.sha256(encoded_block).hexdigest()
            if cur_hash[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    # adding a transaction into the current pool of transactions before adding them into a block
    def add_transaction(self, Patient_Id,Patient_Name,Age,Admit_Date,Diagnosis,Insurance_Number):
        self.transactions_pool.append({ 'Patient_Id': Patient_Id,
                                        'Patient_Name': Patient_Name,      
                                        'Age': Age,
                                        'Admit_Date': Admit_Date,
                                        'Diagnosis': Diagnosis,
                                        'Insurance_Number': Insurance_Number})

    # adding a node into the network of connected nodes maintaining blockchain
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # updating the chain of a node by comparing with chains in other nodes
    # the chain with the maximum length among all nodes is considered the latest chain
    # with this function we find the latest chain among all nodes
    def update_chain(self):
        connections = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in connections:
            response = requests.get(f'http://{node}/get_node_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    #verify function performs the zero-knowledge proof to check if the miner really found the correct nonce(sensitive data x)
    def verify(self):

        #choosing r as a random value between (0,p-1)
        blockchain.r=random.randint(0,9)

        #calculating h value as (g^r) % p
        blockchain.h=pow(blockchain.g,blockchain.r,blockchain.p)
       
        #requesting the verifier to send b
        response = requests.get(f'http://127.0.0.1:5001/get_b')
        if response.status_code == 200:
            blockchain.b = response.json()['b']
        
        #calculating s value as (r+bx) % (p-1)
        blockchain.s=(blockchain.r + (blockchain.b*blockchain.x))%(blockchain.p-1)

        #requesting verifier to send l 
        response = requests.get(f'http://127.0.0.1:5001/get_l')
        if response.status_code == 200:
            blockchain.l = response.json()['l']

        #calculating the final value = ((h * (y ^ p)) % p )    
        blockchain.val=(blockchain.h * (pow(blockchain.y,blockchain.b)))%(blockchain.p)

        #if the value returned by verifier(l) is equal to the value generated by miner(val),then verification is successful 
        if blockchain.val==blockchain.l :
            return True
        else:
            return False
        

        

# creating a web app using flask
app = Flask(__name__)

# creating an address for the node on the mentioned port number
node_address = str(uuid4()).replace('-', '')

# creating an object of the Blockchain class
blockchain = Blockchain()


# making connections between the nodes
# the nodes to be connected are provided in JSON format during API call
@app.route('/make_connections', methods=['POST'])
def make_connections():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Connections made.',
                'connected_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# adding a new transaction into the current pool of transactions
# transaction details are provided in JSON format during API call
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['Patient_Id','Patient_Name','Age','Admit_Date','Diagnosis','Insurance_Number']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    blockchain.add_transaction(json['Patient_Id'], json['Patient_Name'], json['Age'], json['Admit_Date'],json['Diagnosis'],json['Insurance_Number'])
    response = {'message': 'This transaction is successfully added to the Transaction Pool. '}
    return jsonify(response), 201


# mining a block and displaying the information on the current block with its hash value
# before mining a block, it is checked whether the chain of the node is updated or not
# a hash value is generated using all the information on the block by calling the proof_of_work function
@app.route('/mine_block', methods=['GET'])
def mine_block():
    flag = blockchain.update_chain()
    prev_block = blockchain.fetch_previous_block()
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(prev_hash)
    [block, cur_hash] = blockchain.proof_of_work(block)
    

    #calling the verify function 3 times, ie ,performing 3 rounds of zero-knowledge proof
    flag=True
    for i in range(3):
        if blockchain.verify()==False:
            flag=False

    #if all rounds of zero-knowledge prrof returned true,then the miner is legit 
    if flag :
        print("verification successful")
        print("verifier calulated: ",blockchain.val)
        print("The miner calculated: ",blockchain.l)
        blockchain.chain.append(block)
        response1 = {'message': 'Congratulations, you just mined a block!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'nonce': block['nonce'],
                    'previous_hash': block['prev_hash'],
                    'transactions': block['transactions'],
                    'current_hash': cur_hash}
        return jsonify(response1), 200
    else :
        print("verification says u r imposter")
        print(blockchain.val)
        print(blockchain.l)
        response={}
        return jsonify(response), 200

# retrieving the complete chain details of the node provided
@app.route('/get_node_chain', methods=['GET'])
def get_node_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# display the complete chain details along with corresponding hash values for all blocks
@app.route('/get_chain', methods=['GET'])
def get_chain():
    output = []
    for block in blockchain.chain:
        cur_hash = blockchain.hash(block)
        output.append({'block': block, 'cur_hash': cur_hash})
    response = {'Chain': output, 'Length': len(output)}
    return jsonify(response), 200

#display only those transactions that were added by this node in the blockchain
@app.route('/view_user', methods=['GET'])
def view_user():
    output = []
 
    for x in range(len(blockchain.my_block_indices)): 
        print(blockchain.my_block_indices[x])
        output.append({'block': blockchain.chain[blockchain.my_block_indices[x]]})
   
    response = {'Chain': output, 'Length': len(output)}
    return jsonify(response), 200


# updating the chain to the latest chain in the network and displaying the updated chain
@app.route('/update_chain', methods=['GET'])
def update_chain():
    is_chain_updated = blockchain.update_chain()
    if is_chain_updated:
        response = {'message': 'The chain of the current node has been updated',
                    'updated_chain': blockchain.chain}
    else:
        response = {'message': 'No updates needed. The chain is the latest one.',
                    'updated_chain': blockchain.chain}
    return jsonify(response), 200


# returning h value to the caller(which will be a verifier) 
@app.route('/get_h', methods=['GET'])
def get_h():
   
    response = {'h': blockchain.h} 
    return jsonify(response), 200


# returning b value to the caller(which will be a miner) 
@app.route('/get_b', methods=['GET'])
def get_b():
    
    #requesting node(miner in this case) to send h value
    response = requests.get(f'http://127.0.0.1:5001/get_h')
    if response.status_code == 200:
         blockchain.h = response.json()['h']
    blockchain.b=random.randint(0, 1)
    response = {'b': blockchain.b}
    return jsonify(response), 200


# returning s value to the caller(which will be a verifier) 
@app.route('/get_s', methods=['GET'])
def get_s():
    
    response = {'s': blockchain.s}
    
    return jsonify(response), 200


# returning l value to the caller(which will be a miner) 
@app.route('/get_l', methods=['GET'])
def get_l():

    #requesting node(miner in this case) to send h value
    response = requests.get(f'http://127.0.0.1:5001/get_s')
    if response.status_code == 200:
         blockchain.s = response.json()['s']
    
    blockchain.l=pow(blockchain.g,blockchain.s,blockchain.p)
    response = {'l': blockchain.l}
    return jsonify(response), 200


# running the app on mentioned host and port
app.run(host='127.0.0.1', port=5000)
