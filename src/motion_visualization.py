import cv2
import sys
import os
import numpy as np
import math
from helper_function import arrowdraw

block_radius = 2
block_dimension = 2 * block_radius + 1
pixel_search_radius = 40
Tmin = 30
Tmax = 100000
min_vector_dist = 0
print(f"Block Dimension: {block_dimension}x{block_dimension}")

video_folder = "SourceVideo/"
frame_folder = "VideoFrames/"
output_folder = "OutputFrames/"

# change to match video name
video_name = "monkey.avi"
output_video_name = "monkeyvectorized.mp4"


def coloured_box(block):
    # ONLY FUNCTIONS IN TERMINALS WHICH  
    # SUPPORT 24-BIT COLOR MODERN MacOS
    # TERMINALS ARE KNOWN TO HAVE ISSUES
    # IF ON MacOS USE VSCODE TERMINAL
    box = ""
    reset_code = "\033[0m"
    for y in block:
        for x in y:
            rgb_bg_code = f"\033[48;2;{x[2]};{x[1]};{x[0]}m"
            box += f"{rgb_bg_code}{'  '}{reset_code}"
        box += "\n"
    
    print(box)


def square_root_ssd(source_block, target_block):
    source_block = np.array(source_block, dtype=np.int32)
    target_block = np.array(target_block, dtype=np.int32)

    ssd = np.sum(pow((source_block - target_block), 2))

    return math.sqrt(ssd)



def cart_dist(point1, point2):
    """
    Compute the Cartesian (Euclidean) distance between two points in 2D space.

    Parameters:
    point1 (tuple or list): Coordinates of the first point (x1, y1).
    point2 (tuple or list): Coordinates of the second point (x2, y2).

    Returns:
    float: The Cartesian distance between the two points.
    """

    return math.sqrt(pow(point2[0]-point1[0], 2) + pow(point2[1]-point1[1], 2))



def macroblock_compare(x, y, frame, next_frame):
    '''
    Main comparison function

    (x, y) : centroid point (coordinates for pixel at center of block)
    frame : current frame
    next_frame : next frame
    '''
    source_block = frame[y-block_radius:y+block_radius+1, x-block_radius:x+block_radius+1]
    ssd_array = []


    for y_target in range(block_radius, int(frame_height)-block_radius+1, block_dimension):
        for x_target in range(block_radius, int(frame_width)-block_radius+1, block_dimension):
            # if (x_target, y_target) != (x, y) and cart_dist((x, y), (x_target, y_target)) <= pixel_search_radius:
            if cart_dist((x, y), (x_target, y_target)) <= pixel_search_radius:
                target_block = next_frame[y_target-block_radius:y_target+block_radius+1, x_target-block_radius:x_target+block_radius+1]
                # print(target_block.shape)
                # problem with shaping causing error on line 26 with larger block radii

                # block_visualizer(target_block, (x_target, y_target))
                ssd_array.append([square_root_ssd(source_block, target_block), (x_target, y_target)])
    
    closest_matched_block_data = min(ssd_array, key=lambda x: x[0])
    closest_matched_block = next_frame[closest_matched_block_data[1][1]-block_radius:closest_matched_block_data[1][1]+block_radius+1,
                                       closest_matched_block_data[1][0]-block_radius:closest_matched_block_data[1][0]+block_radius+1]
    if show_debugging_info:
        print(f"Blocks Searched: {len(ssd_array)}\nBlock Centered At: {x, y}\nClosest Match: [{round(closest_matched_block_data[0])}, {closest_matched_block_data[1]}\n")
        coloured_box(source_block)
        coloured_box(closest_matched_block)
    if (closest_matched_block_data[0] <= Tmax and closest_matched_block_data[0] >= Tmin and cart_dist((x, y), (closest_matched_block_data[1][0], closest_matched_block_data[1][1])) > min_vector_dist):
        # sys.exit(0)
        return [x, y, closest_matched_block_data[1][0], closest_matched_block_data[1][1]]
    else:
        return None


def block_visualizer(block, centroid_pixel):
    '''
    Neatly prints an NxN matrix, where N is the block_radius, 
    to avoid Python's default matrix truncation. The values 
    are then flipped to correspond to modern RGB standards, 
    as OpenCV (cv2) uses BGR which may lead to confusion.

    block : NxN matrix surrounding the centroid pixel
    centroid_pixel : tuple in the form (x, y) at which the
                     block is centered
    '''
    print(f"Centroid Pixel: {centroid_pixel}")
    for i in block:
        for s in i:
            count = 0
            for p in s[::-1]:
                if count == 0:
                    print("[", end="")
                print(p, end="")
                if count != 2:
                    print(", ", end="")
                else:
                    print("]", end=" ")
                count += 1
        print()


video = cv2.VideoCapture(video_folder + video_name)
frame_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
frame_width = video.get(cv2.CAP_PROP_FRAME_WIDTH)

if not video.isOpened():
    print(f"{video_name} not opened")
    sys.exit(1)

process_video = input("Do you want to compile the video from current output frames (y/n): ")
output_framerate = int(input("What frame rate should the output video be: "))
show_debugging_info = int(input("Do you want to show debugging info (1/0): "))

frame_counter = 0
# array to store video frames
frame_array = []

while (True):
    flag, frame = video.read()
    frame_array.append(frame)
    
    if not flag:
        # flag = true means frame found
        print("video end reached")
        break

    if not os.path.isfile(f"{frame_folder}frame{frame_counter}.png"):
        cv2.imwrite(frame_folder + "frame" + str(frame_counter) + ".png", frame)
    frame_counter += 1

video.release()

print(f"{int(frame_width)}x{int(frame_height)}")

if process_video != "y":
    for frame in range(frame_counter-1):
        vector_array = []
        # block_count = 0
        for y in range(block_radius, int(frame_height)-block_radius+1, block_dimension):
            for x in range(block_radius, int(frame_width)-block_radius+1, block_dimension):
                vector_array.append(macroblock_compare(x, y, frame_array[frame], frame_array[frame+1]))
                # block_count += 1
        filtered_vector_array = [vector for vector in vector_array if vector is not None]
        for vector in filtered_vector_array:
            frame_array[frame] = arrowdraw(frame_array[frame], vector[0], vector[1], vector[2], vector[3])
        cv2.imwrite(output_folder + "output" + str(frame) + ".png", frame_array[frame])
        print(f"Frame: {frame}")


out = cv2.VideoWriter(output_video_name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), output_framerate, (int(frame_width), int(frame_height)))
frame_counter = 0
while True:
    img = cv2.imread(output_folder + 'output%d.png' % frame_counter)
    if img is None:
        print('No more frames to be loaded')
        break
    out.write(img)
    frame_counter += 1
out.release()