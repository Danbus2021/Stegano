#Реализовать внедрение информации в изображение в формате .bmp методом псевдослучайной перестановки.
import os
import random
import struct
import sys
from math import *
import numpy as np
from PIL import Image


def create_mask() -> bin:
    text_mask = 0b11111111
    img_mask = 0b11111111
    text_mask <<= 7
    text_mask %= 256
    img_mask >>= 1
    img_mask <<= 1
    return text_mask, img_mask


def strReadTo2(file_name):
    file = open(file_name, "r")
    list_text = []
    while True:
        char = file.readline(1)
        list_text.append(char)
        if not char:
            break
    file.close()
    str_text = ""
    for i in list_text:
        str_text += i
    bin_result = ''.join(format(ord(x), '08b') for x in str_text)
    return bin_result

def random_list(seed) -> list:
    img = Image.open('cat.bmp')
    width, height = img.size
    l = list(range(55, (width*height)*3))
    random.seed(seed)
    l = sorted(l, key=lambda x: random.random())
    img.close()
    return l

def encrypt():
    text_len = os.stat('text.txt').st_size
    img_len = os.stat('cat.bmp').st_size

    if text_len >= (img_len * 1 / 8) - 54:
        print("Too long text")
        return

    text = open('text.txt', 'r')
    start_bmp = open('cat.bmp', 'rb')
    encode_bmp = open('cat_encode.bmp', 'wb')

    first54 = start_bmp.read(54)
    encode_bmp.write(first54)

    text_mask, img_mask = create_mask()
    l_permutation = random_list(123)

    list_image = list_im()   # массив картинки без заголовка

    count = 0

    while True:
        symbol = text.read(1)
        if not symbol:
            break
        ASCII = ord(symbol)

        for byte_amount in range(0, 8, 1): # проходимся по байту из текста
            img_byte = int.from_bytes((list_image[l_permutation[count]]), sys.byteorder) & img_mask # считываем байт изображения
            bit = ASCII & text_mask  # берем один бит текста и сдвигаем его вправо
            bit >>= 7
            img_byte |= bit   # логическое или (получаем закодированный байт)
            list_image[l_permutation[count]] = img_byte.to_bytes(1, sys.byteorder)
            ASCII <<= 1
            count += 1

    for i in range(len(list_image)):
        encode_bmp.write(list_image[i])

    text.close()
    start_bmp.close()
    return count


def list_im() -> list:
    start_bmp = open('cat.bmp', 'rb')
    list_image = []
    start_bmp.seek(54)
    while True:
        char = start_bmp.read(1)
        list_image.append(char)
        if not char:
            break
    start_bmp.close()
    return list_image

def list_im_encode() -> list:
    start_bmp = open('cat_encode.bmp', 'rb')
    list_image_encode = []
    start_bmp.seek(54)
    while True:
        char = start_bmp.read(1)
        list_image_encode.append(char)
        if not char:
            break
    start_bmp.close()
    return list_image_encode

def decrypt(count_bit, key):
    text = open('decoded.txt', 'w')
    steg_text = ""
    encoded_bmp = open('cat_encode.bmp', 'rb')
    encoded_bmp.seek(54)
    text_mask, img_mask = create_mask()
    img_mask = ~img_mask
    l_permutation = random_list(key)
    list_image = list_im_encode()

    count_read = 0
    count = 0
    while count_read < count_bit:
        symbol = 0
        for bits_read in range(0, 8, 1):
            img_byte = int.from_bytes(list_image[l_permutation[count]], sys.byteorder) & img_mask
            symbol <<= 1
            symbol |= img_byte
            count_read += 1
            count += 1
        text.write(chr(symbol))
        steg_text += chr(symbol)
    text.close()
    # print(steg_text)
    encoded_bmp.close()
    pass

def PSNR(comp):
    img = np.array(Image.open('cat.bmp'))
    img_encode = np.array(Image.open('cat_encode.bmp'))
    with open('cat.bmp', "rb") as f:
        file_data = f.read()
    width = struct.unpack_from('<i', file_data, 18)[0]
    height = struct.unpack_from('<i', file_data, 22)[0]
    img1 = np.copy(img)
    img2 = np.copy(img_encode)
    tmp = 0
    for i in range(0, height):
        for j in range(0, width):
            tmp += (int(img1[i][j][comp]) - int(img2[i][j][comp])) ** 2
    res = 10 * log10((width * height * (2 ** 8 - 1) ** 2)/tmp)
    return res

steg = encrypt()
print(steg)
decrypt(steg, 123)
print("PSNR R: ", PSNR(0))
print("PSNR G: ", PSNR(1))
print("PSNR B: ", PSNR(2))

