# **SlaPPy** = **S**quigg**l**e **a**nd sequence **P**lotter in **Py**thon

## Description

A browser based GUI to map sequence to Squiggle out of a fast5 files created by sequencing with Oxford Nanopore Technology (ONT). It also provides the possibility to visualize the probability for basecalling of different bases at a certain time or sequence position.

## Clone repository

```
>>>git clone git@github.com:Fabianexe/SlaPPy
```

## Installing software

```
>>>python3 setup.py install
```

## Running SlaPPy

starting SlaPPy:

```
>>>slappy
``` 

Then the browser based GUI opens.

First choose a fast5 file by entering the file path in the upper left window.
 
![enter path](https://github.com/Fabianexe/SlaPPy/blob/master/pictures/path.png "enter the path here")

Then you can select a read out of the fast5 file.

![select_read](https://github.com/Fabianexe/SlaPPy/blob/master/pictures/read_selection.png "select a read")

Please choose the ONT Guppy basecall group.

![select_basecall_group](https://github.com/Fabianexe/SlaPPy/blob/master/pictures/basecallgroup.png "select basecall group")

You can activate stack traces to display the probabilities for the different nucleotides.

![stack traces](https://github.com/Fabianexe/SlaPPy/blob/master/pictures/stack_traces.png "stack traces")

There are two different view options: Raw based and Base based. 

In the Raw based mode, the Squiggle can be seen unchanged. 

![Raw based mode](https://github.com/Fabianexe/SlaPPy/blob/master/pictures/raw_based.png "raw based")

In the Base based mode, the distances between the nucleotides are normalized to the same length and the squiggle is either stretched or compressed. 

![Base based mode](https://github.com/Fabianexe/SlaPPy/blob/master/pictures/base_based.png "Base based")

In both modes, red vertical lines mark the positions where a certain base was called. The most likely base is written above the red line. Squiggle and sequence are shown from 3' to 5' end.

In both modes you can zoom in and get a closer look at certain areas by choosing the desired area manual. 
You can also, when Stack Traces is activated, display how likely it is to call which Base at which time. 
This shows the size of the area in the corresponding color, which can be seen in the legend on the right. 