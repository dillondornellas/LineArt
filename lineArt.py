import math
import time
import os
import cv2
import numpy as np
from skimage.draw import line

def spacer(height, width):
    maxSpace = min(height//10, width//10)
    verticalSpace = int(height / maxSpace)
    horizontalSpace = int(width / maxSpace)
    return maxSpace, verticalSpace, horizontalSpace

def top_left(img, line_count, y_inc, x_inc):
    y = 0
    x = img.shape[1] #width
    for lines in range(line_count):
        start = (0,y)
        end = (x,0)
        cv2.line(img, (start), end, (0,0,0), 1)
        y += y_inc
        x -= x_inc
    return img

def top_right(img, line_count, y_inc, x_inc):
    y = img.shape[0] #height
    x = img.shape[1] #width
    for lines in range(line_count):
        start = (width,y)
        end = (x,0)
        cv2.line(crop_img, (start), end, (0,0,0), 1)
        y -= y_inc
        x -= x_inc
    return img

def bot_right(img, line_count, y_inc, x_inc):
    y = img.shape[0] #height
    x = 0
    for lines in range(line_count):
        start = (img.shape[1],y)
        end = (x,img.shape[0])
        cv2.line(crop_img, (start), end, (0,0,0), 1)
        y -= y_inc
        x += x_inc
    return img

def bot_left(img, line_count, y_inc, x_inc):
    y = 0
    x = 0
    for lines in range(line_count):
        start = (0,y)
        end = (x,img.shape[0])
        cv2.line(crop_img, (start), end, (0,0,0), 1)
        y += y_inc
        x += x_inc
    return img

def corner_pop(node_list):
    try:
        node_list.remove((0,0))
    except:
        None
    try:
        node_list.remove((width,0))
    except:
        None
    try:
        node_list.remove((0,height))
    except:
        None
    try:
        node_list.remove((width,height))
    except:
        None
    return node_list

def darkest_line(imgage, start, frame_side):
    best_line = math.inf
    line_strength = 0
    for index, node in enumerate(frame_side):
        # if index % 2 == 0:
        discrete_line = list(zip(*line(*start, *node)))
        for pixel in discrete_line:
            # sum the pixel values along the line
            try:
                               # image[HEIGHT][WIDTH]
                               # image[y][x]                    
                line_strength += imgage[pixel[1]][pixel[0]]
            except:
                None
        #averge pixel strength
        line_strength /= len(discrete_line)
        #print(int(line_strength), node, len(discrete_line))
        if line_strength < best_line:
            best_node = node
            best_line = line_strength
    return best_line, best_node

########## OPTIONS ##########
#total lines requested      #                  
lines2draw = 900            #      
#create a video             #     
createVideo = False         #         
#node pixel spacing         #         
pixels = 10                 # 
#initialize starting point  #                  
start = (0,0)               #
#############################

# load in img
img1 = cv2.imread('face.jpg', cv2.IMREAD_GRAYSCALE) 
base_img = cv2.imread('face.jpg', 3) 

# crop img to face
crop_img = img1[0:570, 300:750]
crop_base = base_img[0:570, 300:750]

height = crop_img.shape[0]
width = crop_img.shape[1]

# create canvas
line_img = np.ones([height,width,3], np.uint8) *255
line_img2 = np.ones([height,width,3], np.uint8) *255

# create a list of nodes along the frame every 10 pixels
y_nodes = list(range(0,height+1,pixels))
x_nodes = list(range(0,width+1,pixels))

# create a list of all nodes along the frame
top = []
bottom = []
left = []
right = []
for x in x_nodes:
    top.append((x, 0))
    bottom.append((x, height))
for y in y_nodes:
    left.append((0, y))
    right.append((width, y))

# remove all corner nodes --> TO AVOID FLAT LINES ALONG BASES
top = corner_pop(top)
bottom = corner_pop(bottom)
left = corner_pop(left)
right = corner_pop(right)

#region TestRegion

#Testing Line Art functions
#line_count, y_inc, x_inc = spacer(height,width)
#new_img = bot_left(crop_img, line_count, y_inc, x_inc)
#new_img = bot_right(crop_img, line_count, y_inc, x_inc)
#new_img = top_left(crop_img, line_count, y_inc, x_inc)
#new_img = top_right(crop_img, line_count, y_inc, x_inc)

#endregion

node_sequence = []
index = 0
for line_count in range(lines2draw):
    node_sequence.append(start)
    
    # Not used since corner nodes have been removed
    # (0,0) corner case
    if start == (0,0):
        best_line = math.inf

        bot_line, bot_node = darkest_line(crop_img, start, bottom)
        if bot_line < best_line:
            best_node = bot_node
            best_line = bot_line

        right_line, right_node = darkest_line(crop_img, start, right)
        if right_line < best_line:
            best_node = right_node
            best_line = right_line
    # (width,0) corner case
    elif start == (width,0):
        best_line = math.inf

        bot_line, bot_node = darkest_line(crop_img, start, bottom)
        if bot_line < best_line:
            best_node = bot_node
            best_line = bot_line

        left_line, left_node = darkest_line(crop_img, start, left)
        if left_line < best_line:
            best_node = left_node
            best_line = left_line
    # (width,height) corner case
    elif start == (width,height):
        best_line = math.inf

        top_line, top_node = darkest_line(crop_img, start, top)
        if top_line < best_line:
            best_node = top_node
            best_line = top_line

        left_line, left_node = darkest_line(crop_img, start, left)
        if left_line < best_line:
            best_node = left_node
            best_line = left_line
    # (0,height) corner case
    elif start == (0,height):
        best_line = math.inf

        top_line, top_node = darkest_line(crop_img, start, top)
        if top_line < best_line:
            best_node = top_node
            best_line = top_line

        right_line, right_node = darkest_line(crop_img, start, right)
        if right_line < best_line:
            best_node = right_node
            best_line = right_line
             
    # x == 0 --> Left wall
    elif start[0] == 0:
        best_line = math.inf

        top_line, top_node = darkest_line(crop_img, start, top)
        if top_line < best_line:
            best_node = top_node
            best_line = top_line

        bot_line, bot_node = darkest_line(crop_img, start, bottom)
        if bot_line < best_line:
            best_node = bot_node
            best_line = bot_line

        right_line, right_node = darkest_line(crop_img, start, right)
        if right_line < best_line:
            best_node = right_node
            best_line = right_line
     
    # x == width --> Right wall
    elif start[0] == crop_img.shape[1]:
        best_line = math.inf

        top_line, top_node = darkest_line(crop_img, start, top)
        if top_line < best_line:
            best_node = top_node
            best_line = top_line

        bot_line, bot_node = darkest_line(crop_img, start, bottom)
        if bot_line < best_line:
            best_node = bot_node
            best_line = bot_line

        left_line, left_node = darkest_line(crop_img, start, left)
        if left_line < best_line:
            best_node = left_node
            best_line = left_line

    # y == height --> Bottom wall
    elif start[1] == crop_img.shape[0]:
        best_line = math.inf

        top_line, top_node = darkest_line(crop_img, start, top)
        if top_line < best_line:
            best_node = top_node
            best_line = top_line

        right_line, right_node = darkest_line(crop_img, start, right)
        if right_line < best_line:
            best_node = right_node
            best_line = right_line

        left_line, left_node = darkest_line(crop_img, start, left)
        if left_line < best_line:
            best_node = left_node
            best_line = left_line

    # x == 0 --> Top wall
    elif start[1] == 0:
        best_line = math.inf

        bot_line, bot_node = darkest_line(crop_img, start, bottom)
        if bot_line < best_line:
            best_node = bot_node
            best_line = bot_line

        right_line, right_node = darkest_line(crop_img, start, right)
        if right_line < best_line:
            best_node = right_node
            best_line = right_line

        left_line, left_node = darkest_line(crop_img, start, left)
        if left_line < best_line:
            best_node = left_node
            best_line = left_line

    #print(best_node)
    cv2.line(crop_img, start, best_node, (255,255,255), 1)
    cv2.line(crop_base, start, best_node, (255,255,255), 1)
    cv2.line(line_img, start, best_node, (0,0,0), 1)

    numpy_horizontal = np.hstack((crop_base, line_img))

    cv2.imshow("Comparator", numpy_horizontal)
    cv2.waitKey(10)   

    if createVideo == True:
        # code to generate video (1)
        fname = 'line_art-{0:0=4d}.png'.format(index)
        fpath = 'E:/GitHub/lineArt/lines'
        cv2.imwrite(os.path.join(fpath, fname), numpy_horizontal)
        index += 1

    # start of next line
    start = best_node

print(node_sequence)

# save final image
cv2.imwrite('lineArt.png', line_img)

if createVideo == True:
    # code to generate video (2)
    vid_fname = 'face_draw.avi'
    files = [os.path.join(fpath, f) for f in os.listdir(fpath) if 'line_art' in f]
    files.sort()
    out = cv2.VideoWriter(vid_fname,cv2.VideoWriter_fourcc('M','J','P','G'), 30, (width*2,height))
    [out.write(cv2.imread(fname)) for fname in files]
    out.release()
    
cv2.waitKey(0)
cv2.destroyAllWindows()
