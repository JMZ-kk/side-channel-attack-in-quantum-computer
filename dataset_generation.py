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

def getData(sched):
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
    time_intervals = np.diff(total_times, prepend=total_times[0])
    total_energy = np.sum(total_power * time_intervals)
    return total_energy,sched.duration,total_power

benchmarks=['QASMBench/small/deutsch_n2/deutsch_n2.qasm',
            'QASMBench/small/iswap_n2/iswap_n2.qasm',
            'QASMBench/small/quantumwalks_n2/quantumwalks_n2.qasm',
            'QASMBench/small/grover_n2/grover_n2.qasm',
            'QASMBench/small/dnn_n2/dnn_n2.qasm',
            'QASMBench/small/teleportation_n3/teleportation_n3.qasm',
            'QASMBench/small/qaoa_n3/qaoa_n3.qasm',
            'QASMBench/small/toffoli_n3/toffoli_n3.qasm',
            'QASMBench/small/linearsolver_n3/linearsolver_n3.qasm',
            'QASMBench/small/fredkin_n3/fredkin_n3.qasm',
            'QASMBench/small/wstate_n3/wstate_n3.qasm',
            'QASMBench/small/basis_change_n3/basis_change_n3.qasm',
            'QASMBench/small/qrng_n4/qrng_n4.qasm',
            'QASMBench/small/cat_state_n4/cat_state_n4.qasm',
            'QASMBench/small/inverseqft_n4/inverseqft_n4.qasm',
            'QASMBench/small/adder_n4/adder_n4.qasm',
            'QASMBench/small/hs4_n4/hs4_n4.qasm',
            'QASMBench/small/bell_n4/bell_n4.qasm',
            'QASMBench/small/qft_n4/qft_n4.qasm',
            'QASMBench/small/variational_n4/variational_n4.qasm',
            'QASMBench/small/vqe_uccsd_n4/vqe_uccsd_n4.qasm',
            # 'QASMBench/small/basis_trotter_n4/basis_trotter_n4.qasm',
            'QASMBench/small/qec_sm_n5/qec_sm_n5.qasm',
            'QASMBench/small/lpn_n5/lpn_n5.qasm',
            'QASMBench/small/qec_en_n5/qec_en_n5.qasm',
            'QASMBench/small/pea_n5/pea_n5.qasm',
            'QASMBench/small/error_correctiond3_n5/error_correctiond3_n5.qasm',
            'QASMBench/small/simon_n6/simon_n6.qasm',
            'QASMBench/small/qaoa_n6/qaoa_n6.qasm',
            'QASMBench/small/vqe_uccsd_n6/vqe_uccsd_n6.qasm',
            'QASMBench/small/hhl_n7/hhl_n7.qasm']
bench_total_energy_list = []
bench_duration_list = []
bench_mean_power_list = []
bench_total_power_traces = []
bench_index=[]
max_num=64
for bench in range(len(benchmarks)):
    qc = qiskit.qasm2.load(benchmarks[bench])
    n_q = qc.num_qubits
    simulator = FakeCasablancaV2()
    n_physical = simulator.num_qubits
    physical_bits = list(range(n_physical))
    possible_mappings = list(itertools.permutations(physical_bits, n_q))
    if len(possible_mappings)>max_num:
        possible_mappings = random.sample(possible_mappings, max_num)
    else:
        random.shuffle(possible_mappings)
    for i in range(len(possible_mappings)):
        mapping = possible_mappings[i]
        layout_dict = {qc.qubits[virtual]: physical for virtual, physical in enumerate(mapping)}
        layout = Layout(layout_dict)
        circ = transpile(qc, simulator, initial_layout=layout)
        sched = schedule(circ, simulator)
        total_energy, duration, total_power_trace = getData(sched)
        mean_power = total_energy / duration
        data = {
            'total_energy': total_energy,
            'duration': duration,
            'mean_power': round(mean_power, 5),
            'total_power_trace': list(total_power_trace),
        }
        with open('data_64/'+str(bench)+'_'+str(i)+'.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)


# for error_rate in [0, 0.00001, 0.0001, 0.001, 0.01, 0.1]:
#     for layout_n in [1, 2, 4, 8, 16, 32, 64, 128]:
#         circuit_list = chosen_indexes[layout_n]
#         ans = random.randint(0, len(circuit_list) - 1)
#
#         new_duration = duration_list[ans] * (1 + np.random.normal(0, error_rate))
#         new_total_energy = total_energy_list[ans] * (1 + np.random.normal(0, error_rate))
#         new_mean_power = mean_power_list[ans] * (1 + np.random.normal(0, error_rate))
#         total_power_trace = total_power_traces[ans]
#         new_power_trace = np.array(total_power_trace)
#         for i in range(len(new_power_trace)):
#             new_power_trace[i] = new_power_trace[i] * (1 + np.random.normal(0, error_rate))
#
#             guess = 0
#             for i in range(len(possible_mappings)):
#                 if abs(duration_list[i] - new_duration) < abs(duration_list[guess] - new_duration):
#                     guess = i
#             if guess == ans:
