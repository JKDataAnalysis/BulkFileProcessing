<h1>Core program for creating analyses of multiple data files</h1>
<p></p><b>This script is very much still under development</b></p>
<p>The file is currently called tkinterPlay.py and is in the venv/lib folder (to be changed)</p>
This program will form the core for scripts to perform the same analyses on multiple data files and write the results to file. It will perform the following:
<ul>
  <li>Read in predefined data file definitions (e.g. delimiters, number of header rows, etc).</li>
  <li>Allow the user to select the folder containing their data files</li>
  <li>Iterate through the files, reading in each in turn and performing an analysis. In this version of the script only basic example analyses will be conducted 
    (e.g. mean, min, max, count) but my modifying the analysis function. In principle, any analysis could be added</li>
  <li>Write the results of the analyses to file</li>
</ul>
