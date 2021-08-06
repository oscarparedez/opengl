#Lab1
#Oscar Paredez 19109

import struct
from obj import Obj

def glInit(width, height):
    return Renderer(width, height)

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # short 
    return struct.pack('=h', w)

def dword(w):
    # long
    return struct.pack('=l', w)

def color(r, g, b):
    if r >=0 and r <=1 and g >=0 and g <=1 and b >=0 and b <=1:
        return bytes([round(b*255), round(g*255), round(r*255)])

BLACK = color(0, 0, 0)

class Renderer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def glCreateWindow(self, width, height):
        self.framebuffer = [[BLACK for x in range(self.width)] for y in range(self.height)]

    def glViewPort(self, x, y, width, height):
        self.initialViewPortX = x
        self.initialViewPortY = y
        self.viewPortX = width
        self.viewPortY = height
        self.polygonV = []

    def glClearColor(self, r, g, b):
        self.current_color = color(r, g, b)

    def glClear(self):
        self.framebuffer = [[self.current_color for x in range(self.width)] for y in range(self.height)]

    def glColor(self, r, g, b):
        self.vertex_color = color(r, g, b)

    def glVertex(self, x, y):
        posX = int((x+1)*(self.viewPortX/2)+self.initialViewPortX)
        posY = int((y+1)*(self.viewPortY/2)+self.initialViewPortY)
        self.framebuffer[posY][posX] = self.vertex_color
    
    def line(self, x0, y0, x1, y1):
        # y = mx + b
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

            dy = abs(y1 - y0)
            dx = abs(x1 - x0)
        
        if x1 < x0:
            t1, t2 = x0, y0
            x0, y0 = x1, y1
            x1, y1 = t1, t2           

        offset = 0 * 2 * dx
        threshold = 0.5 * 2 * dx

        y = y0
        x = x0

        points = []
        while x <= x1:
            if steep:
                points.append((y, x))
            else:
                points.append((x, y))
                
            offset += (dy) * 2
            if offset >= threshold:
                y += 0.001 if y0 < y1 else -0.001
                threshold += 1 * 2 * dx
            x += 0.001    
        for point in points:
            # if point[0] <= 1 and point[0] >= -1 and point[1] <= 1 and point[1] >= -1:
                # self.glVertex(*point)
            # print(int((point[0]+1)*(self.viewPortX/2)+self.initialViewPortX), int((point[1]+1)*(self.viewPortY/2)+self.initialViewPortY))
            # self.glVertex(int((point[0]+1)*(self.viewPortX/2)+self.initialViewPortX), int((point[1]+1)*(self.viewPortY/2)+self.initialViewPortY))
            self.glVertex(((point[0]-self.initialViewPortX)*(2/self.viewPortX)-1), ((point[1]-self.initialViewPortY)*(2/self.viewPortY)-1))

    def load(self, filename, translate, scale):
        model = Obj(filename)
    
        for face in model.faces:
            vcount = len(face)
            for j in range(vcount):
                f1 = face[j][0]
                f2 = face[(j + 1) % vcount][0]

                v1 = model.vertices[f1 - 1]
                v2 = model.vertices[f2 - 1]

                x1 = ((v1[0] + translate[0])* scale[0])
                y1 = ((v1[1] + translate[1])* scale[1])
                x2 = ((v2[0] + translate[0])* scale[0])
                y2 = ((v2[1] + translate[1])* scale[1])

                self.line(x1, y1, x2, y2)

    def draw_polygon(self, filename, scale):
        with open(filename) as f:
            lines = f.read().splitlines()
            for i in range(len(lines)):
                x0, y0 = lines[i % len(lines)].split(', ')
                x1, y1 = lines[(i + 1) % len(lines)].split(', ')
                self.line(int(x0)*scale[0], int(y0)*scale[1], int(x1)*scale[0], int(y1)*scale[1])

    def fill_polygon(self, filename):
        
        #Algoritmo que traza lineas verticales de izquierda a derecha para rellenar una figura
        verticesX = []
        verticesY = []
        insideX = []
        with open(filename) as f:
            lines = f.read().splitlines()
            for i in range(len(lines)):
                x, y = lines[i % len(lines)].split(', ')
                verticesX.append(int(x))
                verticesY.append(int(y))

            xmin, xmax, ymin, ymax = min(verticesX), max(verticesX), min(verticesY), max(verticesY)   
            for y in range(ymin, ymax):
                for x in range(xmin, xmax):
                    if self.framebuffer[y][x] == self.vertex_color:
                        # print(y)
                        insideX.append(x)
                for num in range(insideX[0], insideX[-1]):
                    self.framebuffer[y][num] = self.vertex_color
                insideX = []
            insideX = []


    def write(self, filename):
        f = open(filename, 'bw')
        # file header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14+40+3*(self.width*self.height)))
        f.write(dword(0))
        f.write(dword(14+40))
        # info header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(3*(self.width*self.height)))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        # bitmap
        for y in range(self.height):
            for x in range(self.width):
                f.write(self.framebuffer[y][x])
        f.close()

    def glFinish(self):
        self.write('a.bmp')

r = glInit(2000, 2000)
r.glCreateWindow(2000, 2000)
r.glViewPort(100, 100, 1800, 1800)
r.glClearColor(0, 0, 0)
r.glClear()
r.glColor(1, 1, 1)
# r.load('./models/ferrari.obj', [0, 0], [0.5, 0.5])

r.draw_polygon('./polygons/polygon1.txt', [1, 1])
r.fill_polygon('./polygons/polygon1.txt')
r.glColor(0.2, 0.2, 1)
r.draw_polygon('./polygons/polygon2.txt', [1, 1])
r.fill_polygon('./polygons/polygon2.txt')
r.glColor(0, 1, 1)
r.draw_polygon('./polygons/polygon3.txt', [1, 1])
r.fill_polygon('./polygons/polygon3.txt')
r.glColor(0.8, 0.2, 1)
r.draw_polygon('./polygons/polygon4.txt', [1, 1])
r.fill_polygon('./polygons/polygon4.txt')
r.glColor(0, 0, 0)
r.draw_polygon('./polygons/polygon5.txt', [1, 1])
r.fill_polygon('./polygons/polygon5.txt')

r.glFinish()
