#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 17:59:14 2020

@author: mdtamjidhossain
"""
import pandas as pd
import json 
import sys
#%%

directory = "/home/user/Desktop/BlockchainBasedSG/"
DAScriptLocation = str(directory) + "selectMiningNode.py" 


'''
[[71, 0.9900000095367432, 72, 0.6200000047683716, 73, -100.0, 74, -35.0, 81, 1.0, 82, 3.799999952316284, 83, 0.0, 84, 0.0, 91, 0.9599999785423279, 92, -4.349999904632568, 93, 0.0, 94, 0.0], [11, 1.0, 12, 0.0, 13, 71.94999694824219, 14, 24.06999969482422, 21, 1.0, 22, 9.670000076293945, 23, 163.0, 24, 14.460000038146973], [31, 1.0, 32, 4.769999980926514, 33, 85.0, 34, -3.6500000953674316, 41, 0.9900000095367432, 42, -2.4100000858306885, 43, 0.0, 44, 0.0], [51, 0.9800000190734863, 52, -4.019999980926514, 53, -90.0, 54, -30.0, 61, 1.0099999904632568, 62, 1.9299999475479126, 63, 0.0, 64, 0.0]]
'''
#%%

def main(arg0, arg1):
    
    if ((str(arg0) == str(DAScriptLocation)) & (type(arg1) == str) & (str(arg1) != "")):
    
        ini_list = str(arg1)
        
        ini_list1, ini_list2 = ini_list.split('/')
    
        res1 = json.loads(ini_list1)
        
        res2 = json.loads(ini_list2) 


        measurement_index_list = []
        measurement_values_list = []
        
        for nodes in res1:
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
        
        actual_avg_values = final_df_measurement['values'].mean()
        
        res2_list1 = []
        res2_list2 = []
        for i in range(len(res2)):
            try:
                res2_list1.append(res2[2*i])
                res2_list2.append(res2[2*i+1])
            except:
                continue
            
        df_res2 = pd.DataFrame()
        df_res2['nodes'] = res2_list1
        df_res2['avg_values'] = res2_list2
        
        df_res2['abs_diff_from_actual_average'] = df_res2.apply(lambda row: abs(actual_avg_values - row['avg_values']), axis = 1)
        df_res2 = df_res2.sort_values('abs_diff_from_actual_average', ascending = True)
        df_res2 = df_res2.reset_index(drop = True)
        
        miningNode =  df_res2['nodes'][0]

    
        print(miningNode)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1])













    
