from qiskit import *
from qiskit.visualization import *
from qiskit.providers.fake_provider import FakeCasablancaV2
import numpy as np
import matplotlib.pyplot as plt
import qiskit.qasm2
import itertools
from qiskit.transpiler import Layout
import random
import json
import os
import glob
import pickle

circuit_list= {}
max_nq=6
for nq in range(1,max_nq+1):
    circuit_list[nq]=[]
json_files = glob.glob(os.path.join('data_bv_2', '*.json'))
for json_file in json_files:
    filename = os.path.basename(json_file)
    tp=filename.split('_')
    with open(json_file, 'r') as file:
        data = json.load(file)
        total_power_trace = data['total_power_trace']
        circuit_list[int(tp[1])].append(total_power_trace)

try_times = 300
corrects=np.zeros(max_nq)
for nq in range(1,max_nq+1):
    base=circuit_list[nq]
    for j in range(try_times):
        ans = random.randint(0,len(base)-1)
        new_power_trace = np.array(base[ans])
        guess = 0
        min_dis=999999999
        for i in range(len(base)):
            if len(new_power_trace) == len(base[i]):
                t_dis = 0
                for j in range(len(new_power_trace)):
                    t_dis +=abs(10000*base[i][j] - 10000*new_power_trace[j])
                if t_dis < min_dis:
                    min_dis=t_dis
                    guess=i
        if guess == ans:
            corrects[nq-1] += 1

corrects/=try_times
X = range(1,max_nq+1)
plt.xlabel('Number of qubits')
plt.ylabel('Accuracy')
plt.plot(X, corrects, label='Total Power Trace')
plt.savefig('bv_co.png')