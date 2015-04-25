NLP Spam Detection Project
======

Steps
------

<ol>
  <li>Download and extract the tools and data set from the links below.</li>
  <li>Use the preprocessor script to generate the .ARFF files for Weka, and N-gram data sets for the Berkley Language Model tool.</li>
  <li>Run the convert script to convert the .ARFF files into a bag-of-words format for Weka (using Weka's filter modules).</li>
  <li>Use the run script to run a Weka classifier on the final .ARFF files.</li>
</ol>

Data Preprocessor
------

TODO

Data and Tool Resources
------

This is a list of sources of data and tools.

DATASET: trec07p
http://plg.uwaterloo.ca/~gvcormac/treccorpus07/

TOOL: Weka 3.6.12
http://www.cs.waikato.ac.nz/ml/weka/downloading.html

TOOK: Berkley Language Model 1.1.5
https://code.google.com/p/berkeleylm/
