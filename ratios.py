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

                # for i, presion_actual in enumerate(data):
                #     error = 0

                #     if i >= data.shape[0]:
                #         break
                    
                #     if (presion_iter >= presion_actual[0]) and (presion_iter < data[i+1][0]):
                #         m,b = linearization(data[:][0],data[:][1])
                #     else:
                #         continue

                #     temp = b + m*presion_iter

                #     if presion_iter <= map:
                #         error = abs(temp - data['TheoricalDiastolic'])
                #         if gerror_dia > error:
                #             gerror_dia = error

                #     else:
                #         error = abs(temp - data['TheoricalSistolic'])
                #         if gerror_sys > error:
                #             gerror_sys = error

    
    results_json = json.dumps(results_list)
    
    jsonFile = open("ratios.json","w")
    jsonFile.write(results_json)
    jsonFile.close()

    print(diastolic_limits,systolic_limits, diastolic_pulses, systolic_pulses, diastolic_pulse, systolic_pulse, data['pressure'], data['pulse'])       
    #print(data.shape[0])       
    #plt.plot(data['pressure'],data['pulse'])
    #plt.show()