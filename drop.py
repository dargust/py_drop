import pygame as py
import random
import sys
py.init()

if len(sys.argv) > 1:
    try:
        a,b = sys.argv[1].split('x')
    except:
        print "Incorrect syntax, usage: python drop.py 50x50"
        a,b = 180,320
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

class Game():
    class Player():
        def __init__(self):
            self.size = 5
            self.rect = py.Rect(_width/2-self.size/2,_height-self.size,self.size,self.size)
            self.delta = 0
        def update(self):
            if 0 < self.rect.left+self.delta < _width-self.size: self.rect.left += self.delta
    class Block():
        def __init__(self,delta_delta):
            size = random.randint(4,9)
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
        self.player.update()
        for block in self.block_list:
            if block.rect.colliderect(self.player.rect): self.done = True
            block.update()
        self.surface.fill((255,255,255))
        py.draw.rect(self.surface,(0,0,255),self.player.rect)
        for block in self.block_list: py.draw.rect(self.surface,(0,0,0),block.rect)
        if self.done:
            if self.alpha > 0:
                self.alpha -= 5
                self.surface.set_alpha(self.alpha)
            else:
                self.alpha = 0
                self.surface.set_alpha(self.alpha)
                if self.end_counter > 0: self.end_counter -= 1
                else: return 1
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
        if game.update():
            print game.score
            done = True
        screen.fill((255,255,255))
        display_surf = py.transform.scale(game.surface,(WINDOW_WIDTH,WINDOW_HEIGHT))
        screen.blit(display_surf,(0,0))
        py.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()

py.quit()
