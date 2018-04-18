from vtk import (
    vtkCubeSource,
    vtkPolyDataMapper,
    vtkPolyData,
    vtkPoints,
    vtkCellArray,
    vtkActor,
    vtkCamera,
    vtkRenderer,
    vtkRenderWindow,
    vtkSTLReader
)

def create3DGrid(height, width, depth):
    # height
    ys = [i - height/2 for i in range(height)]*width*depth
    # width
    xs = []
    for i in range(width):
        xs += [i - width/2]*height
    xs *= depth
    # depth
    zs = []
    for i in range(depth):
        zs += [i]*width*height

    points = vtkPoints()
    vertices = vtkCellArray()
    for x, y, z in zip(xs, ys, zs):
        id = points.InsertNextPoint([x, y, z])
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(id)

    grid = vtkPolyData()
    grid.SetPoints(points)
    grid.SetVerts(vertices)
    return grid

def createCube():
    cube_data = vtkCubeSource()# initialize
    cube_data.SetXLength(10)
    cube_data.SetYLength(10)
    cube_data.SetZLength(50)
    return cube_data

def createScene(poly_data):
    dataMapper = vtkPolyDataMapper()# initialize
    try:
        dataMapper.SetInputConnection(poly_data.GetOutputPort())# tell the mapper it will process cube_data
    except AttributeError:
        dataMapper.SetInputData(poly_data)

    poly_actor = vtkActor()# initialize
    poly_actor.SetMapper(dataMapper)# actually process the data and store result
    return poly_actor

def createCamera():
    camera = vtkCamera()# initialize
    camera.SetPosition(0, 0, 0);
    camera.SetFocalPoint(0, 0, 0);
    return camera

def createRenderer(camera, actor):
    renderer = vtkRenderer()# initialize
    renderer.SetActiveCamera(camera)
    renderer.AddActor(actor)
    renderer.SetBackground(0, 0, 0)# Background color white
    return renderer

def createWindow(renderer, width = 1920, height = 1080):
    window = vtkRenderWindow()# initialize
    window.SetSize(width, height)
    window.SetPosition(0, 0)
    window.AddRenderer(renderer)
    return window

from abstracts import Scene

class DemoCube(Scene):
    def __init__(self):
        self.cube_data = createCube()
        self.cube_actor = createScene(self.cube_data)
        self.camera = createCamera()
        self.renderer = createRenderer(self.camera, self.cube_actor)
        self.window = createWindow(self.renderer)
        self.camX = 0
        self.camY = 0
    def render(self):
        self.window.Render()
    def moveCameraBy(self, incX, incY):
        self.camX += incX
        self.camY += incY
        self.camera.SetPosition(self.camX, self.camY, 150)

class Grid3D(Scene):
    def __init__(self, height, width, depth, pointSize = 5):
        self.grid_data = create3DGrid(height, width, depth)
        self.grid_actor = createScene(self.grid_data)
        self.grid_actor.GetProperty().SetPointSize(pointSize)
        self.camera = createCamera()
        self.renderer = createRenderer(self.camera, self.grid_actor)
        self.window = createWindow(self.renderer)
        self.camX = 0
        self.camY = 0
    def render(self):
        self.window.Render()
    def moveCameraBy(self, incX, incY):
        self.camX += incX
        self.camY += incY
        self.camera.SetPosition(self.camX, self.camY, 75)#TODO 50 (distance from object) should be adjusted based on face size
        # self.camera.SetFocalPoint(self.camX/3.0, self.camY/3.0, 0);# first 2 params should be based on face angle or even gaze

class STL(Scene):
    def __init__(self, filename):
        self.stl_data = vtkSTLReader()
        self.stl_data.SetFileName(filename)
        self.stl_actor = createScene(self.stl_data)
        self.stl_actor.RotateX(-90)
        self.camera = createCamera()
        self.renderer = createRenderer(self.camera, self.stl_actor)
        self.window = createWindow(self.renderer)#, 1920//2, 1080//2)
        self.camX = 50
        self.camY = 10
    def render(self):
        self.window.Render()
    def moveCameraBy(self, incX, incY):
        self.camX += incX
        self.camY += incY
        self.camera.SetPosition(self.camX, self.camY, 200)
