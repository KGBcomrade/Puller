import numpy as np
import cv2
import math
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
from sklearn.linear_model import (RANSACRegressor)

def find_fiber(edges, **args):
    y, x = edges.shape
    num = np.tile(np.linspace(0, 1, y), (x, 1)).T
    edges = edges > 0
    s = np.sum(edges, axis=0)
    m = np.sum(edges * num, axis=0) / s
    st = np.sqrt(np.sum(edges * (num - m)**2, axis=0) / s)
    std = np.nanmedian(st)
    X = np.linspace(0, 1, x)
    bad = np.argwhere(np.isnan(m))
    X = np.delete(X, bad)
    m = np.delete(m, bad)
    ransac = RANSACRegressor(random_state=42).fit(X.reshape([-1, 1]), m)
    return float(ransac.estimator_.coef_), float(ransac.predict([[0]])), std


def turn_crop(im, alf, b, std, **args):
    w = args.get('width', 4)
    up = max(b, b + alf)
    down = min(b, b + alf)
    y, x = im.shape
    up = int(np.clip(up + w * std, 0, 1) * y)
    down = int(np.clip(down - w * std, 0, 1) * y)
    cr_im = im[down:up, :]
    y_new = cr_im.shape[0]
    M = cv2.getRotationMatrix2D([x / 2, y_new / 2],
                                np.arctan(alf * y / x) * 180 / np.pi, 1)
    rotated = cv2.warpAffine(cr_im,
                             M, [cr_im.shape[1], cr_im.shape[0]],
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated, (M, up, down)


def cuts(m, n):
    y, x = m.shape
    step = x / n
    b = np.ceil(np.arange(step, x, step)).astype(int)
    lis = np.split(m, b, axis=1)
    means = []
    for l in lis:
        means.append(l.mean(axis=1))
    return np.stack(means)

def ed(m):
    return 2 * m[1:-1] - m[:-2] - m[2:]


def fit(m, x, show=False):
    return np.sqrt(np.mean(ed(m) ** 2))


class window_fit():
    def __init__(self, arr, w):
        self.arr = arr
        self.w = w
        self.x, self.y = arr.shape
        self.v = np.ones_like(arr) * float('-inf')
        self.Y = np.arange(self.y)
        self.boards = np.zeros([self.x, 2])

    def get(self, x, y):
        x0 = math.floor(x)
        x1 = math.ceil(x)
        y0 = math.floor(y)
        y1 = math.ceil(y)
        s0 = self.calc(x0, y0)
        s1 = self.calc(x1, y1)
        s = s1 * (y - y0) + s0 * (1 - (y - y0))
        return s

    def calc(self, x, y):
        if self.v[x, y] == float('-inf'):
            s = fit(self.arr[x, y:y + self.w], self.Y[y:y + self.w])
            self.v[x, y] = np.log(s)
            print('a')
            return np.log(s)
        else:
            return self.v[x, y]

    def get_between(self, y0, y1):
        y0, y1 = min(y0, y1), max(y0, y1)
        y0 = max(0, math.ceil(y0))
        y1 = min(self.y - 1, math.floor(y1))
        return np.arange(y0, y1 + 1)

    def get_arr(self, x):
        X = np.argwhere(self.v[x] != float('-inf'))
        Y = self.v[x, X]
        return X.flatten(), Y.flatten()

    def calc_grad(self, n):
        self.v = np.abs(np.gradient(self.arr, axis=1))

    def find_edge(self, coef, coef2, w):
        for x in range(self.x):
            p, val = self.get_arr(x)
            peaks, props = find_peaks(val, height=val.max() * coef, prominence=val.max() * coef2, width=1)

            ind = 0
            ind2 = -1
            self.boards[x, 0] = w * props['left_ips'][ind] + (1 - w) * peaks[ind]
            self.boards[x, 1] = w * props['right_ips'][ind2] + (1 - w) * peaks[ind2]


def getFiberEdges(im, lbound=None, ubound=None, leftbound=None, rbound=None):
    y, x = im.shape
    coef = 1
    thr = 200
    im4 = cv2.resize(im, dsize=(x // coef, y // coef))
    edges = cv2.Canny(im4, thr, thr * 2, L2gradient=True)
    if lbound is not None:
        edges[:lbound, :] = 0
    if ubound is not None:
        edges[ubound:, :] = 0
    if leftbound is not None:
        edges[:, :leftbound] = 0
    if rbound is not None:
        edges[:, rbound:] = 0
    alf, b, std = find_fiber(edges, plot=True)
    rotated, [M, up, down] = turn_crop(im, alf, b, std, width=4, plot=True)
    mas = cuts(rotated, 30)
    wf = window_fit(mas, 0)
    wf.calc_grad(150)
    wf.find_edge(0.3, 0.1, .6)

    X = np.linspace(0, 1, wf.boards.shape[0])

    Rev = np.linalg.inv(M[:, :-1])
    d = M[:, -1].T
    board1X = np.zeros_like(wf.boards[:, 0])
    board1Y = np.zeros_like(wf.boards[:, 0])
    board2X = np.zeros_like(wf.boards[:, 1])
    board2Y = np.zeros_like(wf.boards[:, 1])
    y, x = im.shape
    X = np.linspace(0, x, wf.boards.shape[0])
    for i, b in enumerate(wf.boards[:, 0]):
        xy = Rev @ (np.array([X[i], b]) - d)
        board1X[i] = xy[0]
        board1Y[i] = xy[1] + down
    for i, b in enumerate(wf.boards[:, 1]):
        xy = Rev @ (np.array([X[i], b]) - d)
        board2X[i] = xy[0]
        board2Y[i] = xy[1] + down

    return board1X, board1Y, board2X, board2Y

def getFiberEdgesLinear(im):
    board1X, board1Y, board2X, board2Y = getFiberEdges(im)

    [a1, b1] = np.polyfit(board1X, board1Y, 1)
    [a2, b2] = np.polyfit(board2X, board2Y, 1)

    return a1, b1, a2, b2
    
def getFiberInterp(im, lbound=None, ubound=None, leftbound=None, rbound=None, scale=1):
    board1X, board1Y, board2X, board2Y = getFiberEdges(im, lbound, ubound, leftbound, rbound)
    xmin = np.max((board1X.min(), board2X.min()))
    xmax = np.min((board1X.max(), board2X.max()))
    lineX = np.linspace(xmin, xmax, 100)
    upper = interp1d(board1X, board1Y)
    lower = interp1d(board2X, board2Y)
    mid = (upper(lineX) + lower(lineX)) / 2

    return lineX * scale, mid * scale