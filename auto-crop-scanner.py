from cgitb import reset
from os import listdir
import cv2
import numpy as np

BATCH_MANUAL_OUTPUT = "Batch_Man/"
BATCH_AUTO_OUTPUT = "Batch_Auto/"
SCANS_INPUT_PATH = "Scans/"

auto_counter = 0
man_counter = 0
batch_counter = 1
max_counter = 0

def get_all_scans(path):
    scans = listdir(path)
    scans.sort()
    print(scans)
    return scans
def scale_down(img, scale_percent):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized_img
def separate_in_four(scale_down, img):
    scale_percent = 50
    resized_img = scale_down(img, scale_percent)

    height = resized_img.shape[0]
    height_cutoff = height // 2
    width = resized_img.shape[1]
    width_cutoff = width // 2

    left_1 = resized_img[height_cutoff:,:width_cutoff]
    left_2 = resized_img[:height_cutoff,:width_cutoff]
    right_1 = resized_img[height_cutoff:,width_cutoff:]
    right_2 = resized_img[:height_cutoff,width_cutoff:]

    img_list = list()
    img_list.append(left_1)
    img_list.append(left_2)
    img_list.append(right_1)
    img_list.append(right_2)
    return img_list
def separate_and_validate(img_list, low_green, high_green):
        global auto_counter, man_counter, batch_counter, max_counter
        mask_list = list()
        for img in img_list: 
            mask = cv2.inRange(img, low_green, high_green)
            max_left_mask = None
            max_top_mask = None
            max_right_mask = None
            max_bottom_mask = None
            top_found = False
        
            for i in range(mask.shape[0]):
                for y in range(mask.shape[1]):
                    if mask[i][y] == 255:
                        if not top_found:
                            max_top_mask = i
                            top_found = True
                        if max_left_mask == None or max_left_mask > y:
                            max_left_mask = y
                        if max_right_mask == None or max_right_mask < y:
                            max_right_mask = y
                        if max_bottom_mask == None or max_bottom_mask < i:
                            max_bottom_mask = i
        
            max_top_mask -= 40
            max_left_mask -= 40
            max_right_mask += 40
            max_bottom_mask += 40
            print(f"Top: {max_top_mask} || Left: {max_left_mask} || Right: {max_right_mask} || Bottom: {max_bottom_mask}")         
            
            img_virgin = img.copy()        
            cv2.rectangle(img, (max_left_mask, max_top_mask), (max_right_mask, max_bottom_mask), (255,0,0))
            mask_list.append(mask)
            cv2.imshow("mask", mask)
            cv2.imshow("img", img)

            if max_counter == 4:
                max_counter = 0
                auto_counter = 0
                man_counter = 0
                batch_counter += 1
            
            k = cv2.waitKey(0)
            if k == 13:
                if max_left_mask < 0:
                    max_left_mask = 0
                if max_right_mask > img.shape[1]:
                    max_right_mask = img.shape[1]
                if max_top_mask < 0:
                    max_top_mask = 0
                if max_bottom_mask > img.shape[0]:
                    max_bottom_mask = img.shape[0]
                img = img_virgin[max_top_mask:max_bottom_mask+max_top_mask, max_left_mask:max_left_mask+max_right_mask]
                cv2.imwrite(f"{BATCH_AUTO_OUTPUT}{batch_counter}-{auto_counter}.jpg", img)
                auto_counter += 1
                man_counter += 1
            elif k == 109:
                img = img_virgin
                cv2.imwrite(f"{BATCH_MANUAL_OUTPUT}{batch_counter}-{man_counter}.jpg", img)
                man_counter += 1
                auto_counter += 1
            max_counter += 1

scans = get_all_scans(SCANS_INPUT_PATH)
for scan in scans:
    img = cv2.imread(f"{SCANS_INPUT_PATH}{scan}")
    img_list = separate_in_four(scale_down, img)

    low_green = np.array([36, 25, 25])
    high_green = np.array([70, 255, 255])
    separate_and_validate(img_list, low_green, high_green)

cv2.destroyAllWindows()