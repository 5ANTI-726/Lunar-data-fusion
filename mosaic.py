from PIL import Image, ImageFilter
from time import sleep
import numpy
import os

#Probable parent file: '/Users/santi/Desktop/Near infrared imaging, site 1'

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
def quality_estimation(parent_folder_path):
    #Input: Parent folder path string.
    #Output: Array with decimal estimations of image quality.

    quality_matrix = []
    dimensions = []
    dimensional_assignment = []
    for file in os.listdir(parent_folder_path):
        if file.endswith(".tif"):
            im = Image.open(parent_folder_path + '/' + file)

            width, height = im.size
            dimensions.append(width)
            dimensional_assignment.append(width)
            dead_pixel_count = 0
            fix_count = 0
            for x in range(0,width):
                for y in range(0,height):
                    if im.getpixel((x,y)) == 0:
                        dead_pixel_count += 1
                        interpolate, pixeltype = interpolation_criteria(im,x,y)
                        if interpolate:
                            fix_count += 1
            top = width*height-dead_pixel_count
            bottom = width*height-dead_pixel_count+fix_count
            if bottom != 0:
                quality_measure = top/bottom
            else:
                quality_measure = 0
            quality_matrix.append(quality_measure)
    histo = list(numpy.histogram(dimensions,range(1,500))[0])
    return quality_matrix, histo, dimensional_assignment
def mosaic_create(parent_folder_path,save_folder_path):
    #Input: Folder path and save path destination.
    #Output: None.

    print("Estimating quality of data...")
    #Estimate quality of data
    quality_matrix, histo, dimensional_assignment = quality_estimation(parent_folder_path)
    quality_order = list(numpy.argsort(quality_matrix))

    print("Building list of TIFF files")
    #Build list of TIFF file names
    tiff_list = []
    for file in os.listdir(parent_folder_path):
        if file.endswith(".tif"):
            tiff_list.append(file)

    print("Constructing mosaics...")
    #Go through every all possible dimensions.
    for dimension in range(1,499):
        #Begin creating image if there is at least one image of that dimension.
        if histo[dimension-1] > 0:
            #Create black canvas with appropriate dimensions.
            basis = Image.new('L', (dimension,dimension), color = 0)
            for index in quality_order:
                #In order of quality, and if they have correct dimensions, add to canvas.
                next_image = Image.open(parent_folder_path + '_processed/' + tiff_list[quality_order[index]][:-4] + '_processed.tif')
                d_next_image_x, d_next_image_y = next_image.size
                x_basis,y_basis = basis.size
                if d_next_image_x == dimension and d_next_image_x == d_next_image_y:
                    for x in range(0,dimension):
                        for y in range(0,dimension):
                            basis.putpixel((x,y), next_image.getpixel((x,y)))

            #Save file
            basis.save(save_folder_path + '/' + 'mosaic_' + str(dimension) + '.tif')
def folder_batch_mosaic(folders):
    for parent_folder_path in folders:
        #Get parent folder path. The blow comment is for requesting specific
        #source folder from user.
        #parent_folder_path = input("What folder are the images located in?")

        #Create storage folder with similar filename in grandparent directory
        destination = parent_folder_path + '_processed_mosaics'
        try:
            os.mkdir(destination)
            print("Made new '_processed_mosaics' folder")
        except:
            pass

        mosaic_create(parent_folder_path,destination)
folders = [
    '/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/Original:processed data and scripts/512_00N_30N_000_045/Near infrared imaging, site 5'
]
folder_batch_mosaic(folders)
