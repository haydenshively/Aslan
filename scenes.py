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

SCREEN_X = 3072.0
SCREEN_Y = 1920.0

def create3DGrid(height, width, depth, spacing = 1.0):
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
        id = points.InsertNextPoint([x*spacing, y*spacing, z*spacing])
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(id)

    grid = vtkPolyData()
    grid.SetPoints(points)
    grid.SetVerts(vertices)
    return grid

def createCube(height, width, depth):
    cube_data = vtkCubeSource()# initialize
    cube_data.SetXLength(width)
    cube_data.SetYLength(height)
    cube_data.SetZLength(depth)
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

def enableOffAxisProjectionFor(camera):
    screen_x = SCREEN_X/SCREEN_X
    screen_y = SCREEN_Y/SCREEN_X
    camera.SetUseOffAxisProjection(True)
    camera.SetScreenBottomLeft(-0.5*screen_x, -0.5*screen_y, -1)# x, y, z
    camera.SetScreenBottomRight(0.5*screen_x, -0.5*screen_y, -1)# x, y, z
    camera.SetScreenTopRight(0.5*screen_x, 0.5*screen_y, -1)# x, y, z
    camera.SetEyeSeparation(0.06)# this is the default

def createRenderer(camera, actors):
    renderer = vtkRenderer()# initialize
    renderer.SetActiveCamera(camera)
    for actor in actors: renderer.AddActor(actor)
    renderer.SetBackground(0, 0, 0)# Background color white
    return renderer

def createWindow(renderer, width = SCREEN_X, height = SCREEN_Y):
    window = vtkRenderWindow()# initialize
    window.SetSize(int(width), int(height))
    window.SetPosition(0, 0)
    window.AddRenderer(renderer)
    return window

from abstracts import Scene

class DemoCube(Scene):
    def __init__(self):
        self.cube_data = createCube(12, 12, 12)
        self.cube_actor = createScene(self.cube_data)
        self.cube_actor.SetPosition(0, 0, -100)
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
        #TODO distance from object should be adjusted based on face size
        self.camera.SetPosition(self.camX, self.camY, 200)
        #TODO first 2 params should be based on face angle or even gaze
        self.camera.SetFocalPoint(0, 0, -100)

class Grid3D(Scene):
    def __init__(self, height, width, depth, pointSize = 4):
        # CREATE ACTORS --------------------------------------------------------
        # grid -----------------------------------------------------------------
        self.grid_data = create3DGrid(height, width, depth, 0.05)
        self.grid_actor = createScene(self.grid_data)
        self.grid_actor.GetProperty().SetPointSize(pointSize)
        self.grid_actor.SetPosition(0, 0, 0)
        # cube -----------------------------------------------------------------
        self.cube_data = createCube(0.05, 0.05, 0.25)
        self.cube_actor = createScene(self.cube_data)
        self.cube_actor.SetPosition(0, 0, 0)
        self.cube_actor.GetProperty().SetAmbient(0.5)# add ambient light
        # ----------------------------------------------------------------------
        # PREPARE TO DISPLAY ---------------------------------------------------
        # basic camera, renderer, and window -----------------------------------
        self.camera = createCamera()
        self.renderer = createRenderer(self.camera, [self.grid_actor, self.cube_actor])
        self.window = createWindow(self.renderer)
        # off-axis projection --------------------------------------------------
        enableOffAxisProjectionFor(self.camera)
        # ----------------------------------------------------------------------
        # INITIALIZE OTHER INSTANCE PROPERTIES ---------------------------------
        self.camX = 0
        self.camY = 0
        # ----------------------------------------------------------------------
    def render(self):
        self.window.Render()
    def moveCameraBy(self, incX, incY):
        """
        incX: number of pixels to increment in the X direction
        incY: number of pixels to increment in the Y direction

        We divide incX by SCREEN_X so that the result has units of "screen-widths"
        We divide incY by SCREEN_Y so that the result has units of "screen-heights"
        """
        self.camX += (incX/SCREEN_X)
        self.camY += (incY/SCREEN_Y)
        # assume user is sitting W away from the screen (see comment in main.py)
        self.camera.SetPosition(self.camX, self.camY, 1.0)
        #TODO distance from object should be adjusted based on face size
        self.camera.SetFocalPoint(0, 0, -1)

    def moveCameraTo(self, x, y):
        """
        x: number of pixels to increment in the X direction
        y: number of pixels to increment in the Y direction

        We divide x by SCREEN_X so that the result has units of "screen-widths"
        We divide y by SCREEN_Y so that the result has units of "screen-heights"
        """
        self.camX = (x/SCREEN_X)
        self.camY = (y/SCREEN_Y)
        # assume user is sitting W away from the screen (see comment in main.py)
        self.camera.SetPosition(self.camX, self.camY, 1.0)
        #TODO first 2 params should be based on face angle or even gaze
        self.camera.SetFocalPoint(0, 0, -1)

class STL(Scene):
    def __init__(self, filename):
        # CREATE ACTORS --------------------------------------------------------
        # stl file -------------------------------------------------------------
        self.stl_data = vtkSTLReader()
        self.stl_data.SetFileName(filename)
        self.stl_actor = createScene(self.stl_data)
        self.stl_actor.SetScale(0.1, 0.1, 0.1)
        """
        This is a minimal example. You can do a lot more to make things look
        better. For example, rotate the actor:
        self.stl_actor.RotateX(-90)
        """
        # ----------------------------------------------------------------------
        # PREPARE TO DISPLAY ---------------------------------------------------
        # basic camera, renderer, and window -----------------------------------
        self.camera = createCamera()
        self.renderer = createRenderer(self.camera, [self.stl_actor])
        self.window = createWindow(self.renderer)
        # off-axis projection --------------------------------------------------
        enableOffAxisProjectionFor(self.camera)
        # ----------------------------------------------------------------------
        # INITIALIZE OTHER INSTANCE PROPERTIES ---------------------------------
        self.camX = 0
        self.camY = 0
        # ----------------------------------------------------------------------
    def render(self):
        self.window.Render()
    def moveCameraBy(self, incX, incY):
        """
        incX: number of pixels to increment in the X direction
        incY: number of pixels to increment in the Y direction

        We divide incX by SCREEN_X so that the result has units of "screen-widths"
        We divide incY by SCREEN_Y so that the result has units of "screen-heights"
        """
        self.camX += (incX/SCREEN_X)
        self.camY += (incY/SCREEN_Y)
        # assume user is sitting W away from the screen (see comment in main.py)
        self.camera.SetPosition(self.camX, self.camY, 1.0)
        #TODO distance from object should be adjusted based on face size
        self.camera.SetFocalPoint(0, 0, -1)

    def moveCameraTo(self, x, y):
        """
        x: number of pixels to increment in the X direction
        y: number of pixels to increment in the Y direction

        We divide x by SCREEN_X so that the result has units of "screen-widths"
        We divide y by SCREEN_Y so that the result has units of "screen-heights"
        """
        self.camX = (x/SCREEN_X)
        self.camY = (y/SCREEN_Y)
        # assume user is sitting W away from the screen (see comment in main.py)
        self.camera.SetPosition(self.camX, self.camY, 1.0)
        #TODO first 2 params should be based on face angle or even gaze
        self.camera.SetFocalPoint(0, 0, -1)
