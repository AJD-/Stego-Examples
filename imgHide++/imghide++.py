from PIL import Image
import sys
import os
import random
import math
import secrets
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from bitstring import BitArray

def main():
    global maxLenChar, maxLenBits
    # Clear screen lambda function
    cls = lambda: os.system('cls' if os.name=='nt' else 'clear')
    while(True):
        try:
            ans = input("imgHider++\n\
------------------------------\n\
1. Encode Lossless Image with ASCII message, encrypted with rng password\n\
------------------------------\n\
2. Decode Lossless Image with ASCII message, key from file\n\
3. See capacity of a particular image\n\
------------------------------\n\
4. Exit\n\
>>")
            # Encode image with message from input, encrypted with generated password
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
                data = bytearray(msg,'utf-8')
                # Generate 32 byte/AES-256 secret key, output to file
                secret = secrets.token_bytes(32)
                cipher = AES.new(secret, AES.MODE_CBC)
                ct_bytes = cipher.encrypt(pad(data, AES.block_size))
                st = b64encode(secret).decode('utf-8')
                ct = b64encode(ct_bytes).decode('utf-8')
                print("Secret: {}\nCipher Text: {}".format(st, ct))
                print(len(ct_bytes))
                with open("secret.txt", "w") as sout:
                    sout.write(st)
                with open("cipher.txt", "w") as cout:
                    cout.write(ct)
                bitstring = BitArray(ct_bytes)
                encImgFileName = "enc_{}".format(imgFile)
                encImg = encode_img(img, bitstring.bin)
                if encImg:
                    print("Saving Image...")
                    encImg.save(encImgFileName)
                    print("Image encoded, opening...")
                    os.startfile(encImgFileName)            

            # Decode message from image
            elif ans == '2':
                # Get image file from user
                imgFile = input("Enter the image you wish to decode: ")
                img = Image.open(imgFile)
                encoded_msg = decode_img(img)
                # Restore any zeros that may have been mistaken as EOF
                while(len(encoded_msg) % 8 != 0):
                    encoded_msg += "0"
                encoded_msg = encoded_msg[::-1]
                encoded_msg = int(encoded_msg, 2)
                encoded_msg = encoded_msg.to_bytes(encoded_msg.bit_length() + 7 // 8, 'big').decode('utf-8', errors='ignore')
                # Remove trailing white space
                encoded_msg = encoded_msg[::-1].rstrip(' \t\r\n\0')
                print("Encoded message:\n{}".format(encoded_msg))

            # Get capacity of a given image
            elif ans == '3':
                imgFile = input("Enter the image you wish to see the capacity of: ")
                img = Image.open(imgFile)
                print(img, img.mode)
                # Each pixel can hold three bits of information
                maxLenBits = math.floor((img.size[0]*img.size[1]*3)- 7)
                print("Max message length = {} bits".format(maxLenChar,maxLenBits))

            # Exit the program
            elif ans == '4':
                sys.exit()

            # Continute/Clear Screen
            input("Press enter to continue...")
            cls()
        except KeyboardInterrupt:
            print("Operation cancelled, closing...")
        #except Exception as e:
            #print("Unexpected error occurred: {}".format(e))

def encode_img(img, data):
    global maxLenChar, maxLenBits
    print("Data: {}".format(data))
    try:
        print("Encoding image...")
        if len(data) > maxLenBits:
            print("Message must be less than {} bits".format(maxLenBits))
            return False
        if 'RGB' not in img.mode and 'RGBA' not in img.mode:
            print("Image must be in RGB/RGBA mode, it is currently in {} mode.".format(img.mode))
            return False
        encodedImg = img.copy()
        w,h = img.size
        with open("msgin.txt", "w") as msgin:
            msgin.write(data)
        # Image = a 2d array of pixels
        # Each pixel is made up of r,g,b values
        bstream = bitstring_to_bitstream(data)
        for row in range(h):
            for col in range(w):
                if(img.mode == 'RGB'):
                    r,g,b = img.getpixel((col, row))
                else:
                    r,g,b,a = img.getpixel((col, row))                
                redlsb = next(bstream)
                r = set_bit(r, redlsb)
                greenlsb = next(bstream)
                g = set_bit(g, greenlsb)
                bluelsb = next(bstream)
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
    maxlen = 128
    msg = ""
    for row in range(h):
        for col in range(w):
            if(img.mode == 'RGB'):
                r,g,b = img.getpixel((col, row))
            else:
                r,g,b,a = img.getpixel((col, row))
            # Convert integer value of pixel to binary string
            r = bin(r)
            g = bin(g)
            b = bin(b)
            # Get least significant digit of each pixel
            if(maxlen > 0):
                msg += str(r[-1:])
            else:
                continue
            maxlen -= 1
            if(maxlen > 0):
                msg += str(g[-1:])
            else:
                continue
            maxlen -= 1
            if(maxlen > 0):
                msg += str(b[-1:])
            else:
                continue
            maxlen -= 1
        if(maxlen == 0):
            break
    with open("foundmsg.txt", "w") as msgout:
        msgout.write(msg)
    print(msg)
    return msg

def bitstring_to_bitstream(bitstring):
    if not isinstance(bitstring, BitArray):
        print("Len(bitstring): {}".format(len(bitstring)))
        for num in bitstring:
            yield int(num)
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

