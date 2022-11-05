from PIL import Image, ImageFilter
from time import sleep
import os

#Probable parent file: '/Users/santi/Desktop/Near infrared imaging, site 1'

def over_80_filter(parent_folder_path,save_folder_path):
    #Input: Folder path and save path destination.
    #Output: None.

    for file in os.listdir(parent_folder_path):
        if file.endswith(".tif"):
            im = Image.open(parent_folder_path + '/' + file)
            width, height = im.size
            dead_pixel_count = 0
            for x in range(0,width):
                for y in range(0,height):
                    if im.getpixel((x,y)) == 0:
                        dead_pixel_count += 1

            completeness = (width*height-dead_pixel_count)/(width*height)
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
        destination = parent_folder_path + '_processed_over_80'
        try:
            os.mkdir(destination)
            print("Made new '_processed_over_80' folder")
        except:
            pass

        print('Examining parent folder: ' + parent_folder_path + '\n')
        over_80_filter(parent_folder_path,destination)
folders = [
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_00N_30N_000_045/Near infrared imaging, site 1_processed_mosaics',
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_00N_30N_000_045/Near infrared imaging, site 3_processed_mosaics',
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_00N_30N_000_045/Ultraviolet-visible imaging, site 1_processed_mosaics',
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_00N_30N_000_045/Ultraviolet-visible imaging, site 3_processed_mosaics',

'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_00N_30N_270_315/Near infrared imaging, site 2_processed_mosaics',
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_00N_30N_270_315/Ultraviolet-visible imaging, site 2_processed_mosaics',

'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_30S_00S_000_045/Near infrared imaging, site 4_processed_mosaics',
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Training-testing/512_30S_00S_000_045/Ultraviolet-visible imaging, site 4_processed_mosaics'
]
folder_batch_80filter(folders)
