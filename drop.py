from __future__ import print_function
import pygame as py
import random
import sys
import os.path
import hashlib,binascii
py.init()

if len(sys.argv) > 1:
    try:
        a,b = sys.argv[1].split('x')
        if int(a) < 45 or int(b) < 80:
            a,b = 45,80
            print("window must be 45x80 or larger")
    except:
        print("Incorrect syntax\nusage: python drop.py 360x640")
        a,b = 180,320
        py.quit()
        sys.exit()
    WINDOW_WIDTH = int(a)
    WINDOW_HEIGHT = int(b)
else:
    WINDOW_WIDTH = 180
    WINDOW_HEIGHT = 320
_width = 45
_height = 80
FPS = 30

print("creating window: "+str(WINDOW_WIDTH)+"x"+str(WINDOW_HEIGHT))
screen = py.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),py.HWSURFACE|py.DOUBLEBUF|py.RESIZABLE)
py.display.set_icon(py.image.load("icon.ico"))
py.display.set_caption("Bobl")
clock = py.time.Clock()
font = py.font.Font(None,256)

def md5(fileName, excludeLine="", includeLine=""):
    m = hashlib.md5()
    try:
        fd = open(fileName,"rb")
    except IOError:
        return
    content = fd.readlines()
    fd.close()
    for eachLine in content:
        if excludeLine and eachLine.startswith(excludeLine):
            continue
        m.update(eachLine)
    m.update(includeLine)
    return m.hexdigest()
class Game():
    class Player():
        def __init__(self):
            self.image = py.image.load("Player.png")
            self.size = 5
            self.rect = self.image.get_rect()
            self.rect.x,self.rect.y = _width/2-self.size/2,_height-self.size
            self.delta = 0
        def update(self):
            if 0 < self.rect.left+self.delta < _width-self.size: self.rect.left += self.delta
    class Block():
        block_image_list = []
        for i in xrange(4,10):
            block_image_list.append(py.image.load("Block"+str(i)+".png"))
        block_image_special = py.image.load("Block_special.png")
        block_image_point = py.image.load("Block_point.png")
        def __init__(self,delta_delta,btype=0):
            size = random.randint(4,9)
            if btype == 0:
                self.image = self.block_image_list[size-4]
            elif btype == 1:
                self.image = self.block_image_special
            elif btype == 2:
                size = 4
                self.image = py.transform.scale(self.block_image_point,(size,size))
            self.type = btype
            self.delta = 0
            self.delta_delta = delta_delta
            if delta_delta == 0:
                self.delta = 1
            self.rect = py.Rect(random.randint(0,_width-size),-size,size,size)
        def update(self):
            self.rect.top += int(self.delta)
            self.delta += self.delta_delta
    def __init__(self):
        self.timer = py.time.Clock()
        self.player = self.Player()
        self.surface = py.Surface((_width,_height))
        self.background_image = py.image.load("Background.png")
        self.alpha = 255
        self.surface.set_alpha(self.alpha)
        self.number_of_blocks = 30
        self.block_delay = 30
        self.block_delta = 0.125
        self.level,self.level_timer = 0,0
        self.level_timer_max = 5000
        self.score = 0
        self.holding_left,self.holding_right = False,False
        self.block_list = []
        self.tick_counter = 0
        self.end_counter = 60
        self.done = False
        self.block_point_counter = 0
        self.block_point_counter_max = 150
        self.high_score = 0
        self.game_over = None
        file_broken = False
        if os.path.isfile("gameinfo.dat"):
            print("checking highscores...")
            with open("gameinfo.dat","rb") as f:
                f.seek(16)
                numbers_string = ""
                for c in f.read(): numbers_string += str(ord(c))
                if numbers_string: self.high_score = int(numbers_string)
                print("highscore: "+str(self.high_score))
            with open("gameinfo.dat","rb") as f:
                if not f.read(16) == binascii.unhexlify(md5(os.path.abspath(__file__),includeLine=str(self.high_score))):
                    print("highscores file corrupt...")
                    print("exiting...")
                    file_broken = True
        if file_broken:
            os.remove("gameinfo.dat")
            self.high_score = 0
    
    def update(self):
        if self.holding_left: self.player.delta = -1
        elif self.holding_right: self.player.delta = 1
        else: self.player.delta = 0
        if self.tick_counter >= self.block_delay:
            self.tick_counter = 0
            if not len(self.block_list) < self.number_of_blocks: self.block_list.pop(0)
            block = self.Block(self.block_delta)
            self.block_list.append(block)
            if not self.done: self.score += 1
            self.level_timer += self.timer.tick()
        self.tick_counter += 1
        if self.level_timer >= self.level_timer_max and self.level < 30:
            self.level += 1
            if self.block_delay > 3: self.block_delay -= 1
            self.block_delta -= 0.0025
            self.level_timer = 0
            self.level_timer_max = int(self.level_timer_max * 1.1)
            self.block_list.append(self.Block(0,1))
        self.block_point_counter += 1
        if self.block_point_counter >= self.block_point_counter_max:
            self.block_point_counter = 0
            self.block_list.append(self.Block(0.01,2))
        self.player.update()
        for block in self.block_list:
            if block.rect.colliderect(self.player.rect):
                if not block.type == 2:
                    self.done = True
                else:
                    if not self.game_over:
                        self.score += 10
                        self.block_list.remove(block)
            block.update()
        self.surface.blit(self.background_image,(0,0))
        self.surface.blit(self.player.image,self.player.rect)
        for block in self.block_list: self.surface.blit(block.image,block.rect)
        if self.done:
            if not self.game_over:
                self.background_image_2 = py.transform.scale(self.background_image,(WINDOW_WIDTH,WINDOW_HEIGHT))
                self.text = py.transform.scale(font.render(str(self.score),1,(1,1,1)),(WINDOW_WIDTH,WINDOW_HEIGHT/4))
                self.game_over = True
            if self.alpha > 0:
                self.alpha -= 5
                self.surface.set_alpha(self.alpha)
            else:
                self.alpha = 0
                self.surface.set_alpha(self.alpha)
                if self.end_counter > 0: self.end_counter -= 1
                else: return 1
            screen.blit(self.background_image_2,(0,0))
            screen.blit(self.text,(0,WINDOW_HEIGHT/6))
        return 0

def main():
    global screen
    global WINDOW_WIDTH
    global WINDOW_HEIGHT
    finished = False
    while not finished:
        game = Game()
        print("game initialised...")
        done = True
        menu = True
        text1 = font.render("Play:  ENTER",1,(0,0,0))
        text2 = font.render("Quit: ESCAPE",1,(0,0,0))
        text3 = font.render("Highscore:"+str(game.high_score),1,(0,0,0))
        menu_background = py.transform.scale(game.background_image,(WINDOW_WIDTH,WINDOW_HEIGHT))
        print("entering menu...")
        while menu:
            for event in py.event.get():
                if event.type == py.QUIT:
                    menu = False
                    finished = True
                elif event.type == py.VIDEORESIZE:
                    WINDOW_WIDTH,WINDOW_HEIGHT = event.dict['size']
                    screen = py.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),py.HWSURFACE|py.DOUBLEBUF|py.RESIZABLE)
                    menu_background = py.transform.scale(game.background_image,(WINDOW_WIDTH,WINDOW_HEIGHT))
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        menu = False
                        finished = True
                    elif event.key == py.K_RETURN:
                        menu = False
                        done = False
            text1 = py.transform.scale(text1,(WINDOW_WIDTH,WINDOW_HEIGHT/8))
            text2 = py.transform.scale(text2,(WINDOW_WIDTH,WINDOW_HEIGHT/8))
            text3 = py.transform.scale(text3,(WINDOW_WIDTH,WINDOW_HEIGHT/8))
            screen.blit(menu_background,(0,0))
            screen.blit(text1,(0,0))
            screen.blit(text2,(0,WINDOW_HEIGHT-WINDOW_HEIGHT/8))
            screen.blit(text3,(0,WINDOW_HEIGHT/6))
            py.display.flip()
            clock.tick(30)
        if not done: print("entering game...")
        while not done:
            for event in py.event.get():
                if event.type == py.QUIT:
                    done = True
                    finished = True
                elif event.type == py.VIDEORESIZE:
                    WINDOW_WIDTH,WINDOW_HEIGHT = event.dict['size']
                    screen = py.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),py.HWSURFACE|py.DOUBLEBUF|py.RESIZABLE)
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE: done = True
                    elif event.key == py.K_LEFT: game.holding_left = True
                    elif event.key == py.K_RIGHT: game.holding_right = True
                elif event.type == py.KEYUP:
                    if event.key == py.K_LEFT: game.holding_left = False
                    elif event.key == py.K_RIGHT: game.holding_right = False
            screen.fill((255,255,255))
            if game.update():
                print("Final score: "+str(game.score))
                if game.score > game.high_score:
                    with open("gameinfo.dat","wb") as f:
                        f.write(binascii.unhexlify(md5(os.path.abspath(__file__),includeLine=str(game.score))))
                        for c in str(game.score):
                            f.write(chr(int(c)))
                done = True
            display_surf = py.transform.scale(game.surface,(WINDOW_WIDTH,WINDOW_HEIGHT))
            text = py.transform.scale(font.render(str(game.score),1,(1,1,1)),(WINDOW_WIDTH/5,WINDOW_HEIGHT/10))
            text2 = py.transform.scale(font.render(str(game.high_score),1,(1,1,1)),(WINDOW_WIDTH/5,WINDOW_HEIGHT/10))
            display_surf.blit(text,(0,0))
            display_surf.blit(text2,(0,WINDOW_HEIGHT/10))
            screen.blit(display_surf,(0,0))
            py.display.flip()
            clock.tick(FPS)

if __name__ == '__main__':
    main()

print("exiting...")
py.quit()
