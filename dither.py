#!/usr/bin/env python3
# /// script
# dependencies = ["Pillow"]
# ///

from PIL import Image, ImageEnhance

BAYER_4X4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]

def bayer_dither(img, levels=4):
    width, height = img.size
    px = img.load()
    step = 255 // (levels - 1) if levels > 1 else 255
    for y in range(height):
        for x in range(width):
            old_val = px[x, y]
            threshold = (BAYER_4X4[y % 4][x % 4] / 16.0) * step - (step / 2)
            new_val = int(round((old_val + threshold) / step)) * step
            new_val = min(255, max(0, new_val))
            px[x, y] = new_val
    return img

def main():
    img = Image.open("IMG_1245.jpeg")
    # The original is portrait; rotate so the landscape scene is upright
    # ROTATE_270 = 90° clockwise
    img = img.transpose(Image.ROTATE_270)
    
    w, h = img.size
    # Crop to center the peak (upper half of landscape)
    left = int(w * 0.05)
    top = int(h * 0.10)
    right = int(w * 0.95)
    bottom = int(h * 0.65)
    img = img.crop((left, top, right, bottom))
    
    max_width = 1600
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    
    gray = ImageEnhance.Contrast(img.convert("L")).enhance(1.5)
    
    # Blueprint blue 4-level dither
    d4 = bayer_dither(gray.copy(), levels=4)
    tinted = d4.convert("RGB")
    px = tinted.load()
    for y in range(tinted.height):
        for x in range(tinted.width):
            v = px[x, y][0]
            if v < 64:
                px[x, y] = (6, 8, 16)
            elif v < 128:
                px[x, y] = (22, 32, 55)
            elif v < 192:
                px[x, y] = (50, 78, 130)
            else:
                px[x, y] = (90, 140, 210)
    tinted.save("veleta-dither.jpg", quality=92)
    
    # B/W 2-level dither
    bw = bayer_dither(gray.copy(), levels=2)
    bw.save("veleta-dither-bw.jpg", quality=92)
    
    print("Done: veleta-dither.jpg, veleta-dither-bw.jpg")

if __name__ == "__main__":
    main()
