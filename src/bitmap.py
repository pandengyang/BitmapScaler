# coding=utf-8

import binascii
import struct


class Bitmap(object):
    FILE_HEADER_SIZE = 14
    INFO_HEADER_SIZE_SIZE = 4
    ALIGN = 4

    def __init__(self, pathname):
        self.pathname = pathname

        # 文件头
        self.bfType = None
        self.bfSize = None
        self.bfReserved1 = None
        self.bfReserved2 = None
        self.bfOffBits = None

        # 信息头
        self.biSize = None
        self.biWidth = None
        self.biHeight = None
        self.biPlanes = None
        self.biBitCount = None
        self.biCompression = None
        self.biSizeImage = None
        self.biXPelsPerMeter = None
        self.biYPelsPerMeter = None
        self.biClrUsed = None
        self.biClrImportant = None

        # 调色板
        self.palette = None

        # 图片内容
        self.data = ''
        self.patch = None

    def parse(self):
        with open(self.pathname, 'rb') as f:
            # 文件头
            bmpFileHeaderBytes = f.read(Bitmap.FILE_HEADER_SIZE)
            (self.bfType, self.bfSize, self.bfReserved1, self.bfReserved2,
             self.bfOffBits) = struct.unpack('<2sIHHI', bmpFileHeaderBytes)

            # 信息头
            bmpInfoHeaderSizeBytes = f.read(Bitmap.INFO_HEADER_SIZE_SIZE)
            (self.biSize, ) = struct.unpack('<I', bmpInfoHeaderSizeBytes)
            bmpInfoHeaderBytes = f.read(self.biSize -
                                        Bitmap.INFO_HEADER_SIZE_SIZE)
            (self.biWidth, self.biHeight, self.biPlanes, self.biBitCount,
             self.biCompression, self.biSizeImage, self.biXPelsPerMeter,
             self.biYPelsPerMeter, self.biClrUsed,
             self.biClrImportant) = struct.unpack('<IIHHIIIIII',
                                                  bmpInfoHeaderBytes)

            dataList = []
            data = f.read(1024)
            while data:
                dataList.append(data)
                data = f.read()

            self.data = ''.join(dataList)

            validBytesPerLine = self.biBitCount / 8 * self.biWidth
            if validBytesPerLine % Bitmap.ALIGN == 0:
                self.patch = 0

            else:
                self.patch = Bitmap.ALIGN - validBytesPerLine % Bitmap.ALIGN

    def zoomIn(self, ratio):
        bytesPerPixel = self.biBitCount / 8

        oldBytesPerLine = bytesPerPixel * self.biWidth + self.patch
        oldBiSizeImage = self.biSizeImage
        oldBiHeight = self.biHeight
        oldBiWidth = self.biWidth
        oldData = self.data

        validBytesPerLine = bytesPerPixel * self.biWidth * ratio
        if validBytesPerLine % Bitmap.ALIGN == 0:
            self.patch = 0

        else:
            self.patch = Bitmap.ALIGN - validBytesPerLine % Bitmap.ALIGN

        (self.biSize, self.biWidth, self.biHeight, self.biPlanes,
         self.biBitCount, self.bitCompression, self.biSizeImage,
         self.biXPelsPerMeter, self.biYPelsPerMeter, self.biClrUsed,
         self.biClrImportant) = (
             self.biSize, self.biWidth * ratio, self.biHeight * ratio,
             self.biPlanes, self.biBitCount, self.biCompression,
             self.biHeight * self.biWidth * ratio * ratio * bytesPerPixel +
             self.biHeight * self.patch, self.biXPelsPerMeter,
             self.biYPelsPerMeter, self.biClrUsed, self.biClrImportant)
        (self.bfType, self.bfSize, self.bfReserved1, self.bfReserved2,
         self.bfOffBits) = (self.bfType,
                            self.bfSize + self.biSizeImage - oldBiSizeImage,
                            self.bfReserved1, self.bfReserved2, self.bfOffBits)

        dataList = []
        # 写每一行
        for hIndex in range(oldBiHeight):
            lineData = oldData[hIndex * oldBytesPerLine:(hIndex + 1) *
                               oldBytesPerLine]

            # 每一行写 ratio 遍
            for _ in range(ratio):
                # 写一行中的每一个像素
                for wIndex in range(oldBiWidth):
                    bytesOfPixel = lineData[wIndex *
                                            bytesPerPixel:(wIndex + 1) *
                                            bytesPerPixel]

                    # 每个像素写 ratio 遍
                    for _ in range(ratio):
                        dataList.append(bytesOfPixel)
                        # self.data += bytesOfPixel

                # 补零
                dataList.append('\x00' * self.patch)
                # self.data += '\x00' * self.patch

        self.data = ''.join(dataList)

    def dump(self, pathname):
        bmpFileHeaderBytes = struct.pack('<2sIHHI', self.bfType, self.bfSize,
                                         self.bfReserved1, self.bfReserved2,
                                         self.bfOffBits)

        bmpInfoHeaderBytes = struct.pack(
            '<IIIHHIIIIII', self.biSize, self.biWidth, self.biHeight,
            self.biPlanes, self.biBitCount, self.bitCompression,
            self.biSizeImage, self.biXPelsPerMeter, self.biYPelsPerMeter,
            self.biClrUsed, self.biClrImportant)

        with open(pathname, 'wb') as f:
            f.write(bmpFileHeaderBytes)
            f.write(bmpInfoHeaderBytes)
            f.write(self.data)

    def __str__(self):
        bmpStr = u'''Pathname: %s
bfType: %s
bfSize: %d
bfReserved1: %d
bfReserved2: %d
bfOffBits: %d
biSize: %d
biWidth: %d
biHeight: %d
biPlanes: %d
biBitCount: %d
biCompression: %d
biSizeImage: %d
biXPelsPerMeter: %d
biYPelsPerMeter: %d
biClrUsed: %d
biClrImportant: %d
patch: %d'''

        return bmpStr % (
            self.pathname, self.bfType, self.bfSize, self.bfReserved1,
            self.bfReserved2, self.bfOffBits, self.biSize, self.biWidth,
            self.biHeight, self.biPlanes, self.biBitCount, self.biCompression,
            self.biSizeImage, self.biXPelsPerMeter, self.biYPelsPerMeter,
            self.biClrUsed, self.biClrImportant, self.patch)


if __name__ == "__main__":
    img = Bitmap('24.bmp')
    img.parse()
    print img
    img.zoomIn(4)
    print img
    img.dump('24_2.bmp')