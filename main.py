import pygame,sys,math
from pygame.math import Vector2

WIDTH,HEIGHT = 800,450
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
clock = pygame.time.Clock()
debug = bool(0)

def lerp(a,b,t):
    return a + (b - a) * t

def distance(point1,point2):
    a = point1.x-point2.x
    b = point1.y-point2.y
    return math.sqrt((a**2)+(b**2))

def DrawAll():
    highestLayer = 0
    for obj in objects:
        if obj.layer > highestLayer:
            highestLayer = obj.layer
    for i in range(highestLayer):
        layerList = []
        for obj in objects:
            if obj.layer == i+1:
                obj.Draw(camera)
    for projectile in projectiles:
        projectile.Draw(camera)
    for collectible in collectibles:
        collectible.Draw(camera)

def ScreenToWorldPoint(screenPoint,camera):
    return Vector2(screenPoint.x-camera.x+(WIDTH/2)-(camera.focus.size.x/2),screenPoint.y-camera.y+(HEIGHT/2)-(camera.focus.size.y/2))

def WorldToScreenPoint(screenPoint,camera):
    return Vector2(screenPoint.x+camera.x-(WIDTH/2)+(camera.focus.size.x/2),screenPoint.y+camera.y-(HEIGHT/2)+(camera.focus.size.y/2))

def ScreenToWorldRect(rect,camera):
    pos = Vector2(rect.x,rect.y)
    pos = ScreenToWorldPoint(pos, camera)
    return pygame.Rect(pos.x,pos.y,rect.width,rect.height)

def loadMap(level):
    f = open(f'Levels/{level}.txt','r')
    data = f.read()
    f.close()
    data = data.split("\n")
    gameMap = []
    for row in data:
        gameMap.append(list(row))
    return gameMap

def createMap(map):
    global gameObjects
    gameObjects = []
    gameObjects.append(player)
    gameObjects.append(gun)
    y=0
    for row in map:
        x=0
        for tile in row:
            if tile == "O":
                player.pos = Vector2(x*32,y*32)
            if tile == "1":
                Object(Vector2(x*32,y*32),Vector2(32,32),"sand-top.png",False,True,"sand")
            if tile == "2":
                Object(Vector2(x*32,y*32),Vector2(32,32),"sand-bottom.png",False,True,"sand")
            if tile == "C":
                Cactus(Vector2(x*32,y*32),Vector2(20,32),"cactus-0-0.png",False,False,"cactus",animate=True)
            x+=1
        y+=1

def DrawUI():
    pygame.draw.rect(screen,(255,0,0),pygame.Rect(10,10,100,10))
    pygame.draw.rect(screen,(0,150,0),pygame.Rect(10,10,player.health,10))

    bullet = pygame.image.load("Assets/bullet-icon.png").convert_alpha()
    for i in range(player.bullets):
        i+=1
        screen.blit(bullet,Vector2(WIDTH-(i*7)-10,10))

def clip(img,pos,size):
    newImg = pygame.surface.Surface((size.x,size.y),pygame.SRCALPHA)
    newImg.blit(img,Vector2(-pos.x,-pos.y))
    return newImg

objects = []
class Object:
    def __init__(self,pos,size,color,doPhysics,collisions,name,velo=Vector2(),layer=1,rotation=0,animate=False,animations=[]): #Layer 0 doesn't get rendered
        self.pos = pos
        self.size = size
        if type(color) == type("string"):
            self.image = pygame.image.load(f'Assets/{color}').convert_alpha()
            self.color = None
        elif type(color) == type((255,255,255)):
            self.color = color
            self.image = None
        self.doPhysics = doPhysics
        self.collider = collisions
        self.name = name
        self.velo = velo
        self.layer = layer
        self.rotation = rotation
        self.animate = animate
        self.animations = animations
        self.animation = 0
        self.frame = 0
        self.flipImage = Vector2()
        objects.append(self)

    def rect(self):
        return pygame.Rect(self.pos.x,self.pos.y,self.size.x,self.size.y)

    def Draw(self,camera):
        if self.rect().colliderect(camera.rect()):
            if self.image:
                if self.animate == False:
                    image = pygame.transform.flip(self.image,bool(self.flipImage.x),bool(self.flipImage.y))
                    image = pygame.transform.rotate(image,self.rotation)
                    imageRect = image.get_rect(center = self.pos)
                    screen.blit(image,Vector2(
                    imageRect.x - camera.x + (WIDTH/2),
                    imageRect.y - camera.y + (HEIGHT/2)))
                    #screen.blit(image,Vector2(self.pos.x-camera.x+(WIDTH/2)-(camera.focus.size.x/2),self.pos.y-camera.y+(HEIGHT/2)-(camera.focus.size.y/2)))
                if self.animate == True:
                    #image = pygame.transform.flip(pygame.image.load(f'Assets/{self.animations[self.animation][self.frame]}').convert_alpha(),bool(self.flipImage.x),bool(self.flipImage.y))
                    image = pygame.transform.flip(pygame.image.load(f'Assets/{self.name}-{self.animation}-{self.frame}.png').convert_alpha(),bool(self.flipImage.x),bool(self.flipImage.y))
                    image = pygame.transform.rotate(image,self.rotation)
                    imageRect = image.get_rect(center = self.pos)
                    screen.blit(image,Vector2(
                    imageRect.x - camera.x + (WIDTH/2),
                    imageRect.y - camera.y + (HEIGHT/2)))
            if self.color:
                drawRect = pygame.Rect(self.pos.x-camera.x+(WIDTH/2)-(camera.focus.size.x/2),self.pos.y-camera.y+(HEIGHT/2)-(camera.focus.size.y/2),self.size.x,self.size.y)
                pygame.draw.rect(screen,self.color,drawRect)

    def Physics(self,gravityScale,friction):
        if self.doPhysics:
            self.velo.y+=1*gravityScale
            self.pos.y+=self.velo.y
            for obj in objects:
                if obj != self and obj.collider:
                    if self.rect().colliderect(obj.rect()):
                        if self.velo.y > 0:
                            self.pos.y = obj.pos.y - self.size.y
                        if self.velo.y < 0:
                            self.pos.y = obj.pos.y + obj.size.y
                        self.velo.y = 0
            self.velo.x*=friction
            self.pos.x+=self.velo.x
            for obj in objects:
                if obj != self and obj.collider:
                    if self.rect().colliderect(obj.rect()):
                        if self.velo.x > 0:
                            self.pos.x = obj.pos.x - self.size.x
                        if self.velo.x < 0:
                            self.pos.x = obj.pos.x + obj.size.x
                        self.velo.x = 0

    def center(self):
        return Vector2(self.pos.x+(self.size.x/2),self.pos.y+(self.size.y/2))

    def newAnimation(self,animation):
        self.animations.append(animation)

    def setAnimation(self,animation):
        if self.animation == animation:
            pass
        if self.animation != animation:
            self.animation = animation
            self.frame = 0

    def collideList(self):
        list = []
        for obj in objects:
            if obj != self:
                if self.rect().colliderect(obj.rect()):
                    list.append(obj)
        return list

entities = []
class Entity(Object):
    def __init__(self,pos,size,color,doPhysics,collisions,name,health,velo=Vector2(),layer=1,rotation=0,animate=False,animations=[]):
        super().__init__(pos,size,color,doPhysics,collisions,name,velo,layer,rotation,animate,animations)
        self.health = health
        entities.append(self)

    def Update(self):
        if self.health <= 0:
            Collectible(self.center(),Vector2(6,8),"Assets/bullet-icon.png","bullet",2)
            for list in allLists:
                if self in list:
                    list.remove(self)

class Player(Entity):
    def __init__(self,pos,size,color,doPhysics,collisions,name,health=100,velo=Vector2(),layer=1,rotation=0,animate=False,animations=[]):
        super().__init__(pos,size,color,doPhysics,collisions,name,health,velo,layer,rotation,animate,animations)
        self.bullets = 6
    
    def grounded(self):
        grounded = False
        rect = pygame.Rect(self.pos.x,self.pos.y,self.size.x,self.size.y+1)
        for obj in objects:
            if obj != self and obj.collider:
                if rect.colliderect(obj.rect()):
                    grounded = True
        return grounded

cacti = []
class Cactus(Entity):
    def __init__(self,pos,size,color,doPhysics,collisions,name,health=20,velo=Vector2(),layer=1,rotation=0,animate=False,animations=[]):
        super().__init__(pos,size,color,doPhysics,collisions,name,health,velo,layer,rotation,animate,animations)
        self.newAnimation(("cactus-0-0.png","cactus-0-1.png","cactus-0-2.png","cactus-0-3.png"))
        self.newAnimation(("cactus-1-0.png","cactus-1-1.png","cactus-1-2.png","cactus-1-3.png"))
        cacti.append(self)
        self.target = None
        self.cooldown = 150

    def Shoot(self):
        self.cooldown -= 1
        if player.rect().colliderect(pygame.Rect(self.pos.x-128,self.pos.y-128,288,288)):
            self.target = player
        else:
            self.target = None
        if self.target and self.cooldown < 1:
            self.setAnimation(1)
            self.cooldown = 150
            Projectile(Vector2(self.pos.x+9,self.pos.y+19),self.target.center(),Vector2(11,6),"cactus-spike.png","cactus",10,rotation=math.atan2(self.target.center().x-self.pos.x+9,self.target.center().y-self.pos.y+19))

projectiles = []
class Projectile:
    def __init__(self,pos,target,size,color,type,damage,rotation=0,flipImage=False):
        self.pos = pos
        self.target = target
        self.size = size
        self.color = color
        self.type = type
        self.damage = damage
        self.rotation = rotation
        self.flipImage = flipImage
        dx = target.x - self.pos.x
        dy = target.y - self.pos.y
        angle = math.atan2(dy,dx)
        self.velo = Vector2(10*math.cos(angle),10*math.sin(angle))
        self.timer = 0
        projectiles.append(self)
    
    def Draw(self,camera):
        if camera.rect().collidepoint(self.pos):
            if type(self.color) == type((255,255,255)):
                pygame.draw.circle(screen,self.color,Vector2(self.pos.x-camera.x+(WIDTH/2)-(camera.focus.size.x/2),self.pos.y-camera.y+(HEIGHT/2)-(camera.focus.size.y/2)),self.size)
            if type(self.color) == type(" "):
                image = pygame.transform.rotate(pygame.image.load(f'Assets/{self.color}').convert_alpha(),self.rotation)
                image = pygame.transform.flip(image,self.flipImage,False)
                imageRect = image.get_rect(center = self.pos)
                screen.blit(image,Vector2(
                imageRect.x - camera.x + (WIDTH/2) - (camera.focus.size.x/2),
                imageRect.y - camera.y + (HEIGHT/2) - (camera.focus.size.y/2)))
        
    def Update(self):
        self.timer+=1
        if self.timer >= 300:
            projectiles.remove(self)
        self.pos+=self.velo
        for obj in objects:
            if obj.rect().collidepoint(self.pos):
                if self.type == "player":
                    if obj.name != "player" and obj.name != "gun":
                        if obj in entities:
                            obj.health -= self.damage
                        projectiles.remove(self)
                if self.type == "cactus":
                    if not obj in cacti:
                        if obj in entities:
                            obj.health -= self.damage
                            projectiles.remove(self)

collectibles = []
class Collectible:
    def __init__(self,pos,size,image,name,amount):
        self.pos = pos
        self.size = size
        self.name = name
        self.amount = amount
        self.image = pygame.image.load(image).convert_alpha()
        collectibles.append(self)

    def rect(self):
        return pygame.Rect(self.pos.x,self.pos.y,self.size.x,self.size.y)

    def Draw(self,camera):
        screen.blit(self.image,Vector2(self.pos.x-camera.x+(WIDTH/2)-(camera.focus.size.x/2),self.pos.y-camera.y+(HEIGHT/2)-(camera.focus.size.y/2)))
        Font("Assets/font.png").Render(str(self.amount),ScreenToWorldPoint(self.pos,camera)-Vector2(2,2))

    def Update(self):
        if self.name == "bullet":
            if self.rect().colliderect(player.rect()):
                player.bullets += self.amount
                collectibles.remove(self)


class Camera(pygame.math.Vector2):
    def __init__(self,screenSize,focus,x=0,y=0):
        super().__init__(x,y)
        self.screenSize = screenSize
        self.focus = focus

    def rect(self):
        return pygame.Rect(camera.x-(self.screenSize.x/2)+(self.focus.size.x/2),camera.y-(self.screenSize.y/2)+(self.focus.size.y/2),self.screenSize.x,self.screenSize.y)

class Font:
    def __init__(self,path):
        self.spacing = 1
        self.characterOrder = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '.', '-', ',', ':', '+', "'", '!', '?', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(', ')', '/', '_', '=', '\\', '[', ']', '*', '"', '<', '>', ';']
        fontImg = pygame.image.load(path).convert_alpha()
        currentCharWidth = 0
        self.characters = {}
        characterCount = 0
        for x in range(fontImg.get_width()):
            c = fontImg.get_at((x,0))
            if c[0] == 127:
                charImg = clip(fontImg,Vector2(x-currentCharWidth,0),Vector2(currentCharWidth,fontImg.get_height()))
                self.characters[self.characterOrder[characterCount]] = charImg
                characterCount += 1
                currentCharWidth = 0
            else:
                currentCharWidth += 1
        self.spaceWidth = self.characters['a'].get_width()

    def Render(self,text,pos,scale=1):
        x = 0
        for char in text:
            if char != ' ':
                screen.blit(pygame.transform.scale(self.characters[char],(self.characters[char].get_size()[0]*scale,self.characters[char].get_size()[1]*scale)),Vector2((pos.x+x)*scale,pos.y))
                x += self.characters[char].get_width() + self.spacing
            else:
                x += self.spacing + self.spaceWidth

allLists = [objects,entities,cacti,projectiles,collectibles]

player = Player(Vector2(190,900),Vector2(20,32),"player-0-0.png",True,True,"player",animate=True,layer=2)
player.newAnimation(("player-0-0.png","player-0-1.png","player-0-2.png","player-0-3.png"))
player.newAnimation(("player-1-0.png","player-1-1.png","player-1-2.png","player-1-3.png"))
player.newAnimation(("player-2-0.png","player-2-1.png"))
player.newAnimation(("player-3-0.png","player-3-1.png"))

gun = Object(Vector2(0,0),Vector2(40,10),"gun.png",False,False,"gun",layer=3)

camera = Camera(Vector2(WIDTH,HEIGHT),player)

nextAnimationFrame = pygame.USEREVENT+0
pygame.time.set_timer(nextAnimationFrame,170)

createMap(loadMap(1))
while True:
#Input and event handling
    mouse = Vector2((pygame.mouse.get_pos()[0]+camera.x)+(camera.focus.size.x/2)-(WIDTH/2),pygame.mouse.get_pos()[1]+camera.y+(camera.focus.size.y/2)-(HEIGHT/2))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.health-=1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if player.bullets > 0:
                    dx = mouse.x - player.center().x
                    dy = mouse.y - player.center().y
                    angle = math.atan2(dy,dx)+math.pi
                    player.velo = Vector2(10*math.cos(angle),10*math.sin(angle))
                    Projectile(player.center(),mouse,2,"bullet.png","player",10,rotation=gun.rotation)
                    player.bullets -= 1
        if event.type == nextAnimationFrame:
            for obj in objects:
                if obj.animate:
                    obj.frame += 1
                    if obj.frame > len(obj.animations[obj.animation])-1:
                        obj.frame = 0
                
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        if player.grounded():
            player.velo.y = -10
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.velo.x = -7.5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.velo.x = 7.5
#Camera movement
    camera.x = lerp(camera.x,camera.focus.pos.x,0.08)
    camera.y = lerp(camera.y,camera.focus.pos.y,0.08)
#Player animation controller
    if player.velo.x > 2:
        if player.grounded():
            player.setAnimation(1)
            player.flipImage = Vector2()
        if not player.grounded():
            player.setAnimation(2)
            player.flipImage = Vector2()
    elif player.velo.x < -2:
        if player.grounded():
            player.setAnimation(1)
            player.flipImage = Vector2(1,0)
        if not player.grounded():
            player.setAnimation(2)
            player.flipImage = Vector2(1,0)
    else:
        if player.grounded():
            player.setAnimation(0)
            player.flipImage = Vector2()
        if not player.grounded():
            player.setAnimation(3)
            player.flipImage = Vector2()
#Cacti animation controller
    for cactus in cacti:
        cactus.Shoot()
        if cactus.animation == 1 and cactus.frame == 3:
            cactus.setAnimation(0)
#Gun code
    gun.pos = player.pos
    #Rotate the gun
    dx,dy = mouse.x-gun.pos.x,mouse.y-gun.pos.y
    angle = math.degrees(math.atan2(dx,dy)) - 90
    if angle <= 90 and angle >= -90:
        gun.rotation = angle
        gun.flipImage = Vector2()
    else:
        gun.rotation = angle
        gun.flipImage = Vector2(0,1)
#Drawing to the screen
    screen.fill((245,161,66,))

    DrawAll()

    DrawUI()
#Collectibles
    for collectible in collectibles:
        collectible.Update()
#Cursor
    pygame.mouse.set_visible(False)
    screen.blit(pygame.image.load("Assets/cursor.png").convert_alpha(),Vector2(pygame.mouse.get_pos()[0]-4.5,pygame.mouse.get_pos()[1]-4.5))
#Debug layer
    if debug == True:
        pygame.draw.line(screen,(255,0,0),Vector2(0,HEIGHT/2),Vector2(WIDTH,HEIGHT/2))
        pygame.draw.line(screen,(255,0,0),Vector2(WIDTH/2,0),Vector2(WIDTH/2,HEIGHT))
        pygame.draw.circle(screen,(255,0,0),ScreenToWorldPoint(player.center(),camera),2)
        print(f'Projectiles:{len(projectiles)}')
        for cactus in cacti:
            pygame.draw.rect(screen,(255,0,0),pygame.Rect(ScreenToWorldPoint(cactus.pos,camera).x,ScreenToWorldPoint(cactus.pos,camera).y,20,30))
        for projectile in projectiles:
            pygame.draw.circle(screen,(255,0,0),ScreenToWorldPoint(projectile.pos,camera),2)
        #pygame.draw.rect(screen,(255,0,0),camera.rect(),5)
        #print("player:"+str(player.pos))
        #print("mouse:"+str(mouse))
        #print("camera:"+str(camera.x)+","+str(camera.y))
#Physics & Updates
    for obj in objects:
        obj.Physics(1,0.9)
    for projectile in projectiles:
        projectile.Update()
    for entity in entities:
        entity.Update()
#Update the screen
    WIDTH,HEIGHT = screen.get_width(),screen.get_height()
    camera.screenSize = Vector2(WIDTH,HEIGHT)
    pygame.display.update()
    clock.tick(30)