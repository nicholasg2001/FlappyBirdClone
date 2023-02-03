import pygame
from pygame.locals import *
import random

#intializing game
pygame.init()

clock = pygame.time.Clock()
fps = 60

#define size of game window
screenWidth = 864
screenHeight = 936
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)

#define colors
white = (255, 255, 255)

#define game variables
groundScroll = 0
scrollSpeed = 4
flying = False
gameOver = False
pipeGap = 150
pipeFrequency = 1500 #milliseconds
lastPipeCreated = pygame.time.get_ticks() - pipeFrequency
score = 0
passPipe = False


#load images
backgroundImage = pygame.image.load('bgFlappybird.png')
groundImage = pygame.image.load('groundFlappybird.png')
buttonImage = pygame.image.load('restart.png')


def drawText(text, font, textColor, x, y):
    image = font.render(text, True, textColor)
    screen.blit(image, (x, y))

def resetGame():
    pipeGroup.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screenHeight / 2)
    score = 0
    return score 


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            image = pygame.image.load(f'bird{num}.png')
            self.images.append(image)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.clicked = False


    def update(self):
        
        #gravity mechanics
        if flying:
            self.velocity += 0.5
            #cap velocity at 8 
            if self.velocity > 8:
                self.velocity = 8
            #bird only drops if it's above ground
            if self.rect.bottom < 768: 
                self.rect.y += int(self.velocity)
        if gameOver == False:
            #jumping mechanics
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.velocity = -10
            #prevents user from being able to hold mouse to jump
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
                
            #handle the animation
            self.counter += 1
            flapCooldown = 5
        
            if self.counter > flapCooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            #rotate bird
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipeGap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipeGap / 2)]

    def update(self):
        self.rect.x -= scrollSpeed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self):

        action = False
        
        #get mouse position
        position = pygame.mouse.get_pos()
        #check if mouse is over button
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

birdGroup = pygame.sprite.Group()
pipeGroup = pygame.sprite.Group()

flappy = Bird(100, int(screenHeight / 2))

birdGroup.add(flappy)

#create restart button instance
button = Button(screenWidth // 2 - 50, screenHeight // 2 - 100, buttonImage)

#game loop variable
run = True

#main game loop
while run:

    clock.tick(fps)

    #draw background
    screen.blit(backgroundImage, (0,0))

    birdGroup.draw(screen)
    birdGroup.update()

    pipeGroup.draw(screen)
    
    #draw the ground
    screen.blit(groundImage, (groundScroll,768))

    #check score
    if len(pipeGroup) > 0:
        if birdGroup.sprites()[0].rect.left > pipeGroup.sprites()[0].rect.left\
            and birdGroup.sprites()[0].rect.right < pipeGroup.sprites()[0].rect.right\
            and passPipe == False:
            passPipe = True
        if passPipe:
           if birdGroup.sprites()[0].rect.left > pipeGroup.sprites()[0].rect.right:
                score += 1
                passPipe = False

    drawText(str(score), font, white, int(screenWidth / 2), 20)
    #look for collision
    if pygame.sprite.groupcollide(birdGroup, pipeGroup, False, False)  or flappy.rect.top < 0:
        gameOver = True

    #check if bird hits the ground
    if flappy.rect.bottom >= 768:
        gameOver = True
        flying = False

    if gameOver == False and flying:

        #make new pipes
        timeNow = pygame.time.get_ticks()
        if timeNow - lastPipeCreated > pipeFrequency:
            pipeHeight = random.randint(-100, 100)
            bottomPipe = Pipe(screenWidth, int(screenHeight / 2) + pipeHeight, -1)
            topPipe = Pipe(screenWidth, int(screenHeight / 2) + pipeHeight, 1)
            pipeGroup.add(bottomPipe)
            pipeGroup.add(topPipe)      
            lastPipeCreated = timeNow

        #scroll ground
        groundScroll -= scrollSpeed
        if abs(groundScroll) > 35:
            groundScroll = 0

        pipeGroup.update()

    #check for game over and reset
    if gameOver:
        if button.draw():
            gameOver = False
            score = resetGame()



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and gameOver == False:
            flying = True
    pygame.display.update()

pygame.quit()