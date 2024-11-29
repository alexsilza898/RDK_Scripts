# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/robodk.html
# Note: It is not required to keep a copy of this file, your Python script is saved with your RDK project



from robodk import robolink  # RoboDK API
from robodk import robomath  # Robot toolbox
import time
import random


#------------------------------------
FRAME_NAME = "World"
OBJECT_NAME = "tree"
N_COPIES = 40



RANDOMIZE_SIZE = True
SIZE_RANGE_FACTOR = [0.5, 0.9]  # %/100, minimum and maximum scale

RANDOMIZE_ROTATION = False
ROTATION_MAX = 20  # degrees, maximum rotation along reference Z (+/-)


RANDOMIZE_POSITION = True
POSITION_MAX_y =  3000  # mm, maximum lateral offset (+/-)
POSITION_MAX_x =  3000  # mm, maximum lateral offset (+/-)

#---------------------------------------
# Avoid auto-select
RDK = robolink.Robolink()
RDK.setSelection([])

#---------------------------------------
# Get the reference box
reference_objects = [x for x in RDK.ItemList(robolink.ITEM_TYPE_OBJECT) if 'ref' in x.Name().lower()]
if not reference_objects:
    RDK.ShowMessage(f'No reference  found. Please add a reference object with "{OBJECT_NAME}" and "ref" in its name, i.e. "Reference Box"')
    quit()
ref_obj = RDK.ItemUserPick(itemtype_or_list=reference_objects) if len(reference_objects) > 1 else reference_objects[0]
if not ref_obj.Valid():
    quit()
#RDK.ShowMessage(f'Using reference box: {ref_obj.Name()}')
ref_obj.setVisible(False)
ref_obj.Parent().setParam('Tree', 'Collapse')



#---------------------------------------
# Get the conveyor's reference frame
frame = RDK.Item(FRAME_NAME, robolink.ITEM_TYPE_FRAME)
if not frame.Valid():
    frame = RDK.AddFrame(FRAME_NAME)



def spawn_box():
    # Copy/paste changes the user selection
    selection = RDK.Selection()
    ref_obj.Copy(copy_children=False)
    new_obj = ref_obj.Parent().Paste()
    RDK.setSelection(selection)
    new_obj.setVisible(False)
    new_obj.setName(OBJECT_NAME)

    pose = new_obj.Pose()
    if RANDOMIZE_SIZE:
        scale = random.uniform(SIZE_RANGE_FACTOR[0], SIZE_RANGE_FACTOR[1])
        new_obj.Scale(scale)

    if RANDOMIZE_POSITION:
        lateral_offset_x = random.uniform(-POSITION_MAX, POSITION_MAX)  # Assuming reference frame has Y crossing the conveyor's width
        lateral_offset_y = random.uniform(-POSITION_MAX, POSITION_MAX)  # Assuming reference frame has Y crossing the conveyor's width
        pose = robomath.RelTool(pose, lateral_offset_x, lateral_offset_y, 0)

    if RANDOMIZE_ROTATION:
        rotation = random.uniform(-ROTATION_MAX, ROTATION_MAX)
        pose = robomath.RelTool(pose, 0, 0, 0, 0, 0, rotation)

    new_obj.setPose(pose)

    new_obj.setParentStatic(frame)
    new_obj.setVisible(True)
    
    return new_obj


obj_prev = frame.Childs()


#Remove Objects from previous runs
for obj in obj_prev:
    if obj.Name() == OBJECT_NAME:
        obj.Delete()

RDK.Render(False)
for n in range(N_COPIES):
    # Spawn new objects if space is sufficient
    #if obj_prev[-1].Valid(True) and not RDK.Collision(ref_obj, obj_prev[-1]):
    
    obj_prev.append(spawn_box())
RDK.Render(True)