from cv2 import cv2
import numpy as np
import os

imagesPath = "images"
resultImagesPath = "images_big"
imgTypes = np.array(["SPECULAR", "DIFFUSE", "BUMP", "NORM", "AO"])
coef = 5

for imgType in imgTypes:
    original_img = cv2.imread(os.path.join(imagesPath, "stone_"+imgType+".bmp"))
    imgSize = original_img.shape
    
    newimg = np.zeros((imgSize[0]*coef,imgSize[1]*coef,3), np.uint8)
    for i in range(coef):
        for j in range(coef):
            newimg[imgSize[0]*i:imgSize[0]*(i+1), imgSize[1]*j:imgSize[1]*(j+1), :] = original_img

    cv2.imwrite(os.path.join(resultImagesPath, "stone_"+imgType+"_big.bmp"), newimg)