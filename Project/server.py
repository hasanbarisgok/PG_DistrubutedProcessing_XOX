import socket
import time

s = socket.socket()
host = ""
port = 9999
matrix = [[0 for _ in range(10)] for _ in range(10)]

playerOne = 1
playerTwo = 2

playerConn = []
playerAddr = []

def get_input(currentPlayer):
    if currentPlayer == playerOne:
        player = "Player One's Turn"
        conn = playerConn[0]
    else:
        player = "Player Two's Turn"
        conn = playerConn[1]
    print(player)
    send_common_msg(player)
    try:
        conn.send("Input".encode())
        data = conn.recv(2048 * 10)
        conn.settimeout(20)
        dataDecoded = data.decode().split(",")
        x = int(dataDecoded[0])
        y = int(dataDecoded[1])
        if x < 0 or x >= 10 or y < 0 or y >= 10:
            raise ValueError("Received out of bounds input")
        matrix[x][y] = currentPlayer
        send_common_msg("Matrix")
        send_common_msg(str(matrix))
    except Exception as e:
        conn.send("Error".encode())
        print(f"Error occurred: {e}")

def check_rows():
    result = 0
    for i in range(10):
        for j in range(6):  # Changed to 6 to avoid index out of range
            if matrix[i][j] == matrix[i][j+1] == matrix[i][j+2] == matrix[i][j+3] == matrix[i][j+4] and matrix[i][j] != 0:
                result = matrix[i][j]
                break
    return result

def check_columns():
    result = 0
    for j in range(10):
        for i in range(6):  # Changed to 6 to avoid index out of range
            if matrix[i][j] == matrix[i+1][j] == matrix[i+2][j] == matrix[i+3][j] == matrix[i+4][j] and matrix[i][j] != 0:
                result = matrix[i][j]
                break
    return result

def check_diagonals():
    result = 0
    for i in range(6):  # Changed to 6 to avoid index out of range
        for j in range(6):  # Changed to 6 to avoid index out of range
            if matrix[i][j] == matrix[i+1][j+1] == matrix[i+2][j+2] == matrix[i+3][j+3] == matrix[i+4][j+4] and matrix[i][j] != 0:
                result = matrix[i][j]
                break
            if matrix[i][j+4] == matrix[i+1][j+3] == matrix[i+2][j+2] == matrix[i+3][j+1] == matrix[i+4][j] and matrix[i][j+4] != 0:
                result = matrix[i][j+4]
                break
    return result

def check_winner():
    result = check_rows()
    if result == 0:
        result = check_columns()
    if result == 0:
        result = check_diagonals()
    return result

# Socket program
def start_server():
    try:
        s.bind((host, port))
        print("Tic Tac Toe server started \nBinding to port", port)
        s.listen(2)
        accept_players()
    except socket.error as e:
        print("Server binding error:", e)

# Accept players
# Send player number
def accept_players():
    try:
        for i in range(2):
            conn, addr = s.accept()
            msg = "<<< You are player {} >>>".format(i+1)
            conn.send(msg.encode())

            playerConn.append(conn)
            playerAddr.append(addr)
            print("Player {} - [{}:{}]".format(i+1, addr[0], str(addr[1])))

        start_game()
        s.close()
    except socket.error as e:
        print("Player connection error", e)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        exit()
    except Exception as e:
        print("Error occurred:", e)

def start_game():
    result = 0
    i = 0
    while result == 0 and i < 100:
        if (i % 2 == 0):
            get_input(playerOne)
        else:
            get_input(playerTwo)
        result = check_winner()
        i += 1

    send_common_msg("Over")

    if result == 1:
        lastmsg = "Player One is the winner!!"
    elif result == 2:
        lastmsg = "Player Two is the winner!!"
    else:
        lastmsg = "Draw game!! Try again later!"

    send_common_msg(lastmsg)
    time.sleep(10)
    for conn in playerConn:
        conn.close()

def send_common_msg(text):
    playerConn[0].send(text.encode())
    playerConn[1].send(text.encode())
    time.sleep(1)

start_server()
