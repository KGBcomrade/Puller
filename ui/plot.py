from PyQt6.QtWidgets import QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class Plot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=8, dpi=100, xlabel=None, ylabel=None) -> None:
        super(QWidget, self).__init__(parent)
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvasQTAgg, self).__init__(fig)
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.line = None
        
        

    def plot(self, x, y):
        if self.line is None:
            [self.line] = self.axes.plot(x, y)
            self.axes.grid()

            if self.xlabel is not None:
                self.axes.set_xlabel(xlabel=self.xlabel)
            if self.ylabel is not None:
                self.axes.set_ylabel(ylabel=self.ylabel)

        else:
            self.line.set_xdata(x)
            self.line.set_ydata(y)

            self.axes.relim()
            self.axes.autoscale_view()

        self.draw_idle()