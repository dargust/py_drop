from __future__ import print_function
import pygame as py
import random
import sys
py.init()

if len(sys.argv) > 1:
    try:
        a,b = sys.argv[1].split('x')
    except:
        print("Incorrect syntax\nusage: python drop.py 50x50")
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

screen = py.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),py.HWSURFACE|py.DOUBLEBUF|py.RESIZABLE)
clock = py.time.Clock()
font = py.font.Font(None,256)

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
        block_image = py.image.load("Block.png")
        block_image_special = py.image.load("Block_special.png")
        block_image_point = py.image.load("Block_point.png")
        def __init__(self,delta_delta,btype=0):
            size = random.randint(4,9)
            if btype == 0:
                self.image = py.transform.scale(self.block_image,(size,size))
            elif btype == 1:
                self.image = py.transform.scale(self.block_image_special,(size+2,size+2))
            elif btype == 2:
                size = 4
                self.image = py.transform.scale(self.block_image_point,(size,size))
            self.type = btype
            self.delta = 0
            self.delta_delta = delta_delta
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
            self.block_list.append(self.Block(0.01,1))
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
                    self.score += 10
                    self.block_list.remove(block)
            block.update()
        self.surface.blit(self.background_image,(0,0))
        self.surface.blit(self.player.image,self.player.rect)
        for block in self.block_list: self.surface.blit(block.image,block.rect)#py.draw.rect(self.surface,(0,0,0),block.rect)
        if self.done:
            if self.alpha > 0:
                self.alpha -= 5
                self.surface.set_alpha(self.alpha)
            else:
                self.alpha = 0
                self.surface.set_alpha(self.alpha)
                if self.end_counter > 0: self.end_counter -= 1
                else: return 1
            text = py.transform.scale(font.render(str(self.score),1,(1,1,1)),(WINDOW_WIDTH,WINDOW_HEIGHT))
            screen.blit(text,(0,0))
        return 0

def main():
    global screen
    global WINDOW_WIDTH
    global WINDOW_HEIGHT
    game = Game()
    done = False
    while not done:
        for event in py.event.get():
            if event.type == py.QUIT: done = True
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
            done = True
        display_surf = py.transform.scale(game.surface,(WINDOW_WIDTH,WINDOW_HEIGHT))
        screen.blit(display_surf,(0,0))
        py.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()

py.quit()
