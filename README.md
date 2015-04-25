NLP Spam Detection Project
======


Steps for Bag-Of-Words Data:
------

<ol>
  <li>Download and extract the tools and data set from the links below.</li>
  <li>Use the <b>preprocessor.py</b> script to generate the .ARFF files for Weka.</li>
  <li>Run the <b>convert</b> script or Condor submit files to convert the .ARFF files into a bag-of-words format for Weka (using Weka's filter modules).</li>
  <li>Use the <b>run</b> script or Condor submit files to run a Weka classifier on the final .ARFF files.</li>
</ol>


Steps to Generate and Use N-Gram Models:
------

<ol>
  <li>Use the <b>preprocessor.py</b> script to generate the N-gram data sets for the Berkley Language Model tool. Use only the training set to do this. The <b>generate_ngram_files</b> script generates everything using the first 60000 emails as training examples.</li>
  <li>Run the <b>build_ngram_models</b> script to use the Berkley LM tool to generate models (.apra files) for each of the N-Gram data sets.</li>
  <li>Use the models (TODO)</li>
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
