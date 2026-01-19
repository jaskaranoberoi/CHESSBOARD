import numpy as np

def ChessBoard_Creation():
   
    ChessBoard_Array = np.empty((8, 8), dtype=str)

    ChessBoard_Array[0, 0] = 'r' 
    ChessBoard_Array[0, 1] = 'n'  
    ChessBoard_Array[0, 2] = 'b'  
    ChessBoard_Array[0, 3] = 'q' 
    ChessBoard_Array[0, 4] = 'k'  
    ChessBoard_Array[0, 5] = 'b' 
    ChessBoard_Array[0, 6] = 'n'  
    ChessBoard_Array[0, 7] = 'r'  

    ChessBoard_Array[1, :] = 'p'

    ChessBoard_Array[7, 0] = 'R'  
    ChessBoard_Array[7, 1] = 'N'  
    ChessBoard_Array[7, 2] = 'B' 
    ChessBoard_Array[7, 3] = 'Q'  
    ChessBoard_Array[7, 4] = 'K'  
    ChessBoard_Array[7, 5] = 'B' 
    ChessBoard_Array[7, 6] = 'N'  
    ChessBoard_Array[7, 7] = 'R'  

    ChessBoard_Array[6, :] = 'P'

    ChessBoard_Array[2:6, :] = '*'  
    
    return ChessBoard_Array

chessboard = ChessBoard_Creation()
print(chessboard)
