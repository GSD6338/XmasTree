import cv2
import board
import neopixel
import time 

total_leds = 500
MASTERDIR = "0"

pixels = neopixel.NeoPixel(board.D18, total_leds)
cam = cv2.VideoCapture(0)

for led in range(total_leds):
    # switch on one light then save a picture and then move on
    pixels[led] = (255, 255, 255)

    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break

    img_name = f"/home/pi/Desktop/datset_py/{led}_{MASTERDIR}.png"
    cv2.imwrite(img_name, frame)
    print("{} written!".format(img_name))
    pixels[led] = (0, 0, 0)
    time.sleep(1)

cam.release()