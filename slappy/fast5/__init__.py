"""Classes to interact with Fast5 files"""
import h5py
import numpy as np


class Fast5Read:
    """Class that represents one read in a multi fast5 file"""
    
    def __init__(self, name, read):
        """Construct the read
        
        :param name: The name of the read as it is in the fast5 file
        :param read: The read as h5py object
        """
        self._name = name
        self._read = read
    
    def get_name(self):
        """Get the name of the read.
        
        :return: The name of the read as str.
        """
        return self._name
    
    def get_raw(self):
        """Get the raw data points of the read
        
        :return: The raw data as numpy array
        """
        return np.asarray(self._read['Raw/Signal'])
    
    def get_raw_g0(self):
        """ Get the raw data points of the read. Where every point with a value <0 is set to 0.
        
        :return: The corrected raw data as numpy array
        """
        return [x if x >= 0 else 0 for x in self.get_raw()]
    
    def get_basecals(self):
        """Get the id of ever bascall group that is present in the read. This can be used in the other functions.
        
        :return: The id (three numbers) as array
        """
        return [x.split('_')[-1] for x in filter(lambda x: x.startswith('Basecall_'), self._read['Analyses'].keys())]
    
    def get_seq(self, basecall_group='000'):
        """Return the Sequence as it is saved in the fastq value of the basecall group.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The sequence as string
        """
        return self.get_fastq(basecall_group).split('\n')[1].strip()[::-1]
    
    def get_rev_seq(self, basecall_group='000'):
        """Return the reversed sequence as it is saved in the fastq value of the basecall group.
        Thus the 3' end of the sequence is at the beginen like in the raw data.

        :param basecall_group: The id of the basecall group as str.
        :return: The sequence as string
        """
        return self.get_fastq(basecall_group).split('\n')[1].strip()
    
    def get_moves(self, basecall_group='000'):
        """Get the move data as it is saved from guppy in the basecall group.
        A 1 means that the trace at the same position create a new base.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The moves as numpy array.
        """
        path = 'Analyses/Basecall_1D_{group}/BaseCalled_template/Move'.format(group=basecall_group)
        return np.asarray(self._read[path])
    
    def get_traces(self, basecall_group='000'):
        """Get the traces data as it is saved from guppy in the basecall group.
        Every trace are 8 values. That represents each the property of one of the bases (4 bases with each flip flop)
        The Trace order is: A, C, G, U, A, C, G, U.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The moves as numpy array.
        """
        path = 'Analyses/Basecall_1D_{group}/BaseCalled_template/Trace'.format(group=basecall_group)
        return np.asarray(self._read[path])
    
    def get_step(self, basecall_group='000'):
        """Get the step parameter of the basecall group. This parameter defines how many raw signals are in one trace.
        This value depends on the model that guppy uses and is fixed for every model.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The step parameter as int
        """
        path = 'Analyses/Basecall_1D_{group}/Summary/basecall_1d_template'.format(group=basecall_group)
        return int(self._read[path].attrs["block_stride"])
    
    def get_start(self, basecall_group='000'):
        """The position of the first trace. This paremeter defines where the traces (and basecalls) start.
        It can be greater then zero when somthing is clipped by guppy.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The beginning of the first trait as int.
        """
        path = 'Analyses/Segmentation_{group}/Summary/segmentation'.format(group=basecall_group)
        return int(self._read[path].attrs["first_sample_template"])
    
    def get_fastq(self, basecall_group='000'):
        """Return the complete fastq entry including a qualite string.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The complete fastq entry of the basecall group as str.
        """
        path = 'Analyses/Basecall_1D_{group}/BaseCalled_template/Fastq'.format(group=basecall_group)
        return self._read[path][()].decode('UTF-8')
    
    def get_basepositions(self, basecall_group='000'):
        """ Get the start positions of the basecalls in the raw data.
        This uses the start and step paremter to calculate the trace positions.
        Then the moves are used to map the traces to the bases.
        
        :param basecall_group: The id of the basecall group as str.
        :return: The raw positions of the basecalls as list of ints.
        """
        moves = self.get_moves(basecall_group)
        start = self.get_start(basecall_group)
        step = self.get_step(basecall_group)
        basepoints = []
        for i in range(len(moves)):
            if moves[i]:
                basepoints.append(start + (step * i))
        return basepoints


class Fast5:
    """The class that represents one multi fast5 file"""
    def __init__(self, path, mode='r'):
        """Open the file.
        The file can be open in read (r), append(a) or write(w) modus.
        However, no writing options are implemented so far.
        
        :param path: The path to the file as string.
        :param mode: The mode how the file should open as one character string.(Default "r")
        """
        self.root = h5py.File(path, mode=mode)
    
    def __iter__(self):
        """Iterate over the reads in the file
        
        :return: An iterator over the names of the reads.
        """
        for read_name in self.root:
            yield read_name
    
    def __getitem__(self, item):
        """Get for a name of a read the coresponding Fast5Read object
        
        :param item: The name of a read in the fast5 file as string
        :return: The Fast5Read object of this read.
        """
        return Fast5Read(item, self.root[item])
    
    def get_basecall_groups(self):
        """ Get the basecall groups of the file.
        It is assumed that every read have the same groups thus simply the groups of a random read are returned.
        
        :return: A tuple of the name of the group as it is saved in the fast5 and the id of the basecall group (three numbers as string).
        """
        read = self.root[next(iter(self))]
        for group in read['Analyses']:
            if group.startswith('Basecall'):
                end = group.split('_')[-1]
                name = read['Analyses'][group].attrs["name"].decode('UTF-8')
                yield name, end
