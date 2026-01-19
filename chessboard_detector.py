import torch
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def get_chessboard(PathOFImage):
    # Loading the ChessBoards Corner Model
    model_ChessCorner = torch.hub.load("yolov5", 'custom', path="Models\exp4\weights\\best.pt", source='local')

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
    model = torch.hub.load("yolov5", 'custom', path="Models\exp3\weights\best.pt", source='local')

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
        temp = bounding_boxes_array[i][1] + (bounding_boxes_array[i][3]/0.95)
        if piece_names[i]=='black-rook':
            temp = temp - miny + 10 - 26
        else:
            temp = temp - miny + 12
        print(temp)
        columno = int(temp/y)
        print(columno)
        columno = 7 - columno
        if columno<0:
            columno = abs(columno + 2 -1)
    
        #First Find out the row
        temp = bounding_boxes_array[i][0] + (bounding_boxes_array[i][2]/2)
        print("\n\n",temp)
        if (temp - minx) < X/2:
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
        elif(temp - minx) > X/2:
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