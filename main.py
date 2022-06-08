import win32api
import pygame
import random


def get_fps():
    settings = win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1)
    return getattr(settings, 'DisplayFrequency')


def get_resolution():
    return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)


# System Information
FPS = get_fps()
SCREEN_SIZE = get_resolution()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (200, 200, 200)

DINO1 = pygame.image.load('Sprites/dino-1.png') 
DINO2 = pygame.image.load('Sprites/dino-2.png')
CROUCH_DINO1 = pygame.image.load('Sprites/dino-ducking-1.png')
CROUCH_DINO2 = pygame.image.load('Sprites/dino-ducking-2.png')
BIRB1 = pygame.image.load('Sprites/flappy-bird-1.png')
BIRB2 = pygame.image.load('Sprites/flappy-bird-2.png')
CACTUS1 = pygame.image.load('Sprites/cactus-1.png')
CACTUS2 = pygame.image.load('Sprites/cactus-2.png')
CACTUS3 = pygame.image.load('Sprites/cactus-3.png')
CLOUD1 = pygame.image.load('Sprites/cloud-1.png')
CLOUD2 = pygame.image.load('Sprites/cloud-2.png')
RESTART = pygame.image.load('Sprites/restart_button.png')

JUMP_FRAMES = FPS // 3
LEG_SWAP_FRAMES = FPS // 10
FLAP_FRAMES = FPS // 15
SCORE_FRAMES = FPS // 10
CACTUS_FRAMES_LOW = 100
CACTUS_FRAMES_HIGH = 200
FAR_CLOUD_FRAMES_LOW = 150
FAR_CLOUD_FRAMES_HIGH = 300
CLOSE_CLOUD_FRAMES_LOW = 250
CLOSE_CLOUD_FRAMES_HIGH = 400
BIRB_FRAMES_LOW = 400
BIRB_FRAMES_HIGH = 600

BASE_X = SCREEN_SIZE[0] // 15
BASE_Y = 4 * SCREEN_SIZE[1] // 5

CACTUS_DELAY_LOW = 0
CACTUS_DELAY_HIGH = 50

SPEED_LOWER_BOUND = 0.75
SPEED_UPPER_BOUND = 2


class Cactus(pygame.sprite.Sprite):
    def __init__(self, dt):
        self.dt = dt
        self.image = random.choice((CACTUS1, CACTUS2, CACTUS3))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_SIZE[0] - 1
        self.rect.y = BASE_Y - self.image.get_size()[1]
        self.mask = pygame.mask.from_surface(self.image)
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        self.rect.x -= FPS // 10 * self.dt
        if self.rect.x + self.image.get_size()[0] < 0:
            self.kill()


class FlappyBirb(pygame.sprite.Sprite):
    def __init__(self, dt):
        self.dt = dt
        self.count = 0
        self.wing_orientation = 0
        self.image = BIRB1
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_SIZE[0] - 1
        self.rect.y = random.randint(SCREEN_SIZE[0] // 5, BASE_Y - SCREEN_SIZE[0] // 20) - self.image.get_size()[1]
        self.mask = pygame.mask.from_surface(self.image)
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        self.count = (self.count + 1) % FLAP_FRAMES

        if self.count == 0:
            self.wing_orientation = 1 - self.wing_orientation
            if self.wing_orientation == 0: self.image = BIRB1
            if self.wing_orientation == 1: self.image = BIRB2

        self.rect.x -= FPS // 15 * self.dt
        if self.rect.x + self.image.get_size()[0] < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self, dt, far):
        self.dt = dt
        self.far = far

        if self.far:
            self.image = random.choice((CLOUD1, CLOUD2))
            self.image = pygame.transform.scale(self.image, (75, 75))
            self.image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            self.div_speed = random.randint(30, 60)

        else:
            self.image = random.choice((CLOUD1, CLOUD2))
            self.image = pygame.transform.scale(self.image, (150, 150))
            self.div_speed = random.randint(15, 25)

        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_SIZE[0] - 1

        if self.far:
            self.rect.y = random.randint(self.image.get_size()[1] + SCREEN_SIZE[0] // 15,
                                         self.image.get_size()[1] + SCREEN_SIZE[0] // 6) - self.image.get_size()[1]

        else:
            self.rect.y = random.randint(self.image.get_size()[1],
                                         self.image.get_size()[1] + SCREEN_SIZE[0] // 10) - self.image.get_size()[1]

        pygame.sprite.Sprite.__init__(self)

    def update(self):
        if self.far:
            self.rect.x -= FPS // self.div_speed * self.dt
            if self.rect.x + self.image.get_size()[0] < 0:
                self.kill()

        else:
            self.rect.x -= FPS // self.div_speed * self.dt
            if self.rect.x + self.image.get_size()[0] < 0:
                self.kill()


class DinoRunner:
    def __init__(self):
        pygame.init()

        self.font = pygame.font.SysFont('Comic Sans MS', 75)

        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
        self.clock_tick = pygame.time.Clock()

        restart_rect = RESTART.get_rect()
        restart_rect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)

        self.score = 0
        self.score_counter = 0

        self.crouch_info = {'crouching': False}
        self.jump_info = {'jumping': False, 'count': JUMP_FRAMES}
        self.jump_info = {'jumping': False, 'count': JUMP_FRAMES}

        self.dt = 1

        self.cur_x = BASE_X
        self.cur_y = BASE_Y - DINO1.get_rect().size[1]

        self.current_image = DINO1
        self.cacti = pygame.sprite.OrderedUpdates()
        self.birbs = pygame.sprite.OrderedUpdates()
        self.far_clouds = pygame.sprite.OrderedUpdates()
        self.close_clouds = pygame.sprite.OrderedUpdates()

        self.leg_counter = 0
        self.leg_orientation = 0
        self.cactus_counter = 100
        self.birb_counter = 500
        self.far_cloud_counter = 50
        self.close_cloud_counter = 150

        self.jump_frames = JUMP_FRAMES

        self.speed_dir = SPEED_LOWER_BOUND

        self.paused = self.lost = False

        while True:
            self.screen.fill(LIGHT_GREY)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_x, click_y = event.pos
                    if (self.paused or self.lost) and restart_rect.collidepoint(click_x, click_y):
                        self.reset()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not self.lost:
                        self.paused = not self.paused

                    if (self.paused or self.lost) and event.key == pygame.K_RETURN:
                        self.reset()

            if not self.paused and not self.lost:
                self.score_counter = (self.score_counter + 1) % SCORE_FRAMES
                if self.score_counter == 0:
                    self.score += self.dt

                keys = pygame.key.get_pressed()

                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    self.crouch_info['crouching'] = True
                    self.jump_info['count'] = min(self.jump_info['count'], 0)
                else:
                    self.crouch_info['crouching'] = False

                if not self.crouch_info['crouching'] and (
                        keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]):
                    self.jump_info['jumping'] = True

                self.leg_counter = (self.leg_counter + 1) % LEG_SWAP_FRAMES
                if self.leg_counter == 0 and not self.jump_info['jumping']:
                    self.leg_orientation = 1 - self.leg_orientation

                self.cactus_counter -= 1
                if self.cactus_counter == 0:
                    self.create_cactus()
                    self.cactus_counter = random.randint(CACTUS_FRAMES_LOW, CACTUS_FRAMES_HIGH)

                self.birb_counter -= 1
                if self.birb_counter == 0:
                    self.create_birb()
                    self.cactus_counter += random.randint(CACTUS_DELAY_LOW, CACTUS_DELAY_HIGH)
                    self.birb_counter = random.randint(BIRB_FRAMES_LOW, BIRB_FRAMES_HIGH)

                self.far_cloud_counter -= 1
                if self.far_cloud_counter == 0:
                    self.create_far_cloud()
                    self.far_cloud_counter = random.randint(FAR_CLOUD_FRAMES_LOW, FAR_CLOUD_FRAMES_HIGH)

                self.close_cloud_counter -= 1
                if self.close_cloud_counter == 0:
                    self.create_close_cloud()
                    self.close_cloud_counter = random.randint(CLOSE_CLOUD_FRAMES_LOW, CLOSE_CLOUD_FRAMES_HIGH)

                self.jump()
                self.crouch()
                self.far_clouds.update()
                self.close_clouds.update()
                self.birbs.update()
                self.cacti.update()

            else:
                self.screen.blit(RESTART, restart_rect)

            pygame.draw.line(self.screen, BLACK,
                             (0, BASE_Y - DINO1.get_size()[0] // 5),
                             (SCREEN_SIZE[0], BASE_Y - DINO1.get_size()[0] // 5), width=5)

            self.show_dino(self.leg_orientation)
            self.cacti.draw(self.screen)
            self.birbs.draw(self.screen)
            self.far_clouds.draw(self.screen)
            self.close_clouds.draw(self.screen)

            if not self.paused and not self.lost:
                for cactus in self.cacti:
                    xoffset = self.cur_x - cactus.rect.x
                    yoffset = self.cur_y - cactus.rect.y
                    mask = pygame.mask.from_surface(self.current_image)

                    if cactus.mask.overlap(mask, (xoffset, yoffset)):
                        self.game_over()

                for birb in self.birbs:
                    xoffset = self.cur_x - birb.rect.x
                    yoffset = self.cur_y - birb.rect.y
                    mask = pygame.mask.from_surface(self.current_image)

                    if birb.mask.overlap(mask, (xoffset, yoffset)):
                        self.game_over()

            self.text_surface = self.font.render(f'Score: {int(self.score)}', False, (0, 0, 0))
            self.screen.blit(self.text_surface, (SCREEN_SIZE[0] - self.text_surface.get_size()[0] - 50, 50))

            if self.paused or self.lost:
                self.screen.blit(RESTART, restart_rect)

            if self.dt <= SPEED_LOWER_BOUND: self.speed_dir = 1
            if self.dt >= SPEED_UPPER_BOUND: self.speed_dir = -1
            self.dt += self.speed_dir / 1000

            pygame.display.update()
            self.clock_tick.tick(FPS)

    def reset(self):
        self.score = 0
        self.score_counter = 0

        self.crouch_info = {'crouching': False}
        self.jump_info = {'jumping': False, 'count': JUMP_FRAMES}
        self.jump_info = {'jumping': False, 'count': JUMP_FRAMES}

        self.dt = 1

        self.cur_x = BASE_X
        self.cur_y = BASE_Y - DINO1.get_rect().size[1]

        self.current_image = DINO1
        self.cacti = pygame.sprite.OrderedUpdates()
        self.birbs = pygame.sprite.OrderedUpdates()
        self.far_clouds = pygame.sprite.OrderedUpdates()
        self.close_clouds = pygame.sprite.OrderedUpdates()

        self.leg_counter = 0
        self.leg_orientation = 0
        self.cactus_counter = 100
        self.birb_counter = 500
        self.far_cloud_counter = 50
        self.close_cloud_counter = 150

        self.jump_frames = JUMP_FRAMES

        self.speed_dir = SPEED_LOWER_BOUND

        self.paused = self.lost = False

    def pause(self):
        pass

    def game_over(self):
        self.lost = True
        self.paused = False

    def create_cactus(self):
        cactus = Cactus(self.dt)
        self.cacti.add(cactus)

    def create_birb(self):
        birb = FlappyBirb(self.dt)
        self.birbs.add(birb)

    def create_far_cloud(self):
        far_cloud = Cloud(self.dt, True)
        self.far_clouds.add(far_cloud)

    def create_close_cloud(self):
        close_cloud = Cloud(self.dt, False)
        self.close_clouds.add(close_cloud)

    def show_dino(self, p):
        if not self.crouch_info['crouching']:
            if p == 0: self.screen.blit(DINO1, (self.cur_x, self.cur_y))
            if p == 1: self.screen.blit(DINO2, (self.cur_x, self.cur_y))
        else:
            if p == 0: self.screen.blit(CROUCH_DINO1, (self.cur_x, self.cur_y))
            if p == 1: self.screen.blit(CROUCH_DINO2, (self.cur_x, self.cur_y))

    def jump(self):
        if self.jump_info['jumping']:
            if self.crouch_info['crouching']:
                self.cur_y -= self.jump_info['count'] * 0.2
                self.jump_info['count'] -= 1

                self.cur_y -= self.jump_info['count'] * 0.2
                self.jump_info['count'] -= 1

            else:
                self.cur_y -= self.jump_info['count'] * 0.4
                self.jump_info['count'] -= 1

            if self.cur_y > BASE_Y - self.current_image.get_size()[1]:
                self.cur_y = BASE_Y - self.current_image.get_size()[1]
                self.jump_info = {'jumping': False, 'count': JUMP_FRAMES}
                self.leg_orientation = 1 - self.leg_orientation

    def crouch(self):
        if self.crouch_info['crouching']:
            self.current_image = CROUCH_DINO1
        else:
            self.current_image = DINO1


DinoRunner()
