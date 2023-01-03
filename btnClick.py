from gpiozero import LED, Button
from time import sleep



def pressBtn():
    print("Press!! Btn !!")


btn = Button(2)

btn.when_pressed=pressBtn
