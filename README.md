# pascal-compiler

This project requires Python 2.7.

## Usage

To run any of the examples, I have included a nice Python helper script. The script is called 'runner.py'.
That file will take care of instantiating the parser and simulator class, and will also run the scanner.
To run an example, uncomment ONE of the lines that look like this:
`tokens = get_token(PascalFile(input_file_location='arrays.pas', output_location=''))`

This will effectively run the scanner and allow the script to grab those tokens and supply it to the Parser which
will then be supplied to the Emulator. That example is the arrays example which gets that total AND reverses
the array. Since I support string literals, the console output has a nice display to show that.

You can comment out that line and uncomment any of the others to quickly see the sample Pascal files being run.

## Scripts

`pascal_loader/`: Takes care of initializing some Pascal specific directives.
`constants.py`: Holds constants such as opcodes and functions that are used in other scripts.
`tokenizer.py`: This is the scanner. It grabs all the tokens and returns a list.
`parse.py`: This holds the Parser class.
`emulator`: This holds the Emulator class which runs the p-code generated by the Parser.