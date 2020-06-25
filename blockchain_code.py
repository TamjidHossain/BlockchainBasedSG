#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 00:58:09 2020

@author: mdtamjidhossain
"""

#%%
import hashlib

import json

import time

import sys
#%%
directory = "/home/user/Desktop/BlockchainBasedSG/"

blockchain_text_dir = directory

reward = 10.0


arg1 = str(sys.argv[1])
    
arg1 = arg1.replace("'", '"')

res = json.loads(arg1)


consumption_data = res[0][1]

owner = res[1][1]

recipient = res[2][1]

open_consumption_values = []

blockchain_text_file = blockchain_text_dir + "blockchain_" + str(owner) + ".txt"

blockchain_file = open(blockchain_text_file,"r")

blockchain_file_data = blockchain_file.read()

dataPack2 = str(blockchain_file_data)

dataPack2 = dataPack2.replace("'", '"')

res2 = json.loads(dataPack2)

blockchain = res2


blockchain_file.close()

#%%

def hash_prev_block(block):

    return hashlib.sha256(json.dumps(block).encode()).hexdigest()


#%%
   
def valid_proof(consumption_values, last_hash, nonce):

    guess = (str(consumption_values) + str(last_hash) + str(nonce)).encode()

    guess_hash = hashlib.sha256(guess).hexdigest()

    # print(guess_hash)

    return guess_hash[0:2] == '00'



def pow():

    last_block = blockchain[-1]

    last_hash = hash_prev_block(last_block)

    nonce = 0

    while not valid_proof(open_consumption_values, last_hash, nonce):

        nonce += 1

    return nonce

#%%
   
def get_last_value():

    """ extracting the last element of the blockchain list """

    return(blockchain[-1])



def add_value(recipient, sender=owner, consumption_data=1.0):

    consumption_value = {'sender': sender,

    'recipient': recipient,

    'consumption_data': consumption_data}

    open_consumption_values.append(consumption_value)
   
#%%
   
def mine_block(cur_index):
   
    mining_time = time() 

    last_block = blockchain[-1]

    prev_hash = last_block['current_hash']

    nonce = pow()

    reward_consumption_value = {

            'sender': 'CC',

            'recipient': owner,

            'reward': reward

        }

    open_consumption_values.append(reward_consumption_value)
   
    block_without_current_hash = {

        'previous_hash': prev_hash,

        # 'index': len(blockchain),
        'index': cur_index+1,
       
        'timestamp': mining_time,

        'consumption_value': open_consumption_values,

        'nonce': nonce

    }
   
    curr_hash = hash_prev_block(block_without_current_hash)

    block = {

        'previous_hash': prev_hash,

        # 'index': len(blockchain),
        'index': cur_index+1,
       
        'timestamp': mining_time,
       
        'current_hash': curr_hash,

        'consumption_value': open_consumption_values,

        'nonce': nonce

    }

    blockchain.append(block)
    
    msg = "mining done"
    
    return msg
   

       
#%%
       
def verify_chain():

    index = 0

    valid = True

    for block in blockchain:
        if index == 0:

            index += 1

            continue

        elif block['previous_hash'] == blockchain[index - 1]['current_hash']:

            valid = True

        else:

            valid = False

            break

        index += 1

    return valid


#%%
    

add_value(recipient, consumption_data=consumption_data)


cur_index = blockchain[-1]['index']

if(mine_block(cur_index) == "mining done"):
    
    output = "New block successfully added to the blockchain"

else:
    output = "Block Mining unsuccessful|"

if not verify_chain():
    
    if len(blockchain) > 2:
        
        manipulation_text_file_name = str(directory) + "blockchain_manipulation_attempt.txt"
        
        manipulation_text_file = open(manipulation_text_file_name, "wt")
        
        n = manipulation_text_file.write("Blockchain Manipulation Attempt found by "+ str(owner) + " at Epoch time: " + str(time()))
        
        manipulation_text_file.close()
        
        output = output + " but verification has not been carried out due to only 2 blocks available|"
    
    
    else:
        
        text_file = open(blockchain_text_file, "wt")
        
        n = text_file.write("Blockchain Manipulated|")
        
        text_file.close()

else:
    
    text_file = open(blockchain_text_file, "wt")
        
    n = text_file.write(str(blockchain))
    
    text_file.close()
    
    output = output + " and verification also successful|"

if ((output == "New block successfully added to the blockchain and verification also successful|") | (output == "New block successfully added to the blockchain but verification has not been carried out due to only 2 blocks available|")):
    
    final_output = output + "Updated Blockchain = " + str(blockchain[-2:])
    
    print(final_output)
    
else:
    print(output)




#%%

    
    
    
    
    
    
    
    
    
    
    
    
    

