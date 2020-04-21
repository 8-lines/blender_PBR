import bpy
import os

namePostfix = "_big"

# set the stone as active object
stone = bpy.context.scene.objects["stone"]
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = stone
stone.select_set(True)

# Create a material
new_mat = bpy.data.materials.new("img_material")
bpy.context.object.active_material = new_mat

# Enable nodes:
new_mat.use_nodes = True
BSDF = new_mat.node_tree.nodes["Principled BSDF"]

# Add a diffuse shader, upload image and link to material:    
img_diff = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
img_diff.location = (-300,475)
img_loc = filepath = os.path.abspath(".\\images"+namePostfix+"\\stone_DIFFUSE"+namePostfix+"_processed.bmp")
img_diff.image = bpy.data.images.load(filepath=img_loc)
new_mat.node_tree.links.new(BSDF.inputs['Base Color'], img_diff.outputs['Color'])

# Add a specular shader, upload image and link to material:    
img_spec = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
img_spec.location = (-550,475)
img_loc = filepath = os.path.abspath(".\\images"+namePostfix+"\\stone_SPECULAR"+namePostfix+".bmp")
img_spec.image = bpy.data.images.load(filepath=img_loc)
img_spec.image.colorspace_settings.name = 'Non-Color'
new_mat.node_tree.links.new(BSDF.inputs['Specular'], img_spec.outputs['Color'])

# Add a normal map, upload image:    
img_norm = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
img_norm.location = (-700,150)
img_loc = filepath = os.path.abspath(".\\images"+namePostfix+"\\stone_NORM"+namePostfix+".bmp")
img_norm.image = bpy.data.images.load(filepath=img_loc)
img_norm.image.colorspace_settings.name = 'Non-Color'

# Add a bump map, upload image:    
img_bump = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
img_bump.location = (-850,475)
img_loc = filepath = os.path.abspath(".\\images"+namePostfix+"\\stone_BUMP"+namePostfix+"_processed.bmp")
img_bump.image = bpy.data.images.load(filepath=img_loc)
img_bump.image.colorspace_settings.name = 'Non-Color'

# Create and combine normal and bump maps and link to material:
map_norm = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
map_norm.location = (-400,150)
map_norm.uv_map = "UVMap"
map_bump = new_mat.node_tree.nodes.new("ShaderNodeBump")
map_bump.location = (-200,150)
map_bump.inputs[0].default_value = 1 # Strength of the bump map
new_mat.node_tree.links.new(map_norm.inputs['Color'], img_norm.outputs['Color'])
new_mat.node_tree.links.new(map_bump.inputs['Normal'], map_norm.outputs['Normal'])
new_mat.node_tree.links.new(map_bump.inputs['Height'], img_bump.outputs['Color'])
new_mat.node_tree.links.new(BSDF.inputs['Normal'], map_bump.outputs['Normal'])

# Change the view to 'Rendered'
for area in bpy.context.screen.areas: # iterate through areas in current screen
    if area.type == 'VIEW_3D':
        for space in area.spaces: # iterate through spaces in current VIEW_3D area
            if space.type == 'VIEW_3D': # check if space is a 3D view
                space.shading.type = 'MATERIAL' # set the viewport shading to rendered

bpy.ops.file.pack_all()
# save .blend file
bpy.ops.wm.save_as_mainfile(filepath="stone.blend")