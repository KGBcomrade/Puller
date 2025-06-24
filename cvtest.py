import numpy as np
import cv2
from matplotlib import pyplot as plt
from misc import Cam, getFiberInterp, getFiberEdges

camTop = Cam('t_top')
camSide = Cam('t_side')
photoTop = camTop.getPhoto()
photoSide = camSide.getPhoto()

topX, topY = getFiberInterp(photoTop, 135, -20)
board1X, board1Y, board2X, board2Y = getFiberEdges(photoTop, 135, -20)
sideX, sideY = getFiberInterp(photoSide, 20, 160)
board1XS, board1YS, board2XS, board2YS = getFiberEdges(photoSide, 20, 160)

plt.imshow(photoTop)
plt.plot(topX, topY)
plt.plot(board1X, board1Y, color='red')
plt.plot(board2X, board2Y, color='red')
plt.show()
plt.imshow(photoSide)
plt.plot(sideX, sideY)
plt.plot(board1XS, board1YS, color='red')
plt.plot(board2XS, board2YS, color='red')
plt.show()