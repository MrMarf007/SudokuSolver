import pygame
import copy
import sys

# +===================== Author: =====================+
# |                                                   |
# |     __       __                       ______      |
# |    |  \     /  \                     /      \     |
# |    | ##\   /  ##  ______    ______  |  ######\    |
# |    | ###\ /  ### |      \  /      \ | ##_  \##    |
# |    | ####\  ####  \######\|  ######\| ## \        |
# |    | ##\## ## ## /      ##| ##   \##| ####        |
# |    | ## \###| ##|  #######| ##      | ##          |
# |    | ##  \# | ## \##    ##| ##      | ##          |
# |     \##      \##  \####### \##       \##          |
# |                                                   |
# +===================================================+ 
#
# +---------------------- TODO: ----------------------
# |
# | - add more boards
# |
# +---------------------------------------------------


BOARDS = {
    "master1" : "000910000900600300083050070000000005000000000200001407102070600004000290000060000",
    "master2" : "906004000030010095000000800000080300400001082020000700000000007050090021300500000",
    "random1" : "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
    "empty"   : "000000000000000000000000000000000000000000000000000000000000000000000000000000000"
}

LINE_COLOR = (255, 255, 255)
BG_COLOR = (50, 50, 50)

#region - handle command line arguments

parameters = {
    "board" : "000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "size" : 500,
    "mode" : "fast", # "step", "fast", "fastStep" or "console"
    "data" : False
}

modes = ["step", "fast", "fastStep", "console"]

for i in range(1, len(sys.argv)):
    match (sys.argv[i]):
        
        case "-b":
            val = sys.argv[i + 1]
            if (len(val) == 81 and val.isdigit()) or val in BOARDS:
                parameters["board"] = val
            else:
                print("Input error: Invalid board string, using empty board")

        case "-s":
            try:
                val = int(sys.argv[i + 1])
                parameters["size"] = val
            except:
                print("Input error: Invalid size, using default size (500)")

        case "-m":
            val = sys.argv[i + 1]
            if val in modes:
                parameters["mode"]  = val
            else:
                print("Input error: Invalid mode, using fast mode")

        case "-d":
            parameters["data"]  = True

#endregion

#region - initialization / constants
        
#Initialize Pygame
pygame.init()

# Create the Pygame window
window = pygame.display.set_mode((parameters["size"] + 200, parameters["size"] + 200))
pygame.display.set_caption("Sudoku Board")

CELL_SIZE = parameters["size"] // 9

board = []
collapseBoard = []
savedBoards = []

selectedCell = (-1, -1)

finished = False
doStep = False

#endregion

def getBoard():
    newBoard = []
    newCollapseBoard = []

    if parameters["board"] in BOARDS:
        newBoard = parseBoard_StoL(BOARDS[parameters["board"]])
    elif len(parameters["board"]) == 81 and parameters["board"].isdigit():
        newBoard = parseBoard_StoL(parameters["board"])
    else:
        print("Invalid board string, using empty board")
        newBoard = parseBoard_StoL(BOARDS["empty"])

    newCollapseBoard = createCollapseBoard(newBoard)
    return newBoard, newCollapseBoard

def parseBoard_StoL(boardString):
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            row.append(int(boardString[i * 9 + j]))
        board.append(row)
    return board

def parseBoard_LtoS(boardList):
    boardString = ""
    for i in range(9):
        for j in range(9):
            boardString += str(boardList[i][j])
    return boardString

def printCollapseBoard(collapseBoard):
    rows = []
    for i in range(9):
        row = [
            "| ",
            "| ",
            "| "
        ]
        for j in range(9):
            vals = collapseBoard[i][j]
            if vals == [] and board[i][j] != 0:
                row[0] += " VAL  "
                row[1] += "  " + str(board[i][j]) + "   "
                row[2] += "      "
            else: 
                for k in range(9):
                    if k + 1 in vals:
                        row[k // 3] += str(k + 1) + " "
                    else:
                        row[k // 3] += "  "
            row[0] += "| "
            row[1] += "| "
            row[2] += "| "
        rows.append(row)
    print("                             collapseBoard:                              ")
    for r in rows:
        print("+-------+-------+-------+-------+-------+-------+-------+-------+-------+")
        print(r[0] + "\n" + r[1] + "\n" + r[2])
    print("+-------+-------+-------+-------+-------+-------+-------+-------+-------+")

def printBoard(board):
    print("          board           ")
    for i in range(9):
        row = ""
        for j in range(9):
            if j % 3 == 0:
                row += "| "
            if board[i][j] == 0:
                val = " "
            else:
                val = str(board[i][j])
            row += val + " "
        if i % 3 == 0:
            print("+-------+-------+-------+")
        print(row + "|"	)
    print("+-------+-------+-------+")
    print(parseBoard_LtoS(board))

def insertVal(data, x, y, val):
    if parameters["data"]: 
        print ("inserting " + str(val) + " at " + str(x) + " " + str(y) + " ~ " + data)

    board[x][y] = val
    collapseBoard[x][y] = []

    for i in range(9):
        if val in collapseBoard[x][i]:
            collapseBoard[x][i].remove(val)
        if val in collapseBoard[i][y]:
            collapseBoard[i][y].remove(val)
    for i in range(3):
        for j in range(3):
            if val in collapseBoard[(x // 3) * 3 + i][(y // 3) * 3 + j]:
                collapseBoard[(x // 3) * 3 + i][(y // 3) * 3 + j].remove(val)

def removeVal(x, y):
    if parameters["data"]:
        print ("removing " + str(board[x][y]) + " at " + str(x) + " " + str(y))

    board[x][y] = 0
    global collapseBoard # dont like this
    collapseBoard = createCollapseBoard(board)

def createCollapseBoard(board):
    newCollapseBoard = []

    # *** create full collapse board ***
    for i in range(9):
        row = []
        for j in range(9):
            row.append([1,2,3,4,5,6,7,8,9])
        newCollapseBoard.append(row)

    # *** filter out values from inside cell's box for every cell ***
    # go through every box
    for i in range(3):
        for j in range(3):
            boxContents = []
            # for every cell in this box that has a value, save that value
            for k in range(3):
                for l in range(3):
                    val = board[i * 3 + k][j * 3 + l]
                    if val != 0:
                        newCollapseBoard[i * 3 + k][j * 3 + l] = []
                    boxContents.append(val)

            # for every value found, go through the box and remove that value from the collapse list of every cell with that value in its collapse list
            for val in boxContents:
                for k in range(3):
                    for l in range(3):
                        if val in newCollapseBoard[i * 3 + k][j * 3 + l]:
                            newCollapseBoard[i * 3 + k][j * 3 + l].remove(val)

    # *** filter out values from cell's row/column for every cell ***
    # go through every row and column
    # one row and one column are handled at the same time, saves duplicate code and extra loop
    for i in range(9):
        rowContents = []
        colContents = []
        # for every cell in this row/column that has a value, save that value
        for j in range(9):
            valRow = board[i][j]
            valCol = board[j][i]

            if valRow != 0: newCollapseBoard[i][j] = []
            if valCol != 0: newCollapseBoard[j][i] = []

            rowContents.append(valRow)
            colContents.append(valCol)

        # for every value found, go through the row and remove that value from the collapse list of every cell with that value in its collapse list
        for val in rowContents:
            for j in range(9):
                if val in newCollapseBoard[i][j]:
                    newCollapseBoard[i][j].remove(val)

        # same but for the column
        for val in colContents:
            for j in range(9):
                if val in newCollapseBoard[j][i]:
                    newCollapseBoard[j][i].remove(val)

    return newCollapseBoard

def validateBoard(board):
    wrongCells = []
    emptyCells = 0
    for i in range(9):
        for j in range(9):
            val = board[i][j]
            allowed = collapseBoard[i][j]
            if val != 0:
                for x in range(9):
                    if val == board[i][x] and x != j:
                        wrongCells.append((i, x))
                        wrongCells.append((i, j))
                    if val == board[x][j] and x != i:
                        wrongCells.append((x, j))
                        wrongCells.append((i, j))
                for y in range(3):
                    for z in range(3):
                        if val == board[(i // 3) * 3 + y][(j // 3) * 3 + z] and (i // 3) * 3 + y != i and (j // 3) * 3 + z != j:
                            wrongCells.append(((i // 3) * 3 + y, (j // 3) * 3 + z))
            else:
                emptyCells += 1
                if allowed == []:
                    wrongCells.append((i, j))
                
    global finished, doStep
    if emptyCells == 0 and not finished:
        print("Board is finished")
        finished = True
        doStep = False
        
    wrongCells = list(set(wrongCells))
    return wrongCells

def draw_board(board, collapseBoard, selected, faults):
    # draw the cells
    for i in range(9):
        for j in range(9):
            # Calculate the position of each cell
            x = 100 + j * CELL_SIZE
            y = 100 + i * CELL_SIZE

            # display amount of possible numbers
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            num = len(collapseBoard[i][j])
            if (i, j) == selected:
                s.fill((128,128,255,80))
            elif (i, j) in faults:
                s.fill((255,0,0,80))
            else:
                s.fill((0, num * 28, 0, 80))
            
            window.blit(s, (x,y))

            # Draw the cell lines
            pygame.draw.rect(window, LINE_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 1)

            # Draw the numbers
            number = board[i][j]
            if number != 0:
                font = pygame.font.Font(None, int(parameters["size"] * (8 / 100)))
                text = font.render(str(number), True, LINE_COLOR)
                window.blit(text, (x + CELL_SIZE/2 - pygame.font.Font.size(font, "1")[0]/2, y + CELL_SIZE/2 - pygame.font.Font.size(font, "1")[1]/2.5))

    # draw the boxes
    for i in range(3):
        for j in range(3):
            size = CELL_SIZE * 3
            # Calculate the position of each cell
            x = 100 + j * size
            y = 100 + i * size

            # Draw the cell
            pygame.draw.rect(window, LINE_COLOR, (x, y, size, size), 3)

def updateBoard(board, collapseBoard, faults):
    if len(faults) > 0:
        if parameters["data"]:
            print("invalid board")

        try:
            (oldBoard, oldCollapseBoard, oldX, oldY, oldVal) = savedBoards.pop()
        except:
            global doStep
            print ("Current sudoku seems impossible to solve (user inputs are treated as correct numbers, maybe that is the problem)\nPress \'R\' to reset the board and try again\nPress \'ESC\' to exit the game")
            doStep = False
            return board, collapseBoard
        else:
            board = oldBoard
            collapseBoard = oldCollapseBoard
            collapseBoard[oldX][oldY].remove(oldVal)

    if parameters["mode"] == "fast" or parameters["mode"] == "fastStep":
        changed = update_cells(collapseBoard) or update_boxes(collapseBoard) or update_rowsAndCols(collapseBoard)
    else:
        changed = update_cells(collapseBoard)
        if not changed:
            changed = update_boxes(collapseBoard)
        if not changed:
            changed = update_rowsAndCols(collapseBoard)

    if not changed:
        lowest = 10
        lowpos = (-1,-1)
        br = False
        for i in range(9):
            if br: break
            for j in range(9):
                if br: break
                cell = collapseBoard[i][j]
                if len(cell) < lowest and cell != []:
                    if len(cell) == 2:
                        br = update_guess(board, collapseBoard, i, j)
                        break
                    lowest = len(cell)
                    lowpos = (i, j)
        if lowpos != (-1,-1):
            if not br: 
                update_guess(board, collapseBoard, lowpos[0], lowpos[1])

    return board, collapseBoard
#region - updateBoard helper functions
            
def update_cells(collapseBoard):
    ret = False
    for i in range(9):
        for j in range(9):
            if len(collapseBoard[i][j]) == 1:
                insertVal("cl", i, j, collapseBoard[i][j][0])
                if parameters["mode"] == "fast" or parameters["mode"] == "fastStep":
                    ret = True
                else:
                    return True
    return ret
    
def update_boxes(collapseBoard):
    ret = False
    for i in range(3):
        for j in range(3):
            amounts = [0,0,0,0,0,0,0,0,0]
            box = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
            for k in range(3):
                for l in range(3):
                    for val in collapseBoard[i * 3 + k][j * 3 + l]:
                        if val != []:
                            amounts[val - 1] += 1
                            box[val - 1] = ((i * 3 + k, j * 3 + l))

            for v in range(9):
                if amounts[v] == 1:
                    (newx, newy) = box[v]
                    insertVal("bx", newx, newy, v + 1)
                    if parameters["mode"] == "fast" or parameters["mode"] == "fastStep":
                        ret = True
                    else:
                        return True      
    return ret

def update_rowsAndCols(collapseBoard):
    ret = False
    for i in range(9):
        amountsRows = [0,0,0,0,0,0,0,0,0]
        amountsCols = [0,0,0,0,0,0,0,0,0]
        row = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
        col = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
        for j in range(9):
            for val in collapseBoard[i][j]:
                if val != []:
                    amountsRows[val - 1] += 1
                    row[val - 1] = (i, j)
            for val in collapseBoard[j][i]:
                if val != []:
                    amountsCols[val - 1] += 1
                    col[val - 1] = (j, i)

        for v in range(9):
                if amountsRows[v] == 1:
                    (newx, newy) = row[v]
                    insertVal("rc1", newx, newy, v + 1)
                    if parameters["mode"] == "fast" or parameters["mode"] == "fastStep":
                        ret = True
                    else:
                        return True

                if amountsCols[v] == 1:
                    (newx, newy) = col[v]
                    insertVal("rc2", newx, newy, v + 1)
                    if parameters["mode"] == "fast" or parameters["mode"] == "fastStep":
                        ret = True
                    else:
                        return True
    return ret

def update_guess(board, collapseBoard, x, y):
    cell = collapseBoard[x][y]
    oBoard = copy.deepcopy(board)
    oCollapseBoard = copy.deepcopy(collapseBoard)
    savedBoards.append((oBoard,oCollapseBoard,x,y,cell[0]))
    insertVal("guess", x, y, cell[0])
    return parameters["mode"] == "step"

#endregion

#region - main game loop
board, collapseBoard = getBoard()
running = True

while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                printCollapseBoard(collapseBoard)

            if event.key == pygame.K_p:
                printBoard(board)

            if event.key == pygame.K_ESCAPE:
                selectedCell = (-1, -1)

            # start solve button
            if event.key == pygame.K_SPACE:
                selectedCell = (-1, -1)
                finished = False
                doStep = True

            if event.key == pygame.K_RIGHT:
                (x, y) = selectedCell
                if x != -1 and y != -1:
                    y = (y + 1) % 9
                    selectedCell = (x, y)
            
            if event.key == pygame.K_LEFT:
                (x, y) = selectedCell
                if x != -1 and y != -1:
                    y = (y - 1) % 9
                    selectedCell = (x, y)

            if event.key == pygame.K_DOWN:
                (x, y) = selectedCell
                if x != -1 and y != -1:
                    x = (x + 1) % 9
                    selectedCell = (x, y)

            if event.key == pygame.K_UP:
                (x, y) = selectedCell
                if x != -1 and y != -1:
                    x = (x - 1) % 9
                    selectedCell = (x, y)

            # reset button
            if event.key == pygame.K_r:
                board, collapseBoard = getBoard()
                finished = False
                doStep = False

            # clear cell
            if event.key == pygame.K_0 and selectedCell != (-1, -1):
                finished = False
                (x, y) = selectedCell
                if board[x][y] != 0:
                    removeVal(x, y)
            
            # insert number into cell
            if ( event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9] 
                and selectedCell != (-1, -1) ):
                
                (x, y) = selectedCell
                currentVal = board[x][y]
                newVal = int(event.unicode)

                if currentVal != newVal:
                    if currentVal != 0:
                        removeVal(x, y)
                    insertVal("user", x, y, newVal)
                finished = False

        # select cell
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            y = (pos[0] - 100) // CELL_SIZE
            x = (pos[1] - 100) // CELL_SIZE
            selectedCell = (x, y)

    # Validate if the board is correct
    faults = validateBoard(board)

    # Draw the Sudoku board
    window.fill(BG_COLOR)
    draw_board(board, collapseBoard, selectedCell,  faults)

    # Update the display
    pygame.display.update()

    # if the board is full and correct, stop updating the board
    # also, only update is doStep is True, meaning the user wants to solve a step of the board
    if not finished and doStep:
        # execute one solve step (in fast mode, this might solve more than one cell per step)
        board, collapseBoard = updateBoard(board, collapseBoard, faults)
        # if in step mode, pause after each step
        if parameters["mode"] == "step" or parameters["mode"] == "fastStep":
            doStep = False

pygame.quit()
#endregion