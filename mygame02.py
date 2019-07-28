import pygame
import pygame.locals as locals
import random

pygame.init()

class Line(object):
    def __init__(self):
        self.HEIGHT = 3
        self.WIDTH = Game.SIZE[0]
        self.surf = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.surf.fill((0, 0, 0))

    def draw(self,surface):#将黑块画在屏幕上
        surface.blit(self.surf,(0,int(Game.SIZE[1]/2)))


class Obstacle(object):
    IMG0 = pygame.image.load("./res/up.png")

    IMG1 = pygame.transform.rotate(IMG0,180)

    Imgs =  []
    Imgs.append(IMG0)
    Imgs.append(IMG1)


    def __init__(self,num):
        self.num = num
        self.y = int(Game.SIZE[1]/2)
        self.x = Game.SIZE[0]
        if num==0:
            self.y-=Obstacle.Imgs[num].get_height()

    def draw(self,surface):
        surface.blit(Obstacle.Imgs[self.num],(self.x,self.y))

    def update(self):
        self.x -= 5

class ObstacleManager(object):
    def __init__(self,surface):
        self.obstacles = []
        self.surface = surface
        self.count = 0

    def draw_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.draw(self.surface)

    def update_obstacles(self):
        self.createObstacal()
        index = len(self.obstacles) - 1
        while index >= 0:
            obstacle = self.obstacles[index]
        #     if obstacle.alive:
            obstacle.update()
        #     else:
        #         self.obstacles.remove(obstacle)
            index -= 1

    def createObstacal(self):  # 生成管道
        self.count += 1
        if self.count % 80 == 0:
            self.obstacles.append(Obstacle(random.randint(0,1)))
            self.count = 0




class Hero(object):
    IMG = pygame.image.load("./res/hero.png")

    def __init__(self):
        self.temp = Hero.IMG.get_height()
        self.x = 30
        self.y = int(Game.SIZE[1]/2)-Hero.IMG.get_height()
        self.alive = True

    def draw(self,surface):
        surface.blit(Hero.IMG,(self.x,self.y))

    def update(self):
        self.y+=self.temp
        self.temp = -self.temp

    def knock(self,obstacals):
        for obstacal in obstacals:
            if self.x < obstacal.x+ Obstacle.IMG0.get_width():
                if (self.x + Hero.IMG.get_width()) >= obstacal.x and self.x<(obstacal.x+Obstacle.IMG0.get_width()):
                    if (self.y-180<0 and obstacal.y-180<0) or (self.y-180>=0 and obstacal.y-180>=0):
                        self.alive = False

class Game(object):
    SIZE = (720,360)
    FPS = 60
    def __init__(self):
        self.surface = pygame.display.set_mode(Game.SIZE)
        self.clock = pygame.time.Clock()
        self.Running = True
        self.line = Line()
        # self.obstacal = Obstacle(random.randint(0,1))
        self.hero = Hero()
        self.obstacal_manager = ObstacleManager(self.surface)


    def start(self):
        while self.Running:
            self.control()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(Game.FPS)

    def control(self):
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self.stop()
            if event.type == locals.KEYDOWN:
                if event.key == locals.K_SPACE:
                    self.hero.update()


    def draw(self):
        self.surface.fill((255,255,255))
        self.line.draw(self.surface)
        # self.obstacal.draw(self.surface)
        self.hero.draw(self.surface)
        self.obstacal_manager.draw_obstacles()

    def update(self):
        self.hero.knock(self.obstacal_manager.obstacles)
        # self.obstacal.update()
        self.obstacal_manager.update_obstacles()
        if self.hero.alive == False:
            self.restart()
            print("a")


    def stop(self):
        self.Running = False

    def restart(self):
        self.__init__()


if __name__=='__main__':
    game = Game()
    game.start()