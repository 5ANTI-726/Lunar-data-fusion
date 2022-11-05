from PIL import Image, ImageFilter
from time import sleep
import os

#Probable parent file: '/Users/santi/Desktop/Near infrared imaging, site 1'
def getfolders():
    #Input: None.
    #Output: Array of formatted folder paths.

    #This method is a UI with text processing capabilities. It will request,
    #clean, and return folder paths.
    folders = []

    #Get the number of elements in the folder array.
    numberfolders = int(input('How many parent folders do you want processed?'))
    for i in range(0,numberfolders):
        if i == 0:
            folders.append(input('Drop folder to process'))
        else:
            folders.append(input('Drop next folder to process'))

    #Remove the any backslashes added by the terminal to blank spaces, since
    #these are not required/don't work as file paths when using Pillow.
    c_folders = []
    for folder in folders:
        corrected = ""
        for i in range(0,len(folder)):
            if folder[i] != "\\":
                corrected = corrected + folder[i]
        c_folders.append(corrected)

    #Return the final array of folders, split as different elements, without backslashes.
    return c_folders

    return c_folders
def over_80_filter(parent_folder_path,save_folder_path):
    #Input: Folder path and save path destination.
    #Output: None.

    for file in os.listdir(parent_folder_path):
        if file.endswith(".tif"):
            im = Image.open(parent_folder_path + '/' + file)
            width, height = im.size

            #Only continue if the image is a square to allow for upscaling later
            #without aspect ration changes.
            if width == height:
                dead_pixel_count = 0
                for x in range(0,width):
                    for y in range(0,height):
                        if im.getpixel((x,y)) == 0:
                            dead_pixel_count += 1

                completeness = (width*height - dead_pixel_count) / (width*height)
                if completeness >= 0.8:
                    print('File: ' + file[-4:] + '_over_80' + '.tif' + '\n')
                    print(str(100*completeness) + '% complete' + '\n')
                    im.save(save_folder_path + '/' + file[:-4] + '_over_80' + '.tif')
def folder_batch_80filter(folders):
    for parent_folder_path in folders:
        #Get parent folder path. The blow comment is for requesting specific
        #source folder from user.
        #parent_folder_path = input("What folder are the images located in?")

        #Create storage folder with similar filename in grandparent directory
        destination = parent_folder_path + '_over_80'
        try:
            os.mkdir(destination)
            print("Made new '_over_80' folder")
        except:
            pass

        print('Examining parent folder: ' + parent_folder_path + '\n')
        over_80_filter(parent_folder_path,destination)

folder_batch_80filter(getfolders())
