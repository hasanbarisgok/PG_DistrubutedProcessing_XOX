import pygame
import socket
import time
import threading

s = socket.socket()
host = input("Enter the server IP:")
port = 9999

playerOne = 1
playerOneColor = (255, 0, 0)
playerTwo = 2
playerTwoColor = (0, 0, 255)
bottomMsg = ""
currentPlayer = 0
xy = (-1, -1)
allow = 0  # Allow handling mouse events
matrix = [[0 for _ in range(10)] for _ in range(10)]  

# Create worker threads
def create_thread(target):
    t = threading.Thread(target=target)  # Argument - target function
    t.daemon = True
    t.start()

# Initialize Pygame
pygame.init()

width = 1000
height = 1000
screen = pygame.display.set_mode((width, height))

# Set title
pygame.display.set_caption("Tic Tac Toe")

# Set icon
icon = pygame.image.load("tictactoe.png")
pygame.display.set_icon(icon)

# Fonts
bigfont = pygame.font.Font('freesansbold.ttf', 64)
smallfont = pygame.font.Font('freesansbold.ttf', 32)
backgroundColor = (255, 255, 255)
titleColor = (0, 0, 0)
subtitleColor = (128, 0, 255)
lineColor = (0, 0, 0)

def centerMessage(message, color):

    font = smallfont
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(width / 2, height - 50))
    screen.blit(text, text_rect)

def buildScreen(bottomMsg, string, playerColor=subtitleColor):
    screen.fill(backgroundColor)
    
    if "One" in string or "1" in string:
        playerColor = (0, 128, 0)  
    elif "Two" in string or "2" in string:
        playerColor = (128, 0, 0)  

    # Center the grid
    grid_offset = 100  # Offset to center the 800x800 grid in the 1000x1000 screen

    #Drawing lines (skip to first and near lines)
    for i in range(1, 10):
        x = grid_offset + 80 * i
        pygame.draw.line(screen, lineColor, (x, grid_offset), (x, grid_offset + 800), 4)
    
    for j in range(1, 10):
        y = grid_offset + 80 * j
        pygame.draw.line(screen, lineColor, (grid_offset, y), (grid_offset + 800, y), 4)

    # Render and blit the title and subtitle outside the grid
    title = bigfont.render("TIC TAC TOE", True, titleColor)
    screen.blit(title, (width // 2 - title.get_width() // 2, 20))
    
    subtitle = smallfont.render(str.upper(string), True, playerColor)
    screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, 100))

    centerMessage(bottomMsg, playerColor)

def printCurrent(current, pos, color):
    currentRendered = bigfont.render(str.upper(current), True, color)
    screen.blit(currentRendered, pos)

def printMatrix(matrix):
    grid_offset = 100
    for i in range(10):
        for j in range(10):
            x = grid_offset + j * 80 + 40  # Calculate the center position of the cell
            y = grid_offset + i * 80 + 40
            current = " "
            color = titleColor
            if i < len(matrix) and j < len(matrix[i]):
                if matrix[i][j] == playerOne:
                    current = "X"
                    color = playerOneColor
                elif matrix[i][j] == playerTwo:
                    current = "O"
                    color = playerTwoColor
            printCurrent(current, (x, y), color)

def validate_input(x, y):
    if x < 0 or y < 0 or x >= 10 or y >= 10:
        print("\nOut of bound! Enter again...\n")
        return False
    elif matrix[x][y] != 0:
        print("\nAlready entered! Try again...\n")
        return False
    return True

def handleMouseEvent(pos):
    global xy
    x = pos[0]
    y = pos[1]
    grid_offset = 100
    cell_size = 80
    if x < grid_offset or x >= grid_offset + cell_size * 10 or y < grid_offset or y >= grid_offset + cell_size * 10:
        xy = (-1, -1)
    else:
        col = (x - grid_offset) // cell_size
        row = (y - grid_offset) // cell_size
        if validate_input(row, col):
            matrix[row][col] = currentPlayer
            xy = (row, col)

def start_player():
    global currentPlayer
    global bottomMsg
    try:
        s.connect((host, port))
        print("Connected to:", host, ":", port)
        recvData = s.recv(2048 * 10)
        bottomMsg = recvData.decode()
        if "1" in bottomMsg:
            currentPlayer = 1
        else:
            currentPlayer = 2
        start_game()
        s.close()
    except socket.error as e:
        print("Socket connection error:", e)

def start_game():
    running = True
    global matrix
    global bottomMsg
    global currentPlayer
    create_thread(accept_msg)
    while running: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if allow:
                    handleMouseEvent(pos)

        buildScreen(bottomMsg, "Player {}'s turn".format(currentPlayer))
        printMatrix(matrix)
        pygame.display.update()

def accept_msg():
    global matrix
    global msg
    global bottomMsg 
    global allow
    global xy
    global currentPlayer
    while True:
        try: 
            recvData = s.recv(2048 * 10)
            recvDataDecode = recvData.decode()
            buildScreen(bottomMsg, recvDataDecode)

            if recvDataDecode == "Input":
                failed = 1
                allow = 1
                xy = (-1, -1)
                while failed:
                    try:
                        if xy != (-1, -1):
                            coordinates = str(xy[0])+"," + str(xy[1])
                            s.send(coordinates.encode())
                            failed = 0
                            allow = 0
                            # Switch the current player after a move
                            currentPlayer = playerTwo if currentPlayer == playerOne else playerOne
                    except:
                        print("Error occurred....Try again")

            elif recvDataDecode == "Error":
                print("Error occurred! Try again..")
            
            elif recvDataDecode == "Matrix":
                print(recvDataDecode)
                matrixRecv = s.recv(2048 * 100)
                matrixRecvDecoded = matrixRecv.decode("utf-8")
                matrix = eval(matrixRecvDecoded)

            elif recvDataDecode == "Over":
                msgRecv = s.recv(2048 * 100)
                msgRecvDecoded = msgRecv.decode("utf-8")
                bottomMsg = msgRecvDecoded
                msg = "~~~Game Over~~~"
                break
            else:
                msg = recvDataDecode

        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            time.sleep(1)
            break

        except:
            print("Error occurred")
            break

start_player()
