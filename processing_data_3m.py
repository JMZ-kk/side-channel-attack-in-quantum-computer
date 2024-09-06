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

json_files = glob.glob(os.path.join('data', '*.json'))
bench_total_energy_list = []
bench_duration_list = []
bench_mean_power_list = []
bench_total_power_traces = []
bench_index = []
bound = 64
for json_file in json_files:
    filename = os.path.basename(json_file)
    temp = filename.split('_')
    if int(temp[1].split('.')[0]) >= bound:
        continue
    print(filename)
    bench = int(temp[0])
    with open(json_file, 'r') as file:
        data = json.load(file)
        total_energy = data['total_energy']
        duration = data['duration']
        mean_power = data['mean_power']
        total_power_trace = data['total_power_trace']
        bench_total_energy_list.append(total_energy)
        bench_duration_list.append(duration)
        bench_mean_power_list.append(mean_power)
        bench_total_power_traces.append(total_power_trace)
        bench_index.append(bench)

for error_rate in [0, 0.00001, 0.0001, 0.001, 0.01, 0.1]:
    X = range(7)
    Y = np.zeros((3, len(X)))
    idx = 0
    for layout_n in [1, 2, 4, 8, 16, 32, 64]:
        last_bench = -1
        chosen_indexes = []
        tp = 0
        for i in range(len(bench_index)):
            if last_bench != bench_index[i]:
                last_bench = bench_index[i]
                tp = 1
                chosen_indexes.append(i)
            elif tp < layout_n:
                tp += 1
                chosen_indexes.append(i)
        corrects = np.zeros(4)
        try_times = 30
        for j in range(try_times):
            ans = random.choice(chosen_indexes)
            new_duration = bench_duration_list[ans] * (1 + np.random.normal(0, error_rate))
            new_total_energy = bench_total_energy_list[ans] * (1 + np.random.normal(0, error_rate))
            new_mean_power = bench_mean_power_list[ans] * (1 + np.random.normal(0, error_rate))
            new_power_trace = np.array(bench_total_power_traces[ans])
            for i in range(len(new_power_trace)):
                new_power_trace[i] = new_power_trace[i] * (1 + np.random.normal(0, error_rate))
            guess = 0
            for i in range(len(bench_duration_list)):
                if abs(bench_duration_list[i] - new_duration) < abs(bench_duration_list[guess] - new_duration):
                    guess = i
            if guess == ans:
                corrects[0] += 1
            guess = 0
            for i in range(len(bench_total_energy_list)):
                if abs(bench_total_energy_list[i] - new_total_energy) < abs(
                        bench_total_energy_list[guess] - new_total_energy):
                    guess = i
            if guess == ans:
                corrects[1] += 1
            guess = 0
            for i in range(len(bench_total_energy_list)):
                if abs(bench_mean_power_list[i] - new_mean_power) < abs(bench_mean_power_list[guess] - new_mean_power):
                    guess = i
            if guess == ans:
                corrects[2] += 1

        Y[0][idx] = corrects[0] / (try_times)
        Y[1][idx] = corrects[1] / (try_times)
        Y[2][idx] = corrects[2] / (try_times)
        idx+=1

    plt.ylim(0, 1)
    plt.xticks(X)
    plt.plot(X, Y[0], label='Duration')
    plt.plot(X, Y[1], label='Energy')
    plt.plot(X, Y[2], label='Mean Power')
    plt.title('Error rate: ' + str(error_rate))
    plt.xlabel('$Log_2(No. Layout)$')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('er ' + str(error_rate) + '.png')
    plt.clf()
