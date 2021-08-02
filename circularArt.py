import math
import time
import os
import cv2
import numpy as np
from skimage.draw import line

def createNodes(cp, r, nodes):
    coordinates = [] 
    arc = (2*math.pi) / nodes
    for n in range(nodes):
        x_i =int( cp[0] + (r * math.cos(arc * n)))
        y_i =int( cp[1] + (r * math.sin(arc * n)))
        coordinates.append((x_i, y_i))
    return coordinates

def darkest_line(image, start, nodes, last_node):
    best_line = math.inf
    line_strength = 0
    for index, node in enumerate(nodes):
        if node != start and node != last_node:
            # if index % 2 == 0:
            discrete_line = list(zip(*line(*start, *node)))
            for pixel in discrete_line:
                # sum the pixel values along the line
                try:
                                   # image[HEIGHT][WIDTH]
                                   # image[y][x]                    
                    line_strength += image[pixel[1]][pixel[0]]
                except:
                    None
            #averge pixel strength
            line_strength /= len(discrete_line)
            #print(int(line_strength), node, len(discrete_line))
            if line_strength < best_line:
                best_node = node
                best_line = line_strength
                #print(str(best_node) + str(line_strength))
    return best_node, best_line

########## OPTIONS ##########
#total lines requested      #                  
lines2draw = 900            #              
#nodes                      #         
n = 150                     # 
#create a video             #     
createVideo = True          # 
#############################

# load in img
img1 = cv2.imread('face.jpg', cv2.IMREAD_GRAYSCALE) 
base_img = cv2.imread('face.jpg', 3) 

# define hight/width variables
height = img1.shape[0]
width  = img1.shape[1]
# find center point of image
c_x = math.floor(width / 2)
c_y = math.floor(height / 2)
c = (c_x, c_y)

# compute radius, using the shortest between height and width
r = int(math.floor(min(height, width) / 2))

# error check
if((c_x + r) > width) or ((c_y + r) > height):
    raise Exception("Computed radius acessing pixels which are out of bounds")

# crop img 
crop_img  = img1[(c_y-r):(c_y+r), (c_x-r):(c_x+r)]
crop_base = base_img[(c_y-r):(c_y+r), (c_x-r):(c_x+r)]

# define hight/width variables
h_crop = crop_img.shape[0]
w_crop = crop_img.shape[1]
# find center point of cropped image
c_x2 = math.floor(w_crop / 2)
c_y2 = math.floor(h_crop / 2)
cp2 = (c_x2, c_y2)

# create node sequence of 'n' nodes
nodes = createNodes(cp2, r, n)

# create canvas
line_img  = np.ones([h_crop,w_crop,3], np.uint8) * 255

# draw nodes on canvas
for i in range(n):
    line_img = cv2.circle(line_img, (nodes[i][0], nodes[i][1]), 1, (0, 0, 0), 1)

# use first node as starting point
start = nodes[0]
last_node = start
node_sequence = []
index = 0
for line_count in range(lines2draw):
    
    best_node, best_line = darkest_line(crop_img, start, nodes, last_node)
    #print( "start : " + str(start) + " best : " + str(best_node) + " last : " + str(last_node))
    #if (line_count % 25 == 0):
    #    print(line_count)
    cv2.line(crop_img, start, best_node, (255,255,255), 1)
    cv2.line(crop_base, start, best_node, (255,255,255), 1)
    cv2.line(line_img, start, best_node, (0,0,0), 1)
    
    # start of next line
    last_node = start
    start = best_node

    numpy_horizontal = np.hstack((crop_base, line_img))
    cv2.imshow("Comparator", numpy_horizontal)
    cv2.waitKey(10)  
    
    if createVideo == True:
        # code to generate video (1)
        fname = 'line_art-{0:0=4d}.png'.format(index)
        fpath = 'E:/GitHub/LinArt/lines'
        cv2.imwrite(os.path.join(fpath, fname), numpy_horizontal)
        index += 1

    #cv2.waitKey(10) 

# save final image
cv2.imwrite('lineArtCircle.png', line_img)

if createVideo == True:
    # code to generate video (2)
    vid_fname = 'face_draw_circle.avi'
    files = [os.path.join(fpath, f) for f in os.listdir(fpath) if 'line_art' in f]
    files.sort()
    out = cv2.VideoWriter(vid_fname,cv2.VideoWriter_fourcc('M','J','P','G'), 30, (width*2,height))
    [out.write(cv2.imread(fname)) for fname in files]
    out.release()

cv2.waitKey(0)
cv2.destroyAllWindows()

