import numpy as np

def Validity_Of_Move(Arr1,Arr2):
    result = np.array_equal(Arr1, Arr2)
    print(result)  # True
    if(result):
        return 0
    
    #Find Differences:
    count = 0
    for i in range(0,8):
        for j in range(0,8):
            if(Arr1[i][j]==Arr2[i][j]):
                count=count+1
    if(count!=2):
        return -1
    
    #Find_Which_Piece_Moved




Arr1 = np.full((8, 8), '*', dtype=str)
print(Arr1)

Arr2 = np.full((8,8), '*', dtype=str)
print(Arr2)

print(Validity_Of_Move(Arr1,Arr2))