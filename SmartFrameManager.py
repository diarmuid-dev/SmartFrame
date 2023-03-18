import os
from PIL import Image
from dotenv import load_dotenv

class SmartFrameManager():
    photos = []
    photo_dir_path = ""
    install_path = ""
    active = False

    def SmartFrameManager(self, photo_dir_path, install_path):
        self.photo_dir_path = photo_dir_path
        self.install_path = install_path

    ## Launch the photo frame
    def doLaunch(self):
        os.system(f'sudo xinit ${self.install_path}/start.sh')
        active = True

    ## Launch the photo frame
    def doShutDown(self):
        os.system(f'sudo shutdown now')
        active = True

    ## Sync photos with google drive
    def doSyncPhotos(self):
        os.system(f'sudo xinit ${self.install_path}/start.sh')

    ## Store index of photos, write to file to read in on restart
    def doIndexFiles(self):
        photos = os.listdir(self.photo_dir_path)
        file = open('index.txt', 'w')
        file.write(photos)
        file.close()
        self.doCreateThumbnails()   

    ## Find files which do not currently have thumbnails and create them
    def doCreateThumbnails(self):
        thumbs = os.listdir(self.photo_dir_path + "/thumbnail")
        
        new_thumbs = list(set(self.photos - thumbs))

        for file in new_thumbs:
            try:
                image = Image.open(self.photo_dir_path + "/" + file)
                image.thumbnail((90, 90))
                image.save(self.photo_dir_path + "/thumbnail/" + file)
            except IOError:
                pass

    def getPhotoList(self):
        return self.photos

    def getThumbnail(self, file):
        image = Image.open(self.photo_dir_path + "/thumbnail/" + file)
        return image

def SmartFrameServer():  
    smManager = None

    def SmartFrameServer(self):
        self.smManager = SmartFrameManager(os.getenv('photo_dir_path'), os.getenv('install_path'))

if ('__name__' == 'main'):
    load_dotenv()
    SmartFrameServer()