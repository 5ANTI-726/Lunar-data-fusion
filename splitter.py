from PIL import Image, ImageFilter
from playsound import playsound
import os.path as path
from time import sleep
import math
import os

def id_site(string):
    return string[string.find('site') + 5: string.find('/')]

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

def cutter(source, target):
    #Input: Parent folder path, the filename of the image of interest, and
    #the number of output images.
    #Output: Array with the 'target' number of output images.

    source = source.resize((420, 420))
    tsqrt = int(math.sqrt(target))
    minisize = int(420/tsqrt)

    output_1 = Image.new('L', (minisize,minisize), color = 0)
    output_2 = Image.new('L', (minisize,minisize), color = 0)
    output_3 = Image.new('L', (minisize,minisize), color = 0)
    output_4 = Image.new('L', (minisize,minisize), color = 0)
    output_5 = Image.new('L', (minisize,minisize), color = 0)
    output_6 = Image.new('L', (minisize,minisize), color = 0)
    output_7 = Image.new('L', (minisize,minisize), color = 0)
    output_8 = Image.new('L', (minisize,minisize), color = 0)
    output_9 = Image.new('L', (minisize,minisize), color = 0)

    meta = [output_1, output_2, output_3, output_4, output_5, output_6, output_7, output_8, output_9]

    for l in range(0,tsqrt):
        for i in range(0,tsqrt):
            im = Image.new(source.mode, (minisize, minisize))
            for j in range(0,minisize):
                for k in range(0,minisize):
                    #DEBUGGING
                    #print(str((l, i, j, k)))
                    #print(str((i*minisize + j, l*minisize + k)))
                    meta[tsqrt*l + i].putpixel((j,k), source.getpixel((i*minisize + j, l*minisize + k)))
    return meta

def split(origin, split_num, destination_parent):
    #Input: Source folder, the number of images to create, the folder to store
    #the images in, and an index for the amount of folders processed so far.
    #Output: None.

    #This method calls the cutting method on each image within the site and
    #saves the resulting images according to their output order within separate folders.
    #This requires that the images corresponding to the same subareas (i.e. quadrants)
    #come out with the same index each time and are saved in the correct 'Set #' file.

    for item in os.listdir(origin):
        if item == "Preselected data":
            #print(origin + item)
            item += "/"
            if item[0] != ".":
                for site_data in  os.listdir(origin + item):
                    #print(origin + item + site_data)
                    site_data += "/"
                    if site_data[0] != ".":
                        site_num = int(id_site(site_data))
                        parent_directory = origin + item + site_data
                        destination_directory = destination_parent + '/Set '

                        print("Collimating laser beams in " + site_data)
                        for file in os.listdir(parent_directory):
                            if file.endswith(".tif") or file.endswith(".png"):
                                im = Image.open(parent_directory + file)
                                meta = cutter(im, split_num)
                                for i in range(0,split_num):
                                    set_path = destination_directory + str(split_num*(site_num-1) + i)
                                    if not path.isdir(set_path + '/'):
                                        os.mkdir(set_path + '/')
                                    meta[i].save(set_path + '/' + file[:-4] + '_' + str(i) + '.png')

test_train_folder = '/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Split data'
origin = "/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/"

split(origin , 4, test_train_folder)
