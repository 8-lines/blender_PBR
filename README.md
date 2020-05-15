# blender_PBR
Making a PBR texture from image and integrating into Blender.

## Requirements
All requirements you can install from the 'requirements.txt' file. Just run $ pip install -r requirements.txt

1. Add path to a folder with blender.exe to the PATH in Windows
2. Photo of the stone should be placed into "images" folder and named "stone.jpg"
3. Model of the stone should be placed into the root folder (e.g. next to run.bat) and named "stone.obj"

## Running on Windows:
1. Run "run.bat".
2. When finished, close the console.
3. Open "stone.blend" file. All done!

## Running in Docker:
1. Download "Dockerfile"
2. Run "docker build ./" inside directory with "Dockerfile".
3. When finished, run "docker run -it image_id" (you get image_id after successful completion of step 2).
4. Run "./linux-run.sh"

## Structure
* "images" folder contains generated textures and original image of the stone
* "images_big" folder contains enlarged textures
* "seams_coords.csv" folder contains coordinates of edges of UV map
* "output" folder contains the results
