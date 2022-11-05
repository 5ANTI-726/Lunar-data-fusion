from PIL import Image, ImageFilter
from time import sleep
import math
import os

def id_site(string):
    return string[string.find('site') + 5]

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

def cutter(parent_folder_path, image, target):
    #Input: Parent folder path, the filename of the image of interest, and
    #the number of output images.
    #Output: Tuple with the 'target' number of output images.

    #Split source 'image' in the 'parent_folder_path' into 'target' number of sub images.

    tsqrt = int(math.sqrt(target))
    minisize = int(420/tsqrt)

    #Resize everything into 420 because the numbers 1 through 7 are factors.
    source = Image.open(parent_folder_path + '/' + image).resize((420,420))

    output = []

    for l in range(0,tsqrt):
        for i in range(0,tsqrt):
            im = Image.new(source.mode, (minisize, minisize))
            for j in range(0,minisize):
                for k in range(0,minisize):
                    #DEBUGGING
                    #print(str((i, j, j, k)))
                    #print(str((i*minisize + j, l*minisize + k)))
                    im.putpixel((j,k), source.getpixel((i*minisize + j, l*minisize + k)))
            output.append(im)

    return output

def split(parent_folder_path, split_num, test_train_folder, folder_index):
    #Input: Source folder, the number of images to create, the folder to store
    #the images in, and an index for the amount of folders processed so far.
    #Output: None.

    #This method calls the cutting method on each image within the site and
    #saves the resulting images according to their output order within separate folders.
    #This requires that the images corresponding to the same subareas (i.e. quadrants)
    #come out with the same index each time and are saved in the correct 'Set #' file.
    print(parent_folder_path)
    site  = id_site(parent_folder_path)

    for image_name in os.listdir(parent_folder_path):
        if image_name.endswith(".tif") or image_name.endswith(".png"):
            #The cutter method returns a tuple storing all iamges created from
            #the Image object created from 'image_name'.
            images = cutter(parent_folder_path, image_name, split_num)
            for i in range(0, split_num):
                set = "/Set " + str(folder_index*split_num + i) + "/"
                new_file_name = str(test_train_folder + set + image_name[:-4] + '_sub_' + str(i) + image_name[-4:])
                try:
                    os.mkdir(test_train_folder + '/Set ' + str(folder_index*split_num + i))
                except:
                    print("Set parent file already created.")
                images[i].save(new_file_name)

def folder_batch_preprocessing(folders, split_num, test_train_folder):
    #Input: List of folders, number of images to create, and the folder where we
    #will store test/train images (not sorted into the two categories yet).
    #Output: None.

    #This method only calls for the cutting of each image in a site.
    for i in range(0,len(folders)):
        split(folders[i], split_num, test_train_folder, i)

test_train_folder = '/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Split data'
folder_batch_preprocessing(getfolders(), 4, test_train_folder)
