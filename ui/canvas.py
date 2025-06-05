from PyQt6.QtWidgets import QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=8, dpi=100, xlabel=None, ylabel=None) -> None:
        super(QWidget, self).__init__(parent)
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvasQTAgg, self).__init__(fig)

    def imshow(self, im):
        self.axes.imshow(im, cmap='gray')
        self.draw_idle()

    def plot(self, x, y):
        self.axes.plot(x, y, color='red', linewidth=2)
        self.draw_idle()