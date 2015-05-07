NLP Spam Detection Project
======


Setup
------

Do all of the following from the base directory (where this README file is located).

<ol>
  <li>Download and extract the Trec 2007 data set into the project directory (link below).</li>
  <li>Download and build Weka and the Berkley Language Model 1.1.6 from the links below. Keep the builds in the project directory, or otherwise edit all of the classpaths in the project scripts.</li>
  <li>Create the following directories if they do not exist:
    <ol>
      <li><code>mkdir -p Data/NGramTrain/lower_chars</code></li>
      <li><code>mkdir -p Data/NGramTrain/lower_words</code></li>
      <li><code>mkdir -p Data/NGramTrain/upper_chars</code></li>
      <li><code>mkdir -p Data/NGramTrain/upper_words</code></li>
      <li><code>mkdir -p Data/NGramTest/lower_chars</code></li>
      <li><code>mkdir -p Data/NGramTest/lower_words</code></li>
      <li><code>mkdir -p Data/NGramTest/upper_chars</code></li>
      <li><code>mkdir -p Data/NGramTest/upper_words</code></li>
      <li><code>mkdir -p Models/Evaluations</code></li>
    </ol>
  </li>
  <li>Now you are ready to start the preprocessing and experiment steps below.</li>
</ol>


Bag of Words Preprocessing and Experiments
------

<ol>
  <li>Use <b>preprocessor.py</b> to generate the filtered bag-of-words training set on the first 67877 (90%) emails:<br>
    <code>python preprocessor.py trec07 1 67877 Data/train_bulk.arff -stopwords stopwords.txt</code><br>
    This can also be done using the Condor <code>CondorJobFiles/preprocess</code> submit file.</li>
  <li>Similarly, generate the filtered bag-of-words testing set on the remaining 7542 (10%) emails:<br>
    <code>python preprocess.py trec07 67878 75419 Data/test_bulk.arff -stopwords stopwords.txt</code><br>
    This can also be done using the Condor <code>CondorJobFiles/preprocess_test</code> submit file.</li>
  <li>Run the <b>convert</b> script. This will automatically convert and standardize all the bag-of-words .arff data files generated in the last two steps, assuming they were named correctly:<br>
    <code>Data/train_bulk.arff -> Data/train_std.arff</code><br>
    <code>Data/test_bulk.arff -> Data/test_std.arff</code><br>
    This can also be done using the Condor <code>CondorJobFiles/convert</code> submit file (but change the Java 8 path).</li>
  <li><b>TODO</b></li>
</ol>


N-Gram Preprocessing and Experiments
------

<ol>
  <li>Run the <b>generate_ngram_files</b> script. This will call <code>preprocessor.py</code> appropriately to generate all of the n-gram sets from the training data and create separate test files for each message in the test set. It will create extra N-Gram training files for the first 61089 (81%) emails. The remaining 6788 (9%) of training messages will be used for evaluation on the N-Gram models. The files will be stored in the directories created above.<br>
    Four types of sets will be generated: lower_chars, lower_words, upper_chars, and upper_words. The "lower" data means all characters have been converted to lowercase, and "upper" means they have not been converted. The "words" data is to generate the N-Grams for words, whereas the "chars" data is for generating N-Grams on the individual characters in the message instead.<br>
    For both the training set and the test set, each message will be stored individually in its own file and will be <i>unlabeled</i> for evaluation usage. However, for the first 90% of the training set, all emails will additionally be stored in two other separate files - one containing all spam messages and the other containing all ham messages - for the Berkley LM classifier to learn a model from.<br>
    This step can also be done using the Condor <code>CondorJobFiles/preprocess_ngrams</code> submit file.<br>
  <li>Run the <b>build_ngram_models</b> script. This will take all of the N-Gram data sets created from the previous step and generate .arpa and .binary model files in the <code>Models</code> directory. These files are used for evaluating test data against the N-Gram models.<br>
    By default, N (for the <i>N</i>-Gram parameter) is set to 3. You can pass in a numerical argument to the script to change the value of N. You may want to modify the code by setting the <code>types</code> list to only include model types that you want to generate.<br>
    This step can also be done using the Condor <code>CondorJobFiles/build_ngram_models</code> submit file. To change N when using Condor will require modifying the parameters in the submit file.<br>
    NOTE: You will need to modify the Java 8 path in the <code>build_ngram_models</code> script.</li>
  <li>Now it's time to run the evaluation on the training data to set up an .arff file for the Weka classifier. Follow these steps:
    <ol>
      <li>Edit the <code>ngram_to_weka.config</code> file to add which model types and N-values you wish to use for classification. The existing config file is documented, so follow those instructions.</li>
      <li>Run the <code>ngram_to_weka.py</code> script to evaluate all of the messages for each model and N-value:<br>
      <code>python ngram_to_weka.py trec07p Data/NGramTrain 1 60000 Models/ config Data/train_ngram.arff</code>. Note that this process will that a <i>very long time</i> to run.<br>
      NOTE: You will need to modify the Java 8 path at the top of the <code>ngram_to_weka.py</code> file.<br>
    </ol>
  </li>
  <li><b>TODO</b></li>
</ol>


Mixed Features Preprocessing and Experiments
------

<ol>
  <li>TODO: preprocess test data to n-gram format.</li>
  <li>TODO: evaluate each test email message on all of the spam and ham n-gram models.</li>
  <li>TODO: run the Weka classifiers.</li>
</ol>


Data Preprocessor Documentation
------

<code>preprocess.py</code>

TODO


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
