REM !!!-------Please add a path to folder with blender.exe to the PATH-------!!!

python bitmap2material\photo2material.py
python scripts\multiple_texture.py
IF NOT EXIST stone.blend (blender -b --python scripts\create_blend_file.py)
blender stone.blend -b --python scripts\get_seams_coords.py
python scripts\color_edges.py
blender stone.blend -b --python scripts\set_shaders.py
cmd /k