# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:33:32 2020

@author: lab-user
"""

import struct as st
import pandas as pd
import numpy as np
import subprocess
import zipfile
import socket
import json
import sys
#%%
directory = "/home/user/Desktop/BlockchainBasedSG/"

index_value_dict = dict()
index_value_dict = {11:1.0, 12:0.0, 13:71.95, 14:24.07, 21:1.0, 22:9.67, 23:163.0, 24:14.46}

def consumption_value_calc(dataPack):
    
    ini_list = str(dataPack)
            
    
    res = json.loads(ini_list)
    
    
    
    measurement_index_list = []
    measurement_values_list = []
    
    for nodes in res:
        for i in range(len(nodes)):
            try:
                measurement_index_list.append(nodes[2*i])
                measurement_values_list.append(nodes[2*i+1])
                
            except:
                continue
    
    
    df_measurement = pd.DataFrame()
    df_measurement['index'] =  measurement_index_list
    df_measurement['values'] =  measurement_values_list
    
    final_df_measurement = df_measurement.sort_values(['index'], ascending=True)
    final_df_measurement = final_df_measurement.reset_index(drop = True)
    final_df_measurement['consumption_type'] = final_df_measurement.apply(lambda row: 'Vm' if(row['index']%10 == 1) else ('Vp' if (row['index']%10 == 2) else ( 'P' if (row['index']%10 == 3) else ('Q' if(row['index']%10 == 4) else '' ))), axis = 1)
    
    final_df_measurement_pivot = pd.DataFrame()
    final_df_measurement_pivot = pd.pivot_table(final_df_measurement, index = ['consumption_type'], values = ['values'], aggfunc = np.mean)
    final_df_measurement_pivot = final_df_measurement_pivot.reset_index()
    
    consumption_type_list = []
    values_list = []
    consumption_val_list = []
    final_consumption_val_list = []
    
    consumption_type_list = final_df_measurement_pivot['consumption_type'].to_list()
    values_list = final_df_measurement_pivot['values'].to_list()
    
    for i in range(len(consumption_type_list)):
        consumption_val_list.append(consumption_type_list[i])
        consumption_val_list.append(round(values_list[i],3))
        final_consumption_val_list.append(consumption_val_list)
        consumption_val_list = []

    return final_consumption_val_list

#%%

# Relays act as a server
tcp_ip = '0.0.0.0'
tcp_port = 20001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((tcp_ip, tcp_port))
s.listen(1)
con, address = s.accept()
print('Conneceted by ', address)

relay_resp_pack_list = []
count = 1
while 1:
    if (count%6) == 0:
        index_value_dict[12] = -300.0
    else:
        index_value_dict[12] = 0.0
        
    relay_req_pack = con.recv(1024)
    if not relay_req_pack:
        break

    if(len(relay_req_pack) == 10):
        # relay unpack the received data
        relay_unpack_req_and_len = st.unpack('<BB',relay_req_pack[0:2])
        relay_req_unpack_indices_len = len(relay_req_pack) - len(relay_unpack_req_and_len)
        relay_req_unpack_indices = st.unpack('{}B'.format(relay_req_unpack_indices_len), relay_req_pack[2:])
        
        relay_req_unpack_indices = list(relay_req_unpack_indices)
        relay_req_unpack_indices_values = [index_value_dict[i] for i in relay_req_unpack_indices]
        
        
        
        
        # relay pack the response data
        relay_resp = 11
        relay_resp_len = 2 + 5 * len(relay_req_unpack_indices_values)
        relay_resp_format = '<BB'
        for i in relay_req_unpack_indices_values:
            relay_resp_format += 'Bf'
        
        index_value_list = []
        for (a,b) in zip(relay_req_unpack_indices,relay_req_unpack_indices_values):
            index_value_list.append(a)
            index_value_list.append(b)
            
        relay_resp_pack = st.pack(relay_resp_format,relay_resp,relay_resp_len,*index_value_list)
        con.sendall(relay_resp_pack)
        relay_req_unpack_indices_values = []
        relay_req_unpack_indices = []
    else:
        dataPack1 = str(relay_req_pack.decode('utf-8'))
        
        if "Mining Data=" in dataPack1:
            
            '''
            [[51, 0.9800000190734863, 52, -4.019999980926514, 53, -90.0, 54, -30.0, 61, 1.0099999904632568, 62, 1.9299999475479126, 63, 0.0, 64, 0.0], [31, 1.0, 32, 4.769999980926514, 33, 85.0, 34, -3.6500000953674316, 41, 0.9900000095367432, 42, -2.4100000858306885, 43, 0.0, 44, 0.0], [71, 0.9900000095367432, 72, 0.6200000047683716, 73, -100.0, 74, -35.0, 81, 1.0, 82, 3.799999952316284, 83, 0.0, 84, 0.0, 91, 0.9599999785423279, 92, -4.349999904632568, 93, 0.0, 94, 0.0], [11, 1.0, 12, 0.0, 13, 71.94999694824219, 14, 24.06999969482422, 21, 1.0, 22, 9.670000076293945, 23, 163.0, 24, 14.460000038146973]]
            '''
            dataPack = relay_req_pack.decode('utf-8')
            dataPack = dataPack1.replace("Mining Data=","")
            consumption_val = consumption_value_calc(dataPack)
            
            final_consumption_val = []
            final_consumption_val.append(['consumption_data',consumption_val])
            final_consumption_val.append(['owner', 'R1'])
            final_consumption_val.append(['recipient', 'CC'])
            
            
            dataPack = str(final_consumption_val)
    
            blockchain_script_name = str(directory) + "blockchain_code.py"
            blockchain_script = blockchain_script_name
            blockchain_out1 = subprocess.check_output([sys.executable, 
                                          blockchain_script,
                                          dataPack])
            blockchain_out = blockchain_out1.decode("utf-8").strip('\n')

            ## Own blockchain copy
            blockchain_file1 = str(directory) + "blockchain_R1.txt"
            blockchain_file1 = open(blockchain_file1,"r")
            blockchain_file_data1 = blockchain_file1.read()
            dataPack5 = str(blockchain_file_data1)
            dataPack5 = dataPack5.replace("'", '"')
            res5 = json.loads(dataPack5)            ##res5 is for R1
            
            
            if (len(res5) > 10):
                filename_index = str(res5[-1]['index'])[0:-1]
                
                filename = str(directory) + "blockchain"+ str(filename_index) + "_R1.zip"
                file_zip = zipfile.ZipFile(filename, 'w')
                file_zip_name = str(directory) + "blockchain_R1.txt"
                file_zip.write(file_zip_name, compress_type=zipfile.ZIP_DEFLATED)
                 
                file_zip.close()
                
                res12 = []
                res12.append(res5[-1])
                text_file_name = str(directory) + "blockchain_R1.txt"
                text_file = open(text_file_name, "wt")
                n = text_file.write(str(res12))
                text_file.close()
            
            
            final_consumption_val = []
            con.sendall(blockchain_out1)
            count = count+1
        
        else:
            
            dataPack1 = str(relay_req_pack.decode('utf-8'))
            
            if "Updated Blockchain = " in dataPack1:
                
                ## Own blockchain copy
                blockchain_file_name = str(directory) + "blockchain_R1.txt"
                blockchain_file = open(blockchain_file_name,"r")
                blockchain_file_data = blockchain_file.read()
                dataPack2 = str(blockchain_file_data)
                dataPack2 = dataPack2.replace("'", '"')
                res2 = json.loads(dataPack2)            ##res2 is for R1
                
                # blockchain from DA
                blockchain_DA = []
                blockchain_DA = dataPack1.split("=")
                dataPack3 = blockchain_DA[1].strip(" ")
                dataPack3 = dataPack3.replace("'", '"')
                res3 = json.loads(dataPack3)
                
                if res3[-2] == res2[-1]:
                    blockchain_verification_feedback = "chain verified"
                    print("Chain verification feedback - "+ str(blockchain_verification_feedback))
                    con.sendall(blockchain_verification_feedback.encode('utf-8'))
            
            elif "Verified Blockchain = " in dataPack1:
                
                # blockchain copy from DA
                blockchain_DA = []
                blockchain_DA = dataPack1.split("=")
                dataPack4 = blockchain_DA[1].strip(" ")
                dataPack4 = dataPack4.replace("'", '"')
                res4 = json.loads(dataPack4)
                
                ## Own blockchain copy
                blockchain_file1_name = str(directory) + "blockchain_R1.txt"
                blockchain_file1 = open(blockchain_file_name,"r")
                blockchain_file_data1 = blockchain_file1.read()
                dataPack5 = str(blockchain_file_data1)
                dataPack5 = dataPack5.replace("'", '"')
                res5 = json.loads(dataPack5)            ##res5 is for R1
               
                
                res5.append(res4[-1])
                text_file_name = str(directory) + "blockchain_R1.txt"
                text_file = open(text_file_name, "wt")
                n = text_file.write(str(res5))
                text_file.close()

                if (len(res5) > 10):
                    filename_index = str(res5[-1]['index'])[0:-1]
                    filename = str(directory) + "blockchain"+ str(filename_index)+"_R1.zip"
                    file_zip = zipfile.ZipFile(filename, 'w')
                    file_zip_name = str(directory) + 'blockchain_R1.txt'
                    file_zip.write(file_zip_name, compress_type=zipfile.ZIP_DEFLATED)
                     
                    file_zip.close()
                    res12 = []
                    res12.append(res5[-1])
                    
                    text_file_name = str(directory) + "blockchain_R1.txt"
                    text_file = open(text_file_name, "wt")
                    n = text_file.write(str(res12))
                    text_file.close()
                        
                if n != 0:
                    update_chain_feedback = "chain updated"
                    print("Chain Update Feedback - "+ str(update_chain_feedback))
                    con.sendall(update_chain_feedback.encode('utf-8'))
                    count = count+1
                    
            else:
                ## blockchain copy of DA
                dataPack1 = dataPack1.replace("'", '"')
                res1 = json.loads(dataPack1)            ## res1 is for DA

                ## Own blockchain copy
                blockchain_file_name = str(directory) + "blockchain_R1.txt"
                blockchain_file = open(blockchain_file_name,"r")
                blockchain_file_data = blockchain_file.read()
                dataPack2 = str(blockchain_file_data)
                dataPack2 = dataPack2.replace("'", '"')
                res2 = json.loads(dataPack2)            ##res2 is for R1
                
    
                if len(res1) < len(res2):               ## if DA has less entry than R1
                    # if((res1[-1] == res2[-1]) & ((res1[-2]) == res2[-2])):  
                    if(res1[-1] == res2[-1]):  
                        feedback_txt = "already updated"
                    else:
                        feedback_txt = "Blockchain manipulated"
                elif(len(res1) == len(res2)):
                    if (res1[-1] == res2[-1]):
                        feedback_txt = "already updated"
                else:
                    feedback_txt = "Blockchain manipulated"
                    
                
                print("Chain status feedback - " + str(feedback_txt))
                
                con.sendall(feedback_txt.encode('utf-8'))
        
