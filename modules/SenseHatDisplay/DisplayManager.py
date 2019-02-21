import sense_hat
from sense_hat import SenseHat
import time
from enum import Enum

class Colors(Enum):
    Green = (0, 255, 0)
    Yellow = (255, 255, 0)
    Blue = (0, 0, 255)
    Red = (255, 0, 0)
    White = (255,255,255)
    Nothing = (0,0,0)
    Pink = (255,105, 180)
    Orange = (255,165, 0)
class DisplayManager(object):
    #Define pixel layout for Raspberry Logo
    def __raspberry(self):
        G = Colors.Green.value
        N = Colors.Nothing.value
        R = Colors.Red.value
        logo = [
        N, G, G, N, N, G, G, N, 
        N, N, G, G, G, G, N, N,
        N, N, R, R, R, R, N, N, 
        N, R, R, R, R, R, R, N,
        R, R, R, R, R, R, R, R,
        R, R, R, R, R, R, R, R,
        N, R, R, R, R, R, R, N,
        N, N, R, R, R, R, N, N,
        ]
        return logo

    #On Init, Set Rotation and flash Logo (also set bright lights)
    def __init__(self):
        self.s = SenseHat()
        self.s.set_rotation(90)
        self.__displayImage(self.__raspberry())#Flash the raspberry pi logo at initialization
        time.sleep(5)
        self.s.clear()
        self.s.low_light = False
        self.s.show_message("Azure IoT Edge" , text_colour=[0,0,255])
        time.sleep(5)

    
    #Use this method to set pixels for a specific image on the SenseHat display
    def __displayImage(self, image):
        self.s.set_pixels(image)
    #Use this module to display a text message in a specific color on the SenseHat display
    def __displayMessage(self,message, textcolor):
        self.s.show_message(message, text_colour=textcolor)

    def DisplayMessage(self,strMessage):
        self.__displayMessage(strMessage,Colors.Green)
            


    