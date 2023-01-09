# IOT-Project 123木頭人
## Introduction
使用步進馬達實現木頭人旋轉的效果，利用相機鏡頭去偵測是否有人物在移動，並加上按鈕控制遊戲的開始與結束。
**遊戲規則:**
1. 按下按鈕，遊戲開始
2. 木頭人一邊撥放音樂一邊轉向玩家
3. 面對玩家後啟動偵測功能，若偵測到有人物在移動就會發出警告聲音
4. 10 秒後木頭人轉回去
5. 重複2~4步驟的動作，若被偵測到移動五次，會播放失敗音效表示遊戲結束
6. 在木頭人旋轉期間，再次按下按鈕表示遊戲結束，會撥放成功音效

**影片連結:**
[木頭人遊戲-挑戰成功](https://youtu.be/asxDR7Kr3Dc), 
[木頭人遊戲-挑戰失敗](https://youtube.com/shorts/hW-8wiIlAPU)

 <img src="https://github.com/littletreeeeeee/IotProject-123WoodMan/blob/main/woodman.jpg?raw=true" width = "300" alt="图片名称" align=center />



## 硬體需求
* Rasberry Pi 3 *1
* 相機鏡頭 *1
* 步進馬達 *1
* 馬達控制板 *1
* 麵包版 *1
* 四腳輕觸按鈕 *1
* 音源線 *1
* 外接喇叭 *1
* 公對公杜邦線 *2
* 公對母杜邦線 *2
* 母對母杜邦線 *6

## 電路圖
 <img src="https://github.com/littletreeeeeee/IotProject-123WoodMan/blob/main/IOT%20PIC.PNG?raw=true"  alt="图片名称" align=center />

## 開發步驟
### 步驟一 :  開發步進馬達旋轉180度，停頓後轉回去的功能
```python
import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
 
pin = [37, 31, 33, 35]
for i in range(4):
    gpio.setup(pin[i], gpio.OUT)
 
forward_sq = ['0011', '1001', '1100', '0110']
reverse_sq = ['0110', '1100', '1001', '0011']
 
def forward(steps, delay):
    for i in range(steps):
        for step in forward_sq:
            set_motor(step)
            time.sleep(delay)
 
def reverse(steps, delay):
    for i in range(steps):
        for step in reverse_sq:
            set_motor(step)
            time.sleep(delay)
 
def set_motor(step):
    for i in range(4):
        gpio.output(pin[i], step[i] == '1')
 
set_motor('0000')
forward(180, 0.01)
set_motor('0000')
reverse(180,0.01)
```
### 步驟二 :  測試按鈕開/關功能
```python 
from gpiozero import LED, Button

from time import sleep

def pressBtn():
	print("Press!! Btn !!")

btn = Button(2)
btn.when_pressed=pressBtn
```
### 步驟三 :   測試播放聲音功能，使用Pytube下載youtube音樂
```python 
import os
from pytube import YouTube
from playsound import playsound

yt=YouTube("https://www.youtube.com/watch?v=YIiWdy1XjQI")

print("download...")
yt.streams.filter().get_audio_only().download(filename='123Music.mp3')
print('OK')
playsound('123Music.mp3')
```
### 步驟四 :   測試使用相機+opencv 實現偵測物體是否有移動功能
**<font color=red>Note : </font>** 
	1.  OpenCV 安裝後無法正常使用，需要另外安裝以下套件
	2.  安裝後須開啟相機設定，否則無法開啟鏡頭。
```python
$sudo apt-get install lib atlas-base dev Python3 -m pip install bumpy -I
$sudo raspi-config #相機鏡頭設定
```
```python
import cv2
from gpiozero import LED, Button
from time import sleep
import RPi.GPIO as gpio
import time
from playsound import playsound

is_start=False;
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
while True:
    start = time.time()
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
            if cv2.contourArea(c) < 1000: # 设置敏感度
                continue
            else:
                print("咦,有什么东西在动0.0")
                break
        pre_frame = gray_lwpCV
    key = cv2.waitKey(1) & 0xFF
    # 按'q'健退出循环
    if key == ord('q'):
        break
# When everything done, release the capture
camera.release()
cv2.destroyAllWindows()
```
### 步驟五 :  合併以上功能，實現如介紹的遊戲規則
```python
import RPi.GPIO as gpio
import time
from playsound import playsound
import asyncio
import cv2
from gpiozero import LED, Button
from time import sleep

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
IsStart=True #是否開始
IsFirstTime=True #是否為第一次
IsRestart=True #是否要重新開始
isBreak=False 

grabCount=0
pin = [37, 31, 33, 35]
for i in range(4):
    gpio.setup(pin[i], gpio.OUT)
 
forward_sq = ['0011', '1001', '1100', '0110']
reverse_sq = ['0110', '1100', '1001', '0011']

#按鈕的Function 第一次按下後遊戲開始
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
        global grabCount
        grabCount=0
        IsRestart=True;
        IsStart=True;

#遊戲開始，
def StartFunction():
   global IsStart
   while IsStart:
        print(IsStart)
        set_motor('0000')
        # asyncio.run(playMusic())
        asyncio.run(main())

async def main():
    global IsFirstTime
    global isBreak 
    # 使用非同步方式，實現可以編播音樂邊讓步進旋轉的效果
    await asyncio.gather(playMusic(),forward(180, 0.005))
    global IsStart
	global grabCount
	# 若重新按下按鈕isBreak=True 且被抓到小於五次，表示遊戲結束，要開始要再按一次按鈕
    if isBreak==True and grabCount<5:
        IsFirstTime=True
    else:
        #馬達到定位後開始偵測
        startDetect()
        time.sleep(5);
        #將馬達轉回去
        set_motor('0000')
        reverse(180,0.005)
        print('reverse')
        time.sleep(3);
        print('sleep 3')

#馬達向前行，若此時按下按鈕會撥放遊戲破關音效，遊戲結束
async def forward(steps, delay):
    print('forward2')
    global isBreak
    for i in range(steps):
        if isBreak==True:
            break
        for step in forward_sq:
            set_motor(step)
            time.sleep(delay)
            if btn.is_pressed:
                global IsStart
                IsStart=False
                isBreak=True
                print("btn.is_pressed")
                playsound("win.mp3")
                print("play win mp3")
                break

#馬達轉回原本位置，若此時按下按鈕會撥放遊戲破關音效，遊戲結束
def reverse(steps, delay):
    global isBreak
    for i in range(steps):
        if isBreak==True:
            break
        for step in reverse_sq:
            set_motor(step)
            time.sleep(delay)
            if btn.is_pressed:
                global IsStart
                IsStart=False
                print("btn.is_pressed")
                playsound("win.mp3")
                print("play win mp3")
                isBreak=True
                break;
                
def set_motor(step):
    for i in range(4):
        gpio.output(pin[i], step[i] == '1')
                            
 #播放木頭人音效
async def playMusic():
    playsound('123Music.mp4',0)
    print('play music2')

#開始偵測
def startDetect():
    camera = cv2.VideoCapture(0) # 参数0表示第一个摄像头
   
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
    
   
    startDetect=time.time() #設定開始偵測時間，後續判斷若偵測超過十秒，木頭人就轉回去
    while detect:
        start = time.time()
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
                    grabCount=grabCount+1 #若被抓到被抓到的次數就+1
                    
                    if grabCount >= 5: #若被抓到超過五次，播放失敗音效並結束遊戲
                        detect=False
                        IsStart=False
                        playsound('fail.mp3')
                        print("Catch by 5 times!! you lose")

                    break
            pre_frame = gray_lwpCV
        if detect==False:
            break;
    # When everything done, release the capture
    camera.release()    
    cv2.destroyAllWindows()
       
#按鈕按下去開始執行各個function      
btn = Button(2)
btn.when_pressed=pressBtn

```


## 參考資料

**步進馬達控制功能 :** *http://hophd.com/raspberry-pi-stepper-motor-control/*

**按鈕功能 :**  *https://ithelp.ithome.com.tw/articles/10216027?fbclid=IwAR2xrsCke46xArizmTbNG8yDDnDJL4YDH_jGbVcE3VjrqIVt2t14NVoxdlw*

**使用OpenCV所遇到問題 :**  *https://stackoverflow.com/questions/53347759/importerror-libcblas-so-3-cannot-open-shared-object-file-no-such-file-or-dire?fbclid=IwAR0x9I0QmOVqnB-SzI2biRL3mZhsBGLO4E297U4FXOjniMzwi05jhgWLYv4*

**無法使用相機時的解法 :** *https://atceiling.blogspot.com/2020/03/raspberry-pi-66pipi-vision.html?fbclid=IwAR2mbG_wMIx5c8OjmwzGxF9znS8G-v2uleMEUYaWqe91_YjeOJUmyfd5VNg*

**下載影片、聲音功能 :** *https://steam.oxxostudio.tw/category/python/example/youtube-download.html?fbclid=IwAR3GcJ75KJMJJkfpLnNVDPoL-ITqyz9_WwaWpLRqjUtUVil1ISJ2nxGQxGI#a4*

**播放音檔 :** *https://blog.csdn.net/weixin_44298361/article/details/115550091?fbclid=IwAR3fYRH_2FW4ipwQWbUPi_N49nhKaNaOeR0E7omV_hPWmNUlJSpgRLJkgVA*

**OpenCV+Python 偵測物體是否有移動 :** *https://l.facebook.com/l.php?u=https%3A%2F%2Fblog.csdn.net%2Flwplwf%2Farticle%2Fdetails%2F72934468%3Ffbclid%3DIwAR3fYRH_2FW4ipwQWbUPi_N49nhKaNaOeR0E7omV_hPWmNUlJSpgRLJkgVA&h=AT0MMyOlWa0QxowowCFUPhawJpkiAgNhkHOcr3j3VXEd4kEaaV4SiVgXLEgIE7WdJIQ6uLC1eHTJtVLxt606YBwINvdQwN43FYXMNlQXL1OWwmaRopwGpfB6qw7Q-cgTLs2U6rxhcM_dTDr9bfl2pA*
