#import chess # type: ignore
import chess.engine #type: ignore
import chess.pgn #type: ignore
import time
import numpy as np
from pathlib import Path
#from chessboard_detector import get_chessboard
import requests
import sys
import json
#from ChessBoard_Creation import ChessBoard_Creation
#from Chess_MoveDetection import Chess_MoveDetection
#from Fen_To_Array import fen_to_array
import cv2
from PIL import Image
import torch
import serial
import time
#from LightLeds import light_up_leds

model_ChessCorner = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5', 'custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp4\weights\best.pt', source='local')
model = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5', 'custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp3\weights\best.pt', source='local')
#model_handdetection = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5','custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp5\weights\best.pt', source='local')

camera_index = 1  # Change if necessary
cap = cv2.VideoCapture(camera_index)

img_saved = False

fen_array = np.full(120, '', dtype=object)



def get_chessboard(PathOFImage):
    # Loading the ChessBoards Corner Model

    # Setting the confidence Level
    model_ChessCorner.conf = 0.05

    # Define the source folder or image path
    image_path = PathOFImage

    result_ChessCorner = model_ChessCorner(image_path)
    result_ChessCorner.print()
    result_ChessCorner.save()

    corner_coordinates = []

    # Extract the x, y coordinates of the chessboard corners
    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()
    for detection in detections_ChessCorner:
        xmin, ymin, xmax, ymax, confidence, class_id = detection
        width = xmax - xmin
        height = ymax - ymin
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        corner_coordinates.append((center_x, center_y))
        #print(f"Chessboard corner detected at (x, y): ({center_x}, {center_y}) with confidence {confidence:.2f}")

    # Convert the list of coordinates to a NumPy array
    corner_coordinates_array = np.array(corner_coordinates)
    corner_coordinates_array[:] = corner_coordinates_array.astype(int)

    # Removing Duplicacy or Corners Which are very near(Sometimes more than 4 corners come)
    i = 0
    while i < len(corner_coordinates_array) - 1:
        j = i + 1
        while j < len(corner_coordinates_array):
            if abs(corner_coordinates_array[i][0] - corner_coordinates_array[j][0]) < 40 and abs(corner_coordinates_array[i][1] - corner_coordinates_array[j][1]) < 40:
                corner_coordinates_array = np.delete(corner_coordinates_array, j, axis=0)
            else:
                j += 1
        i += 1

    # Print the array with all stored coordinates
    #print("All detected corners' coordinates as NumPy array:\n\n", corner_coordinates_array)

    # Finding the minimum value of X
    minx = corner_coordinates_array[0][0]
    for i in range(1, len(corner_coordinates_array)):
        if minx > corner_coordinates_array[i][0]:
            minx = corner_coordinates_array[i][0]

    # Finding the second minimum value of X
    minx2 = float('inf')
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][0] != minx and corner_coordinates_array[i][0] < minx2:
            minx2 = corner_coordinates_array[i][0]

    # Handle case where there is no valid second minimum
    if minx2 == float('inf'):
        minx2 = None

    # Finding the maximum value of X
    maxx = corner_coordinates_array[0][0]
    for i in range(1, len(corner_coordinates_array)):
        if maxx < corner_coordinates_array[i][0]:
            maxx = corner_coordinates_array[i][0]

    # Finding the second maximum value of X
    maxx2 = float('-inf')  # Initialize with negative infinity
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][0] != maxx and corner_coordinates_array[i][0] > maxx2:
            maxx2 = corner_coordinates_array[i][0]

    # Handle case where there is no valid second maximum
    if maxx2 == float('-inf'):
        maxx2 = None


    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][0] == minx):
            y1 = corner_coordinates_array[i][1]

    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][0] == minx2):
            y2 = corner_coordinates_array[i][1]

    # Finding the minimum value of Y
    miny = corner_coordinates_array[0][1]
    for i in range(1, len(corner_coordinates_array)):
        if miny > corner_coordinates_array[i][1]:
            miny = corner_coordinates_array[i][1]

    # Finding the second minimum value of Y
    miny2 = float('inf')
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][1] != miny and corner_coordinates_array[i][1] < miny2:
            miny2 = corner_coordinates_array[i][1]

    #print("Minimum X value:", minx)
    #print("Second minimum X value:", minx2)

    # Finding the maximum value of Y
    maxy = corner_coordinates_array[0][1]
    for i in range(1, len(corner_coordinates_array)):
        if maxy < corner_coordinates_array[i][1]:  # Change > to <
            maxy = corner_coordinates_array[i][1]

    # Finding the second maximum value of Y
    maxy2 = float('-inf')  # Initialize with negative infinity for second max
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][1] != maxy and corner_coordinates_array[i][1] > maxy2:  # Change < to >
            maxy2 = corner_coordinates_array[i][1]

    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][1] == maxy):
            x1 = corner_coordinates_array[i][0]

    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][1] == maxy2):
            x2 = corner_coordinates_array[i][0]

    #print("Minimum Y value:", maxy)
    #print("Second minimum Y value:", maxy2)

    #Finding the Value of X and Y
    Y = abs(y2-y1)
    X = abs(x2-x1)
    x = X/8
    y = Y/8

    #print("\nValue of Y:",Y,"\nValue of X:",X, "\nValue of x:",x,"\nValue of y:",y,)

    ChessBoard = np.full((8, 8), '*', dtype=str)
    #print(ChessBoard)


    # Load the trained model (replace 'best.pt' with the path to your model if needed)
    # Set the confidence threshold (e.g., 0.5)
    model.conf = 0.65   # You can change this to adjust the confidence level

    # Inference on the image or a folder of images
    print(f"Using image path: {image_path}")

    # Uncomment below to use for chess piece detection
    results = model(image_path)

    results.print()
    results.save()

    # Optionally, you can access the results and bounding boxes
    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()

    # Extract chess piece details: (x, y), width, height, and piece name
    df = results.pandas().xyxy[0]

    bounding_boxes_with_names = []

    # Loop through each detected object
    for index, row in df.iterrows():
        xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        width = xmax - xmin
        height = ymax - ymin
        confidence = row['confidence']
        piece_name = row['name']  # Assuming the model's labels are chess piece names
        
        # Append the (xmin, ymin, width, height, piece_name) to the list
        bounding_boxes_with_names.append([xmin, ymin, width, height, piece_name])
        
        # Optional: print details for each detected piece
        #print(f"Detected {piece_name}: (x, y) = ({xmin}, {ymin}), width = {width}, height = {height}, confidence = {confidence:.2f}")

    # Convert the list to a NumPy array (without piece names since it's a string)
    bounding_boxes_array = np.array([item[:4] for item in bounding_boxes_with_names])

    # Print the NumPy array for bounding boxes
    #print(bounding_boxes_array)
    #print("Bounding Boxes (xmin, ymin, width, height):\n", bounding_boxes_array)

    # Print the piece names separately
    piece_names = [item[4] for item in bounding_boxes_with_names]
    #("Piece Names:\n", piece_names)

    for i in range(0,len(bounding_boxes_array)):
        #Finding Out the Column
        temph = bounding_boxes_array[i][1] + (bounding_boxes_array[i][3]/0.95)
        if temph<Y/2:
          if piece_names[i]=='black-rook':
              temph = temph - miny -20
        #   elif piece_names[i]=='white-bishop':
        #       temph = temph - miny - 25
          else:
              temph = temph - miny -5 #For right Half
        elif temph>Y/2:
            if piece_names[i]=='black-rook':
              temph = temph - miny -20
            elif piece_names[i]=='white-rook':
              temph = temph - miny -15
            # elif piece_names[i]=='white-bishop':
            #   temph = temph - miny + 10
            else:
              temph = temph - miny 
        print(temph)
        columno = int(temph/y)
        print(columno)
        columno = 7 - columno
        if columno<0:
            columno = abs(columno + 2 -1)
    
        #First Find out the row
        temp = bounding_boxes_array[i][0] + (bounding_boxes_array[i][2]/2)
        print("\n\n",temp)
        if (temp - minx) < X/4 and temph < Y/2: #First two right Quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='white-bishop':
              temph = temph - miny + 10
            else:
                temp = temp - minx - 19 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1
        if (temp - minx) < X/4 and temph > Y/2: #First two left Quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx - 19 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1

        elif(temp - minx) < X/2 and (temp - minx) > x/4 and temph <Y/2: #Third,Fourth row right quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx + 10 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1

        elif(temp - minx) < X/2 and (temp - minx) > x/4 and temph > Y/2: #Third,Fourth row left quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx + 10 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1

        elif(temp - minx) > X/2 and (temp - minx) < 3*X/2 and temph < Y/2: #5,6 row right quarter
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            if piece_names[i]=='white-bishop':
              temp = maxx - temp - ((abs(maxx-maxx2)/8)*(columno))/1.8
            elif piece_names[i]=='white-rook':
              temp = maxx - temp - 15 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            elif piece_names[i]=='white-knight':
              temp = maxx - temp - 5 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            else:
                temp = maxx - temp + 2 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1

        elif(temp - minx) > X/2 and (temp - minx) < 3*X/2 and temph > Y/2: #5,6 row left quarter
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            temp = maxx - temp -1 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1

        elif(temp - minx) > 3*X/2 and temph < Y/2: #7,8 ROW RIGHT QUARTER
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            temp = maxx - temp -7 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1

        elif(temp - minx) > 3*X/2 and temph < Y/2: #7,8 ROW LEFT QUARTER
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            temp = maxx - temp -13 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1  
            # else:
            #     ChessBoard[7-rowno][columno+1] = temp1

    #print(ChessBoard)
    return ChessBoard


ret, current_frame = cap.read()

if not ret:
    print("Failed to grab frame")

# Check if the image is in portrait mode (height > width)
# height, width, _ = current_frame.shape
# # if height > width:
#     # Rotate the image by 90 degrees to make it horizontal
# current_frame = cv2.rotate(current_frame, cv2.ROTATE_90_CLOCKWISE)

# Display the current frame
#cv2.imshow("Camera", current_frame)

# Save the image only once
img_path = r'C:\Users\anmol\OneDrive\Desktop\HardWar\captured_image.png'

# Capture the current frame
cv2.imwrite(img_path, current_frame)
print(f"Image saved at: {img_path}")
img_saved = True

# Load the YOLOv5 model for hand detection

# Set the confidence threshold
model_handdetection.conf = 0.45

# Perform inference on the image
results = model_handdetection(img_path)

# Print the results
results.print()

# Save the results
results.save()

# Check if a hand is detected
detected_objects = results.pandas().xyxy[0]  # Get the detection results as a DataFrame

if len(detected_objects) > 0:
    print("Hand detected! Capturing another image...")
    # Capture another image if hand is detected
    time.sleep(5)
    cv2.imwrite(img_path, current_frame)
    print(f"Second image saved at: {img_path}")
else:
    print("No hand detected.")

ChessBoard = get_chessboard(img_path)
print(ChessBoard) 