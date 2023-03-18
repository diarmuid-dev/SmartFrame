import tkinter as tk
from tkinter import ttk
import threading
from multiprocessing import current_process
from multiprocessing.connection import Listener
from PIL import Image, ImageTk
from dotenv import load_dotenv
import os
import time
import sys

class SmartFrame(tk.Tk):
    def __init__(self, pathToImages, seconds):
        super().__init__()
        self.config(cursor="")
        self.interval = int(seconds)*1000
        self.pathToImages = pathToImages
        self.title('Smart Frame')
        self.attributes('-fullscreen', True)
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f'{self.width}x{self.height}')
        
        self.images = self.getImages()
        self.image = -1

        self.canvas = tk.Canvas(self, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack()
        
        self.image_container = self.canvas.create_image(0,0, anchor="nw",image=None)
        
        self.iterateImage()
        
        # # Create prev and next buttons
        # self.prevBtn=self.createButton(int(self.width/3), self.height, 0, 0)
        # self.canvas.tag_bind(self.prevBtn,"<Button-1>", self.prevImage)
        # self.prevBtn=self.createButton(int(self.width/3), self.height, int(self.width*2/3), 0)
        # self.canvas.tag_bind(self.prevBtn,"<Button-1>", self.prevImage)
        
    # To get a transparent rectangle on Tkinter, we must make a transparent 
    # image in Pillow first then display it on the canvas
    def createButton(self, sizeX, sizeY, posX, posY):
          alpha = int(0)
          fill = "yellow"
          fill = self.winfo_rgb(fill) + (alpha,)
          image = Image.new('RGBA', (sizeX, sizeY), fill)
          transparent = ImageTk.PhotoImage(image)
          return self.canvas.create_image(posX, posY, image=transparent, anchor='nw')
        
    def getImages(self):
        files = [f for f in os.listdir(self.pathToImages) if os.path.isfile(self.pathToImages + f)]
        return files
    
    def iterateImage(self):
        self.image = (self.image+1)%len(self.images)
        self.displayImage()
        self.after(self.interval, self.iterateImage)
        
    def nextImage(self, event):
        self.image = (self.image+1)%len(self.images)
        self.displayImage()
    
    def prevImage(self, event):
        self.image = (self.image-1)%len(self.images)
        self.displayImage()    
    
    # Convert images into a format which Tkinter can read and then update canvas
    # to display new image
    def displayImage(self):
        tempImage = Image.open(self.pathToImages + self.images[self.image])
        tempImage = self.scale(self.width, tempImage)
        self.dispImage = ImageTk.PhotoImage(tempImage)
        self.canvas.itemconfig(self.image_container,
            image=self.dispImage)
            
    def scale(self, width, image):
        ogWidth, ogHeight = image.size
        ratio = ogHeight/ogWidth
        image = image.resize((width, (int(width*ratio))))
        return image

    def close(self):
        self.quit()

    ## Listen on a local socket for communication from the Manager
    def command(self):
        address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
        listener = Listener(address, authkey=bytes(os.getenv('multicast_key'), encoding='utf8'))
        while True:
            conn = listener.accept()
            print('connection accepted from', listener.last_accepted)
            while True:
                msg = conn.recv()
                print(msg)
                # do something with msg
                conn.close()
                if msg == 'close':
                    listener.close()
                    self.close()
                elif msg == 'nextImage':
                    self.nextImage(None)
                elif msg == 'prevImage':
                    self.prevImage(None)
                break

if __name__ == "__main__":
    if (not len(sys.argv) > 2):
        print("Please run in the following format: python3 images.py {path} {interval}")
        exit(0)
    if (not sys.argv[2].isnumeric()):
        print("Invalid interval, please provide an interval in seconds")
        exit(0)
    if (not os.path.exists(sys.argv[1])):
        print("Please enter a valid path to the image files")
        exit(0)
    load_dotenv()
    smartFrame = SmartFrame(sys.argv[1], sys.argv[2])
    x = threading.Thread(target=smartFrame.command)
    x.start()
    smartFrame.mainloop()
    print('running!')