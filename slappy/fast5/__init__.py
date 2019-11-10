import h5py
import numpy as np


class Fast5Read:
    def __init__(self, name, read):
        self._name = name
        self._read = read
        
    def get_name(self):
        return self._name
    
    def get_raw(self):
        return np.asarray(self._read['Raw/Signal'])
    
    def get_raw_g0(self):
            return [x if x >= 0 else 0 for x in self.get_raw()]
    
    def get_basecals(self):
        return [x.split('_')[-1] for x in filter(lambda x: x.startswith('Basecall_'), self._read['Analyses'].keys())]
    
    def get_seq(self, basecall_group='000'):
        return self.get_fastq(basecall_group).split('\n')[1].strip()[::-1]
    
    def get_rev_seq(self, basecall_group='000'):
        return self.get_fastq(basecall_group).split('\n')[1].strip()
    
    def get_moves(self, basecall_group='000'):
        path = 'Analyses/Basecall_1D_{group}/BaseCalled_template/Move'.format(group=basecall_group)
        return np.asarray(self._read[path])
    
    def get_traces(self, basecall_group='000'):
        path = 'Analyses/Basecall_1D_{group}/BaseCalled_template/Trace'.format(group=basecall_group)
        return np.asarray(self._read[path])
    
    def get_step(self, basecall_group='000'):
        path = 'Analyses/Basecall_1D_{group}/Summary/basecall_1d_template'.format(group=basecall_group)
        return int(self._read[path].attrs["block_stride"])
    
    def get_start(self, basecall_group='000'):
        path = 'Analyses/Segmentation_{group}/Summary/segmentation'.format(group=basecall_group)
        return int(self._read[path].attrs["first_sample_template"])

    def get_fastq(self, basecall_group='000'):
        path = 'Analyses/Basecall_1D_{group}/BaseCalled_template/Fastq'.format(group=basecall_group)
        return self._read[path][()].decode('UTF-8')
    
    def get_basepositions(self, basecall_group='000'):
        moves = self.get_moves(basecall_group)
        start = self.get_start(basecall_group)
        step = self.get_step(basecall_group)
        basepoints = []
        for i in range(len(moves)):
            if moves[i]:
                basepoints.append(start + (step * i))
        return basepoints


class Fast5:
    def __init__(self, path, mode='r'):
        self.root = h5py.File(path, mode=mode)
        
    def __iter__(self):
        for read_name in self.root:
                yield read_name

    def __getitem__(self, item):
        return Fast5Read(item, self.root[item])
    
    def get_basecall_groups(self):
        read = self.root[next(iter(self))]
        for group in read['Analyses']:
            if group.startswith('Basecall'):
                end = group.split('_')[-1]
                name = read['Analyses'][group].attrs["name"].decode('UTF-8')
                yield name, end
