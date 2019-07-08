# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:30:20 2019

@author: nbenacho
"""
import numpy as np
import math
from laspy import file as File
import os
import matplotlib as style
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#GroundFiltred_Segment_Cloud.las
fileName = "GroundFiltred_Segment_Cloud_filtrePct.las"

inFile = File.File(fileName, mode="r")
point_records = inFile.points

dataset = np.vstack([inFile.x, inFile.y, inFile.z]).transpose()

# Bornes dalle LIDAR
Xmin = inFile.header.min[0]
Xmax = inFile.header.max[0]
Ymin = inFile.header.min[1]
Ymax = inFile.header.max[1]

Zmin = inFile.header.min[2]
Zmax = inFile.header.max[2]

# distance between  max and min
distance_x = Xmax - Xmin
distance_y = Ymax - Ymin

# fixe step
stpx = 0.07
stpy = 0.85

# nbr Cells
nbCellX = int(math.ceil(distance_x / stpx))
nbCellY = int(math.ceil(distance_y / stpy))

print("nbCellX",nbCellX)
print("nbCellY",nbCellY)

s = (nbCellX, nbCellY)
w, h = nbCellX, nbCellY


matrix = [[0 for y in range(h)] for x in range(w)]
i = 0

for p in dataset:
    calcX = p[0]
    valeurXFromRef = calcX - Xmin

    calcY = p[1] 
    valeurYFromRef = calcY - Ymin

    calcZ = p[2]
    
    x = divmod(valeurXFromRef, stpx)
    celluleX = int(x[0])
    y = divmod(valeurYFromRef, stpy)
    celluleY = int(y[0])
    
#    print("celluleX",celluleX)
#    print("celluleY",celluleY)

    
    #print("cellule (X,Y;Z)  (", celluleX ,",", celluleY ,";", calcZ,")\n")
    celluleCourante = matrix[celluleX][celluleY]
 
    if (celluleCourante == 0):
        # if cell is empty
        cellule = [None] * 6
        # liste des points
        
        listePoints = []
        # listePoints.append(p)
        listePoints.append((i, calcX, calcY, calcZ))
        cellule[0] = listePoints
        # Zmin
        cellule[1] = calcZ
        # Zmax
        cellule[2] = calcZ
        # Nb points
        # cellule[3] = len(listePoints)
        cellule[3] = 1
        
        cellule[4] = calcZ
        # Moyenne des Z
        cellule[5] = cellule[4]/cellule[3]
        
        matrix[celluleX][celluleY] = cellule

    else:
        # Sinon on compare le Z courant a celui de la cellule
        # Si le Z courant est superieur au Z de la cellule
        # On met le point courant dans la cellule
        listePoints = celluleCourante[0]
        zMinCellule = celluleCourante[1]
        zMaxCellule = celluleCourante[2]
        # listePoints.append(p)
        listePoints.append((i, calcX, calcY,calcZ))
        celluleCourante[0] = listePoints
        if (calcZ > zMaxCellule):
            celluleCourante[2] = calcZ
        if (calcZ < zMinCellule):
            celluleCourante[1] = calcZ
        # Nb points
        celluleCourante[3] = celluleCourante[3] + 1
        # Somme des Z
        celluleCourante[4] = celluleCourante[4] + calcZ
        
        # Moyenne Z
        celluleCourante[5] = celluleCourante[4]/celluleCourante[3]
        matrix[celluleX][celluleY] = celluleCourante      
        
    i = i + 1
    
    

pointsIndex = []
resIndex = []
#
#
##for indexCelluleX in range(nbCellX - 1):
indexCelluleY = 13
#   
d = np.array([0])
y = np.array([0])
yRes = np.array([0])
#
for indexCelluleX in range(nbCellX-1):
   
    celluleCourante = matrix[indexCelluleX][indexCelluleY]
    celluleSuiv = matrix[indexCelluleX+1][indexCelluleY]
    
    dtype = [('index', int), ('X', float), ('Y', float), ('Z', float)]
    
    
    if celluleSuiv == 0 or celluleCourante == 0:
        diff = 0
        d = np.append(d, diff)
        y = np.append(y, indexCelluleX)

    if celluleSuiv != 0 and celluleCourante != 0:
        
        diff = celluleSuiv[5] - celluleCourante[5]
#        print("Cellule (",indexCelluleX ,";",indexCelluleY,") : ",celluleCourante[5] , " Diff = " , diff,"\n" )
        pts = np.array(celluleCourante[0], dtype=dtype)
 
        d = np.append(d, diff)
        y = np.append(y, indexCelluleX)
#        
        for index in range(pts.size):
            c = pts[index]
            print("Point",c)
            pointsIndex.append(c[0])
#        
#        #print("diff",diff)
#        
#        if(diff >= 0.06 and diff <= 0.1 ):
#            dtype = [('index', int), ('X', float), ('Y', float), ('Z', float)]
#            resPts = np.array(celluleCourante[0], dtype=dtype)
#            resPts = np.array(celluleSuiv[0], dtype=dtype)
#            print("Res",resPts)
##        
#            for idx in range(resPts.size):
#                p = resPts[idx]
#                #print("Point",c)
#                resIndex.append(p[0])
#                
#
_, ext = os.path.splitext(fileName)

new_file = str(_+"_Coupe"+ext)
outFile2 = File.File(new_file, mode = "w", header = inFile.header)
outFile2.points = point_records[pointsIndex]
outFile2.close()


#res_file = str(_+"_Res"+ext)
#outFile3 = File.File(res_file, mode = "w", header = inFile.header)
#outFile3.points = point_records[resIndex]
#outFile3.close()
#
#
#
# Drow graphe
        
app = tk.Tk()
app.wm_title("Graphe Matplotlib")   

fig = Figure(figsize=(8, 6), dpi=100)

ax = fig.add_subplot(111)

ax.plot(y, d);

plt.grid(True)


graph = FigureCanvasTkAgg(fig, master=app)
canvas = graph.get_tk_widget()
canvas.grid(row=1, column=1)

app.mainloop()


#plt.show()   
            
            #print("Cellule (",indexCelluleX ,";",indexCelluleY,") : ",celluleCourante[5] ,"\n" )
#            if (celluleC > 8 and celluleC < 16 ) :
#                
#                dtype = [('index', int), ('X', float), ('Y', float), ('Z', float)]
#                pts = np.array(celluleCourante[0], dtype=dtype)
#                
#                for index in range(pts.size):
#                    c = pts[index]
#                    listeIndexs.append(c[0])
#                
#               

            



