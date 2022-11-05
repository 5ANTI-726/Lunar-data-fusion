from PIL import Image, ImageFilter
from time import sleep
import os

#Probable parent file: '/Users/santi/Desktop/Near infrared imaging, site 1'

def interpolation(image,x,y,type):
    #Input: Image object, integer coordinates, and classification of pixel in string.
    #Output: None.

    #The interpolation transformation is applied based on the pixel type.
    #image variable is an Image object

    if type == 'no edge':
        image.putpixel((x,y), round((image.getpixel((x,y+1)) + image.getpixel((x,y-1)) + image.getpixel((x+1,y)) + image.getpixel((x-1,y)))/4))
    elif type == 'top edge':
        image.putpixel((x,y), round((image.getpixel((x,y-1)) + image.getpixel((x+1,y)) + image.getpixel((x-1,y)))/3))
    elif type == 'bottom edge':
        image.putpixel((x,y), round((image.getpixel((x,y+1))+ image.getpixel((x+1,y)) + image.getpixel((x-1,y)))/3))
    elif type == 'right edge':
        image.putpixel((x,y), round((image.getpixel((x,y+1)) + image.getpixel((x,y-1)) + image.getpixel((x-1,y)))/3))
    elif type == 'left edge':
        image.putpixel((x,y), round((image.getpixel((x,y+1)) + image.getpixel((x,y-1)) + image.getpixel((x+1,y)))/3))
    elif type == 'corner 1':
        image.putpixel((x,y), round((image.getpixel((x,y-1)) + image.getpixel((x-1,y)))/2))
    elif type == 'corner 2':
        image.putpixel((x,y), round((image.getpixel((x,y-1)) + image.getpixel((x+1,y)))/2))
    elif type == 'corner 3':
        image.putpixel((x,y), round((image.getpixel((x,y+1)) + image.getpixel((x+1,y)))/2))
    elif type == 'corner 4':
        image.putpixel((x,y), round((image.getpixel((x,y+1)) + image.getpixel((x-1,y)))/2))
def interpolation_criteria(im,x,y):
    #Input: Image object and integer coordinates.
    #Output: Boolean value and classification of pixel in string.

    #Variable criteria for qualificatying for interpolation:
    width, height = im.size

    #Nonedge cases
    if x > 0 and x < width-1 and y > 0 and y < height-1:
        up = im.getpixel((x,y+1))
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(down == 0), int(left == 0), int(right == 0)])
        type = 'no edge'

    #Edge cases
    elif x == 0 and y > 0 and y < height-1:
        up = im.getpixel((x,y+1))
        down = im.getpixel((x,y-1))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(down == 0), int(right == 0)])
        type = 'left edge'
    elif y == 0 and x > 0 and x < width-1:
        up = im.getpixel((x,y+1))
        left = im.getpixel((x-1,y))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(left == 0), int(right == 0)])
        type = 'bottom edge'
    elif x == width-1 and y > 0 and y < height-1:
        up = im.getpixel((x,y+1))
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        dead_neighbors = sum([int(up == 0), int(down == 0), int(left == 0)])
        type = 'right edge'
    elif y == height-1 and x > 0 and x < width-1:
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(down == 0), int(left == 0), int(right == 0)])
        type = 'top edge'

    #Corner cases
    elif x == 0 and y == 0:
        up = im.getpixel((x,y+1))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(up == 0), int(right == 0)])
        type = 'corner 3'
    elif x == width-1 and y == 0:
        up = im.getpixel((x,y+1))
        left = im.getpixel((x-1,y))
        dead_neighbors = sum([int(up == 0), int(left == 0)])
        type = 'corner 4'
    elif x == 0 and y == height-1:
        down = im.getpixel((x,y-1))
        right = im.getpixel((x+1,y))
        dead_neighbors = sum([int(down == 0), int(right == 0)])
        type = 'corner 2'
    elif x == width-1 and y == height-1:
        down = im.getpixel((x,y-1))
        left = im.getpixel((x-1,y))
        dead_neighbors = sum([int(down == 0), int(left == 0)])
        type = 'corner 1'

    #Return whether it meets criteria (one allowable dead neighbor)
    if dead_neighbors <= 1:
        return (True,type)
    else:
        return (False,type)
def dead_pixel_fix(im):
    #Input: Image object.
    #Output: Image object with dead pixels fixed.

    #Identify dead pixels and interpolate value from neighbors according to the
    #criteria in last lines of interpolation_criteria() method and interpolation method
    #of interpolation() method.
    width, height = im.size
    dead_pixel_count = 0
    fix_count = 0
    for x in range(0,width):
        for y in range(0,height):
            if im.getpixel((x,y)) == 0:
                dead_pixel_count += 1
                interpolate, pixeltype = interpolation_criteria(im,x,y)
                if interpolate:
                    fix_count += 1
                    interpolation(im,x,y,pixeltype)
    print('This run of dead_pixel_fix() found ', dead_pixel_count, ' dead pixels and fixed ', fix_count, ' pixels.')
    return im
def pre_processing(parent_folder_path,save_folder_path,filename):
    #Input: File path to TIFF image, save folder, and file name.
    #Output: None.

    #We will open image_folder_path as an Image object, apply several
    #preprocessing techniques, and save the new image with the original
    #file name in the save_folder_path.

    im = Image.open(parent_folder_path + '/' + filename)
    #Apply dead_pixel_fix() three times
    processed = dead_pixel_fix(dead_pixel_fix(dead_pixel_fix(im)))

    #Save image
    processed.save(save_folder_path + '/' + filename[:-4] + '_processed.png')
def folder_batch_preprocessing(folders):
    for parent_folder_path in folders:
        #Get parent folder path. The comment below is for requesting specific
        #source folder from user.
        #parent_folder_path = input("What folder are the images located in?")

        #Create storage folder with similar filename in grandparent directory
        destination = parent_folder_path + '_processed_png'
        password = True
        try:
            os.mkdir(destination)
        except:
            confirmation = input('Delete old ..."_processed" directory?').lower()
            if confirmation == 'yes' or confirmation == 'ys' or confirmation == 'y' or confirmation == 'es':
                os.rmdir(destination)
                os.mkdir(destination)
            else:
                password = False
        if password:
            #Progress estimation
            total_files = 0
            for file in os.listdir(parent_folder_path):
                if file.endswith(".tif"):
                    total_files += 1
            print('Images to process: ' + str(total_files))
            print('Progress: \n')

            #Batch processing
            file_count = 0
            for file in os.listdir(parent_folder_path):
                if file.endswith(".tif"):
                    print(str(round(100*file_count/total_files)) + ' %')
                    pre_processing(parent_folder_path,destination,file)
                    file_count += 1

folders = [
'/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Original:processed data and scripts/512_00N_30N_000_045/Ultraviolet-visible imaging, site 1'
]
folder_batch_preprocessing(folders)
