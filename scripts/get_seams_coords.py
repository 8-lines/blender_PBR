import bpy
import bmesh
from mathutils import Vector

#Store key information using indexes so that you can use it either in bmesh or mesh
class EdgeUV:
    def __init__(self, edge_index, v1_index, v2_index,
        face1_index, uv11, uv12, face2_index, uv21, uv22):

        self.edge_index = edge_index
        self.v1_index = v1_index
        self.v2_index = v2_index
        self.face1_index = face1_index
        self.uv11 = uv11
        self.uv12 = uv12
        self.face2_index = face2_index
        self.uv21 = uv21
        self.uv22 = uv22

    def __str__(self):
        return "{self.uv11[0]},{self.uv11[1]},{self.uv12[0]},{self.uv12[1]},{self.uv21[0]},{self.uv21[1]},{self.uv22[0]},{self.uv22[1]}".format(self=self)
        #return "<{self.edge_index}/{self.v1_index}/{self.v2_index}: 
        #[{self.face1_index}: {self.uv11}, {self.uv12}] [{self.face2_index}: 
        #    {self.uv21}, {self.uv22}]>".format(self=self)

#Get the concerned edges
#The one that should be seams and correspond to two faces
def get_island_boundary_edges(bm):
    #Store the current seams
    current_seams = [e for e in bm.edges if e.seam]
    #Clear seams
    for e in current_seams:
        e.seam = False
    #Make seams from uv islands
    bpy.ops.uv.seams_from_islands()
    #Get the result
    boundaries = [e for e in bm.edges if e.seam and len(e.link_faces) == 2]
    #Restore seams
    for e in current_seams:
        e.seam = True
    return boundaries

#Get the uv coordinate for the vertices in the uv loop of the face
def get_uvs(face, uv_layer, v1, v2):
    uv1, uv2 = None, None
    for loop in face.loops:
        if loop.vert == v1:
            uv1 = Vector(loop[uv_layer].uv)
        elif loop.vert == v2:
            uv2 = Vector(loop[uv_layer].uv)
        if uv1 and uv2:
            return uv1, uv2
    return Vector((-1, -1)), Vector((-1, -1))

#Get the complete result in form of array of EdgeUV
def get_boundary_uv_coords(context, object):
    bpy.ops.object.mode_set(mode = 'EDIT')

    #Make bmesh object
    bm = bmesh.from_edit_mesh(object.data)
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    #Get the wanted boundaries
    boundary_edges = get_island_boundary_edges(bm)

    #Current uv layer    
    uv_layer = bm.loops.layers.uv.active

    result = []

    for edge in boundary_edges:
        #Get the faces
        face1 = edge.link_faces[0] # We know to have 2 faces 
        face2 = edge.link_faces[1]

        #Get the vertices
        v1 = edge.verts[0]
        v2 = edge.verts[1]

        #UV coordinates for face1 and v1, v2
        uv11, uv12 = get_uvs(face1, uv_layer, v1, v2)

        #UV coordinates for face2 and v1, v2
        uv21, uv22 = get_uvs(face2, uv_layer, v1, v2)

        edge_uv = EdgeUV( edge.index, v1.index, v2.index, face1.index, uv11, uv12, face2.index, uv21, uv22 )
        result.append( edge_uv )

    bpy.ops.object.mode_set(mode = 'OBJECT')

    return result

#Converts uv coordinates to image size
def uv_to_image(image, uv):
    w, h = image.size
    return (round(uv[0] * (w-1)), round(uv[1] * (h-1)))

#Get image pixel
def pixel_from_co(image, co):
    w = image.size[0]
    i = 4 * (co[1] * w + co[0])
    return img.pixels[index:index+3] #RGBA

stone = bpy.context.scene.objects["stone"]
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = stone
stone.select_set(True)

bpy.ops.object.mode_set(mode = 'EDIT') #entering edit mode
bpy.ops.mesh.select_all(action='SELECT') #select all objects elements
bpy.ops.uv.smart_project() #the actual unwrapping operation
bpy.ops.object.mode_set(mode = 'OBJECT') #exiting edit mode

uvs = get_boundary_uv_coords(bpy.context, bpy.context.active_object)


open("seams_coords.csv", "w+").close()
file = open("seams_coords.csv", "a")

for uv in uvs:
    file.write(str(uv))
    file.write("\n")
file.close()

bpy.ops.wm.save_as_mainfile(filepath="stone.blend")