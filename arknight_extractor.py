import shutil
import time
import cv2
import os
import sys
import re
import concurrent.futures


def read_png(s):
    img = cv2.imread(s, cv2.IMREAD_UNCHANGED)
    return img


def save_png(s, img):
    cv2.imwrite(s, img, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])


def exchange(img, x):
    w, h = img.shape[0:2]
    tempimg = cv2.resize(img, (w*x, h*x), interpolation=cv2.INTER_CUBIC)
    return tempimg


def Do(a, b):
    a[:, :, 3] = b[:, :, 0]
    return a


def process_image(a):
    b = a.replace("[alpha]", '')

    base = read_png(in_dir_path + b)
    alpha = read_png(in_dir_path + a)
    print("Combining %s" % b)
    try:
        if base.shape[0]/alpha.shape[0] != 1:
            alpha = exchange(alpha, int(base.shape[0]/alpha.shape[0]))
        png = Do(base, alpha)
        save_png(out_dir_path + b, png)
    except:
        print("Unable to process %s" % b)


if __name__ == "__main__":
    in_dir_path = './Texture2D/'
    out_dir_path = './Picture/'

    print("initializing...")
    if not os.path.isdir(in_dir_path):
        print("Directory %s does not exisit" % in_dir_path)
        sys.exit()

    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)

    alpha_img_names = []
    file_list = os.listdir(in_dir_path)

    print('Loading pictures from dir...')
    print("%d pictures in total" % len(file_list))
    print('Fixing filename...')

    for i in file_list:
        img = cv2.imread(in_dir_path + i, cv2.IMREAD_UNCHANGED)

        if img is not None and img.shape[0] >= 1024:
            if re.search("#.*#.*", i):  # rename the file
                fixed = i.replace(i[i.rindex('#')-1:], '.png')
                shutil.move(in_dir_path + i, in_dir_path +
                            fixed)
                i = fixed

            if "[alpha]" in i:  # add alpha img to the list
                alpha = i
                base = i.replace("[alpha]", '')
                if alpha in file_list and base in file_list:
                    alpha_img_names.append(i)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_image, alpha_img_names)
