##################################################################
# Codigo para encontrar los ratios caracteristicos
# 
# Utiliza una base de datos con archivos json
# Para ubicar la base de datos modificar 'path'
# 
# path = "PROSIM/"
# 
# 
#################################################################


import json
import os
from matplotlib import pyplot as plt
import numpy as np
from sklearn.preprocessing import normalize
import statistics
path = "PROSIM/"
ext = '.json'

#subject = 1
#record = 1
#version = 4.0
#archive = "subject_" + str(subject) + "_Rec" + str(record) + "_VEsfigmo" + str(version) + "_2022-11-16" + ".json"

def linearization(array_x, array_y):
    sumx = 0
    sumxsq = 0
    sumy = 0
    sumxy = 0

    for i in range(len(array_x)):
        sumx += array_x[i]
        sumy += array_y[i]
        sumxsq += array_x[i]**2
        sumxy += array_x[i]*array_y[i]
    
    d = len(array_x) * sumxsq - sumx**2
    m = (len(array_x) * sumxy - sumx * sumy) / d
    b = (sumy * sumxsq - sumx * sumxy) / d

    return m, b

# def normalize(arr, t_min, t_max):
#     norm_arr = []
#     diff = t_max - t_min
#     diff_arr = max(arr) - min(arr)
#     for i in arr:
#         temp = (((i - min(arr))*diff)/diff_arr) + t_min
#         norm_arr.append(temp)
#     return norm_arr

if __name__ == '__main__' :

    temp = 0 
    results_list = []
    

    for file in os.listdir(path):
        if file.endswith(ext):
            with open(path+file) as f:
                data = f.read()
                data = json.loads(data)
                #data = np.concatenate(([data["pressure"]],[data["pulse"]]))
                #data = np.transpose(data)
                pulso_map = max(data['pulse'])
                map = data['pressure'][data['pulse'].index(pulso_map)]

                diastolic_limits = [[x for x in data['pressure'] if x <= data['TheoricalDiastolic']][-1]]
                diastolic_limits.append([x for x in data['pressure'] if x > data['TheoricalDiastolic']][0])
                if data['TheoricalSistolic'] < data['pressure'][-1]:
                    systolic_limits = [[x for x in data['pressure'] if x < data['TheoricalSistolic']][-1]]
                    systolic_limits.append([x for x in data['pressure'] if x >= data['TheoricalSistolic']][0])
                else:
                    systolic_limits = [[x for x in data['pressure'] if x < data['TheoricalSistolic']][-2]]
                    systolic_limits.append([x for x in data['pressure'] if x < data['TheoricalSistolic']][-1])

                diastolic_pulses = [data['pulse'][data['pressure'].index(diastolic_limits[0])]]
                diastolic_pulses.append(data['pulse'][data['pressure'].index(diastolic_limits[1])])

                systolic_pulses = [data['pulse'][data['pressure'].index(systolic_limits[0])]]
                systolic_pulses.append(data['pulse'][data['pressure'].index(systolic_limits[1])])

                diastolic_m, diastolic_b = linearization(diastolic_limits, diastolic_pulses)
                systolic_m, systolic_b = linearization(systolic_limits, systolic_pulses)

                diastolic_pulse = diastolic_b + diastolic_m * data['TheoricalDiastolic']
                systolic_pulse = systolic_b + systolic_m * data['TheoricalSistolic']

                differential_pulse = data['TheoricalSistolic'] - data['TheoricalDiastolic']

                systolic_ratio = systolic_pulse / pulso_map
                diastolic_ratio = diastolic_pulse / pulso_map

                results_list.append({"pressure-pulse":differential_pulse,
                                    "theorical-systolic":data['TheoricalSistolic'],
                                    "theorical-diastolic":data['TheoricalDiastolic'],
                                    "ratio-diastolic":diastolic_ratio,
                                    "ratio-systolic":systolic_ratio})

                print(data['TheoricalDiastolic'],data['TheoricalSistolic'])
                print(differential_pulse,diastolic_ratio,systolic_ratio)

    variance = []
    dic_pressure_pulse = {}
    normalize_pressure_pulse = {}

    for i in range(16):
        dic_pressure_pulse[str((i+1)*10)] = []
        # normalize_pressure_pulse[str((i+1)*10)] = []

    salto = 10
    offset = 15
    for iter in results_list:
        pressure_pulse = iter['pressure-pulse']

        for i in range(16):
            tag = str((i+1)*10)
            if pressure_pulse > (offset + salto*i) and pressure_pulse <= (offset + salto*(i+1)):
                dic_pressure_pulse[tag].append([iter['ratio-diastolic'],iter['ratio-systolic']])
                
    for i in range(16):
        tag = str((i+1)*10)
        if len(dic_pressure_pulse[tag]) >= 2:
            diastolic_temp = []
            systolic_temp = []

            for j in range(len(dic_pressure_pulse[tag])):
                diastolic_temp.append(dic_pressure_pulse[tag][j][0])
                systolic_temp.append(dic_pressure_pulse[tag][j][1])
            diastolic_norm = normalize([diastolic_temp])
            systolic_norm = normalize([systolic_temp])
            variance.append([statistics.stdev(diastolic_temp),statistics.stdev(systolic_temp)])
            print(tag)
            print(diastolic_temp, systolic_temp, variance[-1])
    
    results_json = json.dumps(results_list)
    
    jsonFile = open("ratios.json","w")
    jsonFile.write(results_json)
    jsonFile.close()

    #print(data['TheoricalDiastolic'], data['TheoricalSistolic'], diastolic_pulse, systolic_pulse, pulso_map, data['pressure'], data['pulse'])              
    #plt.plot(data['pressure'],data['pulse'])
    #plt.show()