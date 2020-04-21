import csv
from cv2 import cv2
import numpy as np
import os
import sys

imgPath = "images"
stoneName = "stone"
imgTypes = ["DIFFUSE", "BUMP"]
imgPostfix = "_big"

original_img = cv2.imread(os.path.join(imgPath+imgPostfix, stoneName+"_"+imgTypes[0]+imgPostfix+".bmp"))
imgSize = int(original_img.shape[0])

coords = []
with open("seams_coords.csv", "r") as coordsFile:
    reader = csv.reader(coordsFile, delimiter=',')
    coords = np.array(list(reader), np.float) * imgSize

coords = coords.astype(int)
lowThickMask = np.zeros((imgSize, imgSize, 3))
mediumThickMask = np.zeros((imgSize, imgSize, 3))
highThickMask = np.zeros((imgSize, imgSize, 3))

lower_color_bounds = (0,254,254)
upper_color_bounds = (0,255,255)
lowLinewidth = 2
mediumLinewidth = 4
highLinewidth = 6
brightnessDisp = 20

maskrandom = np.random.randint(0, 2, (imgSize, imgSize, 1), np.uint8)*255
maskrandom = cv2.cvtColor(maskrandom, cv2.COLOR_GRAY2BGR).astype(np.uint8)
maskrandom1 = np.random.randint(0, 2, (imgSize, imgSize, 1), np.uint8)*255
maskrandom1 = cv2.cvtColor(maskrandom1, cv2.COLOR_GRAY2BGR).astype(np.uint8)
maskrandom2 = np.random.randint(0, 2, (imgSize, imgSize, 1), np.uint8)*255
maskrandom2 = cv2.cvtColor(maskrandom2, cv2.COLOR_GRAY2BGR).astype(np.uint8)

for co in coords:
    cv2.line(lowThickMask, (co[0], co[1]), (co[2], co[3]), (0, 255, 255), lowLinewidth)
    cv2.line(lowThickMask, (co[4], co[5]), (co[6], co[7]), (0, 255, 255), lowLinewidth)

    cv2.line(mediumThickMask, (co[0], co[1]), (co[2], co[3]), (0, 255, 255), mediumLinewidth)
    cv2.line(mediumThickMask, (co[4], co[5]), (co[6], co[7]), (0, 255, 255), mediumLinewidth)

    cv2.line(highThickMask, (co[0], co[1]), (co[2], co[3]), (0, 255, 255), highLinewidth)
    cv2.line(highThickMask, (co[4], co[5]), (co[6], co[7]), (0, 255, 255), highLinewidth)

lowThickMask = cv2.inRange(lowThickMask,lower_color_bounds,upper_color_bounds)
lowThickMask = cv2.cvtColor(lowThickMask, cv2.COLOR_GRAY2BGR).astype(np.uint8)

mediumThickMask = cv2.inRange(mediumThickMask,lower_color_bounds,upper_color_bounds)
mediumThickMask = cv2.cvtColor(mediumThickMask, cv2.COLOR_GRAY2BGR).astype(np.uint8)

highThickMask = cv2.inRange(highThickMask,lower_color_bounds,upper_color_bounds)
highThickMask = cv2.cvtColor(highThickMask, cv2.COLOR_GRAY2BGR).astype(np.uint8)

lowThickMask = lowThickMask & maskrandom
lowThickMask = cv2.cvtColor(lowThickMask, cv2.COLOR_BGR2GRAY).astype(np.uint8)
lowThickMask = cv2.cvtColor(lowThickMask, cv2.COLOR_GRAY2BGR).astype(np.uint8)

mediumThickMask = mediumThickMask & maskrandom1
mediumThickMask = cv2.cvtColor(mediumThickMask, cv2.COLOR_BGR2GRAY).astype(np.uint8)
mediumThickMask = cv2.cvtColor(mediumThickMask, cv2.COLOR_GRAY2BGR).astype(np.uint8)

highThickMask = highThickMask & maskrandom2
highThickMask = cv2.cvtColor(highThickMask, cv2.COLOR_BGR2GRAY).astype(np.uint8)
highThickMask = cv2.cvtColor(highThickMask, cv2.COLOR_GRAY2BGR).astype(np.uint8)

for imgType in imgTypes:
    original_img = cv2.imread(os.path.join(imgPath+imgPostfix, stoneName+"_"+imgType+imgPostfix+".bmp"))
    original_img = cv2.rotate(original_img, cv2.ROTATE_180)
    original_img = cv2.flip(original_img, 1)

    result_image = original_img.copy()

    imgavg = np.array([0,0,0]).astype(np.uint8)
    for i in range(3):
        imgavg[i] = np.average(original_img[:,:,i])

    brightnessRand = np.zeros((imgSize, imgSize, 3))

    if (min(imgavg) >= brightnessDisp):
        brightnessRand[:,:,0] = np.random.randint(-brightnessDisp, brightnessDisp, (imgSize, imgSize), np.int8)
    else:
        brightnessRand[:,:,0] = np.random.randint(-min(imgavg), brightnessDisp, (imgSize, imgSize), np.int8)

    brightnessRand[:,:,1], brightnessRand[:,:,2] = brightnessRand[:,:,0], brightnessRand[:,:,0]
    noise = (brightnessRand + imgavg).astype(np.uint8)

    result_image = (noise & highThickMask) | (result_image & (255 - highThickMask))
    result_image = (noise & mediumThickMask) | (result_image & (255 - mediumThickMask))
    result_image = (noise & lowThickMask) | (result_image & (255 - lowThickMask))

    result_image = cv2.rotate(result_image, cv2.ROTATE_180)
    result_image = cv2.flip(result_image, 1)
    cv2.imwrite(os.path.join(imgPath+imgPostfix, stoneName+"_"+imgType+imgPostfix+"_processed.bmp"), result_image)
