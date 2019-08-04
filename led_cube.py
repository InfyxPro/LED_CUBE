#Welcome to the LED Cube Creater 
#Made by Dominik Chraca
#Last edit July 22, 2019
#This program will allow a user to create pictures or animations and save it to a file 
#This file will be read by the LED boards and displayed via micro SD card

import pygame, time, math, os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import subprocess
import tkinter
from tkinter import filedialog

import datetime

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
#Get area for pyinstaller version
data_folder = resource_path('data')

#globals
max_frames = 100
WIDTH = 1100
HEIGHT = 700 
display = (WIDTH,HEIGHT)
clock = pygame.time.Clock()
frame = 0
frame_loc = 0
y_location = 0
y_select_loc = 0
screen = 0
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PEACH_1 = (205,175,149)
PEACH_2 = (255,218,185)
YELLOW = (255,255,0)
ORANGE = (218,165,32)
PURP_1 = (191,62,255)
PURP_2 = (104,34,139)

cube_vertices = [[[[[0 for i in range(2)] for x in range(8)] for y in range(8)] for z in range(8)]for _frame_ in range(max_frames)] #100 frames

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def message_display(s,text,x,y): #freesansbold.ttf
    global data_folder
    largeText = pygame.font.Font(os.path.join(data_folder,'calibri.ttf'),s)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = (x,y)
    screen.blit(TextSurf, TextRect)

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

def buttons(s,msg,x,y,w,h,ic,ac,number_1,action = None):
    global data_folder
    click = pygame.mouse.get_pressed()
    mouse = pygame.mouse.get_pos()
    
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, ac,(x,y,w,h))
        if action != None and click[0] == 1:
            return action(number_1)
    else:
        pygame.draw.rect(screen, ic,(x,y,w,h))
    smallText = pygame.font.Font(os.path.join(data_folder,'calibri.ttf'),s)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    screen.blit(textSurf, textRect)

def circle_buttons(x,y,radius,ic,number_1,action = None):
    global button_up_watch
    click = pygame.mouse.get_pressed()
    mouse = pygame.mouse.get_pos()
    pygame.draw.circle(screen,ic,(x,y),radius)
    if x+radius > mouse[0] > x-radius and y+radius > mouse[1] > y-radius: 
        if action != None and click[0] == 1:#increment
            if (pygame.key.get_pressed()[K_RSHIFT] or pygame.key.get_pressed()[K_LSHIFT]): # full increment
                return action(number_1[0],10,number_1[1],number_1[2],number_1[3])
            elif(button_up_watch.elapsed() >= 0.1):
                button_up_watch.start()
                return action(number_1[0],1,number_1[1],number_1[2],number_1[3])
            else:
                button_up_watch.start()
        elif action != None and click[2] == 1:#decrement
            if (pygame.key.get_pressed()[K_RSHIFT] or pygame.key.get_pressed()[K_LSHIFT]): # full decrement
                return action(number_1[0],-10,number_1[1],number_1[2],number_1[3])
            elif(button_up_watch.elapsed() >= 0.1):
                button_up_watch.start()
                return action(number_1[0],-1,number_1[1],number_1[2],number_1[3])
            else:
                button_up_watch.start()

class StopWatch:
    def __init__(self):
        self.start()
    def start(self):
        self._startTime = time.time()
    def getStartTime(self):
        return self._startTime
    def elapsed(self, prec=2):
        prec = 1
        diff= time.time() - self._startTime
        return round(diff, prec)
def round(n, p=0):
    m = 10 ** p
    return math.floor(n * m + 0.2) / m
def round_1(n, p=0): # This round has  no extra value
    m = 10 ** p
    return math.floor(n * m) / m

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

def make_square_list(points):
    global max_frames
    for _frame_ in range(max_frames):
        for z in range(0,8):
            for y in range(0,8):
                for x in range(0,8):
                    points[_frame_][x][y][z][0] = list((x*10 - 35, y*10 - 35, z*10 - 35))
                    points[_frame_][x][y][z][1] = list((50,50,50)) #RGB 50 - 250

def Square(_size_, points, yloc):
    global frame
    _size_ = (_size_ / 2) - 2
    glLineWidth(100)
    if (_size_ > 0):
        glPointSize(_size_)
    else:
        glPointSize(1)
    glBegin(GL_POINTS)
    if (yloc): 
        for z in range(0,8):
            for y in range(yloc - 1,yloc):
                for x in range(0,8):
                    glColor3ub(points[frame][x][y][z][1][0],points[frame][x][y][z][1][1],points[frame][x][y][z][1][2])
                    glVertex3sv(points[frame][x][y][z][0])
    else:
        for z in range(0,8):
            for y in range(0,8):
                for x in range(0,8):
                    glColor3ub(points[frame][x][y][z][1][0],points[frame][x][y][z][1][1],points[frame][x][y][z][1][2])
                    glVertex3sv(points[frame][x][y][z][0])
                    

    glEnd()

def increment_led(points, amount, x, y, z): # if amount is 10 or -10, turn completely off or on
    global frame
    points[frame][x][y][z][1][0] += amount * 50
    points[frame][x][y][z][1][1] += amount * 50
    points[frame][x][y][z][1][2] += amount * 50
    if (points[frame][x][y][z][1][0] <=0 or points[frame][x][y][z][1][0] > 250):
        points[frame][x][y][z][1][0] += amount * -50
        points[frame][x][y][z][1][1] += amount * -50
        points[frame][x][y][z][1][2] += amount * -50
    if (amount == 10): # ON
         points[frame][x][y][z][1][0] = 250
         points[frame][x][y][z][1][1] = 250
         points[frame][x][y][z][1][2] = 250
    elif (amount == -10): # OFF
         points[frame][x][y][z][1][0] = 50
         points[frame][x][y][z][1][1] = 50
         points[frame][x][y][z][1][2] = 50

def change_y_loc(value):
    global y_location
    y_location = value

def select_y(value):
    global y_select_loc
    y_select_loc = value

def copy_paste_layer(points):
    global y_location, y_select_loc, frame
    for x in range(0,8):
        for y in range(0,8):
            points[frame][x][y][y_location][1][0] = points[frame][x][y][y_select_loc][1][0]
            points[frame][x][y][y_location][1][1] = points[frame][x][y][y_select_loc][1][1]
            points[frame][x][y][y_location][1][2] = points[frame][x][y][y_select_loc][1][2]

def frame_select(value):
    global frame, frame_loc
    frame_loc = frame

def frame_paste(points):
    global frame, frame_loc
    for z in range(0,8):
        for y in range(0,8):
            for x in range(0,8):
                points[frame][x][y][z][1][0] = points[frame_loc][x][y][z][1][0]
                points[frame][x][y][z][1][1] = points[frame_loc][x][y][z][1][1]
                points[frame][x][y][z][1][2] = points[frame_loc][x][y][z][1][2]

def open_file(points):
    try:
        make_square_list(points) # Reset
        root = tkinter.Tk()
        root.withdraw()
        #file_path = filedialog.askopenfilename() mode='rt', filetypes=ftypes
        file_path = filedialog.askopenfile(mode='rt', filetypes=[('Cube Files', '*.cub')]) 
        file_path_1 = str(file_path)[25:]
        file_path_2 = file_path_1[:-30]
        #print(file_path_2)
        FILE = open(file_path_2,'r')
        READ_FRAME = 0
        raw_data = str
        while (FILE.readable() and (READ_FRAME < 500) and str(raw_data) != ''):
            for z in range(0,8):
                for y in range(0,8):
                    for x in range(0,8):
                        raw_data = FILE.read(1)
                        if (raw_data == ''): # To catch the end of file
                            break
                        data = int(((int(raw_data) / 2) + 1) * 50)
                        points[READ_FRAME][x][z][y][1][0] = data
                        points[READ_FRAME][x][z][y][1][1] = data
                        points[READ_FRAME][x][z][y][1][2] = data
            READ_FRAME += 1
        FILE.close()
    except:
        print("Open failed")

def save_file(points): #Can only have a max of 8 char
    try:
        currentDT = datetime.datetime.now()
        root = tkinter.Tk()
        root.withdraw()
        #file_path = filedialog.askdirectory()
        FILE1 = filedialog.asksaveasfile(defaultextension=".cub")
        FILE1.close()
        os.remove(str(FILE1)[25:-29])#Clean file made by tkinter
        frame_line = str()
        FILE2 = str(FILE1)[25:-33]
        trim_amount = check_file_name_size(str(FILE2))
        if(trim_amount < 0):
            FILE2 = FILE2[:trim_amount]
        FILE = open(FILE2 + ".cub",'w')
        frame_length = get_last_drawn_frame()
        for FRAME in range(0,frame_length+1):
            for z in range(0,8):
                for y in range(0,8):
                    for x in range(0,8):
                        frame_line += (str(int(((points[FRAME][x][z][y][1][0] / 50) - 1) * 2)))
        FILE.write(frame_line)

        FILE.close()
    except:
        print("Save failed")

def get_last_drawn_frame():
    global cube_vertices, max_frames
    latest_frame = 0
    for FRAME in range(0,max_frames):
        for z in range(0,8):
            for y in range(0,8):
                for x in range(0,8):
                    if (cube_vertices[FRAME][x][y][z][1][0] > 50):
                        latest_frame = FRAME
    return latest_frame

def check_file_name_size(file_name):
    file_length = 8
    for i in range(len(file_name) - 1,0,-1):
        if (file_name[i] == '/'): # runs once the file name is done reading
            break
        file_length -= 1
    if (file_length >= 0):
        file_length = 0
    print(file_length)
    return file_length

def main_2d():
    global display,clock ,WIDTH, HEIGHT, frame, screen, mouse_click_watch, button_up_watch, y_location, y_select_loc
    pygame.display.quit()
    pygame.display.init()
    pygame.display.set_caption('LED Cube Creater')
    screen = pygame.display.set_mode(display)
    while(1):
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        screen.fill([175,255,255])
        # Draw boundaries
        pygame.draw.rect(screen, BLACK,(0,HEIGHT*0.15,WIDTH,5)) # Top
        pygame.draw.rect(screen, BLACK,(WIDTH*0.85,0,5,HEIGHT)) # Side
        # For each layer
        buttons(20,"L1 select",WIDTH*0,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,0,select_y)
        buttons(20,"L2 select",WIDTH*0.105,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,1,select_y)
        buttons(20,"L3 select",WIDTH*0.21,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,2,select_y)
        buttons(20,"L4 select",WIDTH*0.315,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,3,select_y)
        buttons(20,"L5 select",WIDTH*0.42,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,4,select_y)
        buttons(20,"L6 select",WIDTH*0.525,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,5,select_y)
        buttons(20,"L7 select",WIDTH*0.63,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,6,select_y)
        buttons(20,"L8 select",WIDTH*0.735,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_1,PURP_2,7,select_y)
        if (y_select_loc == 0):
            buttons(20,"L1 select",WIDTH*0,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,0,select_y)
        elif(y_select_loc == 1):
            buttons(20,"L2 select",WIDTH*0.105,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,1,select_y)
        elif(y_select_loc == 2):
            buttons(20,"L3 select",WIDTH*0.21,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,2,select_y)
        elif(y_select_loc == 3):
            buttons(20,"L4 select",WIDTH*0.315,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,3,select_y)
        elif(y_select_loc == 4):
            buttons(20,"L5 select",WIDTH*0.42,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,4,select_y)
        elif(y_select_loc == 5):
            buttons(20,"L6 select",WIDTH*0.525,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,5,select_y)
        elif(y_select_loc == 6):
            buttons(20,"L7 select",WIDTH*0.63,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,6,select_y)
        elif(y_select_loc == 7):
            buttons(20,"L8 select",WIDTH*0.735,HEIGHT*0.11,WIDTH*0.1,HEIGHT*0.03,PURP_2,PURP_2,7,select_y)
        # For each layer
        buttons(20,"L 1",WIDTH*0,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,0,change_y_loc)
        buttons(20,"L 2",WIDTH*0.105,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,1,change_y_loc)
        buttons(20,"L 3",WIDTH*0.21,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,2,change_y_loc)
        buttons(20,"L 4",WIDTH*0.315,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,3,change_y_loc)
        buttons(20,"L 5",WIDTH*0.42,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,4,change_y_loc)
        buttons(20,"L 6",WIDTH*0.525,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,5,change_y_loc)
        buttons(20,"L 7",WIDTH*0.63,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,6,change_y_loc)
        buttons(20,"L 8",WIDTH*0.735,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_2,PEACH_1,7,change_y_loc)
        if (y_location == 0):
            buttons(20,"L 1",WIDTH*0,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,0,change_y_loc)
        elif(y_location == 1):
            buttons(20,"L 2",WIDTH*0.105,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,1,change_y_loc)
        elif(y_location == 2):
            buttons(20,"L 3",WIDTH*0.21,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,2,change_y_loc)
        elif(y_location == 3):
            buttons(20,"L 4",WIDTH*0.315,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,3,change_y_loc)
        elif(y_location == 4):
            buttons(20,"L 5",WIDTH*0.42,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,4,change_y_loc)
        elif(y_location == 5):
            buttons(20,"L 6",WIDTH*0.525,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,5,change_y_loc)
        elif(y_location == 6):
            buttons(20,"L 7",WIDTH*0.63,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,6,change_y_loc)
        elif(y_location == 7):
            buttons(20,"L 8",WIDTH*0.735,HEIGHT*0,WIDTH*0.1,HEIGHT*0.1,PEACH_1,PEACH_1,7,change_y_loc)
        #Making the grid
        for z in range(0,8):
            for x in range(0,8):
                circle_buttons(int((x+1)*0.1*WIDTH - WIDTH * 0.025),int((z+1)*0.1*HEIGHT + HEIGHT*0.13),10,cube_vertices[frame][x][z][y_location][1],[cube_vertices,x,z,y_location],increment_led)


        #For frame display
        message_display(20,"Frame:",WIDTH*0.9,HEIGHT*0.05)
        message_display(20,str(frame + 1) + "/" + str(max_frames),WIDTH*0.963,HEIGHT*0.05)
        message_display(14,"Frame Selected: " + str(frame_loc + 1),WIDTH*0.93,HEIGHT*0.1)

        #For copying the layers
        buttons(20,"Paste Layer[z]",WIDTH*0.86,HEIGHT*0.16,WIDTH *0.14,HEIGHT*0.05,PEACH_2,PEACH_1,cube_vertices,copy_paste_layer) 

        buttons(20,"Copy Frame[c]",WIDTH*0.86,HEIGHT*0.22,WIDTH *0.14,HEIGHT*0.05,PEACH_2,PEACH_1,1,frame_select)
        buttons(20,"Paste Frame[v]",WIDTH*0.86,HEIGHT*0.27,WIDTH *0.14,HEIGHT*0.05,PEACH_2,PEACH_1,cube_vertices,frame_paste)

        buttons(20,"Open File[o]",WIDTH*0.86,HEIGHT*0.80,WIDTH *0.14,HEIGHT*0.05,PEACH_2,PEACH_1,cube_vertices,open_file)
        buttons(20,"Save File[s]",WIDTH*0.86,HEIGHT*0.85,WIDTH *0.14,HEIGHT*0.05,PEACH_2,PEACH_1,cube_vertices,save_file)

        if (pygame.key.get_pressed()[K_TAB]): # switch to 3d window
            pygame.display.quit()
            pygame.display.init()
            pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
            pygame.display.set_caption('LED Cube Creater')
            gluPerspective(100, (display[0]/display[1]), 0.01, 1000)
            glTranslatef(0,0,-120)
            glRotatef(90, 1, 0, 0)
            glRotatef(90, 1, 0, 0)
            return 0;

        if ((pygame.key.get_pressed()[K_UP] and frame != (max_frames - 1)) and mouse_click_watch.elapsed() > 0.01): # Move up frame
            frame+=1
            mouse_click_watch.start()
        elif (pygame.key.get_pressed()[K_UP] and frame != (max_frames - 1)):
            mouse_click_watch.start()

        if ((pygame.key.get_pressed()[K_DOWN] and frame != 0) and mouse_click_watch.elapsed() > 0.01): # Move down frame
            frame-=1
            mouse_click_watch.start()
        elif (pygame.key.get_pressed()[K_DOWN] and frame != 0):
            mouse_click_watch.start()

        if ((pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL]) and pygame.key.get_pressed()[K_c]):#Copy frame
            frame_select(1)
        if ((pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL]) and pygame.key.get_pressed()[K_v]): # Paste frame
            frame_paste(cube_vertices)
        if ((pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL]) and pygame.key.get_pressed()[K_s]): #Save file
            save_file(cube_vertices)
        if ((pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL]) and pygame.key.get_pressed()[K_o]): #Open file
            open_file(cube_vertices)
        if ((pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL]) and pygame.key.get_pressed()[K_z]): #Paste layer
            copy_paste_layer(cube_vertices)

        pygame.display.flip()

mouse_click_watch = StopWatch()
button_up_watch = StopWatch()

def main():
    global display, clock, mouse_click_watch, frame
    y_location = 0
    x_init = 0
    y_init = 0
    make_square_list(cube_vertices)
    size = 10
    pygame.init()
    display = (1100,700)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    #pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('LED Cube Creater')
    gluPerspective(100, (display[0]/display[1]), 0.01, 1000)
    glTranslatef(0,0,-120)
    glRotatef(90, 1, 0, 0)
    glRotatef(90, 1, 0, 0)
    while True:
        clock.tick(45)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        #To move up frames with mouse
        click = pygame.mouse.get_pressed()
        if (click[0] and mouse_click_watch.elapsed() > 0.05 and frame < max_frames):
            mouse_click_watch.start()
            frame += 1
        elif(click[0]):
            mouse_click_watch.start()
        if (click[2] and mouse_click_watch.elapsed() > 0.05 and frame != 0):
            mouse_click_watch.start()
            frame -= 1
        elif(click[2]):
            mouse_click_watch.start()

        #Moving the actual block
        if (pygame.key.get_pressed()[K_RIGHT]):
            glRotatef(3, 0, 3, 0)
        if (pygame.key.get_pressed()[K_LEFT]):
            glRotatef(-3, 0, 3, 0)
        if (pygame.key.get_pressed()[K_UP]):
            size += 1
            glScale(1.05,1.05,1.05)
        if (pygame.key.get_pressed()[K_DOWN]):
            glScale(0.95,0.95,0.95)
            size -= 1
        if (pygame.key.get_pressed()[K_TAB]): #Change to 2d gui
            main_2d()
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        Square(size,cube_vertices, y_location)       
        pygame.display.flip()


main()
