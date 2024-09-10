import json

from qiskit import *
from qiskit.visualization import *
from qiskit.providers.fake_provider import FakeCasablancaV2
import numpy as np
import matplotlib.pyplot as plt
import qiskit.qasm2
import itertools
from qiskit.transpiler import Layout
import random

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

from qiskit import *

for num_qubits in range(1, 7):
    for i in range(int(pow(2,num_qubits))):
        s = format(i, '0'+str(num_qubits)+'b')
        n = len(s)
        qc = QuantumCircuit(n+1,n)
        qc.x(n)
        qc.h(range(n+1))
        for ii, yesno in enumerate(reversed(s)):
            if yesno == '1':
                qc.cx(ii, n)
        qc.h(range(n+1))
        qc.measure(range(n), range(n))
        simulator = FakeCasablancaV2()
        circ = transpile(qc, simulator)
        sched = schedule(circ, simulator)
        data = {
            'total_power_trace': list(get_bv_data(sched)),
        }
        with open('data_bv_2/' + 'bv_'+str(num_qubits) +'_'+ str(i) + '.json', 'w') as json_file:
            json.dump(data, json_file)


