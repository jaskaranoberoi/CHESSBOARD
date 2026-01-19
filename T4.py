import numpy as np
import cv2
import torch
from pathlib import Path

# Load models
model_ChessCorner = torch.hub.load("yolov5", 'custom', path="Models\\exp4\\weights\\best.pt", source='local')

def order_points(pts, expansion_factor=1.15):
    """Orders the detected corner points into (tl, tr, br, bl) and expands them uniformly."""
    rect = np.zeros((4, 2), dtype="float32")

    # Sort by x-coordinates
    x_sorted = pts[np.argsort(pts[:, 0])]

    left_most = x_sorted[:2]  # Two left-most points
    right_most = x_sorted[2:]  # Two right-most points

    # Sort by y-coordinates to find top-left and bottom-left
    left_most = left_most[np.argsort(left_most[:, 1])]
    (tl, bl) = left_most

    # Sort by y-coordinates to find top-right and bottom-right
    right_most = right_most[np.argsort(right_most[:, 1])]
    (tr, br) = right_most

    rect[0], rect[1], rect[2], rect[3] = tl, tr, br, bl

    # Compute center of detected points
    center_x = np.mean(rect[:, 0])
    center_y = np.mean(rect[:, 1])

    # Expand outward uniformly
    for i in range(4):
        rect[i][0] = center_x + (rect[i][0] - center_x) * expansion_factor
        rect[i][1] = center_y + (rect[i][1] - center_y) * expansion_factor

    return rect

    """Orders the detected corner points into (tl, tr, br, bl) and expands them."""
    rect = np.zeros((4, 2), dtype="float32")

    # Sort by x-coordinates
    x_sorted = pts[np.argsort(pts[:, 0])]

    left_most = x_sorted[:2]  # Two left-most points
    right_most = x_sorted[2:]  # Two right-most points

    # Sort by y-coordinates to find top-left and bottom-left
    left_most = left_most[np.argsort(left_most[:, 1])]
    (tl, bl) = left_most

    # Sort by y-coordinates to find top-right and bottom-right
    right_most = right_most[np.argsort(right_most[:, 1])]
    (tr, br) = right_most

    rect[0], rect[1], rect[2], rect[3] = tl, tr, br, bl

    # Compute center of detected points
    center_x = np.mean(rect[:, 0])
    center_y = np.mean(rect[:, 1])

    # Expand outward
    for i in range(4):
        expansion = top_expansion if i in [0, 1] else expansion_factor
        rect[i][0] = center_x + (rect[i][0] - center_x) * expansion
        rect[i][1] = center_y + (rect[i][1] - center_y) * expansion

    return rect

def GetCroppedImage(PathOfImage):
    model_ChessCorner.conf = 0.05
    image = cv2.imread(PathOfImage)

    result_ChessCorner = model_ChessCorner(PathOfImage)
    result_ChessCorner.print()
    result_ChessCorner.save() 

    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()

    Corner_Coordinates = []
    for detection in detections_ChessCorner:
        xmin, ymin, xmax, ymax, confidence, class_id = detection
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        Corner_Coordinates.append([center_x, center_y])

    Corner_Coordinates_Array = np.array(Corner_Coordinates).astype(int)

    # Remove duplicate close points
    i = 0
    while i < len(Corner_Coordinates_Array) - 1:
        j = i + 1
        while j < len(Corner_Coordinates_Array):
            if abs(Corner_Coordinates_Array[i][0] - Corner_Coordinates_Array[j][0]) < 100 and abs(Corner_Coordinates_Array[i][1] - Corner_Coordinates_Array[j][1]) < 100:
                Corner_Coordinates_Array = np.delete(Corner_Coordinates_Array, j, axis=0)
            else:
                j += 1
        i += 1

    # Order the four detected corners correctly and expand the region
    if len(Corner_Coordinates_Array) != 4:
        print("Error: Could not detect exactly 4 corners!")
        return None

    ordered_corners = order_points(Corner_Coordinates_Array, expansion_factor=1.25)  # Increase factor for more margin

    # Define the destination points (chessboard size)
    board_size = 540  # Slightly increased size
    dst = np.array([
        [0, 0], [board_size - 1, 0], 
        [board_size - 1, board_size - 1], [0, board_size - 1]
    ], dtype="float32")

    # Compute perspective transform and apply it
    M = cv2.getPerspectiveTransform(ordered_corners, dst)
    warped = cv2.warpPerspective(image, M, (board_size, board_size))

    # Save and show the extracted chessboard
    output_path = PathOfImage.replace(".jpg", "_cropped.jpg")
    cv2.imwrite(output_path, warped)
    cv2.imshow("Extracted Chessboard", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(output_path)
    return output_path

# # Example usage
# GetCroppedImage(r"C:\Users\karan\OneDrive\Desktop\C100.jpg")
