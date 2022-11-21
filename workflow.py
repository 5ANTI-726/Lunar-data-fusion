from PIL import Image, ImageFilter
from playsound import playsound
import os.path as path
from time import sleep
import numpy
import os

#Probable parent file: '/Users/santi/Desktop/Near infrared imaging, site 1'

def alarm(value):
    if value:
        playsound('siren.mp3')

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
        corrected = ''
        for i in range(0,len(folder)):
            if folder[i] != '\\':
                if i == (len(folders) - 1):
                    if folder[i] != ' ':
                        corrected = corrected + folder[i]
                else:
                    corrected = corrected + folder[i]
        c_folders.append(corrected)

    #Return the final array of folders, split as different elements, without backslashes.
    return c_folders

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

def mosaic_create(origin, replace_mosaics):
    #Input: Folder path and save path destination.
    #Output: None.

    def quality_estimation(parent_folder_path):
        #Input: Parent folder path string.
        #Output: Array with decimal estimations of image quality.

        quality_matrix = []
        for file in os.listdir(parent_folder_path):
            if file.endswith(".tif") or file.endswith(".png"):
                im = Image.open(parent_folder_path + '/' + file)

                width, height = im.size
                dead_pixel_count = 0
                fix_count = 0
                for x in range(0,width):
                    for y in range(0,height):
                        if im.getpixel((x,y)) <= 10:
                            dead_pixel_count += 1
                            interpolate, pixeltype = interpolation_criteria(im,x,y)
                            if interpolate:
                                fix_count += 1
                top = width*height - dead_pixel_count + fix_count
                bottom = width*height
                if bottom != 0:
                    quality_measure = top/bottom
                else:
                    quality_measure = 0
                quality_matrix.append(quality_measure)
        return quality_matrix

    def contrast(source):
        #Input: Image object.
        #Output: Image object with contrast maximized.


        def mb(floor, ceiling):
            low = 2
            high = 256
            #print("Lowest: " + str(floor))
            #print("Highest: " + str(ceiling))
            b = (high*floor - low*ceiling)/(floor - ceiling)
            m = (low - b)/floor
            return m, b

        def acd(floor, ceiling, register):
            averages = []
            a = 0
            c = 0
            d = 0
            q = ceiling - floor
            for p in range(116, 190):
                a = (p*q - ceiling + 256*floor - 128*255)/(q*(128^2+ceiling*floor) - 128*(ceiling^2 + floor^2))
                c = 255/q - a*(ceiling + floor)
                d = 1 - a*ceiling**2 - c*floor
                temp = []
                for i in range(0,len(register)):
                    x = register[i]
                    temp.append(quadratic_map(a, c, d, x))
                average = sum(temp)/len(temp)
                averages.append(abs(average - 100))

            p = averages.index(min(averages)) + 116
            #print("P: " + str(p))
            a = (p*q - ceiling + 256*floor - 128*255)/(q*(128^2+ceiling*floor) - 128*(ceiling^2 + floor^2))
            c = 255/q - a*(ceiling + floor)
            d = 1 - a*ceiling**2 - c*floor

            return a, c, d

        def linear_map(m, b, x):
            y = m*x + b
            return int(y)

        def quadratic_map(a, c, d, x):
            y = a*x**2 + c*x + d
            return int(y)

        #Get limits for calculating the new pixel values.
        register = []
        x_limit, y_limit = source.size
        for i in range(0, x_limit):
            for j in range(0, y_limit):
                pixel = source.getpixel((i, j))
                if pixel > 3:
                    register.append(pixel)

        #Create the brightness/contrast options if the image is not all black
        if len(register) != 0:
            floor = min(register)
            ceiling = max(register)
            average = sum(register)/len(register)
            #Image transformation diagnostic tools
            #print("Average: " + str(average))
            #print("Ceiling: " + str(ceiling))
            #print("Floor: " + str(floor))
            #source.show()

            #Quasi-linear mapping option
            m, b = mb(floor, ceiling)
            sink_1 = Image.new(source.mode, (x_limit, y_limit))
            for i in range(0, x_limit):
                for j in range(0, y_limit):
                    pixel = source.getpixel((i, j))
                    if pixel * (128/average) <= 256:
                        pixel = int(source.getpixel((i, j)) * (128/average))
                        sink_1.putpixel( (i, j), pixel )
                    else:
                        sink_1.putpixel( (i, j), linear_map(m, b, pixel) )

            #Linear mapping option
            sink_2 = Image.new(source.mode, (x_limit, y_limit))
            for i in range(0, x_limit):
                for j in range(0, y_limit):
                    pixel = source.getpixel((i, j))
                    sink_2.putpixel( (i, j), linear_map(m, b, pixel) )

            #Quadratic mapping option
            a, c, d = acd(floor, ceiling, register)
            sink_3 = Image.new(source.mode, (x_limit, y_limit))
            for i in range(0, x_limit):
                for j in range(0, y_limit):
                    pixel = source.getpixel((i, j))
                    sink_3.putpixel( (i, j), quadratic_map(a, c, d, pixel) )

            return sink_1, sink_2, sink_3
        #If the register is empty, return the original image
        return source, source, source

    for item in os.listdir(origin):
        if item == "Original data and scripts":
            #print(origin + item)
            item += "/"
            for area in  os.listdir(origin + item):
                area += "/"
                if area[0] != ".":
                    for site_data in os.listdir(origin + item + area):
                        site_data += "/"
                        if site_data[-11:] == "_processed/" and not os.exists(origin + item + area + site_data + "mosaic_1.png"):
                            parent_directory = origin + item + area + site_data
                            destination_directory = parent_directory

                            print("Constructing mosaic for " + site_data)

                            #Mosaic creation variables# DO NOT TOUCH
                            #Estimating the quality of every image file in the folder
                            quality_matrix = quality_estimation(parent_directory)
                            quality_order = list(numpy.argsort(quality_matrix))
                            tiff_list = []
                            #Mosaic creation variables# DO NOT TOUCH

                            for file in os.listdir(parent_directory):
                                if file.endswith(".tif") or file.endswith(".png"):
                                    tiff_list.append(file)

                            basis_1 = Image.new('L', (training_image_size,training_image_size), color = 0)
                            basis_2 = Image.new('L', (training_image_size,training_image_size), color = 0)
                            basis_3 = Image.new('L', (training_image_size,training_image_size), color = 0)

                            for index in quality_order:
                                #Add to canvas in order of quality.
                                next_image_1, next_image_2, next_image_3 = contrast( Image.open( parent_directory + tiff_list[quality_order[index]] ) .resize((training_image_size,training_image_size)))

                                for x in range(0,training_image_size):
                                    for y in range(0,training_image_size):
                                        new_pixel_1 = next_image_1.getpixel((x,y))
                                        new_pixel_2 = next_image_2.getpixel((x,y))
                                        new_pixel_3 = next_image_3.getpixel((x,y))
                                        if new_pixel_1 > 10:
                                            basis_1.putpixel((x,y), new_pixel_1)
                                        if new_pixel_2 > 10:
                                            basis_2.putpixel((x,y), new_pixel_2)
                                        if new_pixel_3 > 10:
                                            basis_3.putpixel((x,y), new_pixel_3)

                            if replace_mosaics:
                                os.remove(destination_directory + 'mosaic_1.png')
                                os.remove(destination_directory + 'mosaic_2.png')
                                os.remove(destination_directory + 'mosaic_3.png')

                            #Save first mosaic option
                            basis_1.save(destination_directory + 'mosaic_1.png')
                            #Save second mosaic option
                            basis_2.save(destination_directory + 'mosaic_2.png')
                            #Save third mosaic option
                            basis_3.save(destination_directory + 'mosaic_3.png')

def over80_filter(origin):
    #Input: The project's file; the "Original data and scripts" file has to be
    #an immediate child.
    #Output: None.

    ###FROM DIFFERENT METHOD. EVENTUALLY UPDATE###Navigate through all folders within the "Original data and scripts" folder
    #, looking for folders that start with "Near" or "Ultra". For each of these,
    #an equivalent sibling folder is created with the additional termination
    #"_processed".

    for item in os.listdir(origin):
        if item == "Original data and scripts":
            #print(origin + item)
            item += "/"
            for area in  os.listdir(origin + item):
                area += "/"
                if area[0] != ".":
                    for site_data in os.listdir(origin + item + area):
                        site_data += "/"
                        if site_data[-11:] == "_processed/":
                            parent_directory = origin + item + area + site_data
                            destination_directory = parent_directory[0:-1] + "_over80/"

                            #Detect if folder already exists. If true, skip.
                            if not path.isdir(destination_directory):
                                os.mkdir(destination_directory)

                                print("Filtering incomplete images in " + site_data)
                                for file in os.listdir(parent_directory):
                                    if file.endswith(".tif") or file.endswith(".png"):

                                        im = Image.open(parent_directory + '/' + file)
                                        width, height = im.size

                                        dead_pixel_count = 0
                                        for x in range(0,width):
                                            for y in range(0,height):
                                                if im.getpixel((x,y)) == 0:
                                                    dead_pixel_count += 1

                                        completeness = (width*height - dead_pixel_count) / (width*height)
                                        if completeness >= 0.8:
                                            im.resize((training_image_size,training_image_size)).save(destination_directory + file[:-4] + '_over80.png')

def preprocessing(origin):
    #Input: The project's file; the "Original data and scripts" file has to be
    #an immediate child.
    #Output: None.

    #Navigate through all folders within the "Original data and scripts" folder
    #, looking for folders that start with "Near" or "Ultra". For each of these,
    #an equivalent sibling folder is created with the additional termination
    #"_processed".

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
        #You can suppress satistics on dead pixels for each run.
        #print('This run of dead_pixel_fix() found ', dead_pixel_count, ' dead pixels and fixed ', fix_count, ' pixels.')
        return im

    for item in os.listdir(origin):
        if item == "Original data and scripts":
            #print(origin + item)
            item += "/"
            for area in  os.listdir(origin + item):
                area += "/"
                if area[0] != ".":
                    for site_data in os.listdir(origin + item + area):
                        site_data += "/"
                        if (site_data[0:4] == "Near" or site_data[0:5] == "Ultra") and site_data.find("_") == -1:
                            parent_directory = origin + item + area + site_data
                            destination_directory = parent_directory[0:-1] + "_processed/"
                            prefix = ''
                            if site_data[0:4] == "Near":
                                prefix = "NIR"
                            elif site_data[0:5] == "Ultra":
                                prefix = "UVV"


                            #Detect if folder already exists. If true, skip.
                            if not path.isdir(destination_directory):
                                os.mkdir(destination_directory)
                                print("Preprocessing " + site_data)
                                for file in os.listdir(parent_directory):
                                    if file.endswith(".tif") or file.endswith(".png"):
                                        im = Image.open(parent_directory + file)
                                        processed = dead_pixel_fix(dead_pixel_fix(dead_pixel_fix(dead_pixel_fix(im))))
                                        processed.resize((training_image_size,training_image_size)).save(destination_directory + '/' + prefix + file[:-4] + '_processed.png')


origin = "/Users/santi/Documents/Semestre 1-2-3/MR3038- Estancia de investigación/Proyectos/Data fusion in lunar environment/"
training_image_size = 420
alarmV = True
replace_mosaics = False


print("Begin preprocessing images by removing dead pixels and maximizing contrast...")
preprocessing(origin)
alarm(alarmV)

print("")
print("Begin creating mosaics of site data...")
mosaic_create(origin, replace_mosaics)
alarm(alarmV)

print("")
print("Begin filtering out images with less than 80% content...")
over80_filter(origin)
alarm(alarmV)
