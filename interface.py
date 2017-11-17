from vtk import (
    vtkCubeSource,
    vtkPolyDataMapper,
    vtkActor,
    vtkCamera,
    vtkRenderer,
    vtkRenderWindow,
)

def createCube():
    cube_data = vtkCubeSource()# initialize
    cube_data.SetXLength(10)
    cube_data.SetYLength(10)
    cube_data.SetZLength(50)
    return cube_data

def createScene(poly_data):
    dataMapper = vtkPolyDataMapper()# initialize
    dataMapper.SetInputConnection(poly_data.GetOutputPort())# tell the mapper it will process cube_data

    poly_actor = vtkActor()# initialize
    poly_actor.SetMapper(dataMapper)# actually process the data and store result
    return poly_actor

def createCamera():
    camera = vtkCamera()# initialize
    camera.SetPosition(0, 0, 75);
    camera.SetFocalPoint(0, 0, -25);
    return camera

def createRenderer(camera, actor):
    renderer = vtkRenderer()# initialize
    renderer.SetActiveCamera(camera)
    renderer.AddActor(actor)
    renderer.SetBackground(0, 0, 0)# Background color white
    return renderer

def createWindow(renderer):
    window = vtkRenderWindow()# initialize
    window.SetSize(1920, 1080)
    window.SetPosition(0, 0)
    window.AddRenderer(renderer)
    return window

class DemoCube(object):
    def __init__(self):
        self.cube_data = createCube()
        self.cube_actor = createScene(self.cube_data)
        self.camera = createCamera()
        self.renderer = createRenderer(self.camera, self.cube_actor)
        self.demo = createWindow(self.renderer)
        self.camX = 0
        self.camY = 0
    def render(self):
        self.demo.Render()
    def adjustCamera(self, incX, incY):
        self.camX += incX
        self.camY += incY
        self.camera.SetPosition(self.camX, self.camY, 150)
