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

def get_bv_data(sched):
    time_series = {}
    total_power_trace = {}
    for time, instruction in sched.instructions:
        if isinstance(instruction, qiskit.pulse.Play):
            pulse_waveform = instruction.pulse
            channel = instruction.channel
            if isinstance(pulse_waveform, qiskit.pulse.library.ScalableSymbolicPulse):
                amplitude = pulse_waveform.get_waveform().samples
            else:
                amplitude = pulse_waveform.samples
            power = np.real(amplitude)**2 + np.imag(amplitude)**2
            start_time = time
            times = np.arange(start_time, start_time + len(power))
            if channel not in time_series:
                time_series[channel] = (times, power)
            else:
                existing_times, existing_power = time_series[channel]
                time_series[channel] = (np.concatenate([existing_times, times]),
                                        np.concatenate([existing_power, power]))

            for t, p in zip(times, power):
                if t in total_power_trace:
                    total_power_trace[t] += p
                else:
                    total_power_trace[t] = p
    total_times = np.array(sorted(total_power_trace.keys()))
    total_power = np.array([total_power_trace[t] for t in total_times])
    return total_power

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

try_times = 30
corrects=np.zeros(max_nq)
for nq in range(1,max_nq+1):
    base=circuit_list[nq]
    for j in range(try_times):
        ans = random.randint(0,len(base)-1)
        s = format(ans, '0' + str(nq) + 'b')
        n = len(s)
        qc = QuantumCircuit(n + 1, n)
        qc.x(n)
        qc.h(range(n + 1))
        for ii, yesno in enumerate(reversed(s)):
            if yesno == '1':
                qc.cx(ii, n)
        qc.h(range(n + 1))
        qc.measure(range(n), range(n))
        simulator = FakeCasablancaV2()
        circ = transpile(qc, simulator)
        sched = schedule(circ, simulator)
        new_power_trace = list(get_bv_data(sched))
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