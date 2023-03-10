from PIL import Image
from math import sqrt, floor, ceil
import binascii

COLORS = [(0,0,0), (255,255,255), (0,250, 0), (0,0,255), (255,0, 0), (255,255,0), (255, 170, 0)]
#SCREEN_WIDTH = 230
#SCREEN_HEIGHT = 70
SCREEN_WIDTH = 230
SCREEN_HEIGHT = 230

def hex2bin(HexInputStr, outFormat=4):
    '''This function accepts the following two args.
    1) A Hex number as input string and
    2) Optional int value that selects the desired Output format(int value 8 for byte and 4 for nibble [default])
    The function returns binary equivalent value on the first arg.'''
    int_value = int(HexInputStr, 16)
    if(outFormat == 8):
        output_length = 8 * ((len(HexInputStr) + 1 ) // 2) # Byte length output i.e input A is printed as 00001010
    else:
        output_length = (len(HexInputStr)) * 4 # Nibble length output i.e input A is printed as 1010


    bin_value = f'{int_value:0{output_length}b}' # new style
    return bin_value

def getClosestColor(c, colors):
    """ Returns closest color in 'colors' to target 'c'. All colors are represented
        as RGB tuples.\n
        Method runs in O(N) time, where 'N' is the size of 'colors'. \n
        PARAMETERS:\n
        \tc : Target color to be approximated, formatted as an RGB tuple\n
        \tcolors : a list containing all valid color options, each formatted as an RGB tuple\n
        RETURNS:\n
        \tnearest: the closest avaliable RGB tuple to 'c' contained within 'colors'
    """
    nearest = (0, 0, 0)# always overridden in first iteration of for loop
    minDiff = 1000     # initialised to be greater than all possible differences
    for col in colors:
        diff = sqrt((col[0]-c[0])**2 + (col[1]-c[1])**2 + (col[2]-c[2])**2)
        if(diff < minDiff):
            minDiff = diff
            nearest = col
    return nearest

def clamp(x):
    """ Clamps a given number between 0 and 255.\n
        PARAMETERS:\n
        \tx: Input number to be clamped\n
        RETURNS:\n
        \tclamped: The value of 'x' clamped between 0 and 255
    """
    return max(0, min(255, x))

def applyErr(tup, err, factor):
    """ Adds a percentage of quantization error to specified tuple\n
        PARAMETERS:\n
        \ttup: Three (3) dimensional tuple containing data\n
        \terr: Three (3) dimensional tuple containing quantization error\n
        \tfactor: Percentage of 'err' to be applied to 'tup'\n
        RETURNS:\n
        \t(r,g,b): Three (3) dimensional tuple containing the input data with
            specified amount of error added. Values are rounded and clamped
            between 0 and 255
    """
    r = clamp(int(tup[0] + err[0]*factor))
    g = clamp(int(tup[1] + err[1]*factor))
    b = clamp(int(tup[2] + err[2]*factor))
    return r, g, b

def ditherImage(target, colors = None, colorstops = None, saveOutput = True, outputType = "", showFinal = True):
    #attempt to open target image
    try:
        im = Image.open(target)
        im = im.convert("RGB")
        mode, size = im.mode, im.size
        width, height = size[0], size[1]
        pix = list(im.getdata())
        im.close()
    except:
        print("Oh noes! An I/O error! :O")
        return


    #lambda expression to flatten x,y location
    index = lambda x, y: x + y * width
    #Floyd-Steinberg dithering. https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering
    for y in range(int(height)):
        for x in range(int(width)):
            old = pix[index(x, y)]
            new = getClosestColor(old, COLORS)
            pix[index(x,y)] = new
            #calculates difference in r/g/b channels
            err = (old[0]-new[0], old[1]-new[1], old[2]-new[2])

            if (x != width-1):
                pix[index(x+1,y)] = applyErr(pix[index(x+1,y)], err, 7/16)
            if (y != height-1):
                pix[index(x,y+1)] = applyErr(pix[index(x,y+1)], err, 5/16)
                if (x > 0):
                    pix[index(x-1,y+1)] = applyErr(pix[index(x-1,y+1)], err, 3/16)
                if (x != width-1):
                    pix[index(x+1,y+1)] = applyErr(pix[index(x+1,y+1)], err, 1/16)

    newIm = Image.new(mode, size)
    newIm.putdata(pix)
    return newIm

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

def rgb_epaper_matcher(rgb):
    COLORS = [(0,0,0), (255,255,255), (0,250,0), (0,0,255), (255,0, 0), (255,255,0), (255, 170,0)]


def image_to_e_paper_hex_array(image):
    pix = image.load()
    hex_array = []
    for y in range(image.height):
        for x in range(0, image.width - 1, 2):
            hex_nibble1 = hex2bin(str(COLORS.index(pix[x,y])))
            hex_nibble2 = hex2bin(str(COLORS.index(pix[x + 1,y])))
            hex_array.append(hex(int(hex_nibble1 + hex_nibble2, 2)))
    return hex_array

def hex_array_to_c_bytes_array(hex_array):
    c_bytes_array = "["
    for hex in hex_array:
        c_bytes_array = c_bytes_array + hex + ",\n"
    c_bytes_array = c_bytes_array[:len(c_bytes_array) - 1] + "]"
    return c_bytes_array


if __name__ == "__main__":
    im = Image.open("walmart-2.png")
    im = im.convert("RGB")
    im.thumbnail(size=(SCREEN_WIDTH,SCREEN_HEIGHT))
    im.save('walmart-promotion-scaled.jpg', optimize=True)
    im.close()
    dith_img = ditherImage("walmart-promotion-scaled.jpg", outputType="png")
    add_width = (SCREEN_WIDTH - dith_img.width)/2
    add_height = (SCREEN_HEIGHT - dith_img.height)/2

    final_img = add_margin(dith_img, floor(add_height), floor(add_width), ceil(add_height), floor(add_width), (255, 255, 255)) 
    hex_array = image_to_e_paper_hex_array(dith_img)
    print(hex_array_to_c_bytes_array(hex_array))
    print(len(hex_array))
    dith_img.show()
    print(dith_img.width)
    print(dith_img.height)
    """
    print(dith_img.width)
    print(dith_img.height)

    #dith_img = ditherImage("epaper.jpg", outputType="png")
    final_img.save("epaper_dither.png")    
    final_img.show()
    """