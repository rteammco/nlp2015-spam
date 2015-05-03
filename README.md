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
  <li>Download and extract the tools and data set from the links below.</li>
  <li>Use the <b>preprocessor.py</b> script to generate the N-gram data sets for the Berkley Language Model tool. Use only the training set to do this. The <b>generate_ngram_files</b> script generates everything using the first 60000 emails as training examples.</li>
  <li>Run the <b>build_ngram_models</b> script to use the Berkley LM tool to generate models (.apra files) for each of the N-Gram data sets.</li>
  <li>Use the models (TODO)</li>
</ol>


Data Preprocessor
------

TODO


Experiment Steps
------

Do all of the following from the base directory (where this README file is located).

<ol>
  <li>Download and extract the tools and data set from the links below.</li>
  <li>Create a <code>Data</code> and a <code>Models</code> directory, if they do not exist.</li>
  <li>Use <b>preprocessor.py</b> to generate the filtered training set on the first 60000 emails:<br>
    <code>python preprocessor.py trec07 1 60000 Data/train_bulk.arff -stopwords stopwords.txt</code><br>
    This can also be done using the Condor <code>CondorJobFiles/preprocess</code> submit file.</li>
  <li>Similarly, generate the filtered testing set on the remaining 15419 emails:<br>
    <code>python preprocess.py trec07 60001 75419 Data/test_bulk.arff -stopwords stopwords.txt</code><br>
    This can also be done using the Condor <code>CondorJobFiles/preprocess_test</code> submit file.</li>
  <li>Run the <b>convert</b> script. This will automatically convert and standardize all the fdata files, assuming they were named correctly in the above steps:<br>
    <code>Data/train_bulk.arff -> Data/train_std.arff</code><br>
    <code>Data/test_bulk.arff -> Data/test_std.arff</code><br>
    This can also be done using the Condor <code>CondorJobFiles/convert</code> submit file (but change the Java 8 path).</li>
  <li>Run the <b>generate_ngram_files</b> script. This will call the preprocessor to generate all of the n-gram sets from the training data (first 60000 emails). The difference between this step and the previous steps is that stopwords will not be removed, and instead of .arff files, the output will be formatted for the Berkley LM n-gram program.<br>
    This can also be done using the Condor <code>CondorJobFiles/preprocess_ngrams</code> submit file.</li>
  <li>Run the <b>build_ngram_models</b> script. This will take all of the n-gram data sets and generate .arpa model files in the <code>Models</code> directory. You can modify this script to tweak the parameters of how the models are built.<br>
    This can also be done using the Condor <code>CondorJobFiles/build_ngram_models</code> submit file.<br>
    NOTE: You will need to modify the Java 8 path in the <code>build_ngram_models</code> script.</li>
  <li>TODO: preprocess test data to n-gram format.</li>
  <li>TODO: evaluate each test email message on all of the spam and ham n-gram models.</li>
  <li>TODO: run the Weka classifiers.</li>
</ol>


Data and Tool Resources
------

This is a list of sources of data and tools.

<b><u>DATASET</u>: trec07p</b> <br>
http://plg.uwaterloo.ca/~gvcormac/treccorpus07/ <br>

<b><u>TOOL</u>: Weka 3.6.12</b> <br>
http://www.cs.waikato.ac.nz/ml/weka/downloading.html <br>

<b><u>TOOL</u>: Berkley Language Model 1.1.6</b> <br>
https://code.google.com/p/berkeleylm/ <br>
Download: <code>svn checkout http://berkeleylm.googlecode.com/svn/trunk/ berkeleylm-1.1.6</code> <br>
