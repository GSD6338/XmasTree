import threading
import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from ledsMapReaders.LedsMapReader import LedsMapReader
from ledsAdapters.LedsAdapter import LedsAdapter


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
        glTranslate(0.0, 1.0, 0.0)
        glRotate(self._cameraRotation, 0.0, 1.0, 0.0)
        glRotate(self._cameraRotationX, 1.0, 0.0, 0.0)
        glTranslate(0.0, -1.0, 8.0)
        glMatrixMode(GL_MODELVIEW)
        glutSwapBuffers()

    def drawTree(self):
        for ledIndex in range(0, self._ledsCount):
            glColor3f(float(self._leds[ledIndex][0])/255, float(self._leds[ledIndex][1])/255, float(self._leds[ledIndex][2])/255)
            ledCoords = self._ledsMapReader.getLed(ledIndex)
            glTranslate(ledCoords[0]*self._cameraZoom, ledCoords[1]*self._cameraZoom, ledCoords[2]*self._cameraZoom)
            gluSphere(gluNewQuadric(), 0.03, 10, 10)
            glTranslate(-ledCoords[0]*self._cameraZoom, -ledCoords[1]*self._cameraZoom, -ledCoords[2]*self._cameraZoom)

    def showFrame(self, frame):
        self._leds = frame
