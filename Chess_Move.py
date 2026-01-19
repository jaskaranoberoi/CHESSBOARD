import chess # type: ignore
import chess.engine #type: ignore
import chess.pgn #type: ignore
import time
import numpy as np
from pathlib import Path
#from chessboard_detector import get_chessboard
import requests
import sys
import json
from ChessBoard_Creation import ChessBoard_Creation
from Chess_MoveDetection import Chess_MoveDetection
from MoveValidator import is_legal_move
from Fen_To_Array import fen_to_array
import cv2
from PIL import Image
import torch
#import serial
import time
from Test12 import move_validity
from T6 import Algo2
from Move_Predictor import validate_or_recover
import re
from Trial12 import get_chessboard11

# import pyttsx3
# from LightLeds import light_up_leds

# ser = serial.Serial('COM9', 115200)

ChessBoard_Array_ValidMove = np.array([
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
])


import os
print("Current Working Directory:", os.getcwd())

#engine = pyttsx3.init()
model_ChessCorner = torch.hub.load("yolov5", 'custom', path="Models\\exp4\\weights\\best.pt", source='local')
model = torch.hub.load("yolov5", 'custom', path="Models\\BestModel\\best.pt", source='local')
model_handdetection = torch.hub.load("yolov5",'custom', path="Models\\exp5\\weights\\best.pt", source='local')
#model_handgesture = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5','custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp6\weights\best.pt', source='local')

camera_index = 0  # try 0 if this doesn't work
cap = cv2.VideoCapture(camera_index)

# Wait until the camera is opened (with timeout safety)
start_time = time.time()
while not cap.isOpened():
    if time.time() - start_time > 10:  # wait max 10 seconds
        raise RuntimeError("Camera failed to open!")
    print("Waiting for camera to open...")
    time.sleep(0.5)

print("Camera is ready!")

img_saved = False

# def announce_move(move):
#     engine.say(move)
#     engine.runAndWait()

fen_array = np.full(120, '', dtype=object)
#time.sleep(10)
ChessBoard_array = ChessBoard_Creation()

def get_chessboard(PathOfImage):
    global ChessBoard_Array_ValidMove
    ChessBoard_Array_ValidMove1 = ChessBoard_Array_ValidMove
    model_ChessCorner.conf = 0.05
    Image_path = PathOfImage

    result_ChessCorner = model_ChessCorner(Image_path)
    result_ChessCorner.print()
    result_ChessCorner.save() 

    Corner_Coordinates = []

    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()
    for detection in detections_ChessCorner:
        xmin, ymin, xmax, ymax, confidence, class_id = detection
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        print("Xmin: ",xmin,"Ymin: ", ymin, "Xmax: ",xmax,"Ymax: " ,ymax,"Confidence: " ,confidence,"Class_id: " ,class_id,"Center_X: " ,center_x, "Center_y: ",center_y)

        Corner_Coordinates.append([center_x, center_y])

    print("Raw Corner Coordinates:", Corner_Coordinates)

    Corner_Coordinates_Array = np.array(Corner_Coordinates).astype(int)

    i = 0
    while i < len(Corner_Coordinates_Array) - 1:
        j = i + 1
        while j < len(Corner_Coordinates_Array):
            if abs(Corner_Coordinates_Array[i][0] - Corner_Coordinates_Array[j][0]) < 40 and abs(Corner_Coordinates_Array[i][1] - Corner_Coordinates_Array[j][1]) < 40:
                Corner_Coordinates_Array = np.delete(Corner_Coordinates_Array, j, axis=0)
            else:
                j += 1
        i += 1

    print("Filtered Corner Coordinates:")
    for coord in Corner_Coordinates_Array:
        print(coord)
    
    Corner_Coordinates_Array = Corner_Coordinates_Array[np.argsort(Corner_Coordinates_Array[:, 0], kind='mergesort')]
    X1 = Corner_Coordinates_Array[0][0]
    Y1 = Corner_Coordinates_Array[0][1]

    i1 = 0
    min_x = 1000
    for i in range(0,3):
        if(min_x>abs(X1-Corner_Coordinates_Array[i+1][0])):
            min_x = abs(X1-Corner_Coordinates_Array[i+1][0])
            i1 = i + 1
    X4 = Corner_Coordinates_Array[i1][0]
    Y4 = Corner_Coordinates_Array[i1][1]

    min_y = 1000
    j1 = 0
    for j in range(0,3):
        if(min_y>abs(Y1-Corner_Coordinates_Array[j+1][1])):
            min_y = abs(Y1-Corner_Coordinates_Array[j+1][1])
            j1 = j+1

    X2 = Corner_Coordinates_Array[j1][0]
    Y2 = Corner_Coordinates_Array[j1][1]

    i2 = 0
    j2 = 0
    X3 = 0
    Y3 = 0
    for i in range(0,4):
        if X1!=Corner_Coordinates_Array[i][[0]] and X2!=Corner_Coordinates_Array[i][0] and X4!=Corner_Coordinates_Array[i][0]:
            if X1!=Corner_Coordinates_Array[i][[1]] and X2!=Corner_Coordinates_Array[i][1] and X4!=Corner_Coordinates_Array[i][1]:
                X3 = Corner_Coordinates_Array[i][0]
                Y3 = Corner_Coordinates_Array[i][1]

    print("X1:", X1, "Y1:", Y1)
    print("X2:", X2, "Y2:", Y2)
    print("X3:", X3, "Y3:", Y3)
    print("X4:", X4, "Y4:", Y4)

    Coordinates_arr_X = np.zeros((9,9))
    Coordinates_arr_Y = np.zeros((9,9))

    Coordinates_arr_X[0][0] = X1
    Coordinates_arr_Y[0][0] = Y1

    Coordinates_arr_X[0][8] = X4
    Coordinates_arr_Y[0][8] = Y4

    Coordinates_arr_X[8][0] = X2
    Coordinates_arr_Y[8][0] = Y2

    Coordinates_arr_X[8][8] = X3
    Coordinates_arr_Y[8][8] = Y3

    Coordinates_arr_X[4][0] = (X1 + X2)/2
    Coordinates_arr_Y[4][0] = (Y1 + Y2)/2

    Coordinates_arr_X[2][0] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[0][0])/2
    Coordinates_arr_Y[2][0] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[0][0])/2

    Coordinates_arr_X[6][0] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[8][0])/2
    Coordinates_arr_Y[6][0] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[8][0])/2
    
    Coordinates_arr_X[1][0] = (Coordinates_arr_X[2][0] + Coordinates_arr_X[0][0])/2
    Coordinates_arr_Y[1][0] = (Coordinates_arr_Y[2][0] + Coordinates_arr_Y[0][0])/2
    
    Coordinates_arr_X[3][0] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[2][0])/2
    Coordinates_arr_Y[3][0] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[2][0])/2

    Coordinates_arr_X[5][0] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[6][0])/2
    Coordinates_arr_Y[5][0] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[6][0])/2
    
    Coordinates_arr_X[7][0] = (Coordinates_arr_X[6][0] + Coordinates_arr_X[8][0])/2
    Coordinates_arr_Y[7][0] = (Coordinates_arr_Y[6][0] + Coordinates_arr_Y[8][0])/2
    
    Coordinates_arr_X[0][4] = (Coordinates_arr_X[0][0] + Coordinates_arr_X[0][8])/2
    Coordinates_arr_Y[0][4] = (Coordinates_arr_Y[0][0] + Coordinates_arr_Y[0][8])/2
    
    Coordinates_arr_X[0][2] = (Coordinates_arr_X[0][0] + Coordinates_arr_X[0][4])/2
    Coordinates_arr_Y[0][2] = (Coordinates_arr_Y[0][0] + Coordinates_arr_Y[0][4])/2

    Coordinates_arr_X[0][6] = (Coordinates_arr_X[0][4] + Coordinates_arr_X[0][8])/2
    Coordinates_arr_Y[0][6] = (Coordinates_arr_Y[0][4] + Coordinates_arr_Y[0][8])/2

    Coordinates_arr_X[0][1] = (Coordinates_arr_X[0][0] + Coordinates_arr_X[0][2])/2
    Coordinates_arr_Y[0][1] = (Coordinates_arr_Y[0][0] + Coordinates_arr_Y[0][2])/2

    Coordinates_arr_X[0][3] = (Coordinates_arr_X[0][2] + Coordinates_arr_X[0][4])/2
    Coordinates_arr_Y[0][3] = (Coordinates_arr_Y[0][2] + Coordinates_arr_Y[0][4])/2
    
    Coordinates_arr_X[0][5] = (Coordinates_arr_X[0][4] + Coordinates_arr_X[0][6])/2
    Coordinates_arr_Y[0][5] = (Coordinates_arr_Y[0][4] + Coordinates_arr_Y[0][6])/2
    
    Coordinates_arr_X[0][7] = (Coordinates_arr_X[0][6] + Coordinates_arr_X[0][8])/2
    Coordinates_arr_Y[0][7] = (Coordinates_arr_Y[0][6] + Coordinates_arr_Y[0][8])/2

    Coordinates_arr_X[4][8] = (Coordinates_arr_X[0][8] + Coordinates_arr_X[8][8])/2
    Coordinates_arr_Y[4][8] = (Coordinates_arr_Y[0][8] + Coordinates_arr_Y[8][8])/2
    
    Coordinates_arr_X[2][8] = (Coordinates_arr_X[4][8] + Coordinates_arr_X[0][8])/2
    Coordinates_arr_Y[2][8] = (Coordinates_arr_Y[4][8] + Coordinates_arr_Y[0][8])/2
    
    Coordinates_arr_X[6][8] = (Coordinates_arr_X[4][8] + Coordinates_arr_X[8][8])/2
    Coordinates_arr_Y[6][8] = (Coordinates_arr_Y[4][8] + Coordinates_arr_Y[8][8])/2
    
    Coordinates_arr_X[1][8] = (Coordinates_arr_X[2][8] + Coordinates_arr_X[0][8])/2
    Coordinates_arr_Y[1][8] = (Coordinates_arr_Y[2][8] + Coordinates_arr_Y[0][8])/2
    
    Coordinates_arr_X[3][8] = (Coordinates_arr_X[2][8] + Coordinates_arr_X[4][8])/2
    Coordinates_arr_Y[3][8] = (Coordinates_arr_Y[2][8] + Coordinates_arr_Y[4][8])/2
    
    Coordinates_arr_X[5][8] = (Coordinates_arr_X[4][8] + Coordinates_arr_X[6][8])/2
    Coordinates_arr_Y[5][8] = (Coordinates_arr_Y[4][8] + Coordinates_arr_Y[6][8])/2
    
    Coordinates_arr_X[7][8] = (Coordinates_arr_X[6][8] + Coordinates_arr_X[8][8])/2
    Coordinates_arr_Y[7][8] = (Coordinates_arr_Y[6][8] + Coordinates_arr_Y[8][8])/2

    Coordinates_arr_X[8][4] = (Coordinates_arr_X[8][0] + Coordinates_arr_X[8][8])/2
    Coordinates_arr_Y[8][4] = (Coordinates_arr_Y[8][0] + Coordinates_arr_Y[8][8])/2

    Coordinates_arr_X[8][2] = (Coordinates_arr_X[8][0] + Coordinates_arr_X[8][4])/2
    Coordinates_arr_Y[8][2] = (Coordinates_arr_Y[8][0] + Coordinates_arr_Y[8][4])/2

    Coordinates_arr_X[8][6] = (Coordinates_arr_X[8][4] + Coordinates_arr_X[8][8])/2
    Coordinates_arr_Y[8][6] = (Coordinates_arr_Y[8][4] + Coordinates_arr_Y[8][8])/2

    Coordinates_arr_X[8][1] = (Coordinates_arr_X[8][0] + Coordinates_arr_X[8][2])/2
    Coordinates_arr_Y[8][1] = (Coordinates_arr_Y[8][0] + Coordinates_arr_Y[8][2])/2

    Coordinates_arr_X[8][3] = (Coordinates_arr_X[8][2] + Coordinates_arr_X[8][4])/2
    Coordinates_arr_Y[8][3] = (Coordinates_arr_Y[8][2] + Coordinates_arr_Y[8][4])/2

    Coordinates_arr_X[8][5] = (Coordinates_arr_X[8][4] + Coordinates_arr_X[8][6])/2
    Coordinates_arr_Y[8][5] = (Coordinates_arr_Y[8][4] + Coordinates_arr_Y[8][6])/2

    Coordinates_arr_X[8][7] = (Coordinates_arr_X[8][6] + Coordinates_arr_X[8][8])/2
    Coordinates_arr_Y[8][7] = (Coordinates_arr_Y[8][6] + Coordinates_arr_Y[8][8])/2

    Coordinates_arr_X[1][4] = (Coordinates_arr_X[1][0] + Coordinates_arr_X[1][8])/2
    Coordinates_arr_Y[1][4] = (Coordinates_arr_Y[1][0] + Coordinates_arr_Y[1][8])/2

    Coordinates_arr_X[1][6] = (Coordinates_arr_X[1][4] + Coordinates_arr_X[1][8])/2
    Coordinates_arr_Y[1][6] = (Coordinates_arr_Y[1][4] + Coordinates_arr_Y[1][8])/2

    Coordinates_arr_X[1][2] = (Coordinates_arr_X[1][0] + Coordinates_arr_X[1][4])/2
    Coordinates_arr_Y[1][2] = (Coordinates_arr_Y[1][0] + Coordinates_arr_Y[1][4])/2

    Coordinates_arr_X[1][1] = (Coordinates_arr_X[1][0] + Coordinates_arr_X[1][2])/2
    Coordinates_arr_Y[1][1] = (Coordinates_arr_Y[1][0] + Coordinates_arr_Y[1][2])/2

    Coordinates_arr_X[1][3] = (Coordinates_arr_X[1][2] + Coordinates_arr_X[1][4])/2
    Coordinates_arr_Y[1][3] = (Coordinates_arr_Y[1][2] + Coordinates_arr_Y[1][4])/2
    
    Coordinates_arr_X[1][5] = (Coordinates_arr_X[1][4] + Coordinates_arr_X[1][6])/2
    Coordinates_arr_Y[1][5] = (Coordinates_arr_Y[1][4] + Coordinates_arr_Y[1][6])/2

    Coordinates_arr_X[1][7] = (Coordinates_arr_X[1][6] + Coordinates_arr_X[1][8])/2
    Coordinates_arr_Y[1][7] = (Coordinates_arr_Y[1][6] + Coordinates_arr_Y[1][8])/2

    Coordinates_arr_X[2][4] = (Coordinates_arr_X[2][0] + Coordinates_arr_X[2][8])/2
    Coordinates_arr_Y[2][4] = (Coordinates_arr_Y[2][0] + Coordinates_arr_Y[2][8])/2

    Coordinates_arr_X[2][2] = (Coordinates_arr_X[2][0] + Coordinates_arr_X[2][4])/2
    Coordinates_arr_Y[2][2] = (Coordinates_arr_Y[2][0] + Coordinates_arr_Y[2][4])/2   

    Coordinates_arr_X[2][6] = (Coordinates_arr_X[2][4] + Coordinates_arr_X[2][8])/2
    Coordinates_arr_Y[2][6] = (Coordinates_arr_Y[2][4] + Coordinates_arr_Y[2][8])/2

    Coordinates_arr_X[2][1] = (Coordinates_arr_X[2][0] + Coordinates_arr_X[2][2])/2
    Coordinates_arr_Y[2][1] = (Coordinates_arr_Y[2][0] + Coordinates_arr_Y[2][2])/2

    Coordinates_arr_X[2][3] = (Coordinates_arr_X[2][2] + Coordinates_arr_X[2][4])/2
    Coordinates_arr_Y[2][3] = (Coordinates_arr_Y[2][2] + Coordinates_arr_Y[2][4])/2

    Coordinates_arr_X[2][5] = (Coordinates_arr_X[2][4] + Coordinates_arr_X[2][6])/2
    Coordinates_arr_Y[2][5] = (Coordinates_arr_Y[2][4] + Coordinates_arr_Y[2][6])/2

    Coordinates_arr_X[2][7] = (Coordinates_arr_X[2][6] + Coordinates_arr_X[2][8])/2
    Coordinates_arr_Y[2][7] = (Coordinates_arr_Y[2][6] + Coordinates_arr_Y[2][8])/2

    Coordinates_arr_X[3][4] = (Coordinates_arr_X[3][0] + Coordinates_arr_X[3][8])/2
    Coordinates_arr_Y[3][4] = (Coordinates_arr_Y[3][0] + Coordinates_arr_Y[3][8])/2

    Coordinates_arr_X[3][2] = (Coordinates_arr_X[3][0] + Coordinates_arr_X[3][4])/2
    Coordinates_arr_Y[3][2] = (Coordinates_arr_Y[3][0] + Coordinates_arr_Y[3][4])/2

    Coordinates_arr_X[3][6] = (Coordinates_arr_X[3][4] + Coordinates_arr_X[3][8])/2
    Coordinates_arr_Y[3][6] = (Coordinates_arr_Y[3][4] + Coordinates_arr_Y[3][8])/2

    Coordinates_arr_X[3][1] = (Coordinates_arr_X[3][0] + Coordinates_arr_X[3][2])/2
    Coordinates_arr_Y[3][1] = (Coordinates_arr_Y[3][0] + Coordinates_arr_Y[3][2])/2

    Coordinates_arr_X[3][3] = (Coordinates_arr_X[3][2] + Coordinates_arr_X[3][4])/2
    Coordinates_arr_Y[3][3] = (Coordinates_arr_Y[3][2] + Coordinates_arr_Y[3][4])/2

    Coordinates_arr_X[3][5] = (Coordinates_arr_X[3][4] + Coordinates_arr_X[3][6])/2
    Coordinates_arr_Y[3][5] = (Coordinates_arr_Y[3][4] + Coordinates_arr_Y[3][6])/2
    
    Coordinates_arr_X[3][7] = (Coordinates_arr_X[3][6] + Coordinates_arr_X[3][8])/2
    Coordinates_arr_Y[3][7] = (Coordinates_arr_Y[3][6] + Coordinates_arr_Y[3][8])/2

    Coordinates_arr_X[4][4] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[4][8])/2
    Coordinates_arr_Y[4][4] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[4][8])/2

    Coordinates_arr_X[4][2] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[4][4])/2
    Coordinates_arr_Y[4][2] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[4][4])/2

    Coordinates_arr_X[4][6] = (Coordinates_arr_X[4][4] + Coordinates_arr_X[4][8])/2
    Coordinates_arr_Y[4][6] = (Coordinates_arr_Y[4][4] + Coordinates_arr_Y[4][8])/2

    Coordinates_arr_X[4][1] = (Coordinates_arr_X[4][0] + Coordinates_arr_X[4][2])/2
    Coordinates_arr_Y[4][1] = (Coordinates_arr_Y[4][0] + Coordinates_arr_Y[4][2])/2

    Coordinates_arr_X[4][3] = (Coordinates_arr_X[4][2] + Coordinates_arr_X[4][4])/2
    Coordinates_arr_Y[4][3] = (Coordinates_arr_Y[4][2] + Coordinates_arr_Y[4][4])/2

    Coordinates_arr_X[4][5] = (Coordinates_arr_X[4][4] + Coordinates_arr_X[4][6])/2
    Coordinates_arr_Y[4][5] = (Coordinates_arr_Y[4][4] + Coordinates_arr_Y[4][6])/2
    
    Coordinates_arr_X[4][7] = (Coordinates_arr_X[4][6] + Coordinates_arr_X[4][8])/2
    Coordinates_arr_Y[4][7] = (Coordinates_arr_Y[4][6] + Coordinates_arr_Y[4][8])/2

    Coordinates_arr_X[5][4] = (Coordinates_arr_X[5][0] + Coordinates_arr_X[5][8])/2
    Coordinates_arr_Y[5][4] = (Coordinates_arr_Y[5][0] + Coordinates_arr_Y[5][8])/2

    Coordinates_arr_X[5][2] = (Coordinates_arr_X[5][0] + Coordinates_arr_X[5][4])/2
    Coordinates_arr_Y[5][2] = (Coordinates_arr_Y[5][0] + Coordinates_arr_Y[5][4])/2

    Coordinates_arr_X[5][6] = (Coordinates_arr_X[5][4] + Coordinates_arr_X[5][8])/2
    Coordinates_arr_Y[5][6] = (Coordinates_arr_Y[5][4] + Coordinates_arr_Y[5][8])/2

    Coordinates_arr_X[5][1] = (Coordinates_arr_X[5][0] + Coordinates_arr_X[5][2])/2
    Coordinates_arr_Y[5][1] = (Coordinates_arr_Y[5][0] + Coordinates_arr_Y[5][2])/2

    Coordinates_arr_X[5][3] = (Coordinates_arr_X[5][2] + Coordinates_arr_X[5][4])/2
    Coordinates_arr_Y[5][3] = (Coordinates_arr_Y[5][2] + Coordinates_arr_Y[5][4])/2

    Coordinates_arr_X[5][5] = (Coordinates_arr_X[5][4] + Coordinates_arr_X[5][6])/2
    Coordinates_arr_Y[5][5] = (Coordinates_arr_Y[5][4] + Coordinates_arr_Y[5][6])/2

    Coordinates_arr_X[5][7] = (Coordinates_arr_X[5][6] + Coordinates_arr_X[5][8])/2
    Coordinates_arr_Y[5][7] = (Coordinates_arr_Y[5][6] + Coordinates_arr_Y[5][8])/2

    Coordinates_arr_X[6][4] = (Coordinates_arr_X[6][0] + Coordinates_arr_X[6][8])/2
    Coordinates_arr_Y[6][4] = (Coordinates_arr_Y[6][0] + Coordinates_arr_Y[6][8])/2

    Coordinates_arr_X[6][2] = (Coordinates_arr_X[6][0] + Coordinates_arr_X[6][4])/2
    Coordinates_arr_Y[6][2] = (Coordinates_arr_Y[6][0] + Coordinates_arr_Y[6][4])/2

    Coordinates_arr_X[6][6] = (Coordinates_arr_X[6][4] + Coordinates_arr_X[6][8])/2
    Coordinates_arr_Y[6][6] = (Coordinates_arr_Y[6][4] + Coordinates_arr_Y[6][8])/2

    Coordinates_arr_X[6][1] = (Coordinates_arr_X[6][0] + Coordinates_arr_X[6][2])/2
    Coordinates_arr_Y[6][1] = (Coordinates_arr_Y[6][0] + Coordinates_arr_Y[6][2])/2

    Coordinates_arr_X[6][3] = (Coordinates_arr_X[6][2] + Coordinates_arr_X[6][4])/2
    Coordinates_arr_Y[6][3] = (Coordinates_arr_Y[6][2] + Coordinates_arr_Y[6][4])/2

    Coordinates_arr_X[6][5] = (Coordinates_arr_X[6][4] + Coordinates_arr_X[6][6])/2
    Coordinates_arr_Y[6][5] = (Coordinates_arr_Y[6][4] + Coordinates_arr_Y[6][6])/2

    Coordinates_arr_X[6][7] = (Coordinates_arr_X[6][6] + Coordinates_arr_X[6][8])/2
    Coordinates_arr_Y[6][7] = (Coordinates_arr_Y[6][6] + Coordinates_arr_Y[6][8])/2

    Coordinates_arr_X[7][4] = (Coordinates_arr_X[7][0] + Coordinates_arr_X[7][8])/2
    Coordinates_arr_Y[7][4] = (Coordinates_arr_Y[7][0] + Coordinates_arr_Y[7][8])/2

    Coordinates_arr_X[7][2] = (Coordinates_arr_X[7][0] + Coordinates_arr_X[7][4])/2
    Coordinates_arr_Y[7][2] = (Coordinates_arr_Y[7][0] + Coordinates_arr_Y[7][4])/2

    Coordinates_arr_X[7][6] = (Coordinates_arr_X[7][4] + Coordinates_arr_X[7][8])/2
    Coordinates_arr_Y[7][6] = (Coordinates_arr_Y[7][4] + Coordinates_arr_Y[7][8])/2

    Coordinates_arr_X[7][1] = (Coordinates_arr_X[7][0] + Coordinates_arr_X[7][2])/2
    Coordinates_arr_Y[7][1] = (Coordinates_arr_Y[7][0] + Coordinates_arr_Y[7][2])/2

    Coordinates_arr_X[7][3] = (Coordinates_arr_X[7][2] + Coordinates_arr_X[7][4])/2
    Coordinates_arr_Y[7][3] = (Coordinates_arr_Y[7][2] + Coordinates_arr_Y[7][4])/2

    Coordinates_arr_X[7][5] = (Coordinates_arr_X[7][4] + Coordinates_arr_X[7][6])/2
    Coordinates_arr_Y[7][5] = (Coordinates_arr_Y[7][4] + Coordinates_arr_Y[7][6])/2

    Coordinates_arr_X[7][7] = (Coordinates_arr_X[7][6] + Coordinates_arr_X[7][8])/2
    Coordinates_arr_Y[7][7] = (Coordinates_arr_Y[7][6] + Coordinates_arr_Y[7][8])/2
    
    print(Coordinates_arr_X)
    print("\n\n")
    print(Coordinates_arr_Y)

    ChessBoard = np.full((8, 8), '*', dtype=str)
    model.conf = 0.65

    results = model(Image_path)

    results.print()
    results.save()

    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()

    df = results.pandas().xyxy[0]

    bounding_boxes_with_names = []
    var_bore = []

    for index, row in df.iterrows():
        xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        width = xmax - xmin
        height = ymax - ymin
        avg_x = (xmax + xmin)/2
        avg_y = (ymax+ ymin)/2
        confidence = row['confidence']
        piece_name = row['name']

        var_bore.append([xmin, ymin, xmax, ymax])
        bounding_boxes_with_names.append([avg_x, avg_y, width, height, piece_name])

    print("\n", var_bore)
    bounding_boxes_array = np.array([item[:4] for item in bounding_boxes_with_names])
    print("\nBounding Boxes:")
    for bbox in bounding_boxes_with_names:
        print(f"AvgX={bbox[0]}, AvgY={bbox[1]}, Width={bbox[2]}, Height={bbox[3]}, Piece Name={bbox[4]}")
    piece_names = [item[4] for item in bounding_boxes_with_names]


    for k in range(0,len(bounding_boxes_array)):
        temp1 = '*'
        if piece_names[k]=='Black_rook':
            temp1 = 'r'
            temp_mul = 1
        elif piece_names[k]=='Black_bishop':
            temp1 = 'b'
        elif piece_names[k]=='Black_knight':
            temp1 = 'n'
        elif piece_names[k]=='Black_pawn':
            temp1 = 'p'
        elif piece_names[k]=='Black_queen':
            temp1 = 'q'
        elif piece_names[k]=='Black_king':
            temp1 = 'k'
        elif piece_names[k]=='White_pawn':
            temp1 = 'P'
            temp_mul = 1
        elif piece_names[k]=='White_knight':
            temp1 = 'N'
            temp_mul = 1
        elif piece_names[k]=='White_bishop':
            temp1 = 'B'
            temp_mul = 1
        elif piece_names[k]=='White_king':
            temp1 = 'K'
        elif piece_names[k]=='White_Queen':
            temp1 = 'Q'
        elif piece_names[k]=='White_rook':
            temp1 = 'R'
        #print("We are in loop")
        # if(bounding_boxes_array[k][3]<100):
        #     temp_mul = 1.25
        # elif(bounding_boxes_array[k][3]<125 and bounding_boxes_array[k][3]>=100):
        #     temp_mul = 1
        # elif(bounding_boxes_array[k][3]>=125):
        #     temp_mul = 1.75
        X = bounding_boxes_array[k][0]
        Y = bounding_boxes_array[k][1]
        # X = X + bounding_boxes_array[k][2] * 0.1
        #Y = Y + bounding_boxes_array[k][3] * temp_mul
        # Y = Y+height*0.2
        if str(piece_names[k])!='White_rook' and str(piece_names[k])!='Black_rook':
            Y = Y + bounding_boxes_array[k][3] * 0.55
        else:
            Y = Y + bounding_boxes_array[k][3] * 0.2
        #for i in range(0,8):

        print(X,Y)
        for i in range(0,8):
            for j in range(0,8):
                if X>Coordinates_arr_X[i][j] and X<Coordinates_arr_X[i+1][j+1] and Y<Coordinates_arr_Y[i][j] and Y>Coordinates_arr_Y[i+1][j+1]:
                    print('Inside if condition: ')
                    print(i,j)
                    ChessBoard[i][j] = temp1

    if(move_validity(ChessBoard_Array_ValidMove, ChessBoard)):
        ChessBoard_Array_ValidMove=ChessBoard
    print(ChessBoard)
    return ChessBoard
    #Rotated_ChessBoard = np.rot90(ChessBoard, k=1)
    #print(Rotated_ChessBoard)
    ChessBoard = Algo2(Image_path)
    if(move_validity(ChessBoard_Array_ValidMove, ChessBoard)):
        ChessBoard_Array_ValidMove=ChessBoard
        return ChessBoard
    print(ChessBoard)
    return ChessBoard_Array_ValidMove1

def read_player_color():
    if len(sys.argv) < 2:
        print("Error: Player_Color argument is required.")
        sys.exit(1)

    try:
        player_color = int(sys.argv[1])  # Either 0 or 1
        if player_color not in [0, 1]:
            raise ValueError("Player_Color must be 0 or 1")
        return player_color
    except (IndexError, ValueError) as e:
        print(f"Error processing Player_Color argument: {e}")
        sys.exit(1)

Player_Color = read_player_color()

# Path to the Stockfish engine executable
engine_path = "stockfish\stockfish.exe"

# Start the engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
JC = 0
def fetch_chessboard(image_path):
    global JC
    if JC==0:
        image_path = "Images1\\C52.jpg"  # Double backslashes for Windows paths
        JC += 1
    else:
        image_path = "Images1\\C53.jpg"  # Double backslashes for Windows paths
    
    ChessBoard1 = get_chessboard11(image_path)
    ChessBoard = [['' if piece == '*' else piece for piece in row] for row in ChessBoard1]
    return ChessBoard,ChessBoard1

def array_to_fen(ChessBoard):
    board = chess.Board(None)
    piece_map = {
        'P': 'P', 'p': 'p',
        'R': 'R', 'r': 'r',
        'N': 'N', 'n': 'n',
        'B': 'B', 'b': 'b',
        'Q': 'Q', 'q': 'q',
        'K': 'K', 'k': 'k',
        '*': None
    }
    for row in range(8):
        for col in range(8):
            piece_symbol = ChessBoard[row][col]
            if piece_symbol:
                square = chess.square(col, 7 - row)
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))
    return board.fen()

def send_fen_to_javascript(fen, pgn=None, move_count=None):
    url = 'http://localhost:3000/update_fen'
    payload = {'fen': fen}
    
    if pgn:
        payload['pgn'] = pgn
    if move_count is not None:
        payload['move_count'] = move_count
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"FEN successfully sent to JavaScript: {fen}")
    except requests.RequestException as e:
        print(f"Error sending FEN to JavaScript: {e}")

def get_best_move(board):
    try:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        move = result.move
        board.push(move)
        return move, board
    except Exception as e:
        print(f"Error getting best move: {e}")
        return None, board

def fen_to_pgn(prev_fen, new_fen):
    board = chess.Board(prev_fen)

    new_fen_position = new_fen.split(" ")[0]  # only piece placement

    for move in board.legal_moves:
        move_san = board.san(move)
        board.push(move)

        if board.fen().split(" ")[0] == new_fen_position:
            return move_san

        board.pop()

    raise ValueError(f"Could not find a valid move leading to the new FEN: {new_fen}")

def update_fen_to_move(current_fen, move_side):
    parts = current_fen.split()
    if (move_side == 'white' and parts[1] == 'b') or (move_side == 'black' and parts[1] == 'w'):
        parts[1] = 'b' if move_side == 'black' else 'w'
        return ' '.join(parts)
    else:
        return current_fen

    
def add_castling_rights(fen, castling_rights):
    parts = fen.split()
    
    if len(parts) != 6:
        raise ValueError("Invalid FEN string")

    parts[2] = castling_rights

    updated_fen = ' '.join(parts)
    return updated_fen

def increment_fen_move_count(fen, noofmoves, half_moves):
    parts = fen.split()

    if len(parts) != 6:
        raise ValueError("Invalid FEN string")

    # Move count is in the 6th field (index 5)
    move_count = int(parts[5])

    # Half-move clock is in the 5th field (index 4)
    half_move_clock = int(parts[4])

    if noofmoves % 2 == 0:
        move_count += noofmoves // 2
    else:
        move_count += 1 + (noofmoves // 2)

    half_move_clock = half_moves

    if half_moves == 0:
        half_move_clock = 0

    parts[4] = str(half_move_clock)
    parts[5] = str(move_count)
    
    updated_fen = ' '.join(parts)
    
    return updated_fen

def get_halfmove_count(fen):
    # FEN consists of 6 fields, and the half-move clock is the 5th one.
    fen_fields = fen.split()
    
    # The 5th field contains the half-move clock
    halfmove_clock = int(fen_fields[4])
    
    return halfmove_clock

def get_castling_rights(fen):
    # FEN consists of 6 fields, and the castling rights are the 4th one.
    fen_fields = fen.split()
    
    # The 4th field contains the castling rights
    castling_rights = fen_fields[2]
    
    return castling_rights

def handle_undo_request():
    global previous_fen, move_count, ChessBoard_array,current_fen,Player_Color,previous_black_fen,previous_white_fen,Current_Half_Move,castling_rights
    if previous_fen:
        # if move_count==2 or move_count==1:
        #     ChessBoard_array = ChessBoard_Creation()
        #     fen_to_send = fen_to_array(ChessBoard_array)
        #     previous_fen = fen_to_array(ChessBoard_array)
        #     current_fen = fen_to_array(ChessBoard_array)
        #     previous_white_fen = ChessBoard_Creation()
        #     previous_black_fen = ChessBoard_Creation()
        #     send_fen_to_javascript(fen_to_send,pgn,move_count)
        #     move_count = 0
        #     return
        # elif move_count == 3:
        #     fen_to_send = fen_array[1]
        #     ChessBoard_array = ChessBoard_Creation()
        #     previous_fen = fen_to_array(ChessBoard_array)
        #     current_fen = fen_to_send
        #     previous_white_fen = ChessBoard_Creation()
        #     previous_black_fen = ChessBoard_Creation()
        #     send_fen_to_javascript(fen_to_send,pgn,move_count)
        #     move_count = 0
        #     return
        # # Use previous_fen to revert to the last known good state
        # else:
        fen_to_send = fen_array[move_count-3]
        # ChessBoard_array = fen_to_array(previous_fen)
        
        print("Inside undo function")
        if Player_Color == 1:
            previous_fen = fen_array[move_count-4]
            previous_white_fen = fen_array[move_count-4]
            previous_black_fen = fen_array[move_count-4]
        elif Player_Color == 0:
            previous_fen = fen_array[move_count-4]
            previous_white_fen = fen_array[move_count-4]
            previous_black_fen = fen_array[move_count-4]

        move_count -= 2
        current_fen = fen_to_send
        ChessBoard_array = fen_to_array(previous_fen)
        ChessBoard_Current = fen_to_array(current_fen)
        print(Current_Half_Move)
        previous_fen = current_fen
        Current_Half_Move = get_halfmove_count(previous_fen)
        ChessBoard_array = ChessBoard_Current

        if Player_Color == 1:
            previous_fen = update_fen_to_move(previous_fen, 'black')
            castling_rights = get_castling_rights(previous_fen)

        elif Player_Color == 0:
            previous_fen = update_fen_to_move(previous_fen, 'white')
            castling_rights = get_castling_rights(previous_fen)
        
        send_fen_to_javascript(fen_to_send,pgn,move_count)
        time.sleep(3)
        print(f"Undo: Reverted to FEN: {fen_to_send}")

def compare_piece_positions(fen1, fen2):
    # Extract only the piece placement part from the FEN strings (the first part)
    pieces_fen1 = fen1.split()[0]
    pieces_fen2 = fen2.split()[0]
    
    # Compare the piece placement parts
    if pieces_fen1 == pieces_fen2:
        return False
    else:
        return True
    

# Initialize variables
move_count = 0
game_start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
previous_fen = game_start_fen
previous_white_fen = None
previous_black_fen = None
current_fen = game_start_fen
castling_rights = 'KQkq'
Current_Half_Move = 0


try:
    while True:
        for _ in range(10):  # Read a few frames to let the camera adjust
            ret, _ = cap.read()
            if ret:
                break
            time.sleep(0.1)  # Small delay to retry
        time.sleep(5)
        ret, current_frame = cap.read()
        if not ret:
            print("Failed to grab frame")
        else:
            height, width, _ = current_frame.shape

            # If image is taller than wide, rotate 90 degrees to make it horizontal
            if height > width:
                current_frame = cv2.rotate(current_frame, cv2.ROTATE_90_CLOCKWISE)

            # After this, current_frame will always be horizontal
            height, width, _ = current_frame.shape


        # Display the current frame
        #cv2.imshow("Camera", current_frame)

        # Save the image only once
        img_path = "images\\captured_image.jpg"

        # Capture the current frame
        cv2.imwrite(img_path, current_frame)
        print(f"Image saved at: {img_path}")
        img_saved = True

        # Load the YOLOv5 model for hand detection

        # # Set the confidence threshold
        # model_handgesture.conf = 0.1

        # # Perform inference on the image
        # results = model_handgesture(img_path)

        # # Print the results
        # results.print()

        # # Save the results
        # results.save()

        # # Check if a hand is detected
        # detected_objects = results.pandas().xyxy[0]  # Get the detection results as a DataFrame

        # if len(detected_objects) > 0:
        #     print("Hand detected! Capturing another image...")
        #     # Capture another image if hand is detected
        #     time.sleep(5)
        #     cv2.imwrite(img_path, current_frame)
        #     print(f"Second image saved at: {img_path}")
        # else:
        #     print("No hand detected.")

        model_handdetection.conf = 0.05

        # Perform inference on the image
        #results = model_handdetection(img_path)

        # Print the results
        #results.print()

        # Save the results
        #results.save()

        # Check if a hand is detected
        #detected_objects = results.pandas().xyxy[0]  # Get the detection results as a DataFrame

        # if len(detected_objects) > 0:
        #     print("Hand detected! Capturing another image...")
        #     # Capture another image if hand is detected
        #     time.sleep(5)
        #     cv2.imwrite(img_path, current_frame)
        #     print(f"Second image saved at: {img_path}")
        # else:
        #     print("No hand detected.")

        try:
            response = requests.get('http://localhost:3000/check_undo')
            if response.status_code == 200:
                undo_data = response.json()
                if undo_data.get('undo'):
                    handle_undo_request()
                    # Optionally reset the undo flag on the server
                    requests.post('http://localhost:3000/reset_undo')
            time.sleep(1)  # Check every second or adjust as needed
        except requests.RequestException as e:
            print(f"Error checking undo: {e}")
            time.sleep(3)  # Wait before retrying in case of an error
        except requests.RequestException as e:
            print(f"Error checking undo request: {e}")

        if Player_Color == 0:  #Player As White
            ChessBoard,ChessBoard_Current = fetch_chessboard(img_path)
            current_fen = array_to_fen(ChessBoard)
            Bool_Flag = is_legal_move(previous_fen, current_fen)
            print(Bool_Flag)

            if compare_piece_positions(current_fen, previous_fen) and previous_white_fen != current_fen:
                Piece_Moved = ""
                Piece_Captured = ""
                Castling = ""
                Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                if(no_of_rooks<4):
                    if ChessBoard_Current[0][0]!='r':
                        castling_rights ==castling_rights.replace("q","") 
                    if ChessBoard_Current[0][7]!='r':
                        castling_rights ==castling_rights.replace("k","")  
                    if ChessBoard_Current[7][0]!='R':
                        castling_rights ==castling_rights.replace("Q","") 
                    if ChessBoard_Current[7][7]!='R':
                        castling_rights ==castling_rights.replace("K","")           
                if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                    if move_count%2==0:
                        castling_rights = castling_rights.replace("KQ", "")
                    elif move_count%2!=0:
                        castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'K':
                    castling_rights = castling_rights.replace("KQ", "")
                elif Piece_Moved == 'k':
                    castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("q","")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("k","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("Q","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("K","")

                if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                    Current_Half_Move = 0
                elif(Piece_Captured == "x"):
                    Current_Half_Move = 0
                else:
                    Current_Half_Move += 1

                previous_white_fen = current_fen
                current_fen = add_castling_rights(current_fen, castling_rights)
                current_fen = increment_fen_move_count(current_fen,move_count,Current_Half_Move)
                move_count += 1
                current_fen = update_fen_to_move(current_fen, 'black')
                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #print(f"PGN from previous FEN to new FEN: {pgn}")
                fen_array[move_count-1] = current_fen
                send_fen_to_javascript(current_fen, pgn, move_count)

                ChessBoard_array = ChessBoard_Current
                previous_fen = current_fen
                
                time.sleep(3)
                board = chess.Board(current_fen)
                best_move, updated_board = get_best_move(board)
                current_fen = updated_board.fen()
                previous_black_fen = current_fen
                ChessBoard_Current = fen_to_array(current_fen)

                Piece_Moved = ""
                Piece_Captured = ""
                Castling = ""
                Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                if(no_of_rooks<4):
                    if ChessBoard_Current[0][0]!='r':
                        castling_rights ==castling_rights.replace("q","") 
                    if ChessBoard_Current[0][7]!='r':
                        castling_rights ==castling_rights.replace("k","")  
                    if ChessBoard_Current[7][0]!='R':
                        castling_rights ==castling_rights.replace("Q","") 
                    if ChessBoard_Current[7][7]!='R':
                        castling_rights ==castling_rights.replace("K","")           
                if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                    if move_count%2==0:
                        castling_rights = castling_rights.replace("KQ", "")
                    elif move_count%2!=0:
                        castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'K':
                    castling_rights = castling_rights.replace("KQ", "")
                elif Piece_Moved == 'k':
                    castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("q","")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("k","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("Q","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("K","")

                if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                    Current_Half_Move = 0
                elif(Piece_Captured == "x"):
                    Current_Half_Move = 0
                else:
                    Current_Half_Move += 1
                current_fen = add_castling_rights(current_fen, castling_rights)
                ChessBoard_array = ChessBoard_Current
                Led1 = (Sq[0][0] * 8) + Sq[0][1] + 1
                Led2 = (Sq[1][0] * 8) + Sq[1][1] + 1
                # light_up_leds([Led1, Led2])
                # time.sleep(10)
                # # Turn off all LEDs
                # light_up_leds([])


                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #announce_move(pgn_moves)
                #print(f"PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                fen_array[move_count-1] = current_fen
                send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = current_fen


        elif Player_Color == 1:  #Player as Black
            if move_count == 0:
                board = chess.Board(game_start_fen)
                best_move, updated_board = get_best_move(board)
                current_fen = updated_board.fen()
                ChessBoard_Current = fen_to_array(current_fen)
                previous_white_fen = current_fen
                Piece_Moved = ""
                Piece_Captured = ""
                Castling = ""
                Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                if(no_of_rooks<4):
                    if ChessBoard_Current[0][0]!='r':
                        castling_rights ==castling_rights.replace("q","") 
                    if ChessBoard_Current[0][7]!='r':
                        castling_rights ==castling_rights.replace("k","")  
                    if ChessBoard_Current[7][0]!='R':
                        castling_rights ==castling_rights.replace("Q","") 
                    if ChessBoard_Current[7][7]!='R':
                        castling_rights ==castling_rights.replace("K","")           
                if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                    if move_count%2==0:
                        castling_rights = castling_rights.replace("KQ", "")
                    elif move_count%2!=0:
                        castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'K':
                    castling_rights = castling_rights.replace("KQ", "")
                elif Piece_Moved == 'k':
                    castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("q","")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("k","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("Q","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("K","")

                if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                    Current_Half_Move = 0
                elif(Piece_Captured == "x"):
                    Current_Half_Move = 0
                else:
                    Current_Half_Move += 1

                ChessBoard_array = ChessBoard_Current
                #print(current_fen)
                #print(previous_fen)
                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #announce_move(pgn_moves)
                #print(f"In Player color1 move count 0 PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                fen_array[move_count-1] = current_fen
                send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = update_fen_to_move(previous_fen,'black')
                previous_fen = current_fen
                time.sleep(3)
            else:
                ChessBoard,ChessBoard_Current = fetch_chessboard(img_path)
                current_fen = array_to_fen(ChessBoard)
                Bool_Flag = is_legal_move(previous_fen, current_fen)
                print("Prev Fen = ", previous_fen)
                print("Curr Fen = ", current_fen)
                print(ChessBoard_array)
                print(ChessBoard_Current)
                status, ChessBoard_1 = validate_or_recover(previous_fen, current_fen, ChessBoard_Current, turn="black",mismatch_tolerance=3,require_valid_kings=True, debug=True)
                if(status=="recovered"):
                    print("In loop")
                    ChessBoard_Current=ChessBoard_1
                print(ChessBoard_Current)
                print(ChessBoard)
                ChessBoard = [['' if piece == '*' else piece for piece in row] for row in ChessBoard_Current]
                print(ChessBoard)
                current_fen = array_to_fen(ChessBoard)
                print("Boolean Flag: ", Bool_Flag)

                if current_fen != previous_fen and previous_black_fen != current_fen:
                    Piece_Moved = ""
                    Piece_Captured = ""
                    Castling = ""
                    Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                    if(no_of_rooks<4):
                        if ChessBoard_Current[0][0]!='r':
                            castling_rights ==castling_rights.replace("q","") 
                        if ChessBoard_Current[0][7]!='r':
                            castling_rights ==castling_rights.replace("k","")  
                        if ChessBoard_Current[7][0]!='R':
                            castling_rights ==castling_rights.replace("Q","") 
                        if ChessBoard_Current[7][7]!='R':
                            castling_rights ==castling_rights.replace("K","")           
                    if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                        if move_count%2==0:
                            castling_rights = castling_rights.replace("KQ", "")
                        elif move_count%2!=0:
                            castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'K':
                        castling_rights = castling_rights.replace("KQ", "")
                    elif Piece_Moved == 'k':
                        castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("q","")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("k","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("Q","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("K","")

                    if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                        Current_Half_Move = 0
                    elif(Piece_Captured == "x"):
                        Current_Half_Move = 0
                    else:
                        Current_Half_Move += 1
                    move_count += 1
                    previous_black_fen = current_fen
                    print(previous_fen)
                    current_fen = add_castling_rights(current_fen, castling_rights)
                    current_fen = increment_fen_move_count(current_fen,move_count,Current_Half_Move)
                    print(current_fen)

                    ChessBoard_array = ChessBoard_Current

                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = pgn_moves
                    #print(f" We are here PGN from previous FEN to new FEN: {pgn}")
                    fen_array[move_count-1] = current_fen
                    send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    previous_fen = update_fen_to_move(current_fen, 'white')
                    #print(current_fen)

                    time.sleep(3)
                    board = chess.Board(current_fen)
                    best_move, updated_board = get_best_move(board)
                    current_fen = updated_board.fen()
                    ChessBoard_Current = fen_to_array(current_fen)
                    #print(current_fen)
                    #print(previous_fen)
                    previous_white_fen = current_fen
                    

                    Piece_Moved = ""
                    Piece_Captured = ""
                    Castling = ""
                    Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                    if(no_of_rooks<4):
                        if ChessBoard_Current[0][0]!='r':
                            castling_rights ==castling_rights.replace("q","") 
                        if ChessBoard_Current[0][7]!='r':
                            castling_rights ==castling_rights.replace("k","")  
                        if ChessBoard_Current[7][0]!='R':
                            castling_rights ==castling_rights.replace("Q","") 
                        if ChessBoard_Current[7][7]!='R':
                            castling_rights ==castling_rights.replace("K","")           
                    if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                        if move_count%2==0:
                            castling_rights = castling_rights.replace("KQ", "")
                        elif move_count%2!=0:
                            castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'K':
                        castling_rights = castling_rights.replace("KQ", "")
                    elif Piece_Moved == 'k':
                        castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("q","")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("k","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("Q","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("K","")

                    if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                        Current_Half_Move = 0
                    elif(Piece_Captured == "x"):
                        Current_Half_Move = 0
                    else:
                        Current_Half_Move += 1
                    current_fen = add_castling_rights(current_fen, castling_rights)
                    #current_fen = increment_fen_move_count(current_fen,move_count,Current_Half_Move)
                    Led1 = (Sq[0][0] * 8) + Sq[0][1] + 1
                    Led2 = (Sq[1][0] * 8) + Sq[1][1] + 1
                    # light_up_leds([Led1, Led2])
                    # time.sleep(10)
                    # # Turn off all LEDs
                    # light_up_leds([])
                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = pgn_moves
                    #announce_move(pgn_moves)
                    #print(f" We are here 2 PGN from previous FEN to new FEN: {pgn}")
                    move_count += 1
                    fen_array[move_count-1] = current_fen
                    send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    ChessBoard_array = ChessBoard_Current
                    
        time.sleep(5)

finally:
    engine.quit()
    running = False
    cv2.destroyAllWindows()
    # ser.close()