import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
import sys

class SmartFrame(tk.Tk):
    def __init__(self, pathToImages, seconds):
        super().__init__()
        self.interval = int(seconds)*1000
        self.pathToImages = pathToImages
        self.title('Smart Frame')
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        print(f'{self.width}x{self.height}')
        self.width = 1920
        self.geometry(f'{self.width}x{self.height}')
        
        self.images = self.getImages()
        self.image = 0

        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()
        
        self.image_container = self.canvas.create_image(0,0, anchor="nw",image=None)
        
        self.displayImage()
        
    def getImages(self):
        return os.listdir(self.pathToImages)
        
    def updateImage(self):
        self.image = (self.image+1)%len(self.images)
        self.displayImage()
        
    def displayImage(self):
        tempImage = Image.open(self.pathToImages + self.images[self.image])
        tempImage = tempImage.resize((self.width,self.height))
        self.dispImage = ImageTk.PhotoImage(tempImage)
        self.canvas.itemconfig(self.image_container,
            image=self.dispImage)
        self.after(self.interval, self.updateImage)
        

if __name__ == "__main__":
    if (not len(sys.argv) > 2):
        print("Please run in the following format: python3 images.py \{path\} \{interval\}")
        exit(0)
    print("argv 1" + sys.argv[1])
    print("argv 2" + sys.argv[2])
    smartFrame = SmartFrame(sys.argv[1], sys.argv[2])
    smartFrame.mainloop()