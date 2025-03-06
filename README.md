<h1>Core program for creating analyses of multiple data files</h1>
<p><mark>This script is very much still under development</mark></p>
<p>The script is intended as a generic front end for running analysis on multiple data files. The script allows the user to perform the following:</p>
<ul>
  <li>Choose from a range of predefined source files profiles. These are currently those that the author had ready access to (Kistler Bioware and Tekscan Footscan (both exported as text), but in principle could include anything that could be read into a Pandas Dataframe. The profiles detail all of the required parameters to import the data (e.g. number of header rows, deliminators) and the function to use to read the file. Currently, the only function defined uses Pandas read_csv to import deliminated text files but other functions, including users own custom functions, can be specified in the import profile.</li>
  <li>[To be implemented] As well as reading the data a function can optionally be specified to carry out pre-cleaning of files before import.</li>
  <li>Once a source data file type has been specified, users can add any number of data files to the cue. This can be done by:</li>
  <ol>
    <li>Selecting one or more files from a folder.</li>
    <li>Adding all files within a folder with the option to include sub folders.</li>
  </ol>
  <li>Files can be added from multiple folders and the file cue can be edited to remove files.</li>
  <li>Once one or more files have been added to the cue, the analysis can be run [to be implemented]. This will iterate through each file in turn, load it as a data frame and perform whichever analyses are included in the analysis function (defined in the source file profile).</li>
  <li>The results of the analyses for all files together with basic source data file information (file name, path and number of rows and columns read) can then be written as a CSV file.</li>
</ul>
This program will form the core for scripts to perform the same analyses on multiple data files and write the results to file. It will perform the following:
<ul>
  <hr>
<h2>Using the script</h2>
<p>To use the script: From your own file, import the Bulk File Analyser as:</p>
<blockquote>import BulkFileAnalyser</blockquote>
  <p></p>
<p>Call the 'main' function within <i>BulkFileAnalser</i> as:</p>
<blockquote>BulkFileAnalyser.main()</blockquote>
  <p></p>
<p>For an example script, see <i>AnalysisTemplate</i></p>
  <hr>
<h2>Planned developments</h2>
<ul>
  <li>The core script is still under development so the key priority is to get this fully functioning [core functions not yet implemented indicated above] and conduct further testing and debugging.</li>
  <li>Create an additional script (that can be called from this one) to allow the creation of new data source file profiles. These can be added currently by manually editing the <i>DataFileImportSetting.json</i>i file but this would give a move user friendly option.</li>
  <li>Expand the analysis template to provide basic example functions, for example, some basic analyses types, e.g.:</li>
  <ul>
    <li>Simple single column analysis, e.g. max, min, mean.</li>
    <li>Rowwise analysis using more than one column, e.g. difference between columns and then calculating summary values, e.g. mean and SD of calculated columns.</li>
    <li>Columnwise analyses e.g. finding difference between consecutive rows in a column.</li>
  </ul>
  <li>Add more source file profiles including ones that use other libraries, e.g. C3D.</li>
</ul>
