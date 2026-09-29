import pygame
import random
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)
screen = pygame.display.set_mode(
    (1920,1080),
    pygame.RESIZABLE|pygame.SCALED|pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN,
    vsync=1
)

clock = pygame.time.Clock()
FPS = 60

terrain = []
tx = -360
ty = 360
Gdebug=[]
Sdebug=[]
GSdebug=False

def generate_terrain():
    global tx,ty
    terrain.append((tx,1080))
    terrain.append((tx,1080-ty))
    s = 4 #spikiness
    g = 0 #gradient
    gv=5 #gradient variability, how often gradient changes
    sv=10 #spikiness, as above
    for i in range(1000):
        
        if random.randint(1,10)==1:
            g-=5 #create chasm
            ty-=20
            s+=random.randint(-1,1)
        if random.randint(1,10)==1:
            g+=5 #create mountain
            ty+=20
            s+=random.randint(-1,1)
        if ty < 50:
            g+=3
            ty+=20
        if ty > 720:
            g-=5
            ty-=50
        if 60 < ty < 720:    #only randomise gradient and spikyness at non extreme y values
            if random.randint(1,int(100/gv))==1:
                g = random.randint(-15,15)
            if random.randint(1,int(100/sv))==1:    
                s = random.randint(1,8)
       
        if s < 1: s = 1#clamp g and s within bounds
        if s > 5: s = 5
        if g < -25: g = -15
        if g > 25: g = 15


        if random.randint(1,5)!=1:#1/5 chance to be flat
            ty+=random.randint(s*(g-25),s*(g+25))#add new x and y coordinates
        tx+=random.randint(int(100/s),int(200/s))
            
        terrain.append((tx,1080-ty))
        Gdebug.append((tx,540-10*g))
        Sdebug.append((tx,800-10*s))

    terrain.append((tx,1080))


generate_terrain()
stars = [(random.randint(0, 1920), random.randint(0, 1080), random.randint(1, 2)) for _ in range(69)]
cam_x=0

class Ball:
    def __init__(self,x,y,radius,colour):
        self.x=x
        self.y=1080-y
        self.r=radius
        self.colour=colour
        self.vx=5
        self.vy=0
        self.surface = pygame.Surface((self.r * 2, self.r * 2),pygame.SRCALPHA)
        pygame.draw.circle(self.surface,(255, 255, 255, 255),(radius, radius),radius)
        self.mask = pygame.mask.from_surface(self.surface)
    def movement(self):
        g = 0.2#gravity
        ar = 0.0001#air resistance
        
        self.vy += g # apply g
        
        if self.vx < 0: # air resistance
            self.vx += self.vx**2*ar#add if negative
        if self.vx > 0:
            self.vx -= self.vx**2*ar#subtract if positive
            
        if self.vy < 0: # air resistance (for Y)
            self.vy += self.vy**2*ar
        if self.vy > 0:
            self.vy -= self.vy**2*ar
            
            
        self.x+=self.vx#apply velocity
        self.y+=self.vy
        
        
    def collision(self):
        terrain_mask = pygame.mask.from_threshold(screen, (128, 128, 128,255),(1,1,1,255))
        if terrain_mask.overlap(self.mask,(self.x-cam_x-self.r,self.y-self.r)) != None:
        #binary search to find the two closest terrain coordinates
            left, right = 0, len(terrain) - 1
            while left < right:
                mid = (left + right) // 2
                if terrain[mid][0] < self.x:
                    left = mid + 1
                else:
                    right = mid
            R = max(0, min(right, len(terrain) - 2))#prevent extreme values
            L=R-1 #left and right coords
            #get normal
            dx= terrain[R][0]-terrain[L][0]
            dy= terrain[R][1]-terrain[L][1]
            
            length=(dx**2+dy**2)**0.5
            if int(self.x) == terrain[L][0] or int(self.x) == terrain[R][0]:#collision between 2 points
                nx = 0
                ny = 1
            else:
                nx = -dy / length
                ny = dx / length#rotate 90 degrees and make magnitude 1
            
            dot=self.vx*nx+self.vy*ny
            self.vx-=2*dot*nx
            self.vy-=2*dot*ny
            while terrain_mask.overlap(self.mask,(self.x-cam_x-self.r,self.y-self.r)) != None:
                self.x-nx
                self.y-=ny
            
            
            
    def draw(self):
        pygame.draw.circle(screen,self.colour,(self.x-cam_x,self.y),self.r)
        
        


ball = Ball(480,1000,10,(255,0,0))








while True:
    dt = clock.tick(FPS)/1000
    fps = clock.get_fps()
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit()
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                pygame.quit()
            if e.key==pygame.K_r:
                cam_x=0
                terrain = []
                tx = 0
                ty = 360
                Gdebug=[]
                Sdebug=[]
                generate_terrain()
                ball = Ball(480,1000,10,(255,0,0))
            if e.key ==pygame.K_SPACE:
                ball.vy=-ball.vy
                
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        cam_x+=20
    if keys[pygame.K_a]:
        cam_x-=20
                
                
    screen.fill((0,0,0))
    for x,y,r in stars:
        pygame.draw.circle(screen,(255,255,255),(x, y),r)
        
    pygame.draw.rect(screen, (250, 50, 0), (0, 1020, 1920, 60))
    
    
    cam_x+= (ball.x-720-cam_x)*0.1
    pygame.draw.polygon(screen,(128,128,128),[(x-cam_x,y) for x,y in terrain])
    ball.movement()
    ball.collision()
    
    ball.draw()
    
    
    if GSdebug==True:
        pygame.draw.lines(screen,(0,255,0),False,[(x-cam_x,y) for x,y in Gdebug],3)
        pygame.draw.lines(screen,(0,0,255),False,[(x-cam_x,y) for x,y in Sdebug],3)
        pygame.draw.line(screen,(0,255,0),(0,390),(1920,390))
        pygame.draw.line(screen,(0,255,0),(0,540),(1920,540))
        pygame.draw.line(screen,(0,255,0),(0,690),(1920,690))
        pygame.draw.line(screen,(0,0,255),(0,800),(1920,800))
        
    screen.blit(font.render("FPS:"+str(int(fps)),True,(255,255,255)),(0,0))

    
    pygame.display.flip()