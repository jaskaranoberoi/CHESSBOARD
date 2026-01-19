import numpy as np
from pathlib import Path
import torch

model_ChessCorner = torch.hub.load("yolov5", 'custom', path="Models\\exp4\\weights\\best.pt", source='local')
model = torch.hub.load("yolov5", 'custom', path="Models\\BestModel\\best.pt", source='local')

fen_array = np.full(120, '', dtype=object)

def get_chessboard(PathOfImage):
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
    print(ChessBoard)
    #Rotated_ChessBoard = np.rot90(ChessBoard, k=1)
    #print(Rotated_ChessBoard)
    return 0

# img_path = r"C:\Users\karan\OneDrive\Desktop\IMG20250322061140.jpg"

# ChessBoard = get_chessboard(img_path)
# print("Final Chessboard Coordinates:\n", ChessBoard)