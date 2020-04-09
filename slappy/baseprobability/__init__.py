from math import log2
from collections import defaultdict


class BaseProbertilites:
    def __init__(self, traces, moves):
        self._traces = traces
        self._moves = moves
        self._size = sum(moves)
        self._probability = []
        self._logo = []
    
    def __len__(self):
        return self._size
    
    def at_call(self, f):
        self._probability = []
        trace_length = len(next(iter(self._traces.values()))[0])
        
        i = 0
        k = -1
        while i < trace_length:
            if self._moves[i] == 1:
                k += 1
                if k == f:
                    break
            i += 1
        k = 0
        while i < trace_length and k <= 200:
            if self._moves[i]:
                prop = {base: sum([t[i] for t in trace]) for base, trace in self._traces.items()}
                sum_traces = sum(prop.values())
                self._probability.append({base: k / sum_traces for base, k in prop.items() if k != 0})
            i += 1
        
        return self._probability
    
    def up_to_next_call(self, f):
        self._probability = []
        trace_length = len(next(iter(self._traces.values()))[0])
        prop = defaultdict(lambda: 0)
        i = 0
        k = -1
        while i < trace_length:
            if self._moves[i] == 1:
                k += 1
                if k == f:
                    break
            i += 1
        k = 0
        while i < trace_length and k <= 200:
            if self._moves[i] == 1:
                k += 1
                sum_traces = sum(prop.values())
                if sum_traces != 0:
                    self._probability.append({base: k / sum_traces for base, k in prop.items() if k != 0})
                prop = defaultdict(lambda: 0)
            for base, trace in self._traces.items():
                prop[base] += sum([t[i] for t in trace])
            i += 1
        sum_traces = sum(prop.values())
        if sum_traces != 0:
            self._probability.append({base: k / sum_traces for base, k in prop.items() if k != 0})
        return self._probability
    
    def around_call(self, f):
        trace_length = len(next(iter(self._traces.values()))[0])
        calls = []
        for i in range(trace_length):
            if self._moves[i]:
                calls.append(i)
        
        splits = set()
        saved_split = 0
        for i in range(len(calls)):
            if i + 1 < len(calls):
                next_call = calls[i + 1]
            else:
                next_call = trace_length
            splits.add((calls[i] + next_call) // 2)
            if i == max(f - 1, 0):
                saved_split = (calls[i] + next_call) // 2
        self._probability = []
        prop = defaultdict(lambda: 0)
        i = saved_split + 1 if f != 0 else 0
        pos_count = 0
        while i < trace_length and pos_count <= 200:
            if i in splits:
                sum_traces = sum(prop.values())
                self._probability.append({base: k / sum_traces for base, k in prop.items() if k != 0})
                pos_count += 1
                prop = defaultdict(lambda: 0)
            for base, trace in self._traces.items():
                prop[base] += sum([t[i] for t in trace])
            i += 1
        return self._probability
    
    def make_logo(self):
        e = 0
        self._logo = []
        for props in self._probability:
            h = -sum([f * log2(f) if f != 0 else 0 for f in props.values()])
            r = 2 - (h + e)
            self._logo.append({base: f * r for base, f in props.items()})
        return self._logo
    
    def order_by_probability(self, f=None, t=None):
        if f is None:
            f = 0
        if t is None:
            t = len(self._logo)
        for props in self._logo[f: t]:
            yield sorted([(base, x) for base, x in props.items()], key=lambda x: x[1])
    
    def get_probability(self):
        return self._probability
