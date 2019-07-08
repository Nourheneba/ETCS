# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 16:43:20 2019

@author: nbenacho
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:30:20 2019

@author: nbenacho
"""

import math
import os
import time
import sys
import datetime
from laspy import file as File
import numpy as np
import matplotlib as style
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#GroundFiltred_Segment_Cloud.las
fileName = "GroundFiltred_Segment_Cloud.las"

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
stpy = 0.55

# nbr Cells
nbCellX = int(math.ceil(distance_x / stpx))
nbCellY = int(math.ceil(distance_y / stpy))

#print("nbCellX",nbCellX)
#print("nbCellY",nbCellY)

s = (nbCellX, nbCellY)
w, h = nbCellX, nbCellY

def find_nearest_index(array,value):
    array = np.asarray(array)
    idx = (np.abs(array-value)).argmin()
    return idx

def getIndexes(listePoint, Zmin, Zmax):
    retour = []
    retour.append(find_nearest_index(listePoint, Zmin))
    retour.append(find_nearest_index(listePoint, Zmax))
    return retour


ti = datetime.datetime.now()

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
    
    
    #********************* percentiles ***************************************
    
listeIndexs = []

for indexCelluleX in range(nbCellX):
    for indexCelluleY in range(nbCellY):
        celluleCourante = matrix[indexCelluleX][indexCelluleY]
        if celluleCourante != 0 :
            #print("cellule (X,Y;Z)  (", celluleX ,",", celluleY ,";", calcZ,")\n")
    
            dtype = [('index', int),  ('X', float), ('Y', float), ('Z', float)]
            a = np.array(celluleCourante[0], dtype=dtype)
            a = np.sort(a, order='Z')

            indexTrie = [x[0] for x in a]
                
            zTrie = [x[3] for x in a]
#    
            percentile1 = np.percentile(zTrie, 1)
            percentile10 = np.percentile(zTrie, 10)
            percentile20 = np.percentile(zTrie, 20)
            percentile30 = np.percentile(zTrie, 30)
            percentile40 = np.percentile(zTrie, 40)
            percentile50 = np.percentile(zTrie, 50)
            percentile70 = np.percentile(zTrie, 70)
            percentile80 = np.percentile(zTrie, 80)
            percentile90 = np.percentile(zTrie, 90)
            percentile98 = np.percentile(zTrie, 98)
            percentile99 = np.percentile(zTrie, 99)
               
#            diffPercentile = percentile90 - percentile10
            diffPercentile = percentile99 - percentile1
#    
            if (diffPercentile > 0.12 and diffPercentile < 0.28):
    
                #indexPercentile = getIndexes(zTrie, percentile10, percentile90)
                indexPercentile = getIndexes(zTrie, percentile99 - 0.05, percentile99)
                indexMinRail = indexPercentile[0]
                indexMaxRail = indexPercentile[1]
    
                percentileIndexTrie = indexTrie[indexMinRail:indexMaxRail]
                listeIndexs = listeIndexs + percentileIndexTrie
                
_, ext = os.path.splitext(fileName)
flt_file = str(_+"_filtrePct"+ext)
outFile2 = File.File(flt_file, mode = "w", header = inFile.header)
outFile2.points = point_records[listeIndexs]
outFile2.close()  
                
tf= datetime.datetime.now()
print("---------------------------------------------------------")
print("Nombre de points traités        :",point_records.size)
print("Temps de traitement             :",tf - ti)
print("Nombre de points apres filtrage :",len(listeIndexs))
print("---------------------------------------------------------")
 
