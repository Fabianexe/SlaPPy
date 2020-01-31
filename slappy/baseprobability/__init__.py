from math import log2


class BaseProbertilites:
    def __init__(self, traces, moves, trace_id):
        self._traces = traces
        self._trace_id = trace_id
        self._moves = moves
        self._size = sum(moves)
        self._probability = []
        
    def __len__(self):
        return self._size
    
    def at_call(self, f):
        self._probability = []

        i = 0
        k = -1
        while i < len(self._traces):
            if self._moves[i] == 1:
                k += 1
                if k == f:
                    break
            i += 1
        k = 0
        while i < len(self._traces) and k <= 200:
            if self._moves[i]:
                sum_traces = 0
                prop = [0, 0, 0, 0]
                for j in range(8):
                    prop[j % 4] += self._traces[i][j]
                    sum_traces += self._traces[i][j]
                k += 1
                self._probability.append([k / sum_traces for k in prop])
            i += 1
        
        return self._probability
    
    def up_to_next_call(self, f):
        self._probability = []
        sum_traces = 0
        prop = [0, 0, 0, 0]
        i = 0
        k = -1
        while i < len(self._traces):
            if self._moves[i] == 1:
                k += 1
                if k == f:
                    break
            i += 1
        k = 0
        while i < len(self._traces) and k <= 200:
            if self._moves[i] == 1:
                k += 1
                if sum_traces != 0:
                    self._probability.append([k / sum_traces for k in prop])
                sum_traces = 0
                prop = [0, 0, 0, 0]
            
            for j in range(8):
                prop[j % 4] += self._traces[i][j]
                sum_traces += self._traces[i][j]
            i += 1
        if sum_traces != 0:
            self._probability.append([k / sum_traces for k in prop])
        return self._probability

    def around_call(self, f):
        calls = []
        for i in range(len(self._traces)):
            if self._moves[i]:
                calls.append(i)

        splits = set()
        saved_split = 0
        for i in range(len(calls)):
            if i+1 < len(calls):
                next_call = calls[i+1]
            else:
                next_call = len(self._traces)
            splits.add((calls[i] + next_call)//2)
            if i == max(f-1, 0):
                saved_split = (calls[i] + next_call)//2
        self._probability = []
        sum_traces = 0
        prop = [0, 0, 0, 0]
        i = saved_split+1 if f != 0 else 0
        pos_count = 0
        while i < len(self._traces) and pos_count <= 200:
            if i in splits:
                self._probability.append([k / sum_traces for k in prop])
                pos_count += 1
                sum_traces = 0
                prop = [0, 0, 0, 0]
            for j in range(8):
                prop[j % 4] += self._traces[i][j]
                sum_traces += self._traces[i][j]
            i += 1
        return self._probability
    
    def make_logo(self):
        e = 0
        new_prob = []
        for props in self._probability:
            h = -sum([f * log2(f) if f != 0 else 0 for f in props])
            r = 2 - (h+e)
            new_prob.append([f*r for f in props])
        self._probability = new_prob
        return self._probability
    
    def order_by_probability(self, f=None, t=None):
        if f is None:
            f = 0
        if t is None:
            t = len(self._probability)
        for props in self._probability[f: t]:
            yield sorted([(self._trace_id[i], x) for i, x in enumerate(props)], key=lambda x: x[1])
    
    def get_probability(self):
        return self._probability
