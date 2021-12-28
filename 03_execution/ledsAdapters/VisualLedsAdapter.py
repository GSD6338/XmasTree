import threading
import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from ledsMapReaders.LedsMapReader import LedsMapReader
from ledsAdapters.LedsAdapter import LedsAdapter

import math


class VisualLedsAdapter(LedsAdapter):
    def __init__(self, ledsCount, ledsMapReader, w, h):
        LedsAdapter.__init__(self, ledsCount)
        self._leds = [(0, 0, 0) for i in range(ledsCount)]
        self._ledsMapReader = ledsMapReader
        self._thread = threading.Thread(target=self.startOpenGlThread, args=())
        self._thread.start()
        self._cameraRotation = 0
        self._cameraRotationX = 0
        self._cameraZoom = 1
        self._bounds = (w, h)

    def startOpenGlThread(self):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)
        glutInitWindowSize(self._bounds[0], self._bounds[1])
        glutInitWindowPosition(0, 0)
        wind = glutCreateWindow("OpenGL tree visualization")
        glutDisplayFunc(self.paint)
        glutIdleFunc(self.paint)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); 

        glutMotionFunc(self.rotateTree)
        glutMainLoop()  # Keeps the window created above displaying/running in a loop

    def rotateTree(self, x, y):
        self._cameraRotation = 360*(x - self._bounds[0]/2)/self._bounds[0]
        self._cameraRotationX = -360*(y - self._bounds[1]/2)/self._bounds[1]

    def paint(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Remove everything from screen (i.e. displays all white)
        
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity() # Reset all graphic/shape's position
        glFrustum(-2.0, 2.0, -0.5, 3.5, 6.0, 10.0)
        glTranslate(0.0, 1.0, -8.0)
        glRotate(-self._cameraRotationX, 1.0, 0.0, 0.0)
        glRotate(-self._cameraRotation, 0.0, 1.0, 0.0)
        glTranslate(0.0, -1.0, 0.0)
        self.drawTree()
        self.drawLights()
        glTranslate(0.0, 1.0, 0.0)
        glRotate(self._cameraRotation, 0.0, 1.0, 0.0)
        glRotate(self._cameraRotationX, 1.0, 0.0, 0.0)
        glTranslate(0.0, -1.0, 8.0)
        glMatrixMode(GL_MODELVIEW)
        glutSwapBuffers()
        
    def drawTree(self):
        topLedCoords = [0.0, 0.0, 0.0]
        for ledIndex in range(0, self._ledsCount):
            led = self._ledsMapReader.getLed(ledIndex)
            if led[1] >= topLedCoords[1]:
                topLedCoords = led
    
        glTranslate(topLedCoords[0], 0, topLedCoords[2])
    
        glColor4f(0.3, 0.2, 0.0, 1.0)
        glRotate(-90, 1.0, 0.0, 0.0)
        glutSolidCone(0.1, 3.2, 10, 10)
        glRotate(90, 1.0, 0.0, 0.0)
        
        glColor4f(0.1, 0.8, 0.1, 0.15)
        for hInt in range(17):
            h = float(hInt)/5
            glTranslate(0, h, 0)
            glRotate((hInt/16)*70, 0.0, 1.0, 0.0)
            glRotate(90, 1.0, 0.0, 0.0)
            glutWireCone(1.2 - 0.5/(3.6 - h), h/6, 50, 1)
            glRotate(-90, 1.0, 0.0, 0.0)
            glRotate(-(hInt/16)*70, 0.0, 1.0, 0.0)
            glTranslate(0, -h, 0)
            
        glTranslate(-topLedCoords[0], 0, -topLedCoords[2])
        

    def drawLights(self):
        for ledIndex in range(0, self._ledsCount):
            color = [float(self._leds[ledIndex][0])/255, float(self._leds[ledIndex][1])/255, float(self._leds[ledIndex][2])/255]
            ledCoords = self._ledsMapReader.getLed(ledIndex)
            glTranslate(ledCoords[0]*self._cameraZoom, ledCoords[1]*self._cameraZoom, ledCoords[2]*self._cameraZoom)
            glColor3f(color[0], color[1], color[2])
            gluSphere(gluNewQuadric(), 0.02, 10, 10)
            glColor4f(color[0], color[1], color[2], 0.8)
            gluSphere(gluNewQuadric(), 0.03, 10, 10)
            glTranslate(-ledCoords[0]*self._cameraZoom, -ledCoords[1]*self._cameraZoom, -ledCoords[2]*self._cameraZoom)

    def showFrame(self, frame):
        self._leds = frame
