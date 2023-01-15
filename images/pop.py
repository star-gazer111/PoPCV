import mediapipe as mdp
import pygame as pyg
import numpy 
import cv2
import random
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

pyg.init()
info = pyg.display.Info()

mdp_draw = mdp.solutions.drawing_utils
mdp_draw_styles = mdp.solutions.drawing_styles
mdp_hands = mdp.solutions.hands
hands = mdp_hands.Hands()


height, width = info.current_h, info.current_w
scr= pyg.display.set_mode((width, height))
pyg.display.set_caption('Balloon Pop')
background = pyg.image.load('images/back.png').convert_alpha()
background = pyg.transform.scale(background,(width, height))
health = 5
red_kill_count = 0

class Intro_anim_bubble(pyg.sprite.Sprite):
    def __init__(self,bubble,x,y,speed):
        pyg.sprite.Sprite.__init__(self,self.containers)
        self.image = pyg.image.load(bubble).convert_alpha()
        self.image = pyg.transform.scale(self.image,(75,75))
        self.rect = self.image.get_rect()
        self.rect.y, self.rect.x, self.speed = y, x, speed
        
    def update(self):
        scr.blit(self.image, (self.rect))
        if self.rect.y <=0:
            self.kill()
        elif self.rect.y<=height:
            self.rect.y -= self.speed

def Home_Page(background):
    pyg.init()
    font = pyg.font.Font(None,25)
    game_on, game_over = True, False
    max_bubble= 15
    next_batch = 10
    pyg.time.set_timer(next_batch, 2000)    
    number_of_bubbles = pyg.sprite.Group()
    Intro_anim_bubbleSprite = pyg.sprite.Group()
    Intro_anim_bubble.containers = Intro_anim_bubbleSprite, number_of_bubbles
    while game_on:
        for event in pyg.event.get():
            if event.dict.get('key')==27:
                game_on = False
            elif event.type == pyg.KEYDOWN:
                game_on = False
            elif event.type == next_batch:
                for r in range(random.randint(2,3)):
                    Intro_anim_bubble('images/bubble.png', random.randint(0,width), height, 0.1*random.randint(1,4))
        if len(number_of_bubbles) < max_bubble:
            for r in range(random.randint(2,3)):
                Intro_anim_bubble('images/bubble.png', random.randint(0,width), height, 0.1*random.randint(1,4))
                

        scr.blit(background,(0,0))
        start_text = font.render('Enter a key to Start', True,(0,255,0),None)
        scr.blit(start_text, (width//2 -90,height//2 -10))
        Intro_anim_bubbleSprite.update()
        pyg.display.flip()

class bubble_class(pyg.sprite.Sprite):
    def __init__(self,bubble,x,y,speed,color):
        pyg.sprite.Sprite.__init__(self,self.containers)
        self.image = pyg.image.load(bubble).convert_alpha()
        self.image = pyg.transform.scale(self.image,(75,75))
        self.rect = self.image.get_rect()
        self.rect.y, self.rect.x = y, x
        self.speed, self.radius = speed, 25
        self.speed_x = self.speed
        self.count = 0
        self.color = color

        
    def update(self,score, position):
        global health
        global red_kill_count
        scr.blit(self.image, (self.rect))
        if self.rect.y <=0:
            if self.color == 'blue':
                health -= 1
            self.kill()
        elif self.rect.y<=height and self.speed!=0:
            if self.rect.x >= (width - 90):
                self.rect.x = width - 90
                self.speed_x *= -1
                count = -10
            self.rect.y -= self.speed
            self.rect.x += self.speed_x
            self.count += 1
            if(self.count >= 20):
                self.count = 0
                x = random.randint(0,1)
                if(x==0):
                    self.speed_x *= -1
            if self.rect.collidepoint(*position):
                burst_sound = pyg.mixer.Sound('music/burst.wav')
                pyg.mixer.Sound.play(burst_sound)
                if self.color == 'blue':
                    burst = pyg.image.load('images/bubble_burst.png').convert_alpha()
                    score += 10
                else:
                    burst = pyg.image.load('images/bubble_burst_red.png').convert_alpha()
                    red_kill_count += 1
                    if(red_kill_count >= 4):
                        health -= 1
                        red_kill_count = 0
                    score -= 10
                burst = pyg.transform.scale(burst, (135,100))
                self.image = burst
                scr.blit(burst, (self.rect.x, self.rect.y))
                self.kill()
        return score

    def collide(self, all_bubble_list):
        collections = pyg.sprite.spritecollide(self, all_bubble_list, False, pyg.sprite.collide_circle)
        for each in collections:
            if each.speed == 0:
                self.speed = 0

def get_frame(cap):
    success, frame = cap.read()
    frame = cv2.resize(frame, (width, height))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame)
    x1, y1 = 0,0
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0].landmark
        single_finger = hand_landmarks[8]
        x1, y1 = width - int(single_finger.x*width), int(single_finger.y*height)

        for hand_landmarks in results.multi_hand_landmarks:
            mdp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mdp_hands.HAND_CONNECTIONS,
                mdp_draw_styles.get_default_hand_landmarks_style(),
                mdp_draw_styles.get_default_hand_connections_style())
    
    frame = numpy.rot90(frame)
    frame = pyg.surfarray.make_surface(frame)
    return frame, (x1,y1)


def heart_render(health):
    global width
    for i in range(health):
        heart_image = pyg.image.load('images/heart.png').convert_alpha()
        scr.blit(heart_image, (width-i*65-70,0))

def main_window(background):
    pyg.mixer.init()
    pyg.mixer.music.load('music/GAMETHEME.mp3')
    pyg.mixer.music.play(loops = -1)
    back = pyg.image.load('images/black.jpg').convert()
    back = pyg.transform.scale(back,(width, height))
    game_over_image = pyg.image.load('images/gameover.png')
    global health
    font = pyg.font.Font(None, 60)
    bubble_drop = 10
    pyg.time.set_timer(bubble_drop, 3000)
    score = 0
    game_over = False
    all_bubble_list = pyg.sprite.Group()
    all_sprites = pyg.sprite.Group()
    bubble_class.containers = all_sprites, all_bubble_list
    Home_Page(background)
    menu()
    cap=cv2.VideoCapture(0)
    pyg.mixer.init()
    pyg.mixer.music.load('music/GAMERUNMUSIC.wav')
    pyg.time.delay(500)
    pyg.mixer.music.play(loops = -1)
    
    while not game_over:
        for event in pyg.event.get():
            if event.dict.get('key') == 27:
                game_over = True
            elif event.type == bubble_drop:
                for r in range(random.randint(2,3)):
                    bubble_class('images/bubble.png', random.randint(0,width-100), height, random.randint(1,3), 'blue')
                for r in range(random.randint(0,1)):
                    bubble_class('images/bubble_red.png', random.randint(0,width-100), height, random.randint(1,3), 'red')

        frame, position = get_frame(cap)
        scr.blit(frame, (0,0))
        score_text = font.render(f'Score: {score}', True, (0,255,0 ), None)
        scr.blit(score_text, (10,10))
        heart_render(health)

        if health <= 0:
            game_over_sound = pyg.mixer.Sound('music/game-over.wav')
            pyg.mixer.Sound.play(game_over_sound)
            scr.blit(back, (0,0))
            scr.blit(game_over_image,(width/2-145,height/2-95))
            pyg.display.flip()
            pyg.time.delay(1000)
            game_over  =  True

        if not game_over:
            for bubble in all_bubble_list:
                score = bubble.update(score, position)
            for bubble in all_bubble_list:
                all_bubble_list.remove(bubble)
                bubble.collide(all_bubble_list)
                all_bubble_list.add(bubble)
        else:
            all_sprites.clear(scr, background)
            
        pyg.display.flip()
        pyg.time.Clock().tick(60)    
  
def menu():
    back = pyg.image.load('images/black.jpg').convert()
    back = pyg.transform.scale(back,(width, height))
    start_image = pyg.image.load('images/111.png').convert()
    about_image = pyg.image.load('images/222.png').convert()
    help_image = pyg.image.load('images/333.png').convert()
    quit_image = pyg.image.load('images/444.png').convert()
    team_image = pyg.image.load('images/team_name.png').convert()
    logo = pyg.image.load('images/logo.png').convert_alpha()
    about_2 = pyg.image.load('images/about_2.png').convert()
    help_2 = pyg.image.load('images/help_2.png').convert()
    max_bubble = 25   
    number_of_bubbles = pyg.sprite.Group()
    Intro_anim_bubbleSprite = pyg.sprite.Group()
    Intro_anim_bubble.containers = Intro_anim_bubbleSprite, number_of_bubbles
    while True:
        for event in pyg.event.get():
            if event.type == pyg.MOUSEBUTTONDOWN:
                                    mx , my = pyg.mouse.get_pos()
                                    if mx > width-300 and mx < width-20:
                                            if my > 100 and my < 208:
                                                    flag = False
                                                    scr.blit(back, (0,0))
                                                    scr.blit(start_image,(width-300,100))
                                                    scr.blit(about_image,(width-300,250))
                                                    scr.blit(help_image,(width-300,400))
                                                    scr.blit(quit_image,(width-300,550))
                                                    scr.blit(team_image,(0,height-150))
                                                    scr.blit(logo,(200,100))
                                                    pyg.display.flip()
                                                    return
                                            elif my > 250 and my < 358:
                                                    scr.blit(back, (0,0))
                                                    scr.blit(about_2,(width/2-250,height/2-250))
                                                    pyg.display.flip()
                                                    pyg.time.delay(4000)
                                            elif my > 400 and my < 508:
                                                    scr.blit(back, (0,0))
                                                    scr.blit(help_2,(width/2-250,height/2-250))
                                                    pyg.display.flip()
                                                    pyg.time.delay(5000)
                                            elif my > 550 and my < 658:
                                                    flag = False
                                                    pyg.quit()
            
            if len(number_of_bubbles) < max_bubble:
                for r in range(random.randint(4,5)):
                    Intro_anim_bubble('images/bubble.png', random.randint(0,width-500), height, 0.1*random.randint(1,4))
            
        scr.blit(back, (0,0))
        scr.blit(start_image,(width-300,100))
        scr.blit(about_image,(width-300,250))
        scr.blit(help_image,(width-300,400))
        scr.blit(quit_image,(width-300,550))
        scr.blit(team_image,(0,height-150))
        scr.blit(logo,(200,100))
        Intro_anim_bubbleSprite.update()
        pyg.display.flip()
    

if __name__ == '__main__':
    main_window(background)
    pyg.quit()
    
