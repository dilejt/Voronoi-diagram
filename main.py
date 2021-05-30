import sys
from PyQt5.QtWidgets import QMainWindow,QLabel,QApplication,QPushButton,QLineEdit,QGridLayout,QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from scipy.spatial import Voronoi,voronoi_plot_2d
class MainWindow(QMainWindow):

    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('Diagram Voronoi by Damian Jancewicz')    

        self.label=QLabel('Ile komorek Voronoi chcesz wygenerowac?')
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.inputLine=QLineEdit()
        self.inputLine.setValidator(QIntValidator(1,9999))
        self.inputLine.setMaxLength(4)
        self.inputLine.setPlaceholderText('Podaj liczbe')

        self.button=QPushButton('Generuj')
        self.button.clicked.connect(self.buttonClicked)

        self.figure=plt.figure()
        self.figure.set_facecolor('#f0f0f0')
        self.canvas=FigureCanvas(self.figure)
        self.toolbar=NavigationToolbar(self.canvas,self)

        layout=QGridLayout()
        layout.addWidget(self.toolbar,0,0)
        layout.addWidget(self.canvas,1,0)
        layout.addWidget(self.label,2,0)
        layout.addWidget(self.inputLine,3,0)
        layout.addWidget(self.button,4,0)

        widget=QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        cid = self.figure.canvas.mpl_connect('pick_event', self.on_pick)

    def on_pick(self,event):
        if (isinstance(event.artist,Polygon) and len(self.points)>5):
            poly = event.artist
            arr=[]
            handle=0
            for x in poly.get_xy():
                arr.append(x)
            arr=tuple(map(tuple,arr))
            for p in self.points:
                if(self.point_inside_polygon(x=p[0],y=p[1],poly=arr)):
                    p=np.asarray(p)
                    handle=p
            self.points=[x for x in self.points if not (handle==x).all()]
            if(event.mouseevent.button==3):
                plt.cla()
                self.Voronoi_refresh()
            elif(event.mouseevent.button==1):
                poly.remove()
            self.canvas.draw()

    def point_inside_polygon(self,x,y,poly):
        n=len(poly)
        inside=False
        p1x,p1y=poly[0]
        for i in range(n+1):
            p2x,p2y=poly[i % n]
            if y>min(p1y,p2y):
                if y<=max(p1y,p2y):
                    if x<=max(p1x,p2x):
                        if p1y!=p2y:
                            xinters=(y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x==p2x or x<=xinters:
                            inside=not inside
            p1x,p1y=p2x,p2y
        return inside

    def buttonClicked(self):
        if self.inputLine.text()!="":
            self.plot(int(self.inputLine.text()))

    def plot(self,liczba=5):
        self.points=np.random.rand(liczba,2)
        self.points=np.append(self.points, [[0,-999], [999,0], [0,999], [-999,0]], axis = 0)   
        self.figure.clear()
        self.ax=self.figure.add_subplot(111)
        self.Voronoi_refresh()
        self.canvas.draw()

    def Voronoi_refresh(self):
        vor=Voronoi(self.points)
        voronoi_plot_2d(vor,ax=self.ax,line_colors='#f0f0f0',line_width=5,show_points=False,show_vertices=False)
        for region in vor.regions:
            if not -1 in region:
                polygon=[vor.vertices[i] for i in region]
                self.ax.fill(*zip(*polygon),joinstyle='round',capstyle='round',picker=True)
        self.ax.axis('off')
        self.ax.axis('equal')
        self.ax.set_xlim([0,1])
        self.ax.set_ylim([0,1])
        #self.ax.plot(np.array(vor.vertices)[:,0],np.array(vor.vertices)[:,1],'ko')  
        #self.ax.plot(np.array(self.points)[:,0],np.array(self.points)[:,1],'kx')

if __name__ == '__main__':    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  
    app.exec_()