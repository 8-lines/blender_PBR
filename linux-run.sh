python3 bitmap2material/photo2material.py
python3 scripts/multiple_texture.py
rm stone.blend
rm stone.blend1
blender -b --python scripts/create_blend_file.py
blender stone.blend -b --python scripts/get_seams_coords.py
python3 scripts/color_edges.py
blender stone.blend -b --python scripts/set_shaders.py