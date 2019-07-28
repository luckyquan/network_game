import pygame
import pygame.locals as locals
import random
import neural_network
import aigame_config as config
import evolution
import numpy as np
import os

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
        if self.count % 30 == 0:
            self.obstacles.append(Obstacle(random.randint(0,1)))
            self.count = 0




class Hero(object):
    IMG = pygame.image.load("./res/hero.png")

    def __init__(self,network):
        self.temp = Hero.IMG.get_height()
        self.x = 30
        self.y = int(Game.SIZE[1]/2)-Hero.IMG.get_height()
        self.alive = True
        self.neural_network = network

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

    def get_inputs(self,obstacles):
        obstacle = None
        for p in obstacles:
            if self.x < p.x+Obstacle.IMG0.get_width():
                obstacle  = p
                break
        inputs = []
        for _ in range(config.network[0]):
            inputs.append(0.0)
        inputs[0] = self.y/Game.SIZE[1]
        if obstacle:
            inputs[1] = (self.x + Hero.IMG.get_width())-obstacle.x
            inputs[2] = self.x - (obstacle.x+Obstacle.IMG0.get_width())
            inputs[3] = self.y - obstacle.y

        return inputs

class HeroManager(object):
    def __init__(self,ai):
        self.heros = []
        self.ai = ai
        network_data_list = self.ai.manager.create_Generation()

        for network_data in network_data_list:
            network = neural_network.Neural_Network(config.network[0], config.network[1],
                                                    config.network[2])
            network.setNetwork(network_data)
            hero = Hero(network)
            self.heros.append(hero)

    def drawHeros(self,surface):
        for hero in self.heros:
            hero.draw(surface)

    def updateHeros(self,heros,score):
        index = len(self.heros)-1
        while index>=0:
            hero = self.heros[index]
            if hero.alive:
                inputs = hero.get_inputs(heros)
                ret = hero.neural_network.getResult(inputs)
                if ret[0] > 0.5:
                    hero.update()

            else:
                self.ai.collect_score(hero.neural_network,score)
                self.heros.remove(hero)
            index-=1
    def knock(self,obstacles):
        for hero in self.heros:
            hero.knock(obstacles)

    def is_all_died(self):
        if len(self.heros) == 0:
            return True
        return False

class Evolution_ANN_AI(object):
    def __init__(self):
        self.manager = evolution.GenerationManager()
    def collect_score(self,network,score):
        genome = evolution.Genome(network.getNetwork(),score)
        self.manager.add_genome(genome)


class Game(object):
    SIZE = (720,360)
    FPS = 60
    def __init__(self):
        self.surface = pygame.display.set_mode(Game.SIZE)
        self.clock = pygame.time.Clock()
        self.ai = Evolution_ANN_AI()
        self.generation_num = 0
        self.game_init()


    def game_init(self):
        self.Running = True
        self.score = 0
        self.line = Line()
        self.heromanager = HeroManager(self.ai)
        self.obstacal_manager = ObstacleManager(self.surface)
        self.generation_num += 1
    def start(self):
        while self.Running:
            self.control()
            self.update()
            self.draw()
            pygame.display.update()
            print("世代：", self.generation_num, "存活数量：", len(self.heromanager.heros), "分数：", self.score)
            if self.score >= 5000 and not os.path.exists("my_modle.csv"):
                data = self.heromanager.heros[0].neural_network.getNetwork()
                weight_array = np.array(data['weights'])
                np.savetxt("./res/my_modle.csv", weight_array, delimiter=',')
                break
            self.clock.tick(Game.FPS)

    def control(self):
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self.stop()


    def draw(self):
        self.surface.fill((255,255,255))
        self.line.draw(self.surface)
        # self.obstacal.draw(self.surface)
        self.heromanager.drawHeros(self.surface)
        self.obstacal_manager.draw_obstacles()

    def update(self):
        if self.heromanager.is_all_died():
            self.restart()
            return
        self.heromanager.knock(self.obstacal_manager.obstacles)
        # self.obstacal.update()
        self.heromanager.updateHeros(self.obstacal_manager.obstacles,self.score)
        self.obstacal_manager.update_obstacles()
        self.score+=1



    def stop(self):
        self.Running = False

    def restart(self):
        self.game_init()


if __name__=='__main__':
    game = Game()
    game.start()