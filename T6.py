from T4 import GetCroppedImage
from T3  import get_chessboard

def Algo2(PathofImage):
    Image_Path = GetCroppedImage(PathofImage)
    ChessBoard = get_chessboard(Image_Path)
    return ChessBoard
