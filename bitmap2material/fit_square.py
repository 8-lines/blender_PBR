from skimage import io, color
import numpy as np

def fit_square(img, verbose=False, isPlotting=False):

    square_sides = np.zeros(img.shape)

    
    for j in range(img.shape[1] - 1, -1 , -1):
        for i in range(img.shape[0] - 1, -1 , -1):


            if (img[i,j]):
                square_sides[i, j] = min(square_sides[i, j+1],
                                         square_sides[i+1, j],
                                         square_sides[i+1, j+1]) + 1

    max_vertex = np.unravel_index(np.argmax(square_sides, axis=None),
                                  square_sides.shape)
    max_side = int(square_sides.max())

    if verbose:
        print(max_vertex)
        print(max_side)

        out_img = img.copy()

        x = max_vertex[1]
        y = max_vertex[0]
        out_img[y:y+int(max_side)+1,x:x+int(max_side)+1] = 0.5
        
        if isPlotting:
            io.imshow(square_sides)
            io.show()
            io.imshow(out_img)
            io.show()

    return (max_vertex, max_side)



if __name__ == "__main__":

    img = io.imread('../data/test_mask.png', as_gray=True)

    io.imshow(img)
    io.show()

    print(fit_square(img, verbose=True))
