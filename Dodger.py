''' Dodger.py
   simple game tutorial in Pythonista
   code to implement the game described in this video:
   https://youtu.be/x3mRmpVZ-7U?si=s4lwNLOA84CmIJ4E
   To deploy, get Pythonista app from the App store on your iPad
   Copy this code into a file and run from Pythonista
'''

from scene import *
import sound
import random

YPOS = 41
standing = Texture('plf:AlienGreen_front')
walking = [Texture('plf:AlienGreen_walk1'), Texture('plf:AlienGreen_walk2')]
hit_texture = Texture('plf:AlienGreen_duck')

class Coin(SpriteNode):
    def __init__(self, **kwargs):
        SpriteNode.__init__(self, 'plf:Item_CoinGold', **kwargs)

class Meteor(SpriteNode):
    def __init__(self, **kwargs):
        img = random.choice(['spc:MeteorBrownBig1', 'spc:MeteorBrownBig2', 'spc:MeteorBrownBig3'])
        SpriteNode.__init__(self, img, **kwargs)

class Game(Scene):
    def setup(self):
        self.background_color = '#08e7f4'
        ground = Node(parent=self)
        x = 0
        while x < self.size.w + 64:
            ground.add_child(SpriteNode('plf:Ground_Grass', position=(x, 10)))
            x += 64
        self.player = SpriteNode('plf:AlienBeige_jump', position=(self.size.x/2, YPOS), parent=self)
        self.player.position = self.size.w/2, YPOS
        self.player.anchor_point = (0.5, 0)
        ground.add_child(self.player)
        self.label_score = LabelNode('0', ('futura', 40), parent=self)
        self.label_score.position = self.size.w/2, self.size.h-20
        self.list_of_items = []
        self.list_of_lasers = []
        self.walk_state = -1
        self.game_over = False
        self.new_game()

    def new_game(self):
        for item in self.list_of_items:
            item.remove_from_parent()
        for laser in self.list_of_lasers:
            laser.remove_from_parent()
        self.score = 0
        self.walk_state = -1
        self.list_of_items = []
        self.list_of_lasers = []
        self.game_over = False
        self.label_score.text = '0'
        self.player.position = self.size.w / 2, YPOS
        self.speed = 1
        self.player.texture = standing
        
    def update(self):
        if self.game_over:
            return
        if random.random() < 0.03:
            self.spawn_items()
        self.update_player()
        self.collisions_with_items()
        self.collisions_with_laser()

    def update_player(self):
        g = gravity()
        self.player.x_scale = 1 if g.x > 0 else -1

        if abs(g.y) > 0.5:
            speed = g.x * 50
            xpos = max(0, min(self.size.w, self.player.position.x + speed))
            self.player.position = xpos, YPOS
        if abs(g.x) < 0.5:
            self.player.texture = standing
            self.walk_state = -1
            return
        
        step = int(self.player.position.x / 40) % 2
        if step != self.walk_state:
            self.player.texture = walking[step]
            sound.play_effect('rpg:Footstep00')
            self.walk_state = step
        

    def spawn_items(self):
        if random.random() < 0.3:
            meteor = Meteor(parent=self)
            meteor.position = random.uniform(20, self.size.w), self.size.h
            duration = random.uniform(2, 4)
            self.list_of_items.append(meteor)
            meteor.run_action(Action.sequence(
                Action.move_by(0, -self.size.h, duration),
                Action.remove()))
        else:
            coin = Coin(parent=self)
            coin.position = random.uniform(20, self.size.w), self.size.h-60
            duration = random.uniform(2, 4)
            coin.run_action(Action.sequence(
                Action.move_by(0, -self.size.h, duration),
                Action.remove()
            ))
            self.list_of_items.append(coin)
    
    def collisions_with_items(self):
        for item in self.list_of_items:
            if item.frame.intersects(self.player.frame):
                if isinstance(item, Coin):
                    item.remove_from_parent()
                    self.list_of_items.remove(item)
                    sound.play_effect('arcade:Coin_2')
                    self.score += 10
                    self.label_score.text = str(self.score)
                else:
                    self.player_hit()
                    break

    def collisions_with_laser(self):
        for laser in self.list_of_lasers:
            if not laser.parent:
                self.list_of_lasers.remove(laser)
                continue
            for item in self.list_of_items:
                if not isinstance(item, Meteor):
                    continue
                if laser.frame.intersects(item.frame):
                    sound.play_effect('arcade:Explosion_1', 0.2)
                    self.list_of_items.remove(item)
                    self.list_of_lasers.remove(laser)
                    item.remove_from_parent()
                    laser.remove_from_parent()
                    self.score += 20
                    self.label_score.text = str(self.score)
                    break

    def player_hit(self):
        self.game_over = True
        self.player.texture = hit_texture
        sound.play_effect('arcade:Explosion_1')
        self.player.run_action(Action.sequence(
            Action.move_by(0, -150),
            Action.wait(2*self.speed),
            Action.call(self.new_game)
        ))
    

    def touch_began(self, touch):
        if self.game_over:
            return
        laser = SpriteNode('spc:LaserRed2', position=self.player.position, parent=self)
        laser.run_action(Action.sequence(
            Action.move_by(0, self.size.h, 1),
            Action.remove()
            ))
        sound.play_effect('arcade:Laser_1')
        self.list_of_lasers.append(laser)

if __name__ == '__main__':
    run(Game(), PORTRAIT)
