import filters
from skimage import color, io
from skimage.util import img_as_float
from segmentation import generate_texture


'''img must be float rgb image'''
def bitmap2material(img, expand_nmap=False, verbose=False, isPlotting=False):

    if verbose:
        print('Start processing...', flush=True)

    if verbose:
        print('Making seamless texture...', flush=True)
    img = filters.make_seamless(img)
    gray_img = color.rgb2gray(img)
    if verbose:
        print('...done', flush=True)
        if(isPlotting):
            io.imshow(img)
            io.show()

    if verbose:
        print('Computing normal map...', flush=True)
    n_map = filters.sobel_rgb_decoded(gray_img)
    if verbose:
        print('...done', flush=True)
        if(isPlotting):
            io.imshow(n_map)
            io.show()

    if expand_nmap:
        # works rather slowly, so just optional
        if verbose:
            print('Applying expansion filter to normal map...', flush=True)
        n_map = filters.norm_expansion(n_map, verbose=True)
        if verbose:
            print('...done', flush=True)
            if(isPlotting):
                io.imshow(n_map)
                io.show()

    if verbose:
        print('Computing bump map...', flush=True)
    bump_map = filters.bump_from_normal(n_map, initial_value=gray_img, verbose=False)[0]
    if verbose:
        print('...done', flush=True)
        if(isPlotting):
            io.imshow(bump_map)
            io.show()

    if verbose:
        print('Making Ambient Occlusion map...', flush=True)
    ao_map = filters.ambient_occlusion(bump_map, n_map, verbose=True)
    if verbose:
        print('...done', flush=True)
        if(isPlotting):
            io.imshow(ao_map, cmap='gray')
            io.show()

    if verbose:
        print('Making specular map...', flush=True)
    specular_map = filters.make_specular_map(gray_img)
    if verbose:
        print('...done', flush=True)
        if(isPlotting):
            io.imshow(specular_map, cmap='gray')
            io.show()

    if verbose:
        print('...ready!', flush=True)

    return (img, n_map, bump_map, ao_map, specular_map)


def process_image(img, verbose=False, isPlotting=False):
    if verbose:
        print('Step 1: texture creation.', flush=True)
    texture = generate_texture(img, verbose=verbose, isPlotting=isPlotting)

    if verbose:
        print('Step 2: texture to material.', flush=True)
    return bitmap2material(texture, verbose=verbose, isPlotting=isPlotting)


def process_texture(img, verbose=False, isPlotting=False):
    if verbose:
        print('Step 1: square extraction.', flush=True)
    indent = (max(img.shape[:2]) - min(img.shape[:2])) // 2
    if img.shape[0] < img.shape[1]:
        square_texture = img[:, indent:indent+img.shape[0]]
    elif img.shape[0] > img.shape[1]:
        square_texture = img[indent:indent+img.shape[1], :]
    else:
        square_texture = img

    print(square_texture.shape)
    if isPlotting:
        io.imshow(square_texture)
        io.show()

    square_texture = img_as_float(square_texture)

    if verbose:
        print('Step 2: texture to material.', flush=True)
    return bitmap2material(square_texture, verbose=verbose)



if __name__ == "__main__":

    path = input('Enter image name/path: ')
    #path = '../data/test_sobel.jpg'

    try:
        img = io.imread(path)
    except FileNotFoundError:
        print('File don\'t exist!')

    process_texture(img, verbose=True)
