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
diff_node = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
diff_node.location = (-300,475)
img_path = os.path.abspath(".\\images"+namePostfix+"\\stone_DIFFUSE"+namePostfix+"_processed.bmp")
diff_node.image = bpy.data.images.load(filepath=img_path)
new_mat.node_tree.links.new(BSDF.inputs['Base Color'], diff_node.outputs['Color'])

# Add a specular shader, upload image and link to material:    
spec_node = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
spec_node.location = (-550,475)
img_path = os.path.abspath(".\\images"+namePostfix+"\\stone_SPECULAR"+namePostfix+".bmp")
spec_node.image = bpy.data.images.load(filepath=img_path)
spec_node.image.colorspace_settings.name = 'Non-Color'
new_mat.node_tree.links.new(BSDF.inputs['Specular'], spec_node.outputs['Color'])

# Add a normal map, upload image:    
norm_node = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
norm_node.location = (-700,150)
img_path = os.path.abspath(".\\images"+namePostfix+"\\stone_NORM"+namePostfix+".bmp")
norm_node.image = bpy.data.images.load(filepath=img_path)
norm_node.image.colorspace_settings.name = 'Non-Color'

# Add a bump map, upload image:    
bump_node = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
bump_node.location = (-850,475)
img_path = os.path.abspath(".\\images"+namePostfix+"\\stone_BUMP"+namePostfix+"_processed.bmp")
bump_node.image = bpy.data.images.load(filepath=img_path)
bump_node.image.colorspace_settings.name = 'Non-Color'

# Create and combine normal and bump maps and link to material:
map_norm = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
map_norm.location = (-400,150)
map_norm.uv_map = "UVMap"
map_bump_node = new_mat.node_tree.nodes.new("ShaderNodeBump")
map_bump_node.location = (-200,150)
map_bump_node.inputs[1].default_value = 0.01
map_bump_node.inputs[0].default_value = 1 # Strength of the bump map
new_mat.node_tree.links.new(map_norm.inputs['Color'], norm_node.outputs['Color'])
new_mat.node_tree.links.new(map_bump_node.inputs['Normal'], map_norm.outputs['Normal'])
new_mat.node_tree.links.new(map_bump_node.inputs['Height'], bump_node.outputs['Color'])
new_mat.node_tree.links.new(BSDF.inputs['Normal'], map_bump_node.outputs['Normal'])

# Change the view to 'Rendered'
for area in bpy.context.screen.areas: # iterate through areas in current screen
    if area.type == 'VIEW_3D':
        for space in area.spaces: # iterate through spaces in current VIEW_3D area
            if space.type == 'VIEW_3D': # check if space is a 3D view
                space.shading.type = 'MATERIAL' # set the viewport shading to rendered

# Create a new image and node for baking
bpy.context.scene.render.engine = 'CYCLES' 
bpy.ops.image.new(name="normals_baked", width=1024, height=1024, alpha=0)
baked_node = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
baked_node.location = (-700,-150)
baked_node.image = bpy.data.images["normals_baked"]
baked_node.image.colorspace_settings.name = 'Non-Color'
node_tree = new_mat.node_tree
baked_node.select = True
node_tree.nodes.active = baked_node

# Bake normal and bump maps
bpy.ops.object.bake(type='NORMAL', save_mode='INTERNAL')

# Save the baked image
filepath = os.path.abspath(".\\output\\normals_baked.bmp")
bpy.data.images["normals_baked"].filepath_raw = filepath
bpy.data.images["normals_baked"].file_format = "BMP"
bpy.data.images["normals_baked"].save()

# Create and combine normal map node and link to material:
baked_map_node = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
baked_map_node.location = (-350,-150)
baked_map_node.uv_map = "UVMap"
new_mat.node_tree.links.new(baked_map_node.inputs['Color'], baked_node.outputs['Color'])
new_mat.node_tree.links.new(BSDF.inputs['Normal'], baked_map_node.outputs['Normal'])

# Export the object
bpy.ops.export_scene.gltf(export_format='GLB', ui_tab='GENERAL', filepath=".\\output\\object_textured.glb", export_selected=True, export_yup=True, export_normals=True, export_materials=True, export_texcoords=True, check_existing=True)

bpy.ops.file.pack_all()
# save .blend file
bpy.ops.wm.save_as_mainfile(filepath="stone.blend")