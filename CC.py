# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:19:28 2020

@author: lab-user
"""

import struct as st
import zipfile
import socket
import time
import json
#%%


cc_req_indices = []

cc_req_indices = [11,12,13,14,21,22,23,24,31,32,33,34,41,42,43,44,51,52,53,54,61,62,63,64,71,72,73,74,81,82,83,84,91,92,93,94]

directory = "/home/user/Desktop/BlockchainBasedSG/"
#%%

# CC pack the req, sends it to DA and acts as a client
cc_req = 1
cc_req_len = int(len(cc_req_indices))+2

cc_req_format = '<BB{}B'.format(len(cc_req_indices))
cc_req_pack = st.pack(cc_req_format,cc_req,cc_req_len,*cc_req_indices)

remote_host = '10.0.0.20'
remote_port = 20000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((remote_host, remote_port))
count = 1

while True:
    # request starts here
    s.sendall(cc_req_pack)
    
    data = s.recv(1024)


    feedback_from_DA = str(data.decode('utf-8'))

    if("Verified Blockchain = " in feedback_from_DA):
            
            # blockchain copy from DA
            blockchain_DA = []
            blockchain_DA = feedback_from_DA.split("=")
            dataPack4 = blockchain_DA[1].strip(" ")
            dataPack4 = dataPack4.replace("'", '"')
            res4 = json.loads(dataPack4)
            
            ## Own blockchain copy
            blockchain_file1_name = str(directory) + "blockchain_CC.txt"
            blockchain_file1 = open(blockchain_file1_name,"r")
            blockchain_file_data1 = blockchain_file1.read()
            dataPack5 = str(blockchain_file_data1)
            dataPack5 = dataPack5.replace("'", '"')
            res5 = json.loads(dataPack5)            ##res5 is for R1
            

            
            res5.append(res4[-1])
            text_file_name = str(directory) + "blockchain_CC.txt"
            text_file = open(text_file_name, "wt")
            n = text_file.write(str(res5))
            text_file.close()
            
            if (len(res5) > 10):
                filename_index = str(res5[-1]['index'])[0:-1]
                filename = str(directory)+"blockchain"+ str(filename_index)+"_CC.zip"
                file_zip = zipfile.ZipFile(filename, 'w')
                file_zip_name = str(directory) + 'blockchain_CC.txt'
                file_zip.write(file_zip_name, compress_type=zipfile.ZIP_DEFLATED)
                file_zip.close()
                
                res12 = []
                res12.append(res5[-1])
                text_file_name = str(directory) + 'blockchain_CC.txt'
                text_file = open(text_file_name, "wt")
                n = text_file.write(str(res12))
                text_file.close()
            
            if n != 0:
                update_chain_feedback = "chain updated"
                print("Count - " + str(count) + " Chain Update Feedback - "+ str(update_chain_feedback))
            

    time.sleep(5)
    count = count+1    


