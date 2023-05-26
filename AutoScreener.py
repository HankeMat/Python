#Almost every single piece of this code was made by my teacher tbh
#s/o https://github.com/michto01

import os
import os.path

import mss  # multi-screen screenshots
import mss.tools

import multiprocessing
from pynput import mouse
from PIL import Image, ImageDraw

import signal

file_prefix = "ss"

sct = mss.mss()    # create instance of screenshoter
path = os.getcwd() # use current directory as main path

# Gracefully handle the keybord rage-quit
def keyboardInterruptHandler(signal, frame):
    print(f"\nExiting screenshot application...")
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

# Send new image to processing queue
def on_click(x, y, button, pressed):
    global i
    if button == mouse.Button.left and pressed:
        queue.put((sct.grab(sct.monitors[1]), (x, y)))

def on_move(x, y):
    print(f"Cursor position: ({x}, {y})")

# Process the image (may take some time)
def save(queue) -> None:
    global path
    global file_prefix

    number = 0
    output = str(path) + "/" + str(file_prefix) + "_{}.png"
    os.path.normpath(output) # fix the path to OS conventions

    to_png = mss.tools.to_png

    while "there are screenshots":
        img, pos = queue.get()
        if img is None:
            break

        # Convert the screenshot to PIL Image
        pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')

        # Finally something I made :-)
        # Add red dot to the image at the cursor position
        draw = ImageDraw.Draw(pil_img)
        draw.ellipse((pos[0]-5, pos[1]-5, pos[0]+5, pos[1]+5), fill=(255,0,0))

        # Save the modified screenshot as PNG file
        to_png(pil_img.tobytes(), pil_img.size, output=output.format(number))
        print(f"Created screenshot {number}.")
        number += 1

# Prepare all the prerequisites and fire the mouse listener
def main():
    global path
    suffix = input(f"Save path: '{path}' + <input>: ")
    os.path.normpath(suffix)
    if not os.path.isabs(suffix):
        path = f"{path}{suffix}"
    else:
        path = suffix
    os.path.normpath(path)

    while True:
        with mouse.Listener(on_click=on_click, on_move=on_move) as listener:
            listener.join()

# The proper python main loop and multiprocessing
if __name__ == '__main__':
    # The screenshots queue
    queue= multiprocessing.JoinableQueue()

    # 2 processes: main {this} for grabing and one for saving PNG files
    multiprocessing.Process(target=save, args=(queue,)).start()
    main()
