from skimage import io, color
from skimage.filters import sobel_h, sobel_v, gaussian
from skimage.util import img_as_float
import numpy as np

from math import exp
from itertools import product

def normalized(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

# OpenGL periodical indexing placeholder
def get_texture(img, x, y):
    return img[x % (img.shape[0] - 1), y % (img.shape[1] - 1)]

# copy of OpenGL mix() logic
def ab_mix(x, y, a):
    return x * (1-a) + y * a

# copy of Awesome Bump realization of Gauss function
def ab_gaussian(pos, w):
    return exp( -(pos[0]**2 + pos[1]**2) / (w**2 + 1))


def sobel_rgb_decoded(grey_img):
    # (-) compensates weirdness of the skimage's sobel cernel
    img_sobel_h = -sobel_h(grey_img) * 0.5 + 0.5 #Gy
    img_sobel_v = -sobel_v(grey_img) * 0.5 + 0.5 #Gx

    # rgb encoding
    sobel_rgb = np.dstack((img_sobel_v, img_sobel_h, np.ones_like(grey_img)))
    return sobel_rgb

# copy of mode_normal_expansion_filter from Awesome Bump
def norm_expansion(img, radius=2, flatting=0.5, verbose=True):

    out_img = np.zeros_like(img)

    if verbose:
        last_x = -1

    for x, y in np.ndindex(img.shape[:2]):
        if verbose and x != last_x:
            #print('\t\t%s : %s' % (x, y))
            last_x = x

        filt = np.zeros(3)
        wtotal = 0.

        for i, j in product(range(-radius, radius+1),
                            range(-radius, radius+1)):

            normal = normalized(2*get_texture(img, x-i, y-j) - 1)
            n_len = np.linalg.norm(normal[:2])

            w = ab_mix(n_len,
                       1/(20 * ab_gaussian((i, j), radius) * n_len + 1),
                       flatting + 0.001)

            wtotal += w
            filt += normal * w

        filt /= wtotal
        out_img[x, y] = 0.5 * normalized(filt) + 0.5
            
    return out_img            

# python realisation of AB algorythm
def bump_from_normal(n_map, scale=1, stages=5, iters=1, initial_value=0, verbose=False, isPlotting=False):

    # initial value, might be grey_img itself
    bump_map = np.ones(n_map.shape[:2]) * initial_value

    for k in [scale*(2 ** n) for n in reversed(range(stages))]:
        
        for iteration in range(iters):
            if verbose:
                pass
                #print('k:%s : i:%s' % k, iteration)
            for (x, y) in np.ndindex(n_map.shape[:2]):

                hxp = get_texture(bump_map, x+k, y)
                hxm = get_texture(bump_map, x-k, y)
                hyp = get_texture(bump_map, x, y+k)
                hym = get_texture(bump_map, x, y-k)

                nxp = 2 * (get_texture(n_map, x+k, y)[1] - 0.5)
                nxm = 2 * (get_texture(n_map, x-k, y)[1] - 0.5)
                nyp = 2 * (get_texture(n_map, x, y+k)[0] - 0.5)
                nym = 2 * (get_texture(n_map, x, y-k)[0] - 0.5)

                h = k*(nxp-nxm+nyp-nym)/8.0 + (hxp + hxm + hyp + hym)/4.0
                bump_map[x,y] = h

        if verbose:
            if isPlotting:
                io.imshow(bump_map)
                io.show()

    a = bump_map.min()
    b = bump_map.max()

    x = 1 / (b - a)
    y = - a * x

    return x * bump_map + y, a, b

#copy of AB mode_occlusion_filter
def ambient_occlusion(bump_map, n_map, intensity=1, scale=2, bias=0.5, iters=2, verbose=False, isPlotting=False):

    get_position = lambda u, v: np.array((u, v, get_texture(bump_map, u, v) * bias))
    get_normal = lambda u, v: normalized(get_texture(n_map, u, v) - 0.5)
    ao_map = np.zeros_like(bump_map)

    # xy = tcoord, ij = uv
    def do_ambient_occlusion(xy, ij, p, cnorm):
        diff = get_position(xy[0] + ij[0], xy[1] + ij[1]) - p
        v = normalized(diff)

        return max(0., np.dot(cnorm, v)) * intensity

    if verbose:
        last_x = -1

    for x, y in np.ndindex(bump_map.shape[:2]):
        p = get_position(x, y)
        n = get_normal(x, y)
        ao = 0.

        if verbose and x != last_x:
            last_x = x
            #print('%s : %s' % (x, y))

        for i, j in product(range(-iters, iters + 1),
                            range(-iters, iters + 1)):

            ao += do_ambient_occlusion((x,y),
                                       (i * scale,j * scale),
                                       p,
                                       n)

        ao /= (2*iters + 1) ** 2

        ao_map[x, y] = np.clip(1 - ao, 0, 1)

    return ao_map


def generate_seamless_kernel(shape, radius1, radius2):

    kernel = np.ones(shape)
    center = (shape[0] // 2, shape[1] // 2)

    for pnt in np.ndindex(shape):

        corner = (shape[0] - 1 if pnt[0] > center[0] else 0, shape[1] - 1 if pnt[1] > center[1] else 0)

        dist = np.linalg.norm(np.array(pnt) - np.array(corner))

        kernel[pnt] = max((dist - radius1) / (radius2 - radius1), 0) if dist < radius2 else 1

    return kernel


def weld_images(img1, img2, overlay, axis):

    res_shape = list(img1.shape)
    res_shape[axis] += img2.shape[axis] - overlay
    res = np.zeros(res_shape)

    res[:img1.shape[0], :img1.shape[1]] = img1

    for i in range(img1.shape[axis] - overlay, img1.shape[axis]):
        j = i - img1.shape[axis] + overlay
        coef = j / overlay
        if axis == 0:
            # merge rows
            res[i,:] = img2[j,:]*coef + img1[i,:]*(1 - coef)
        elif axis == 1:
            # merge columns
            res[:, i] = img2[:, j] * coef + img1[:, i] * (1 - coef)

    if axis == 0:
        # fill rest of the rows
        res[img1.shape[0]:, :] = img2[overlay:,:]
    elif axis == 1:
        # fill rest of the columns
        res[:, img1.shape[1]:] = img2[:, overlay:]

    return res

sign = lambda x: 1 if x >= 0 else -1
def make_seamless(img, overlay_coef=0., verbose=False, isPlotting=False):
    overlay = int(overlay_coef * min(img.shape[:2]))
    overlay -= overlay % 2
    center = (img.shape[0] // 2, img.shape[1] // 2)

    left = weld_images(img[center[0] - overlay // 2:, center[1] - overlay // 2:],
                       img[:center[0] + overlay // 2, center[1] - overlay // 2:], overlay, 0)
    right = weld_images(img[center[0] - overlay // 2:, :center[1] + overlay // 2],
                        img[:center[0] + overlay // 2, :center[1] + overlay // 2], overlay, 0)

    out_seamless = weld_images(left, right,overlay, 1)

    radius = min(img.shape[:2]) // 2 + np.round(min(img.shape[:2])*0.07)
    kernel = generate_seamless_kernel(img.shape[:2], 0.7 * radius, radius)

    if verbose:
        if isPlotting:
            io.imshow(kernel)
            io.show()

    for x, y in np.ndindex(img.shape[:2]):
        out_seamless[x, y] = kernel[x,y]*img[x,y] + (1 - kernel[x,y])*out_seamless[x,y]

    if verbose:
        if isPlotting:
            io.imshow(out_seamless)
            io.show()


    return out_seamless


def difference_of_gaussian(grey_img, sigma1, sigma2):

    s1 = gaussian(grey_img, sigma=sigma1)
    s2 = gaussian(grey_img, sigma=sigma2)

    return s1 - s2


def make_specular_map(grey_img, sigma=1, k=1.5, min_value=0.4):
    DoG = difference_of_gaussian(grey_img, sigma, k*sigma)

    DoG = np.where(DoG < 0, DoG + 1, np.ones_like(DoG))

    # shifting values to get better contrast
    x = (min_value - 1) / (DoG.min() - 1)
    y = 1 - x

    return x*DoG + y




if __name__ == "__main__":
    #"""
    path = input('Enter image name/path: ')
    #path = '../data/test_sobel.jpg'

    try:
        img = io.imread(path)
    except FileNotFoundError:
        print('File don\'t exist!')

    print('Start processing...', flush=True)
    img = img_as_float(img)

    print('Making seamless texture...', flush=True)
    img = make_seamless(img, verbose=True)
    io.imsave('out/seamless.png', img)
    gray_img = color.rgb2gray(img)
    print('...done', flush=True)
    io.imshow(img) and io.show()

    print('Computing normal map...', flush=True)
    n_map = sobel_rgb_decoded(gray_img)
    print('...done', flush=True)
    io.imshow(n_map) and io.show()

    #'''
    # works rather slowly, so just optional 
    print('Applying expansion filter to normal map...', flush=True)
    n_map = norm_expansion(n_map, verbose=True)
    print('...done', flush=True)
    io.imshow(n_map) and io.show()
    #'''

    io.imsave('out/n_map.png', n_map)

    print('Computing bump map...', flush=True)
    bump_map = bump_from_normal(n_map, initial_value=gray_img, verbose=False)[0]
    print('...done', flush=True)
    io.imshow(bump_map) and io.show()

    io.imsave('out/bump_map.png', bump_map)

    print('Making Ambient Occlusion map...', flush=True)
    ao_map = ambient_occlusion(bump_map, n_map, verbose=True)
    print('...done', flush=True)
    io.imshow(ao_map, cmap='gray') and io.show()

    io.imsave('out/ao_map.png', ao_map)

    print('Making specular map...', flush=True)
    specular_map = make_specular_map(gray_img)
    print('...done', flush=True)
    io.imshow(specular_map, cmap='gray') and io.show()

    io.imsave('out/specular_map.png', specular_map)

    print('...ready!', flush=True)
