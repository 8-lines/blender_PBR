#cmd entrance file
from skimage import io
from shorcuts import process_image
import os


#path = input('Enter image name/path: ')
path = os.path.join("images", "stone.jpg")
filename = os.path.split(path)[1].split('.')[0]

try:
    photo = io.imread(path)
except FileNotFoundError:
    print('File don\'t exist!')

for map, map_name in zip(process_image(photo, verbose=True, isPlotting=False),
                     ('DIFFUSE', 'NORM', 'BUMP', 'AO', 'SPECULAR')):

    io.imsave(os.path.join("images", "{0}_{1}.bmp".format(filename, map_name)), map)

print('ready.')

