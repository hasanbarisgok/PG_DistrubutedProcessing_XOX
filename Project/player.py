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
msg = "Waiting for peer"
currentPlayer = 0
xy = (-1, -1)
allow = 0 #allow handling mouse events
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
