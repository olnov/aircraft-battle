import pygame
import os
import time
import random
pygame.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aircraft battle")

# Loadaing assets
FIGHTER = pygame.image.load(os.path.join("assets","P38_lvl_0_d0.png"))
ENEMY_FIGHTER = pygame.image.load(os.path.join("assets","Aircraft_09.png"))
ENEMY_FIGHTER = pygame.transform.rotate(ENEMY_FIGHTER, 180)
YELLOW_BULLET = pygame.image.load(os.path.join("assets","bullet_2_orange.png"))
PURPLE_ROCKET = pygame.image.load(os.path.join("assets","rocket_purple.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 10

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def move_bullets(self, vel, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            if bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x+83, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = FIGHTER
        self.bullet_img = YELLOW_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        global score
                        score += 10

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = ENEMY_FIGHTER
        self.bullet_img = PURPLE_ROCKET
        self.mask = pygame.mask.from_surface(self.ship_img)
        # self.max_health = health
        
    def draw(self, window):
        return super().draw(window)
    
    def move(self, vel):
        self.y +=vel
        
    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x-20, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    global score
    run = True
    FPS = 60
    level = 0
    lives = 5
    score = 0
    main_font = pygame.font.SysFont("calibri", 30)
    lost_font = pygame.font.SysFont("comicsans", 60)
    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    bullet_vel = 5

    player = Player(300, 630)
    

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        
        score_label = main_font.render(f"Score: {score}",1,(255,255,255))
        lelel_label = main_font.render(f"Level: {level}",1,(255,255,255))
        lives_label = main_font.render(f"Lives: {lives}",1,(255,255,255))
        
        WIN.blit(lelel_label, (10,10))
        WIN.blit(score_label,(WIDTH/2 - score_label.get_width(),10))
        WIN.blit(lives_label,(WIDTH - lives_label.get_width()-10,10))
        player.draw(WIN)
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + FIGHTER.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + FIGHTER.get_height() < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_bullets(bullet_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        for enemy in enemies:
            enemy.move(enemy_vel)
            
        player.move_bullets(-bullet_vel, enemies)
        
        
        
def main_menu():
    game_font = pygame.font.SysFont("unispace", 50)
    title_font = pygame.font.SysFont("colibri", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        game_title = game_font.render("Aircraft battle but in space",1,(0,255,0))
        title_label = title_font.render("Click mouse to begin...", 1, (255,255,255))
        WIN.blit(game_title, (WIDTH/2 - game_title.get_width()/2,300))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()