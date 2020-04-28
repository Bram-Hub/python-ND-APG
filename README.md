# ND APG
## Authors
2015:
Mike Mathis  
2020:
Salil Chandra, Matthew Salemi

## About
This is a python 3 program which takes as input a set of premises and a goal. If the goal can be reached from the premises, a valid proof will be outputted. Otherwise, the program will respond with an error message. The program takes in a .txt or .bram file and outputs a .tex or .bram file. Below are some example command line inputs.  
```
python proof.py input.txt  
python proof.py input.txt latex  
python proof.py input.bram  
python proof.py input.bram latex
```

## Input

The program will accept as input valid .txt or .bram files. It will automatically detect and parse the file based on the file extension used. Logical statements in any input must be in CNF and the conclusion must be simple as discussed below.

### .txt input file

.txt files must have each premise separated with a new line with parenthesis being optional. Logic operators must be in the form &, |, ~ for and, or, not respectively. The last line in the .txt file will be treated as the goal.

### .bram input file

.bram input files must be valid and conform to standards found at https://github.com/Bram-Hub/Bram-File-Format. The file must specify a goal (max 1) or the last premise will be treated as the goal.

## Output

The program will output to a .bram file by default or a .tex file if specified. In order to output to a .tex file add the latex flag when running the program.  
Ex: ```python proof.py input.bram latex```  
Additionally, compiling the .tex file requires use of the lplfitch package found in this repository or at https://github.com/rzach/lplfitch. Ensure that the .tex file is in the same directory as lplfitch.sty.

## Proof Algorithm

Due to limitations of the algorithm used to generate the proof, only simple conclusions can be solved for such as A or ~A.  

The algorithm works as follows:
   1. Create subproof where conclusion is false
   2. Break down all conjunctions
   3. Break down all disjuntions into subproofs
   4. Search all subproofs for common conclusions
   5. When a contradiction is found, break out of the subproof and conclude contratiction
   6. Conclude the given conclusion
