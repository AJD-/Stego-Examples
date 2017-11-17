import sys
import os
import random
import math
import codecs
import binascii

def main():
    # Clear screen lambda function
    cls = lambda: os.system('cls' if os.name == 'nt' else 'clear')
    while(True):
        try:
            ans = input("Works on txt files.\n\
------------------------------\n\
1. Encode Text file with zero-width joiner message from input\n\
------------------------------\n\
2. Decode Zero-Width Message\n\
------------------------------\n\
3. Exit\n\
>>")
            # Encode text file with message from input
            if ans == '1':
                # Get text file file from user
                txtFileName = input("Enter the text file you wish to encode: ")
                with open(txtFileName, 'r') as txtFile:
                    # Get message from user
                    msg = input("Enter your message: ") 
                    encTxtFileName = "enc_{}".format(txtFileName)
                    data = txtFile.read()
                    encFile = encode_file(data, msg)
                    print(encFile)
                    if encFile:
                        with codecs.open("enc_{}".format(txtFileName), mode="w", encoding="utf-8") as out:
                            print("Saving text file...")
                            out.write(encFile)
                            print("Text file encoded, opening...")
                            os.startfile(encTxtFileName)

            # Decode message from text file
            elif ans == '2':
                # Get text file file from user
                txtFile = input("Enter the text file you wish to decode: ")
                with codecs.open(txtFile, mode='r', encoding="utf-8") as txtFile:
                    encoded_msg = decode_file(txtFile)
                    encoded_msg = encoded_msg[::-1]
                    encoded_msg = int(encoded_msg, 2)
                    encoded_msg = encoded_msg.to_bytes(encoded_msg.bit_length() + 7 // 8, 'big').decode('utf-8', errors='ignore')
                    print("Encoded message:\n{}".format(encoded_msg[::-1].rstrip(' \t\r\n\0')))

            # Exit the program
            elif ans == '3':
                sys.exit()

            # Continute/Clear Screen
            input("Press enter to continue...")
            cls()
        except KeyboardInterrupt:
            print("Operation cancelled, closing...")
        #except Exception as e:
        #    print("Unexpected error occurred: {}".format(e))

def encode_file(txt, msg):
    try:
        bitstream = str_to_bitstream(msg)
        print("Encoding file...")
        encodedMsg = txt
        for num in bitstream:
            if(num == 1):
                encodedMsg = encodedMsg + u"\u200C"
            elif(num == 0):
                encodedMsg = encodedMsg + u"\u200D"
        return encodedMsg
    except KeyboardInterrupt:
        print("User interrupted encoding.")
        return False
    #except Exception as e:
    #    print("Unexpected error occured, " + e)
    #    return False

def decode_file(txt):
    print("Decoding file...")
    msg = ""
    for line in txt:
        for char in line:
            if(char == u"\u200C"):
                msg = msg + '1'
            elif(char == u"\u200D"):
                msg = msg + '0'
    return msg

def str_to_bitstream(str):
    if not isinstance(str, bytes):
        for ch in str:
            ascii = ord(ch)
            ct = 0
            while(ct < 8):
                yield ascii & 1
                ascii = ascii >> 1
                ct += 1
    else:
        for ch in str:
            ct = 0
            while(ct < 8):
                yield ch & 1
                ch = ch >> 1
                ct += 1

def set_bit(oldbyte,newbit):
    if newbit:
        return oldbyte | newbit
    else:
        return oldbyte & 0b11111110

if __name__ == "__main__":
    main()
