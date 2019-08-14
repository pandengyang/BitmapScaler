# coding=utf-8

import binascii
import struct

if __name__ == "__main__":
    scale = 1

    with open('24.bmp', 'rb') as source:
        bmpFileHeaderBytes = source.read(14)
        (bfType, bfSize, bfReserved1, bfReserved2, bfOffBits) = struct.unpack(
            '<2sIHHI', bmpFileHeaderBytes)
        print (bfType, bfSize, bfReserved1, bfReserved2, bfOffBits)

        bmpInfoHeaderSizeBytes = source.read(4)
        (biSize, ) = struct.unpack('<I', bmpInfoHeaderSizeBytes)

        bmpInfoHeaderBytes = source.read(biSize - 4)
        (biWidth, biHeight, biPlanes, biBitCount, biCompression, biSizeImage,
         biXPelsPerMeter, biYPelsPerMeter, biClrUsed,
         biClrImportant) = struct.unpack('<IIHHIIIIII', bmpInfoHeaderBytes)
        print (biWidth, biHeight, biPlanes, biBitCount, biCompression, biSizeImage, biXPelsPerMeter, biYPelsPerMeter, biClrUsed,biClrImportant)

        bmpData = source.read()

    bytesPerPixel = biBitCount / 8
    bytesPerLine = bytesPerPixel * biWidth
    patch = 4 - bytesPerLine * scale % 4
    print patch

    (dBiSize, dBiWidth, dBiHeight, dBiPlanes, dBiBitCount,
     dBitCompression, dBiSizeImage, dBiXPelsPerMeter, dBiYPelsPerMeter,
     dBiClrUsed,
     dBiClrImportant) = (biSize, biWidth * scale,
                         biHeight * scale, biPlanes, biBitCount, biCompression,
                         biHeight * biWidth * scale * scale * bytesPerPixel + biHeight * patch, biXPelsPerMeter,
                         biYPelsPerMeter, biClrUsed, biClrImportant)
    (dBfType, dBfSize, dBfReserved1, dBfReserved2,
     dBfOffBits) = (bfType, bfSize + dBiSizeImage - biSizeImage, bfReserved1,
                    bfReserved2, bfOffBits)

    dBmpFileHeaderBytes = struct.pack('<2sIHHI', dBfType, dBfSize,
                                      dBfReserved1, dBfReserved2, dBfOffBits)

    print dBiWidth
    print dBiHeight
    print dBiSizeImage
    dBmpInfoHeaderBytes = struct.pack(
        '<IIIHHIIIIII', dBiSize, dBiWidth, dBiHeight,
        dBiPlanes, dBiBitCount, dBitCompression, dBiSizeImage,
        dBiXPelsPerMeter, dBiYPelsPerMeter, dBiClrUsed, dBiClrImportant)

    with open('24_dest.bmp', 'wb') as dest:
        dest.write(dBmpFileHeaderBytes)
        dest.write(dBmpInfoHeaderBytes)

        # 写每一行
        for hIndex in range(biHeight):
            lineData = bmpData[hIndex * bytesPerLine:(hIndex + 1) *
                               bytesPerLine]

            # 每一行写 scale 遍
            for _ in range(scale):
                # 写一行中的每一个像素
                for wIndex in range(biWidth):
                    dataOfPixel = lineData[wIndex * bytesPerPixel:
                                           (wIndex + 1) * bytesPerPixel]

                    # 每个像素写 scale 遍
                    for _ in range(scale):
                        dest.write(dataOfPixel)

                # 补零
                for _ in range(patch):
                    dest.write('\x00')