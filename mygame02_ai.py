import pygame
import pygame.locals as locals
import random
import neural_network
import aigame_config as config

import numpy as np

pygame.init()
np.set_printoptions(suppress=True)


class Line(object):
    def __init__(self):
        self.HEIGHT = 3   # 线宽
        self.WIDTH = Game.SIZE[0]  # 线长
        self.surf = pygame.Surface((self.WIDTH, self.HEIGHT))   # 线放在屏幕
        self.surf.fill((0, 0, 0))  # 颜色（黑色）

    def draw(self,surface):#将黑块画在屏幕上
        surface.blit(self.surf,(0,int(Game.SIZE[1]/2)))   # 在屏幕上绘制线


class Obstacle(object):
    IMG0 = pygame.image.load("./res/up.png")  # 障碍物图片

    IMG1 = pygame.transform.rotate(IMG0,180)  # 倒转障碍物

    Imgs =  []
    Imgs.append(IMG0)
    Imgs.append(IMG1)
    WIDTH = IMG0.get_width()  # 图片宽度

    def __init__(self,num):
        self.num = num
        self.y = int(Game.SIZE[1]/2)   # 初始化障碍物位置
        self.x = Game.SIZE[0]
        if num==0:
            self.y-=Obstacle.Imgs[num].get_height()
        self.score = 1

    def draw(self,surface):
        surface.blit(Obstacle.Imgs[self.num],(self.x,self.y))  # 展示

    def update(self):
        self.x -= 5

    def add_score(self,score,hero):

        if hero.x > self.x + Obstacle.WIDTH and self.score == 1:
            score.score += self.score
            self.score = 0


class ObstacleManager(object):
    def __init__(self,surface,score,hero):
        self.obstacles = []
        self.surface = surface
        self.count = 0

        self.score = score
        self.hero = hero

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
            obstacle.add_score(self.score,self.hero)
        #     else:
        #         self.obstacles.remove(obstacle)
            index -= 1

    def createObstacal(self):  # 生成管道
        self.count += 1
        if self.count % 20 == 0:
            self.obstacles.append(Obstacle(random.randint(0,1)))
            self.count = 0


class Hero(object):
    IMG = pygame.image.load("./res/hero.png")
    WIDTH = IMG.get_width()
    HEIGHT = IMG.get_height()

    def __init__(self,network):
        self.temp = Hero.IMG.get_height()
        self.x = 30
        self.y = int(Game.SIZE[1]/2)-Hero.IMG.get_height()
        self.alive = True
        self.neural_network = network

    def draw(self,surface):
        surface.blit(Hero.IMG,(self.x,self.y))

    def update(self,obstacals):
        # self.y+=self.temp
        # self.temp = -self.temp

        obstacal = None
        for obs in obstacals:
            if self.x < obs.x + Obstacle.WIDTH:
                obstacal = obs
                break
        inputs = self.get_inputs(obstacal)
        result = self.neural_network.getResult(inputs)
        if result[0] > 0.5:
            self.y += self.temp
            self.temp = -self.temp


    def knock(self,obstacals):
        for obstacal in obstacals:
            if self.x < obstacal.x+ Obstacle.IMG0.get_width():
                if (self.x + Hero.IMG.get_width()) >= obstacal.x and self.x<(obstacal.x+Obstacle.IMG0.get_width()):
                    if (self.y-180<0 and obstacal.y-180<0) or (self.y-180>=0 and obstacal.y-180>=0):
                        self.alive = False

    def get_inputs(self,obstacle):
        inputs = []
        for _ in range(config.network[0]):
            inputs.append(0.0)
        inputs[0] = self.y/Game.SIZE[1]
        if obstacle:
            inputs[1] = (self.x + Hero.IMG.get_width())-obstacle.x
            inputs[2] = self.x - (obstacle.x+Obstacle.IMG0.get_width())
            inputs[3] = self.y - obstacle.y

        return inputs

class Score(object):
    def __init__(self):
        self.score = 0
        self.all_imgs = []
        for i in range(10):
            img = pygame.image.load("./res/"+str(i)+".png")
            self.all_imgs.append(img)
        self.x = 0  # 初始化图片位置
        self.y = 30
        self.imgs = []

    def draw(self,surface):
        pre_width = 0
        for img in self.imgs:
            surface.blit(img, (self.x + pre_width, self.y))
            self.x = self.x + pre_width
            pre_width = img.get_width()

    def update(self):
        self.imgs.clear()
        indexs = self.splitScore()
        for i in indexs:
            self.imgs.append(self.all_imgs[i])
        width = 0
        for img in self.imgs:
            width += img.get_width()
        self.x = Game.SIZE[0] / 2 - width / 2

    def splitScore(self):
        index_list = []
        i = 1
        score = self.score
        while True:
            ret = score % 10
            index_list.insert(0,ret)
            score = int(self.score / 10 ** i)
            if score == 0:
                break
            i += 1
        return tuple(index_list)

class Game(object):
    SIZE = (720,360)
    FPS = 30

    def __init__(self):
        self.surface = pygame.display.set_mode(Game.SIZE)
        self.clock = pygame.time.Clock()
        self.game_init()


    def game_init(self):
        self.Running = True
        self.line = Line()

        weight_array = np.loadtxt("./res/my_modle.csv")
        network = neural_network.Neural_Network(config.network[0],config.network[1],config.network[2])
        data = network.getNetwork()
        if len(data['weights']) == len(weight_array):
            for i in range(len(data['weights'])):
                data['weights'][i] = weight_array[i]
        network.setNetwork(data)
        self.hero = Hero(network)

        self.score = Score()
        self.obstacal_manager = ObstacleManager(self.surface,self.score,self.hero)

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


    def draw(self):
        self.surface.fill((255,255,255))
        self.line.draw(self.surface)
        # self.obstacal.draw(self.surface)
        self.hero.draw(self.surface)
        self.obstacal_manager.draw_obstacles()
        self.score.draw(self.surface)

    def update(self):
        self.hero.knock(self.obstacal_manager.obstacles)
        if not self.hero.alive:
            self.restart()
            return

        # self.obstacal.update()
        self.obstacal_manager.update_obstacles()
        self.hero.update(self.obstacal_manager.obstacles)
        self.score.update()



    def stop(self):
        self.Running = False

    def restart(self):
        self.game_init()


if __name__=='__main__':
    game = Game()
    game.start()