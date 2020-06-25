
"""
Created on Wed Feb 12 16:19:58 2020

@author: lab-user
"""
import pandas as pd
import numpy as np
import struct as st
import subprocess
import zipfile
import socket
import json
import sys

#%%
directory = "/home/user/Desktop/BlockchainBasedSG/"

node_indices_dict = dict()        

node_indices_dict = {'R1': [11, 12, 13, 14, 21, 22, 23, 24],
                   'R2': [31, 32, 33, 34, 41, 42, 43, 44],
                   'R3': [51, 52, 53, 54, 61, 62, 63, 64],
                   'R4': [71, 72, 73, 74, 81, 82, 83, 84, 91, 92, 93, 94]}

index_value_dict = dict()

relay_port_dict = dict()
relay_port_dict = {'R1':20001,'R2':20002,'R3':20003,'R4':20004}
relay_host_dict = {'R1': '10.0.0.11',"R2":'10.0.0.12' ,'R3':'10.0.0.13','R4':'10.0.0.14'}

relay_socket_dict = {}

print("Initiating comm to relays beforehand")
for relay in relay_host_dict:
    p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p.connect((relay_host_dict[relay], relay_port_dict[relay]))
    relay_socket_dict[relay] = p
    print('Relay {} is connected'.format(relay))

#%%
relay_resp_unpack_indices_list = []
def reemovNestings(l): 
    for i in l: 
        if type(i) == list: 
            reemovNestings(i) 
        else: 
            relay_resp_unpack_indices_list.append(i)


#%%

# DA acts as a server
tcp_ip = '0.0.0.0'
tcp_port = 20000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((tcp_ip, tcp_port))
s.listen(1)
con, address = s.accept()
print('Conneceted by ', address)

data_list = []
relay_resp_unpack_indices_nested_list = []

while 1:
    cc_req_pack = con.recv(1024)                    ## receiving data request from CC 
    if not cc_req_pack:
        break
    
    # DA receives req from CC, unpack it and acts as a server
    da_unpack_req_and_len = st.unpack('<BB',cc_req_pack[0:2])
    da_unpack_indices_len = len(cc_req_pack) - len(da_unpack_req_and_len)
    
    da_unpack_indices = st.unpack('{}B'.format(da_unpack_indices_len), cc_req_pack[2:])
    
    
    # DA creates a request packet for each Relay and acts as client 
    
    da_unpack_indices = list(da_unpack_indices)
    da_indices_dict = dict()
    lst = []
    for i in range (len(da_unpack_indices)):
        for key, value in node_indices_dict.items():
            if da_unpack_indices[i] in value:
                if key not in da_indices_dict.keys():
                    lst = [da_unpack_indices[i]]
                    da_indices_dict[key] = lst  
                    lst = []
                else:
                    lst = da_indices_dict[key]
                    lst.append(da_unpack_indices[i])
                    da_indices_dict.update(key = lst)
                    lst = []
    
    da_indices_dict.pop('key',None)
    
    ## formatting request packet for each relay ------------start------------
    da_req_pack_dict = dict()
    for key, value in da_indices_dict.items():
        da_req_indices = da_indices_dict[key]
        da_req = 1
        da_req_len = len(da_req_indices)+2
        da_req_format = '<BB{}B'.format(len(da_req_indices))
        da_req_pack = st.pack(da_req_format,da_req,da_req_len,*da_req_indices)
        lst = [da_req_pack]
        da_req_pack_dict[key] = lst
        lst =[]
    ## formatting request packet for each relay ------------start------------
        
        
    # DA sends and recieve packet to/from each relay and keep it in a list  
        
    for key, value in da_req_pack_dict.items():
        p = relay_socket_dict[key]
        p.sendall(da_req_pack_dict[key][0])     ## sending request for data to relays
        data = p.recv(1024)                     ## reciving response data from relays
        data_list.append(data)
    
    
    ## unpacking relay data ----------------start--------------------
    da_resp_list = []
    for i in range(len(data_list)):
        relay_resp_pack = data_list[i]
        relay_resp_unpack = st.unpack('<BB',relay_resp_pack[0:2])
        relay_resp_unpack_indices_len = len(relay_resp_pack) - len(relay_resp_unpack)
        
        relay_resp_format='<BB'
        for i in range(int((relay_resp_unpack_indices_len)/5)):
            relay_resp_format += 'Bf'
        
        relay_resp_unpack_indices = st.unpack((relay_resp_format[:1]+relay_resp_format[3:]), relay_resp_pack[2:])
        
        relay_resp_unpack_indices = list(relay_resp_unpack_indices)
        relay_resp_unpack_indices_nested_list.append(relay_resp_unpack_indices)
    
    reemovNestings(relay_resp_unpack_indices_nested_list)
    

    ## unpacking relay data ----------------end--------------------
    

    
    ##-------------------Node wise average calculation start---------------------------
    
    index_value_list = []
    for i in relay_resp_unpack_indices_nested_list:
        for p in i:
            index_value_list.append(p)
            
    for i in range(len(index_value_list)):
        try:
            index_value_dict[index_value_list[2*i]] = index_value_list[2*i+1]
        except:
            pass        
    # if((index_value_dict[12] == -300.0) | (index_value_dict[64] == 179.0474) | (index_value_dict[84] == 250)):
    #     print(index_value_dict)
    df_measurement = pd.DataFrame()

    keyList = []
    valuesList = []
    
    for key in node_indices_dict:
        # print(key, node_indices_dict[key])
        for i in node_indices_dict[key]:
            keyList.append(key)
            valuesList.append(index_value_dict[i])
            

    

    df_measurement['nodes'] = keyList
    df_measurement['values'] = valuesList

    
    df_measurement_pivot = pd.DataFrame()
    df_measurement_pivot = pd.pivot_table(df_measurement, index = ['nodes'], values = ['values'], aggfunc = np.mean)
    df_measurement_pivot.reset_index(inplace=True)
    
    
    nodes_list = []
    avg_list = []
    final_avg_list = []
    nodes_list = df_measurement_pivot['nodes'].to_list()
    avg_list = df_measurement_pivot['values'].to_list()
    
    for i in range(len(nodes_list)):
        final_avg_list.append(nodes_list[i])
        final_avg_list.append(avg_list[i])
   ##-------------------Node wise average calculation end------------------------------
    
    
    ##-------------------Mining Node Selection start--------------------------------------
    final_avg_list = str(final_avg_list)
    final_avg_list = final_avg_list.replace("'", '"')
    dataPack = str(relay_resp_unpack_indices_nested_list) + "/" + str(final_avg_list)
    
    # print(dataPack)
    
    miningNodeSelect_script = str(directory) + "selectMiningNode.py"
    miningNode = subprocess.check_output([sys.executable, 
                                  miningNodeSelect_script,
                                  dataPack])
    miningNode = miningNode.decode("utf-8").strip('\n')
    
    print("Mining Node selection feedback ----------"+ str(miningNode) + "------------has been selected as mining node")
    
    '''
    [[71, 0.9900000095367432, 72, 0.6200000047683716, 73, -100.0, 74, -35.0, 81, 1.0, 82, 3.799999952316284, 83, 0.0, 84, 0.0, 91, 0.9599999785423279, 92, -4.349999904632568, 93, 0.0, 94, 0.0], [11, 1.0, 12, 0.0, 13, 71.94999694824219, 14, 24.06999969482422, 21, 1.0, 22, 9.670000076293945, 23, 163.0, 24, 14.460000038146973], [31, 1.0, 32, 4.769999980926514, 33, 85.0, 34, -3.6500000953674316, 41, 0.9900000095367432, 42, -2.4100000858306885, 43, 0.0, 44, 0.0], [51, 0.9800000190734863, 52, -4.019999980926514, 53, -90.0, 54, -30.0, 61, 1.0099999904632568, 62, 1.9299999475479126, 63, 0.0, 64, 0.0]]
    '''
    ##-------------------Mining Node Selection end--------------------------------------
    
    
    ##-------------------Sending blockchain and data to mining node start----------------
    
    blockchain_file_name = str(directory) + "blockchain_DA.txt"
    
    blockchain_file = open(blockchain_file_name,"r")

    blockchain_file_data = blockchain_file.read()
    
    dataPack6 = str(blockchain_file_data)
    dataPack6 = dataPack6.replace("'", '"')
    res6 = json.loads(dataPack6) 

    if len(res6) > 1:
        blockchain_file_data = res6[-2:]

    else:
        blockchain_file_data = res6[-1:]

    
    feedback_data_from_relay_list = []

    
    nodeList = ['R1', 'R2', 'R3', 'R4']
    for i in nodeList:
        p = relay_socket_dict[i]
        
        p.sendall(str(blockchain_file_data).encode('utf-8'))
        feedback_data_from_relay = p.recv(1024) 
        feedback_data_from_relay = feedback_data_from_relay.decode('utf-8')
        feedback_data_from_relay_list.append(feedback_data_from_relay)
        feedback_data_from_relay = ""
 
    
    print("Chain status feedback - "+ str(feedback_data_from_relay_list))
    
    if feedback_data_from_relay_list == ['already updated', 'already updated', 'already updated', 'already updated']:
        p = relay_socket_dict[miningNode]
        MiningData = "Mining Data="+str(relay_resp_unpack_indices_nested_list)
        p.sendall(str(MiningData).encode('utf-8'))
        mining_feedback = p.recv(1024)
    else:
        pass
    mining_feedback = mining_feedback.decode('utf-8')
    
    mining_feedback1 = []
    
    
    if (("New block successfully added to the blockchain and verification also successful|" in mining_feedback) | ("New block successfully added to the blockchain but verification has not been carried out due to only 2 blocks available|" in mining_feedback)):
        mining_feedback1 = mining_feedback.split('|')
        mining_feedback2 = str(mining_feedback1[1])
        
        blockchain_verification_feedback_list = []
        nodeList_modified = nodeList
        nodeList_modified.remove(miningNode)                     ## removing mining node from verification process
        for i in nodeList_modified:
            p = relay_socket_dict[i]
            
            p.sendall(str(mining_feedback2).encode('utf-8'))
            # print(str(mining_feedback2))
            blockchain_verification_feedback = p.recv(1024) 
            blockchain_verification_feedback = blockchain_verification_feedback.decode('utf-8')
            blockchain_verification_feedback_list.append(blockchain_verification_feedback)
            blockchain_verification_feedback = ""
            # time.sleep(0.5)
            
        
        ## Own blockchain copy
        blockchain_file_name = str(directory) +  "blockchain_DA.txt"   
        blockchain_file = open(blockchain_file_name,"r")
        blockchain_file_data = blockchain_file.read()
        dataPack2 = str(blockchain_file_data)
        dataPack2 = dataPack2.replace("'", '"')
        res2 = json.loads(dataPack2)            ##res2 is for DA
        
        # blockchain from Mining Node
        blockchain_mining_node = []
        blockchain_mining_node = mining_feedback2.split("=")
        dataPack3 = blockchain_mining_node[1].strip(" ")
        dataPack3 = dataPack3.replace("'", '"')
        res3 = json.loads(dataPack3)            ## res3 is from Mining Node
        
        if res3[-2] == res2[-1]:
            blockchain_verification_feedback = "chain verified"
            blockchain_verification_feedback_list.append(blockchain_verification_feedback)
        print("Chain verification feedback - "+ str(blockchain_verification_feedback_list))
        
        if blockchain_verification_feedback_list == ['chain verified', 'chain verified', 'chain verified', 'chain verified']:
            verified_chain = mining_feedback2.replace("Updated Blockchain = ", "Verified Blockchain = ")
            verified_chain_feedback_list = []
            
            for i in nodeList_modified:
                p = relay_socket_dict[i]
                p.sendall(str(verified_chain).encode('utf-8'))
                verified_chain_feedback = p.recv(1024) 
                verified_chain_feedback = verified_chain_feedback.decode('utf-8')
                verified_chain_feedback_list.append(verified_chain_feedback)
                verified_chain_feedback = ""
            
        if verified_chain_feedback_list == ['chain updated', 'chain updated', 'chain updated']:
            ## Own blockchain copy
            blockchain_file1_name = str(directory) + 'blockchain_DA.txt'
            blockchain_file1 = open(blockchain_file1_name,"r")
            blockchain_file_data1 = blockchain_file1.read()
            dataPack5 = str(blockchain_file_data1)
            dataPack5 = dataPack5.replace("'", '"')
            res5 = json.loads(dataPack5)            ##res2 is for R1
            blockchain_file1.close()
            con.sendall(str(verified_chain).encode('utf-8'))
            
            res5.append(res3[-1])
            
            text_file_name = str(directory) + "blockchain_DA.txt"
            text_file = open(text_file_name, "wt")
            n = text_file.write(str(res5))
            text_file.close()
            verified_chain_feedback_list.append('chain updated')
            print("Chain Update Feedback - "+ str(verified_chain_feedback_list))
            
            if (len(res5) > 10):
                filename_index = str(res5[-1]['index'])[0:-1]
                filename = str(directory)+ "blockchain"+ str(filename_index)+"_DA.zip"
                file_zip = zipfile.ZipFile(filename, 'w')
                file_zip_name = str(directory) + "blockchain_DA.txt"
                file_zip.write(file_zip_name, compress_type=zipfile.ZIP_DEFLATED)
                 
                file_zip.close()
                res12 = []
                res12.append(res5[-1])
                text_file_name = str(directory) + "blockchain_DA.txt"
                text_file = open(text_file_name, "wt")
                n = text_file.write(str(res12))
                text_file.close()
                
    
    ## seeting all variables to NULL ----------start--------------
    relay_resp_unpack_indices_list = []
    relay_resp_unpack_indices_nested_list = []
    relay_resp_unpack_indices = []
    data_list = []
    da_resp_pack = ''
    print("---------------------------------------")
    ## seeting all variables to NULL ----------end--------------
    

