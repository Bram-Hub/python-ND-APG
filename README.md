# ND APG
## Authors
2015:
Mike Mathis

## About
This is a python program to take in input via a .txt file and output a .tex file.
The format of the input file must be as follows:
	and - &
	or  - |
	not - ~
With parenthesis optional. Example input files are provided.
The last line on the input file is the conclusion.
The input must be in CNF in order for the program to work.

Due to limitations of the algorithm I used to generate the proof, 
only simple conclusions can be solved for, such as A or ~A

The program is run using python 3 with the input as the first argument
Ex: python proof.py input.txt

The program will output output.tex into the current directory
The tex file can then be converted to a .dvi or .pdf using a latex style provided by 
https://github.com/rzach/lplfitch

The .sty file needed is provided in this zip file, so if latex is installed on your system,
All you need to do is run "latex output.tex" or "pdflatex output.tex: to provide the desired files.

The algorithm works as follows:
	1. Create subproof where conclusion is false
	2. Break down all conjunctions
	3. Break down all disjuntions into subproofs
	4. Search all subproofs for common conclusions
	5. When a contradiction is found, break out of the subproof and conclude contratiction
	6. Conclude the given conclusion


This program was tested using python3 on linux with texlive as the latex compiler

Mike Mathis
