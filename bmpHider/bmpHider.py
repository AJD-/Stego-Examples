from PIL import Image
import sys
import os
import random
import math

def main():
    global maxLen
    # Clear screen lambda function
    cls = lambda: os.system('cls' if os.name=='nt' else 'clear')
    try:
        while(True):
            ans = input("Works on PNG/GIF/BMP.\n\
------------------------------\n\
1. Encode Image with ASCII message from input\n\
2. Encode Image with ASCII message from file\n3. Encode Image with file\n\
------------------------------\n\
4. Decode Image with ASCII message\n\
5. Decode Image with file\n6. See capacity of a particular image\n\
------------------------------\n\
7. Exit\n>>")
            # Encode image with message from input
            if ans == '1':
                # Get image file from user
                imgFile = input("Enter the image you wish to encode: ")
                img = Image.open(imgFile)
                print(img, img.mode)
                # Each pixel can hold three bits of information, each ascii character is eight bytes, 7 zeros are required to end a message
                maxLenChar = math.floor((img.size[0]*img.size[1]*3)/8 - 7)
                maxLenBits = math.floor((img.size[0]*img.size[1]*3)- 7)
                print("Max message length = {} characters/{} bits".format(maxLenChar,maxLenBits))
                # Get message from user
                msg = input("Enter your message: ") 
                encImgFileName = "enc_{}".format(imgFile)
                encImg = encode_img(img, msg)
                if encImg:
                    print("Saving Image...")
                    encImg.save(encImgFileName)
                    print("Image encoded, opening...")
                    os.startfile(encImgFileName)
            # Encode image with message from file
            elif ans == '2':
                # Get image file from user
                imgFile = input("Enter the image you wish to encode: ")
                img = Image.open(imgFile)
                print(img, img.mode)
                # Each pixel can hold three bits of information, each ascii character is eight bytes, 7 zeros are required to end a message
                maxLenChar = math.floor((img.size[0]*img.size[1]*3)/8 - 7)
                maxLenBits = math.floor((img.size[0]*img.size[1]*3)- 7)
                print("Max message length = {} characters/{} bits".format(maxLenChar,maxLenBits))
                # Get message from user
                msgFile = input("Enter the message file: ")
                with open(msgFile) as file:
                     msg = file.read()
                encImgFileName = "enc_{}".format(imgFile)
                encImg = encode_img(img, msg)
                if encImg:
                    print("Saving Image...")
                    encImg.save(encImgFileName)
                    print("Image encoded, opening...")
                    os.startfile(encImgFileName)
            # Encode image with another file
            elif ans == '3':
                # Get image file from user
                imgFile = input("Enter the image you wish to encode: ")
                img = Image.open(imgFile)
                print(img, img.mode)
                # Each pixel can hold three bits of information, each ascii character is eight bytes, 7 zeros are required to end a message
                maxLenChar = math.floor((img.size[0]*img.size[1]*3)/8 - 7)
                maxLenBits = math.floor((img.size[0]*img.size[1]*3)- 7)
                print("Max message length = {} characters/{} bits".format(maxLenChar,maxLenBits))
                # Get message from user
                msgFile = input("Enter the message file: ")
                msg = ""
                with open(msgFile, 'rb') as file:
                     msg = file.read()
                encImgFileName = "enc_{}".format(imgFile)
                encImg = encode_img(img, msg)
                if encImg:
                    print("Saving Image...")
                    encImg.save(encImgFileName)
                    print("Image encoded, opening...")
                    os.startfile(encImgFileName)
            # Decode message from image
            elif ans == '4':
                # Get image file from user
                imgFile = input("Enter the image you wish to decode: ")
                img = Image.open(imgFile)
                encoded_msg = decode_img(img)
                # Restore any zeros that may have been mistaken as EOF
                while(len(encoded_msg) % 8 != 0):
                    encoded_msg += "0"
                encoded_msg = encoded_msg[::-1]
                encoded_msg = int(encoded_msg, 2)
                encoded_msg = encoded_msg.to_bytes(encoded_msg.bit_length() + 7 // 8, 'big').decode('utf-8')
                # Remove trailing white space
                encoded_msg = encoded_msg[::-1].rstrip(' \t\r\n\0')
                print("Encoded message:\n{}".format(encoded_msg))
            # Decode file from image (User must know the filetype stored)
            elif ans == '5':
                # Get image file from user
                imgFile = input("Enter the image you wish to decode: ")
                img = Image.open(imgFile)
                encoded_msg = decode_img(img)
                print("This is currently not complete")
            # Get capacity of a given image
            elif ans == '6':
                imgFile = input("Enter the image you wish to see the capacity of: ")
                img = Image.open(imgFile)
                print(img, img.mode)
                # Each pixel can hold three bits of information, each ascii character is eight bytes, 7 zeros are required to end a message
                maxLenChar = math.floor((img.size[0]*img.size[1]*3)/8 - 7)
                maxLenBits = math.floor((img.size[0]*img.size[1]*3)- 7)
                print("Max message length = {} characters/{} bits".format(maxLenChar,maxLenBits))
            # Exit the program
            elif ans == '7':
                sys.exit()
            # Continute/Clear Screen
            input("Press enter to continue...")
            cls()
    except KeyboardInterrupt:
        print("Operation cancelled, closing...")
    except Exception as e:
        print("Unexpected error occurred: {}".format(e))

def encode_img(img, msg):
    global maxLen
    try:
        bitstream = str_to_bitstream(msg)
        print("Encoding image...")
        if len(msg) > maxLen:
            print("Message must be less than {} chars".format(maxLen))
            return False
        if img.mode != 'RGB':
            print("Image must be in RGB mode")
            return False
        encodedImg = img.copy()
        w,h = img.size
        # Image = a 2d array of pixels
        # Each pixel is made up of r,g,b values
        for row in range(h):
            for col in range(w):
                r,g,b = img.getpixel((col, row))
                redlsb = next(bitstream)
                r = set_bit(r, redlsb)
                greenlsb = next(bitstream)
                g = set_bit(g, greenlsb)
                bluelsb = next(bitstream)
                b = set_bit(b, bluelsb)
                encodedImg.putpixel((col, row),(r, g, b))
        return encodedImg
    except KeyboardInterrupt:
        print("User interrupted encoding.")
        return False
    except Exception as e:
        print("Unexpected error occured, " + e)
        return False

def decode_img(img):
    print("Decoding image...")
    encodedImg = img.copy()
    w,h = img.size
    msg = ""
    for row in range(h):
        for col in range(w):
            r,g,b = img.getpixel((col, row))
            # Convert integer value of pixel to binary string
            r = bin(r)
            g = bin(g)
            b = bin(b)
            # Get least significant digit of each pixel
            msg += str(r[-1:])
            msg += str(g[-1:])
            msg += str(b[-1:])
            # If the last 7 digits are zero, break out and remove unneeded digits
            if msg[-7:] == "0000000":
                msg = msg[:-7]
    return msg

def str_to_bitstream(str):
    for ch in str:
        ascii = ord(ch)
        ct = 0
        while(ct < 8):
            yield ascii & 1
            ascii = ascii >> 1
            ct += 1
    # End of message = 7 LSBs of 0
    for i in range(7):
        yield 0
    # Random values after msg has been encoded
    while(True):
        yield random.randrange(0,1)

def set_bit(oldbyte,newbit):
    if newbit:
        return oldbyte | newbit
    else:
        return oldbyte & 0b11111110

if __name__ == "__main__":
    main()
