![logo](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/slappy.png "logo")


## Description

 **SlaPPy** (**S**quigg**l**e **a**nd sequence **P**lotter in **Py**thon) is a browser based GUI to map sequence to Squiggle out of a fast5 files created by sequencing with Oxford Nanopore Technology (ONT). It also provides the possibility to visualize the probability for basecalling of different bases at a certain time or sequence position.

## Cloning repository

```
git clone git@github.com:Fabianexe/SlaPPy
```

## Installing software

```
python3 setup.py install
```

## Running SlaPPy

starting SlaPPy:

```
slappy
``` 

Then copy the http-link into your desired browser.

First choose a fast5 file by entering the file path in the upper left window.
 
![enter path](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/enter_path.png "enter the path here")

Then you can select manually a read out of the fast5 file.

It is also possible to filter reads using the read-ID.

![filter reads](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/filter_reads.png "Filter reads")

Please choose the ONT Guppy basecall group for further investigation of the reads.

![select_basecall_group](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/basecall_group.png "select basecall group")

## Display options

You can activate stack traces under Graph Options to display the probabilities for the different nucleotides. Also it is possible to normalize the value of current to 1. 
Negative raw values are converted to positive numbers.

There are two different view options of the squiggle and the related traces and called nucleotides: "signal scaled" and "base scaled". 

In the signal scaled mode, the Squiggle can be seen unchanged with respect to duration. 

![Raw based mode](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/raw_based.png "raw based")


In the base scaled mode, the distances between the nucleotides are normalized to the same length and the squiggle is either stretched or compressed. 

![Base based mode](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/base_based.png "Base based")

In both modes, red vertical lines mark the positions where a certain base was called. The most likely base is written above the red line. Squiggle and sequence are shown from 5' to 3' end.

In both modes you can zoom in and get a closer look at certain areas by choosing the desired area manual. 
You can also, when Stack Traces is activated, display how likely it is to call which Base at which time. 
This shows the size of the area in the corresponding color, which can be seen in the legend on the right.

It is also possible by double clicking on a certain nucleotide in the legend to show single traces. 

![single_trace](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/single_trace_raw.png "single trace")

You can select Baseprobability to show a sequence logo representing the probability for each base on a certain position.

![base_prob](https://raw.githubusercontent.com/Fabianexe/SlaPPY/master/pictures/sequence_logo.png "Display base prob.")

The sequence logo is displayed with as subsequence of 200 bases. Use the slider or search to determine the shown range.

There are three different options für displaying the sequence logo of base probabilities:
- "Up next" shows the mean probabilities for the bases between two called bases.
- "At call" shows the probabilites for the bases at the time when the most probable base is called. 

## Search subsequences

You can search for a certain subsequence, mark the position, where the subsequence occured and apply, so the visible subsequence is adjusted in the screen.

![search](https://raw.githubusercontent.com/Fabianexe/SlaPPy/master/pictures/search.png "search subsequence")

Since only a part of the sequence can be displayed as sequence logo, the corresponding area should be selected in the sequence logo beforehand, so that the correct sub-sequence is displayed.

## Help

You can activate the help function in the lower left corner.



