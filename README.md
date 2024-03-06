# SudokuSolver
A simple soduku solver, to practice with python

## board format

a board is saved or entered in string format like this:
```
"000910000900600300083050070000000005000000000200001407102070600004000290000060000"`
```
Where 0 is an empty cell, and the numbers are the values of the cells, the string is read left to right, top to bottom
   
that string is parsed to a board-list like used in the program, and it looks like this:
```
[
    [0, 0, 0, 9, 1, 0, 0, 0, 0], 
    [9, 0, 0, 6, 0, 0, 3, 0, 0], 
    [0, 8, 3, 0, 5, 0, 0, 7, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 5], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [2, 0, 0, 0, 0, 1, 4, 0, 7], 
    [1, 0, 2, 0, 7, 0, 6, 0, 0], 
    [0, 0, 4, 0, 0, 0, 2, 9, 0], 
    [0, 0, 0, 0, 6, 0, 0, 0, 0]
]
```
   
the parseBoard_StoL function converts a string this format, 
and parseBoard_LtoS converts it back to the string format


## collapse board format

the collapse board is a list of lists, where each cell contains a list of possible values for that cell
it is created from the board, and is used to speed up the solving process
it looks like this, where [x] is a list of possible values for that cell:
```
[
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
    [[x],[x],[x],[x],[x],[x],[x],[x],[x]],
]
```

if a cell has a value, its collapseList is empty
