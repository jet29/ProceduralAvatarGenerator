import cv2 as cv
import numpy as np
import random
import os
from itertools import combinations

TRAIT_DIRS = [
    "Background",
    "Body",
    "Head",
    "Mouth",
    "Eyes",
    "Hair"
]

def mergeLayers(layerBottom,layerTop):
    # grab the image dimensions
    h = layerTop.shape[0]
    w = layerTop.shape[1]
    
    # transparencyTreshold = 200

    # # loop over the image, pixel by pixel
    # for y in range(0, h):
    #     for x in range(0, w):
    #         #work by layers
    #         if layerTop[y,x,3] >= transparencyTreshold:
    #             layerBottom[y,x] = layerTop[y,x]

    # loop over the image, pixel by pixel
    for y in range(0, h):
        for x in range(0, w):
            if layerTop[y,x,3] == 0: continue
            #work by layers
            norm_bottom = layerBottom[y,x]/255.0
            norm_top = layerTop[y,x]/255.0
            final_color = (norm_top * norm_top[3]) + (norm_bottom * (1-norm_top[3]))
            layerBottom[y,x] = final_color*255
                
            
    # return the thresholded image
    return layerBottom


def RGBAToRGB(img):
    alpha_channel = img[:,:,3]
    rgb_channels = img[:,:,:3]

    # Alpha factor
    alpha_factor = alpha_channel[:,:,np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor,alpha_factor,alpha_factor), axis=2)

    # Get the base
    base = rgb_channels.astype(np.float32) * alpha_factor
    return base.astype(np.uint8)

def loadPNG(url):
    img = cv.imread(url, cv.IMREAD_UNCHANGED)
    return img
    
def numToBitArray(num):
    num_bits = len(TRAIT_DIRS)
    bits = [(num >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]
    return bits

# get a random avatar with the traits id (id is just a mask of what traits will be present)
def getAvatar(id):

    avatarImage = None

    bits = numToBitArray(id)
    for position, bit in enumerate(bits):
        #this mean that the trait is activated
        if bit == 1:
            #search the dir base for the trait
            traitName = TRAIT_DIRS[position]
            traitDir = "./" + traitName + "/" + traitName
            randomTrait = random.randint(1,3)
            finalDir = traitDir + str(randomTrait) + ".png"

            traitImage = loadPNG(finalDir)

            if avatarImage is None:
                avatarImage = traitImage
            else:
                avatarImage = mergeLayers(avatarImage,traitImage)


    return RGBAToRGB(avatarImage)

# get the files in a folder as string in a list
def getDirFiles(dir):
    file_list = []
    for filename in os.listdir(dir):
        f = os.path.join(dir, filename)
        # checking if it is a file
        if os.path.isfile(f):
            file_list.append(f)
    return file_list

#generate all possible combinations of avatars
def generateAllAvatars():

    file_list = []
    for dir in TRAIT_DIRS:
        file_list += getDirFiles(dir)

    comb = combinations(file_list,len(TRAIT_DIRS))

    comb_list = list(comb)

    #remove combinations from the same folder
    comb_list_final = []
    for i in comb_list:
        splitted = []
        for file in i:
            splitted.append(file.split("\\")[0])

        #if there is no duplicated element in array
        if len(splitted) == len(set(splitted)):
            comb_list_final.append(i)

    # START THE CREATION OF ALL POSSIBLE AVATARS

    #count the number of avatars created
    counter = 0

    #move the current working directory to the destiny folder
    if(os.path.isdir("./all_avatars")):
        #move to the directory
        os.chdir("./all_avatars")
    else:
        #create and move to the directory
        os.mkdir("./all_avatars")
        os.chdir("./all_avatars")

    for avatarTraits in comb_list_final:

        print("creating avatar number: " + str(counter) + "...")

        avatarImage = None
        #create avatar base on the combination
        for dir in avatarTraits:
            final_dir = "..\\" + dir
            traitImage = loadPNG(final_dir)

            if avatarImage is None:
                avatarImage = traitImage
            else:
                avatarImage = mergeLayers(avatarImage,traitImage)

        #convert image to RGB
        RGBAToRGB(avatarImage)

        img_name = "avatar" + str(counter) + ".jpg"
        #save the image
        cv.imwrite(img_name, avatarImage)

        #increase the counter
        counter+=1

    return True
            
def main():
    # get the avatar with two traits (glasses and hat)
    # avatar = getAvatar(0b1111)
    # cv.imshow("test",avatar)

    generateAllAvatars()

    cv.waitKey(0)
    

if __name__ == "__main__":
    # execute only if run as a script
    main()