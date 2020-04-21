import bpy

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)
# import stone from .obj file
if bpy.data.objects.get("stone") is None:
    bpy.ops.import_scene.obj(filepath="stone.obj")
    # set the stone as active object
    stone = bpy.context.scene.objects["stone"]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = stone
    stone.select_set(True)
    # set pivot to the center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
    # move object to (0,0,0)
    bpy.context.object.location = (0,0,0)
    # scale the stone
    stone.scale = (0.01,0.01,0.01)
    
bpy.ops.wm.save_as_mainfile(filepath="stone.blend")