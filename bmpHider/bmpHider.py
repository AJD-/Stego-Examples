from PIL import Image
import sys
import os

imgFile = "enc_blackscienceman.jpg"
msg = "Hello World!"

def main():
    try:
        ans = input("What would you like to do?\n1. Encode Image with message\n2. Decode Image with message\n>>")
        if ans == '1':
            img = Image.open(imgFile)
            print(img, img.mode)
            encImgFileName = "enc_{}".format(imgFile)
            encImg = encode_img(img, msg)
            if encImg:
                print("Saving Image...")
                encImg.save(encImgFileName)
                print("Image encoded, opening...")
                os.startfile(encImgFileName)
        elif ans == '2':
            img = Image.open(imgFile)
            encoded_msg = decode_img(img)
            print("Encoded message: {}".format(encoded_msg))

    except KeyboardInterrupt:
        print("Operation cancelled, closing...")
    except Exception as e:
        print("Unexpected error occurred: {}".format(e))

def encode_img(img, msg):
    print("Encoding image...")
    maxLen = 255
    if len(msg) > maxLen:
        print("Message must be less than {} chars".format(maxLen))
        return False
    if img.mode != 'RGB':
        print("Image must be RGB mode")
        return False
    encodedImg = img.copy()
    w,h = img.size
    index = 0
    rgbaMode = False
    # Image = a 2d array of pixels
    # Each pixel is made up of 3-4 values, a = transparancy for pngs
    for row in range(h):
        for col in range(w):
            try:
                r,g,b,a = img.getpixel((col, row))
                rgbaMode = True
            except ValueError:
                r,g,b = img.getpixel((col, row))                
            except:
                print("Unexpected error occurred")
            if row == 0 and col == 0:
                # Holds len of msg
                print("First pixel, rgbaMode == True")
                pix = len(msg)
            elif index < len(msg):
                # Encode each letter of message to byte format
                pix = ord(msg[index-1])                
            elif rgbaMode:
                # Use transparency bits if avaliable
                pix = a
            else:
                # Otherwise, use red channel
                pix = r
            if rgbaMode:
                encodedImg.putpixel((col, row),(r, g, b, pix))
            else:
                encodedImg.putpixel((col, row),(pix, g, b))
            index += 1
    return encodedImg

def decode_img(img):
    print("Decoding image...")
    encodedImg = img.copy()
    w,h = img.size
    index = 0
    length = 0
    rgbaMode = False
    msg = ""
    for row in range(h):
        for col in range(w):
            try:
                r,g,b,a = img.getpixel((col, row))
                rgbaMode = True
            except ValueError:
                r,g,b = img.getpixel((col, row))                
            except:
                print("Unexpected error occurred")
            # Get length
            if row == 0 and col == 0 and rgbaMode:
                length = a
            elif row == 0 and col == 0:
                length = r
            elif index < length and rgbaMode:
                msg += chr(a)
            elif index < length:
                msg += chr(r)
            index += 1
    return msg

if __name__ == "__main__":
    main()
