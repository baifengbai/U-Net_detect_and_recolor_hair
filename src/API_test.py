# coding:utf-8
'''
API: recolor_hair
Author: LXC
'''

import time

import cv2
import keras
import numpy as np


def predict(model, im):
    h, w, _ = im.shape
    inputs = cv2.resize(im, (480, 480))
    inputs = inputs.astype('float32')
    inputs.shape = (1,) + inputs.shape
    inputs = inputs / 255
    mask = model.predict(inputs)
    # ret, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY_INV)
    mask.shape = mask.shape[1:]
    mask = cv2.resize(mask, (w, h))
    mask.shape = h, w, 1
    return mask


def change_v(v, mask, target):
    # 染发
    epsilon = 1e-7
    x = v / 255                             # 数学化
    target = target / 255
    target = -np.log(epsilon + 1 - target)
    x_mean = np.sum(-np.log(epsilon + 1 - x)  * mask) / np.sum(mask)
    alpha = target / x_mean
    x = 1 - (1 - x) ** alpha
    v[:] = x * 255                          # 二进制化


def recolor(im, mask, color=(0x40, 0x16, 0x66)):
    # 工程化
    color = np.array(color, dtype='uint8', ndmin=3)
    im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    color_hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    # 染发
    im_hsv[..., 0] = color_hsv[..., 0]      # 修改颜色
    change_v(im_hsv[..., 2:], mask, color_hsv[..., 2:])
    im_hsv[..., 1] = color_hsv[..., 1]      # 修改饱和度
    x = cv2.cvtColor(im_hsv, cv2.COLOR_HSV2BGR)
    im = im * (1 - mask) + x * mask
    return im


def main(model, ifn, ofn, color=(0x40, 0x16, 0x66)):
    if isinstance(model, str):
        model = keras.models.load_model(model, compile=False)
    im = cv2.imread(ifn)
    start = time.perf_counter()
    mask = predict(model, im)
    print(time.perf_counter() - start)
    start = time.perf_counter()
    im = recolor(im, mask, color)
    print(time.perf_counter() - start)
    cv2.imwrite(ofn, im)
    cv2.imwrite('mask.jpg', mask * 255)


if __name__ == '__main__':
    # data = np.load('../celeba.npz')
    # images, masks = data['images'], data['masks']
    # cv2.imwrite('celeba.image.123.jpg', images[123])
    # cv2.imwrite('celeba.mark.123.jpg', masks[123])
    main('weights.005.h5', 'C:/Users/40101/Desktop/TEMP-PICS/ce3c38e79cd047f5a33466f9bbd67c30_th.jpg', './recolor.ddd_ori.jpg')
