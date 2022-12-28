import RPi.GPIO as gpio
import time
from playsound import playsound
import asyncio
import cv2
from gpiozero import LED, Button
from time import sleep

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
IsStart=True
IsFirstTime=True
IsRestart=True
grabCount=0
pin = [37, 31, 33, 35]
for i in range(4):
    gpio.setup(pin[i], gpio.OUT)
 
forward_sq = ['0011', '1001', '1100', '0110']
reverse_sq = ['0110', '1100', '1001', '0011']

    
def pressBtn():
    global IsStart
    global IsFirstTime
    global IsRestart

    print("Press!! Btn 1!!"+str(IsStart))

    if (IsFirstTime==True and IsStart==True) and IsRestart==True:
        print("Game Start")
        IsStart=True
        IsFirstTime=False;
        IsRestart=False;
        StartFunction()       
        print("Press!! Btn 2!!"+str(IsStart))
    else :
        print("Game End")
        IsRestart=True;
        IsStart=True;
        

btn = Button(2)

btn.when_pressed=pressBtn

async def forward(steps, delay):
    print('forward2')
    for i in range(steps):
        for step in forward_sq:
            set_motor(step)
            time.sleep(delay)
 
def reverse(steps, delay):
    for i in range(steps):
        for step in reverse_sq:
            set_motor(step)
            time.sleep(delay)
            
async def playMusic():
    playsound('123Music.mp4',0)
    print('play music2')




def set_motor(step):
    for i in range(4):
        gpio.output(pin[i], step[i] == '1')
 
async def main():
    global IsFirstTime
    await asyncio.gather(playMusic(),forward(180, 0.005))
    startDetect()
    global IsStart
    global grabCount
    if IsStart==False and grabCount<5:
        playsound("win.mp3")
        print("play win mp3")
        IsFirstTime=True
    else:
        time.sleep(5);
        set_motor('0000')
        reverse(180,0.005)
        print('reverse')
        time.sleep(3);
        print('sleep 3')

    

    
def startDetect():
    save_path = './face/'
    camera = cv2.VideoCapture(0) # 参数0表示第一个摄像头

    # 判断视频是否打开
    if (camera.isOpened()):
        print('Open')
    else:
        print('摄像头未打开')

# 测试用,查看视频size
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print('size:'+repr(size))

    fps = 5  # 帧率
    pre_frame = None  # 总是取视频流前一帧做为背景相对下一帧进行比较
    i = 0
    global grabCount
    global IsStart
    detect=True
    
    startDetect=time.time()
    
    while detect:
        start = time.time()

        if btn.is_pressed:
            global IsStart
            IsStart=False
            print("btn.is_pressed")
            break
        if start-startDetect >10:
            print("over 10 sec, break!")
            break
        
        grabbed, frame_lwpCV = camera.read() # 读取视频流
        gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY) # 转灰度图

        if not grabbed:
            break
        end = time.time()

           # 运动检测部分
        seconds = end - start
        if seconds < 1.0 / fps:
            time.sleep(1.0 / fps - seconds)
        gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))
        # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
        gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0) 
    
        # 在完成对帧的灰度转换和平滑后，就可计算与背景帧的差异，并得到一个差分图（different map）。还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
        if pre_frame is None:
            pre_frame = gray_lwpCV
        else:
            img_delta = cv2.absdiff(pre_frame, gray_lwpCV)
            thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                if cv2.contourArea(c) < 800: # 设置敏感度
                    continue
                else:
                    playsound('error.mp3')
                    print("咦,有什么东西在动0.0")
                    time.sleep(0.5)
                    grabCount=grabCount+1
                    
                    if grabCount >= 5:
                        detect=False
                        IsStart=False
                        playsound('fail.mp3')
                        print("Catch by 5 times!! you lose")

                    break
            pre_frame = gray_lwpCV
        if detect==False:
            break;
        key = cv2.waitKey(1) & 0xFF
    # 按'q'健退出循环
        if key == ord('q'):
            break
# When everything done, release the capture
    camera.release()
    cv2.destroyAllWindows()    


def StartFunction():
   global IsStart
   while IsStart:
        print(IsStart)
        set_motor('0000')
        # asyncio.run(playMusic())
        asyncio.run(main())
    

