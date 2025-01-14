import pygame, time
from os import system

def cls() : system("cls")
def sign(n) : return +1 if n > 0 else -1
def dist(p1, p2) : return ( (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 ) ** 0.5

screenRes = [1200, 800]
borders, muBorder, eBorder = [10, 10], 0.01, 0.99

class obj:
    grid, radiusMax = list(), 100
    mu, g = 0.5, 10
    objects = list()

    for x in range(int( 2 + screenRes[0] / radiusMax )):
        grid.append( list() )
        for y in range(int( 2 + screenRes[1] / radiusMax )):
            grid[x].append( list() )

    def __init__ (self, m, r, pos, vel, colour, image, mu = 0, e = 1, theta = 0, angVel = 0):
        self.m = m
        self.r = min(obj.radiusMax, r)

        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        obj.grid [int( self.pos[0]/obj.radiusMax )][int( self.pos[1]/obj.radiusMax )] .append(self)

        self.e, self.mu = e, mu
        self.colour = colour
        self.image = pygame.transform.scale(image, (self.r * 2, self.r * 2))
        self.theta = theta
        self.angVel = angVel
        self.moi = self.m * self.r * self.r / 2

        self.n = len( obj.objects )
        obj.objects.append(self)

    def display (self):
        pygame.draw.circle(screen, self.colour, self.pos, self.r)

        img = pygame.transform.rotate(self.image, self.theta)
        screen.blit( img, (self.pos[0] - img.get_width()/2, self.pos[1] - img.get_height()/2) )

    def update (self, dt):
        obj.grid [int( self.pos[0]/obj.radiusMax )][int( self.pos[1]/obj.radiusMax )] .remove(self)

        # friction [here]

        self.pos = self.pos + self.vel*dt
        self.theta =  (self.theta + self.angVel*dt ) % 360

        if not ( borders[0] + self.r < self.pos[0] < screenRes[0] - borders[0] - self.r ):
            self.pos[0] = min(screenRes[0] - borders[0] - self.r, max(self.pos[0], borders[0] + self.r) )
            J = self.m * abs(self.vel[0]) * (1 + eBorder)
            self.vel[0] = - self.vel[0] * eBorder

            Jf = min( (muBorder * J), abs( self.vel[1] * self.m ) )
            self.angVel += -Jf * self.r / self.moi
            self.vel[1] -= sign(self.vel[1]) * Jf / self.m

        if not ( borders[1] + self.r < self.pos[1] < screenRes[1] - borders[1] - self.r ):
            self.pos[1] = min(screenRes[1] - borders[1] - self.r, max(self.pos[1], borders[1] + self.r) )
            J = self.m * abs(self.vel[1]) * (1 + eBorder)
            self.vel[1] = - self.vel[1] * eBorder

            Jf = min( (muBorder * J), abs( self.vel[0] * self.m ) )
            self.angVel += -Jf * self.r / self.moi
            self.vel[0] -= sign(self.vel[0]) * Jf / self.m

        obj.grid [int( self.pos[0]/obj.radiusMax )][int( self.pos[1]/obj.radiusMax )] .append(self)

    def collision (self):
        neighbourhood = [
            [-1, -1], [0, -1], [+1, -1],
            [-1, 0], [0, 0], [+1, 0],
            [-1, +1], [0, +1], [+1, +1]
        ]

        for neighbour in neighbourhood:
            n = [ int( self.pos[0]/obj.radiusMax ) + neighbour[0], int ( self.pos[1]/obj.radiusMax ) + neighbour[1] ]
            if n[0] < 0 or n[1] < 0: continue

            for other in obj.grid[n[0]][n[1]]:
                if  collisions.get( (self.n, other.n) ) != True and dist(other.pos, self.pos) <= self.r + other.r:
                    #Translational Part [...]
                    sep = other.pos - self.pos + pygame.math.Vector2((0.01, 0.01))
                    u1Para = pygame.math.Vector2.project(self.vel, sep)
                    u2Para = pygame.math.Vector2.project(other.vel, sep)
                    u1Perp = self.vel - u1Para
                    u2Perp = other.vel - u2Para
                    e = ( self.e + other.e ) / 2

                    v1Para = ( u1Para * (self.m - e * other.m) + u2Para * other.m * (1 + e) ) / (self.m + other.m)
                    v2Para = ( u2Para * (other.m - e * self.m) + u1Para * self.m * (1 + e) ) / (self.m + other.m)

                    self.vel = v1Para + u1Perp
                    other.vel = v2Para + u2Perp

                    #Rotational Part [...]
                    mu = ( self.mu + other.mu ) / 2
                    # j = mu * 

                    collisions[ (self.n, other.n) ] = True
                    collisions[ (other.n, self.n) ] = True

                    #Logic for stopping the balls to be forced into one another
                    obj.grid [int( self.pos[0]/obj.radiusMax )][int( self.pos[1]/obj.radiusMax )] .remove(self)
                    obj.grid [int( other.pos[0]/obj.radiusMax )][int( other.pos[1]/obj.radiusMax )] .remove(other)

                    self.pos -=  self.m * (self.r + other.r - sep.magnitude()) * (other.pos - self.pos) / ( sep.magnitude() * (self.m + other.m) )
                    other.pos -=  other.m * (self.r + other.r - sep.magnitude()) * (self.pos - other.pos) / ( sep.magnitude() * (self.m + other.m) )

                    obj.grid [int( self.pos[0]/obj.radiusMax )][int( self.pos[1]/obj.radiusMax )] .append(self)
                    obj.grid [int( other.pos[0]/obj.radiusMax )][int( other.pos[1]/obj.radiusMax )] .append(other)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode( screenRes )
    icon = pygame.image.load('images/dumbBall.png')
    pygame.display.set_caption("Rotational Collision for 2D Circular Laminas")
    pygame.display.set_icon(icon)

    obj (10, 45, (200, 200), (120*5, 130*5), (230, 120, 230), pygame.image.load('images/angryBird.png'))
    obj (10, 45, (300, 200), (120*5, 130*5), (130, 220, 230), pygame.image.load('images/cyanBall.png'))
    obj (10, 45, (400, 200), (120*5, 130*5), (130, 120, 230), pygame.image.load('images/greenBall.png'))
    obj (10, 45, (500, 200), (120*5, 130*5), (230, 220, 130), pygame.image.load('images/blueBall.png'))

    cls()
    running = True
    clock = pygame.time.Clock()
    frameRate, dt, FRlimit = 5000, 1/5000, 6969

    while running == True:
        initTime = time.time()
        clock.tick(frameRate*1.42069)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(frameRate)

        #Code Here
        screen.fill( (120, 120, 120) )

        collisions = dict()
        for ball in obj.objects:
            collisions[ (ball.n, ball.n) ] = True
            ball.update(dt)
            ball.display()
            ball.collision()

        pygame.display.update()

        dt = time.time() - initTime
        frameRate = 1 / max(1/FRlimit, dt)