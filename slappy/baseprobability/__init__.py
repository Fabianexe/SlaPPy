from math import log2

trace_id = ['A', 'C', 'G', 'U']

class BaseProbertilites:
    def __init__(self, traces, moves):
        self._traces = traces
        self._moves = moves
        self._size = sum(moves)
        self._probability = []
        
    def __len__(self):
        return self._size
    
    def at_call(self):
        self._probability = []
        for i in range(len(self._traces)):
            if self._moves[i]:
                sum_traces = 0
                prop = [0, 0, 0, 0]
                for j in range(8):
                    prop[j % 4] += self._traces[i][j]
                    sum_traces += self._traces[i][j]
                self._probability.append([k / sum_traces for k in prop])
        
        return self._probability
    
    def up_to_next_call(self):
        self._probability = []
        sum_traces = 0
        prop = [0, 0, 0, 0]
        for i in range(len(self._traces)):
            if self._moves[i] == 1:
                print(len(self._probability))
                if sum_traces != 0:
                    self._probability.append([k / sum_traces for k in prop])
                sum_traces = 0
                prop = [0, 0, 0, 0]
            
            
            for j in range(8):
                prop[j % 4] += self._traces[i][j]
                sum_traces += self._traces[i][j]
        if sum_traces != 0:
            self._probability.append([k / sum_traces for k in prop])
        return self._probability

    def around_call(self):
        calls = []
        for i in range(len(self._traces)):
            if self._moves[i]:
                calls.append(i)

        splits = set()
        for i in range(len(calls)):
            if i+1 < len(calls):
                next_call = calls[i+1]
            else:
                next_call = len(self._traces)
            splits.add((calls[i] + next_call)//2)
        self._probability = []
        sum_traces = 0
        prop = [0, 0, 0, 0]
        for i in range(len(self._traces)):
            if i in splits:
                self._probability.append([k / sum_traces for k in prop])
                sum_traces = 0
                prop = [0, 0, 0, 0]
            for j in range(8):
                prop[j % 4] += self._traces[i][j]
                sum_traces += self._traces[i][j]
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
    
    def order_by_probability(self):
        i = 0
        for props in self._probability:
            print(i)
            i+=1
            yield sorted([(trace_id[i], x) for i, x in enumerate(props)], key=lambda x: x[1])
    
    def get_probability(self):
        return self._probability
