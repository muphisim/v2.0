import gmsh
import GmshModel
import Configure
import CreateInputFile

def createGmshModel(name, geoArgs):
    """
    all arguments
    geoArgs = [Lx, Ly, Lz, cx, cy, R]
    """
    Lx = geoArgs[0]
    Ly = geoArgs[1]
    Lz = geoArgs[2]
    cx = geoArgs[3]
    cy = geoArgs[4]
    R = geoArgs[5]
    
    lcx = 0.3*R
    lcc = 0.2*R
    
    model = gmsh.model
    model.add(name)
    model.geo.addPoint(cx,cy,0,lcc,1)
    model.geo.addPoint(cx+R,cy,0,lcc,2)
    model.geo.addPoint(cx,cy+R,0,lcc,3)
    model.geo.addPoint(cx-R,cy,0,lcc,4)
    model.geo.addPoint(cx,cy-R,0,lcc,5)
    model.geo.addPoint(0.5*Lx,-0.5*Ly,0,lcx,6)
    model.geo.addPoint(0.5*Lx,0.5*Ly,0,lcx,7)
    model.geo.addPoint(-0.5*Lx,0.5*Ly,0,lcx,8)
    model.geo.addPoint(-0.5*Lx,-0.5*Ly,0,lcx,9)
    
    model.geo.addCircleArc(2,1,3,1)
    model.geo.addCircleArc(3,1,4,2)
    model.geo.addCircleArc(4,1,5,3)
    model.geo.addCircleArc(5,1,2,4)
    model.geo.addLine(6,7,5)
    model.geo.addLine(7,8,6)
    model.geo.addLine(8,9,7)
    model.geo.addLine(9,6,8)
    
    model.geo.addCurveLoop([1,2,3,4],9)
    model.geo.addCurveLoop([5,6,7,8],10)
    
    model.geo.addPlaneSurface([9,10],1)
    
    bcFaces = model.geo.extrude([(2,1)],0,0,Lz)
    
    for fa in bcFaces:
        model.geo.addPhysicalGroup(fa[0],[fa[1]],fa[1])

    gmsh.model.geo.synchronize()
    model.mesh.generate(model.getDimension())
    return model

class myConfigure(Configure.Configure):
    def __init__(self):
        """
        configure in oxfem
        Attributes:
            FEM     : all FEM locations
            MM      : all MM locations
            solvers : all solvers
            materials: all material behaviors
            NeumannBCs: all Neumann BCs
            initialBCs: all initial BCs
        """
        # define FEM domains
        self.FEM = {
                   #support All or [(dim,phys), ...] or nothing
                   "Support": "All"
                   #"Support": [(3,1)]
                   }
        # define MM domains
        self.MM = {
              #support All or [(dim,phys), ...] or nothing
              #"Support": "All"
              #"Support": [(3,1)]
              }
        # define solvers - a tuple of dictionary
        self.solvers = ({
                #solver type
                "Solver": "IMPLICIT STATIC",
                #scale factor to estimate time sep for solver
                #"Scale Factor": 1e5,
                "Number of steps":3,
                #output specification, each component of the list corresponds a line in the oxfemm input file
                "Outputs": ((1000,), ("All" , "max"),),
                # start and end time
                "Time": (0.,10.),
                "DispBC":(
                            # each bc contains (type, location(dim, physical) list of prescried components and prescribed values
                            ("DISPLACEMENT RAMP",(2,43), ((0,0.),(1,0.),(2,0.))), 
                            ("DISPLACEMENT RAMP",(2,51), ((0,0.1),(1,0.15),(2,0.2))),
                            ("DISPLACEMENT RAMP",(2,43), ((3,10.),)),
                            ("DISPLACEMENT RAMP",(2,51), ((3,100.),)),
                         ), 
                "Extraction":(
                               ("NODE","TipDisplacement","Unknown","Mean",2233,0),
                               ("NODE","TipDisplacement","Unknown","Mean",2233,1),
                               ("NODE","TipDisplacement","Unknown","Mean",2233,2),
                               ("NODE","TipDisplacement","Unknown","Mean",2233,3),
                               ("NODE","CenterDisplacement","Unknown","Mean",2158,0),
                               ("NODE","CenterDisplacement","Unknown","Mean",2158,1),
                               ("NODE","CenterDisplacement","Unknown","Mean",2158,2),
                               ("NODE","CenterDisplacement","Unknown","Mean",2158,3),
                               ("ELEMENT","DeforEnergy","DEFO_ENERGY","Sum","All"),
                               ("ELEMENT","kineEnergy","KIN_ENERGY","Sum","All"),
                               ("ELEMENT","extEnergy","EXTERNAL_ENERGY","Sum","All"),
                            )
                },
                )
        # define all Neumann BCs
        self.NeumannBCs = {
                "PressureBC": (
                                # type, location, time interval, value
                                #("PRESSURE RAMP", (2,51), (0.,1.), -10.),
                                #("PRESSURE RAMP", (2,52), (0.5,1.), -0.1)
                              ),
                "Flux ExtraDof": (
                                    # type, location, time interval, value
                                    #("HEAT INST", (2,52), (0., 5), (0.,0.,0.)),
                                    # type, location, time interval, value
                                    #("VOLUMETRIC HEAT FLUX", (3,1), (0.,10.), 0.),
                                    # type, location, time interval, h and sink temperature
                                    #("CONVECTION", (2,52), (0., 7.5), (800.,0)),
                                    # type, location, time interval, A and sink temperature
                                    #("RADIATION", (2,52), (0., 8.5), (500.,0)),
                                  )
                #"GRAVITY": 1.
                }
        # define material laws  - a tuple of dictionary
        self.materials = ({
                #material name
                "Name": "Mat1",
                #density
                "Density": 1000.,
                #material type
                "Type": "Linear-Poroelastic",
                #"List of Elements": [(3,1),]
                # parameter of the law, each component of this list corresponds a line in the input file
                "Parameters": [(1E9,0.3,1.),],
                # extra dof field
                "ExtraDof": ("DarcyLaw",(3.75E-5, 1E-5, 3.33E3, 1.)),
                # support All or [(dim,phys), ...]
                "List of Elements": "All",
                },
                )
        self.initialBCs = {
                "INITIAL CONDITIONS EXTRADOF": (10.,)
                }
                
    def getFEMConfigure(self):
        return self.FEM
        
    def getMMConfigure(self):
        return self.MM
    
    def getSolversConfigure(self):
        return self.solvers
        
    def getNeumannBCsConfigure(self):
        return self.NeumannBCs
    
    def getMaterialsConfigure(self):
        return self.materials 
    
    def getInitialBCsConfigure(self):
        return self.initialBCs


Lx=2.
Ly=1.
Lz = 0.1
cx = 0.1
cy = 0.1
R = 0.2

gmsh.initialize()

model = createGmshModel("oneHole",[Lx,Ly,Lz,cx,cy,R])
gmsh.write("oneHole.msh")
gmshModel = GmshModel.GmshModel(model)
config = myConfigure()
CreateInputFile.createInputFile(fileName="input.inp",model=gmshModel,configure=config)
gmsh.finalize()


