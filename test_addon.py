bl_info = {
    "name": "Move X Axis",
    "category": "Object",
}

import bpy
import os
from skimage import io
from shorcuts import process_image


class ObjectMoveX(bpy.types.Operator):
    """My Object Moving Script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.move_x"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Move X by One"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):        # execute() is called when running the operator.

        #path = input('Enter image name/path: ')
        path = "D:\\Usefull soft\\Blender\\2.79\\projects\\Stone_map\\Scripts\\kamen.JPG"
        filename = os.path.split(path)[1].split('.')[0]

        try:
            photo = io.imread(path)
        except FileNotFoundError:
            print('File don\'t exist!')

        for map, map_name in zip(process_image(photo, verbose=True),
                            ('DIFFUSE', 'NORM', 'BUMP', 'AO', 'SPECULAR')):

            io.imsave('{0}_{1}.bmp'.format(filename, map_name), map)


        # Import object
        file_loc = 'D:\\Usefull soft\\Blender\\2.79\\projects\\Stone_map\\stone_old.obj'
        imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
        active_object = bpy.context.selected_objects[0] 
        #print('Imported name: ', active_object.name)

        # Resize object
        active_object.dimensions = (1.0,1.0,1.0)

        # Unwrap object
        bpy.context.scene.objects.active = active_object
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.smart_project()
        bpy.ops.uv.select_all(action='TOGGLE')
        bpy.ops.transform.resize(value=(4.5, 4.5, 4.5))
        bpy.ops.object.editmode_toggle()

        
        # Create a material
        bpy.context.scene.render.engine = 'CYCLES'
        new_mat = bpy.data.materials.new("img_material")
        context.object.active_material = new_mat
        bpy.context.space_data.viewport_shade = 'MATERIAL'

        # Enable 'Use nodes':
        new_mat.use_nodes = True
        nodes = new_mat.node_tree.nodes
        BSDF = new_mat.node_tree.nodes.get('Diffuse BSDF')

        # Add a diffuse shader, upload image and link to material:    
        img_diff = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
        img_diff.location = (-300,475)
        diff_img_loc = filepath="D:\\Usefull soft\\Blender\\2.79\\projects\\Stone_map\\kamen_DIFFUSE.bmp"
        img_diff.image = bpy.data.images.load(filepath=diff_img_loc)
        new_mat.node_tree.links.new(BSDF.inputs[0], img_diff.outputs[0])

        # Add a normal map, upload image and link to material:    
        img_norm = new_mat.node_tree.nodes.new('ShaderNodeTexImage')
        img_norm.location = (-375,150)
        norm_img_loc = filepath="D:\\Usefull soft\\Blender\\2.79\\projects\\Stone_map\\kamen_NORM.bmp"
        img_norm.image = bpy.data.images.load(filepath=norm_img_loc)
        img_norm.color_space = 'NONE'
        map_norm = new_mat.node_tree.nodes.new('ShaderNodeNormalMap')
        map_norm.location = (-200,150)
        new_mat.node_tree.links.new(map_norm.inputs[1], img_norm.outputs[0])
        new_mat.node_tree.links.new(BSDF.inputs[2], map_norm.outputs[0])

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

def register():
    bpy.utils.register_class(ObjectMoveX)


def unregister():
    bpy.utils.unregister_class(ObjectMoveX)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
