#!/usr/bin/python3

from gpiozero import Button
from signal import pause

class EPDEntrypoint:
    
    def __init__(self):
        self.button1 = Button(5)
        self.button2 = Button(6)
        self.button3 = Button(13)
        self.button4 = Button(19)
        
        self.button1.when_pressed = print


        pass


if __name__=="__main__":
    entrypoint = EPDEntrypoint()