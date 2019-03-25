bl_info = {
    "name": "Move X Axis",
    "category": "Object",
}

import bpy
import sys
import os
from skimage import io
sys.path.insert(0, "D:\\Usefull soft\\Blender 2.80\\2.80\\projects\\Stone_map\\Scripts")
from shorcuts import process_image


class Mesh2texture(bpy.types.Operator):    
    """Texture creation script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.create_txtr"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Texture creation"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
  
    def execute(self, context):        # execute() is called when running the operator.

        # Import object
        file_loc = 'D:\\Usefull soft\\Blender 2.80\\2.80\\projects\\Stone_map\\input\\stone_old.obj'
        imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
        active_object = bpy.context.selected_objects[0] 
        #print('Imported name: ', active_object.name)

        # Resize object
        active_object.dimensions = (1.0,1.0,1.0)

        # Unwrap object
        context.view_layer.objects.active = active_object
        #bpy.context.scene.objects.active = active_object
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.smart_project()
        bpy.ops.uv.select_all(action='TOGGLE')
        bpy.ops.transform.resize(value=(4.5, 4.5, 4.5))
        bpy.ops.object.editmode_toggle()


        # Create a material
        new_mat = bpy.data.materials.new("img_material")
        context.object.active_material = new_mat
        
        # Enable nodes:
        new_mat.use_nodes = True
        BSDF = new_mat.node_tree.nodes["Principled BSDF"]

        # Add a diffuse shader, upload image and link to material:    
        img_diff = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
        img_diff.location = (-300,475)
        img_loc = filepath="D:\\Usefull soft\\Blender 2.80\\2.80\\projects\\Stone_map\\input\\kamen_DIFFUSE.bmp"
        img_diff.image = bpy.data.images.load(filepath=img_loc)
        new_mat.node_tree.links.new(BSDF.inputs['Base Color'], img_diff.outputs['Color'])

        # Add a specular shader, upload image and link to material:    
        img_spec = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
        img_spec.location = (-550,475)
        img_loc = filepath="D:\\Usefull soft\\Blender 2.80\\2.80\\projects\\Stone_map\\input\\kamen_SPECULAR.bmp"
        img_spec.image = bpy.data.images.load(filepath=img_loc)
        new_mat.node_tree.links.new(BSDF.inputs['Specular'], img_spec.outputs['Color'])

        # Add a normal map, upload image:    
        img_norm = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
        img_norm.location = (-700,150)
        img_loc = filepath="D:\\Usefull soft\\Blender 2.80\\2.80\\projects\\Stone_map\\input\\kamen_NORM.bmp"
        img_norm.image = bpy.data.images.load(filepath=img_loc)
        img_norm.color_space = 'NONE'

        # Add a bump map, upload image:    
        img_bump = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
        img_bump.location = (-850,475)
        img_loc = filepath="D:\\Usefull soft\\Blender 2.80\\2.80\\projects\\Stone_map\\input\\kamen_BUMP.bmp"
        img_bump.image = bpy.data.images.load(filepath=img_loc)

        # Create and combine normal and bump maps and link to material:
        map_norm = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
        map_norm.location = (-400,150)
        map_bump = new_mat.node_tree.nodes.new("ShaderNodeBump")
        map_bump.location = (-200,150)
        new_mat.node_tree.links.new(map_norm.inputs['Color'], img_norm.outputs['Color'])
        new_mat.node_tree.links.new(map_bump.inputs['Normal'], map_norm.outputs['Normal'])
        new_mat.node_tree.links.new(map_bump.inputs['Height'], img_bump.outputs['Color'])
        new_mat.node_tree.links.new(BSDF.inputs['Normal'], map_bump.outputs['Normal'])


        #bpy.data.screens["Layout"].shading.type = 'MATERIAL'

        return {'FINISHED'}            # Lets Blender know the operator finished successfully. 
  
def add_object_button(self, context):  
    self.layout.operator(  
        Mesh2texture.bl_idname,  
        text=Mesh2texture.__doc__,  
        icon='PLUGIN')  
  
def register():  
    bpy.utils.register_class(Mesh2texture)  
    bpy.types.VIEW3D_MT_object.append(add_object_button)  
    
def unregister():
    bpy.utils.register_class(Mesh2texture)
    
if __name__ == "__main__":  
    register() 