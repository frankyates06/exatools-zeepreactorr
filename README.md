# Exatool

Exatool is written in python and is able to retrieve the full text of an article (when free). Its purpose is to allow a better understanding of the material used by the scientific community using a keyword research. Python scripts to visualize the data are also available.
The development is still ongoing and currently limited to the PubMed database of research articles. 

**If you have questions, find bugs, or have ideas of features you would like to propose, do not hesitate to reach out at mattgitqna@gmail.com**

## Prerequisite 

To run the programs smoothly, you need to have installed the following packages : 
- bs4
- requests
- PyPDF2
- BytesIO
- numpy
- matplotlib

All those packages can be installed with `pip install <package_name>` from the terminal

## Installation

To install the Exatool program, run the following command line in your terminal :
```sh
git clone https://github.com/ZeepReactorr/exatools
```

## Usage

To run the program, enter the following command line in your terminal, filling the gaps with the required parameters :
```sh
python ~/PATH/TO/exatool.py ~/PATH/TO/OUTPUT_DIR 'Pubmed URL' keyword_1 keyword_2... keyword_n
```

The program will keep the progression updated in the console. The ouptut graphical plot will be saved in the output directory you indicated as well as the intermediary files. 
**Be careful that the date range in your Pubmed query and indicated date range variable __match__, if they don't, the plot will not be correct.** <br>
**Make sure that the URL is between quotes, as the command will return an error otherwise.**

Example of prompt : 

```sh
python C:/PATH/TO/exatool.py C:/PATH/TO/OUTPUT/DIRECTORY 'https://pubmed.ncbi.nlm.nih.gov/?term=prokaryote+sequencing&filter=simsearch2.ffrft' Illumina Nanopore
```

This will count the respective occurency of Nanopore or Illumina sequencing for articles related to Prokaryote sequencing throughout pubmed and automatically generate a graph displaying just that. 

> The **reviews** are **filtered out**. Only research papers with methods are taken into account.

## Credit

If you found this tool useful during your research, please cite :

BETTIATI M. (2024). ZeepReactorr/exatools [Python]. https://github.com/ZeepReactorr/exatools (Original work published 2024)

