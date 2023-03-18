import os
import base64
import socketio
from PIL import Image
from dotenv import load_dotenv
from multiprocessing.connection import Client
from aiohttp import web
from io import BytesIO
import pickle

class SmartFrameManager():
    def __init__(self):
        self.photo_dir_path = os.getenv('photo_dir_path')
        self.install_path = os.getenv('install_path')
        self.initFolders()
        self.initIndex()
        self.active = False

    def initFolders(self):
        if not os.path.exists(self.photo_dir_path):
            raise IOError("Path to photos invalid")
            exit()
        
        if not os.path.exists(self.photo_dir_path + "/thumbnail/"):
            os.mkdir(self.photo_dir_path + "/thumbnail/")

    def initIndex(self):
        if os.path.exists(self.photo_dir_path + "/index.data"):
            file = open(self.photo_dir_path + 'index.data', 'r')
            self.photos = pickle.load(file)
            file.close()
        else:
            self.doIndexFiles()

    ## Launch the photo frame
    def doLaunch(self):
        os.system(f'sudo xinit ./start.sh --pointerMode 2')
        active = True

    def doScreenOff(self):
        os.system('./screen_off.sh')

    def doScreenOn(self):
        os.system('./screen_on.sh')

    def adjustScreenOffTime(self):
        os.system(f"crontab -u mobman -l | grep -v 'perl /home/mobman/test.pl'  | crontab -u mobman -")
        os.system("(crontab -u mobman -l ; echo '*/5 * * * * perl /home/mobman/test.pl') | crontab -u mobman -")

    def adjustScreenOnTime(self):
        os.system('./screen_on.sh')

    ## Launch the photo frame
    def doShutDown(self):
        os.system('sudo shutdown now')

    ## Sync photos with google drive
    def doSyncPhotos(self):
        os.system(f'sudo xinit ${self.install_path}/start.sh')

    ## Store index of photos, write to file to read in on restart
    def doIndexFiles(self):
        self.photos = os.listdir(self.photo_dir_path)
        file = open('index.pickle', 'wb')
        pickle.dump(self.photos, file)
        file.close()
        self.doCreateThumbnails()

    ## Find files which do not currently have thumbnails and create them
    def doCreateThumbnails(self):
        thumbs = os.listdir(self.photo_dir_path + "/thumbnail")
        
        new_thumbs = list(set(self.photos) - set(thumbs))

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

load_dotenv()
smart_frame_manager = SmartFrameManager()
sio = socketio.Client()

def multicast(command):
    address = ('localhost', 6000)
    conn = Client(address, authkey=bytes(os.getenv('multicast_key'), encoding='utf8'))
    conn.send(command)
    conn.close()

@sio.on('prevImage')
def start_frame():
    multicast('prevImage')

@sio.on('nextImage')
def start_frame():
    multicast('nextImage')

@sio.on('stopFrame')
def start_frame():
    multicast('close')

@sio.on('get_thumbnail')
def send_thumbnail(photo_name):
    print('requested thumbnail')
    thumbnail = smart_frame_manager.getThumbnail(photo_name)
    thumbnail_bytes = BytesIO()
    thumbnail.save(thumbnail_bytes, format="JPEG")
    return base64.b64encode(thumbnail_bytes.getvalue())

@sio.on('start_frame')
def start_frame():
    smart_frame_manager.doLaunch()
    return 'ok'

@sio.on('shutdown')
def shutdown():
    smart_frame_manager.doShutDown()
    return 'ok'

@sio.on('screen_off')
def screen_off():
    smart_frame_manager.doScreenOff()
    return 'ok'

@sio.on('screen_on')
def screen_on():
    smart_frame_manager.doScreenOn()
    return 'ok'

@sio.on('message')
def recv_msg(data):
    print(data)

@sio.on('recive_thumbnail')
def recv_thumb(data):
    print(data)

sio.connect(os.getenv('url'))
sio.wait()
