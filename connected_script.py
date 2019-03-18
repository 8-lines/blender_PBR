bl_info = {
    "name": "Move X Axis",
    "category": "Object",
}

import os
import bpy
import sys
from sys import platform as _platform
import os.path as op
import traceback
import glob



TITLE = 'Installing Blender reqs'
# todo: Download get_pip from https://bootstrap.pypa.io/get-pip.py and put it in GET_PIP_FOL
GET_PIP_FOL = 'set-this-folder-name'
# todo: update theis list accroding to your requirements, or use a requirements.txt file
REQS = 'matplotlib scipy scikit-image'


def is_windows():
    return _platform == "win32"


def is_osx():
    return _platform == "darwin"


def is_linux():
    return _platform == "linux" or _platform == "linux2"


def install_blender_reqs(blender_fol='', gui=True):
    if blender_fol == '':
        blender_fol = find_blender()
    blender_parent_fol = get_parent_fol(blender_fol)

    # Get pip
    bin_template = op.join(get_parent_fol(blender_fol),  'Resources', '2.7?', 'python') if is_osx() else \
        op.join(blender_fol, '2.7?', 'python')
    blender_bin_folders = sorted(glob.glob(bin_template))
    if len(blender_bin_folders) == 0:
        print("Couldn't find Blender's bin folder! ({})".format(bin_template))
        blender_bin_fol = ''
        choose_folder = gui_input('Please choose the Blender bin folder where python file exists', gui) == 'Ok'
        if choose_folder:
            fol = choose_folder_gui(blender_parent_fol, 'Blender bin folder') if gui else input()
            if fol != '':
                blender_bin_fol = glob.glob(op.join(fol, '2.7?', 'python'))[-1]
        if blender_bin_fol == '':
            return
    else:
        # todo: let the user select the folder if more than one
        blender_bin_fol = blender_bin_folders[-1]
    python_exe = 'python.exe' if is_windows() else 'python3.5m'
    current_dir = os.getcwd()
    os.chdir(blender_bin_fol)
    pip_cmd = '{} {}'.format(op.join('bin', python_exe), op.join(GET_PIP_FOL, 'get-pip.py'))
    if not is_windows():
        run_script(pip_cmd)
        install_cmd = '{} install {}'.format(op.join('bin', 'pip'), REQS)
        run_script(install_cmd)
    else:
        install_cmd = '{} install {}'.format(op.join('Scripts', 'pip'), REQS)
        print(
            'Sorry, automatically installing external python libs in python will be implemented in the future.\n' +
            'Meanwhile, you can do the following:\n' +
            '1) Open a terminal window as administrator: ' +
            'Right click on the "Command Prompt" shortcut from the star menu and choose "Run as administrator"\n' +
            '2) Change the directory to "{}".\n'.format(blender_bin_fol) +
            '3) Run "{}"\n'.format(pip_cmd) +
            '4) Run "{}"\nGood luck!'.format(install_cmd))
    os.chdir(current_dir)


def find_blender():
    blender_fol = ''
    if is_windows():
        blender_win_fol = 'Program Files\Blender Foundation\Blender'
        if op.isdir(op.join('C:\\', blender_win_fol)):
            blender_fol = op.join('C:\\', blender_win_fol)
        elif op.isdir(op.join('D:\\', blender_win_fol)):
            blender_fol = op.join('D:\\', blender_win_fol)
    elif is_linux():
        output = run_script("find ~/ -name 'blender' -type d")
        if not isinstance(output, str):
            output = output.decode(sys.getfilesystemencoding(), 'ignore')
        blender_fols = output.split('\n')
        blender_fols = [fol for fol in blender_fols if op.isfile(op.join(
            get_parent_fol(fol), 'blender.svg')) or 'blender.app' in fol]
        if len(blender_fols) == 1:
            blender_fol = get_parent_fol(blender_fols[0])
    elif is_osx():
        blender_fol = '/Applications/Blender/blender.app/Contents/MacOS'
    return blender_fol


def run_script(cmd, verbose=False):
    import subprocess
    import sys
    try:
        if verbose:
            print('running: {}'.format(cmd))
        if is_windows():
            output = subprocess.call(cmd)
        else:
            output = subprocess.check_output('{} | tee /dev/stderr'.format(cmd), shell=True)
    except:
        print('Error in run_script!')
        print(traceback.format_exc())
        return ''

    if isinstance(output, str):
        output = output.decode(sys.getfilesystemencoding(), 'ignore')
    print(output)
    return output


def get_parent_fol(curr_dir='', levels=1):
    if curr_dir == '':
        curr_dir = get_current_fol()
    parent_fol = op.split(curr_dir)[0]
    for _ in range(levels - 1):
        parent_fol = get_parent_fol(parent_fol)
    return parent_fol


def get_current_fol():
    return op.dirname(op.realpath(__file__))


def choose_folder_gui(initialdir='', title=''):
    import tkinter
    from tkinter.filedialog import askdirectory
    root = tkinter.Tk()
    root.withdraw()  # hide root
    if initialdir != '':
        fol = askdirectory(initialdir=initialdir, title=title)
    else:
        fol = askdirectory(title=title)
    if is_windows():
        fol = fol.replace('/', '\\')
    return fol


def gui_input(message, gui, style=1):
    if gui:
        ret = message_box(message, TITLE, style)
    else:
        ret = input(message)
    return ret


def message_box(text, title='', style=1):
    import pymsgbox
    buttons = {0: ['Ok'], 1: ['Ok', 'Cancel'], 2: ['Abort', 'No', 'Cancel'], 3: ['Yes', 'No', 'Cancel'],
               4: ['Yes', 'No'], 5: ['Retry', 'No'], 6: ['Cancel', 'Try Again', 'Continue']}
    return pymsgbox.confirm(text=text, title=title, buttons=buttons[style])



blender_fol = sys.argv[1] if len(sys.argv) > 1 else ''
is_gui = bool(sys.argv[2]) if len(sys.argv) > 2 else True
install_blender_reqs(blender_fol, is_gui)
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
