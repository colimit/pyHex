from pygraph.classes.graph import *
from pygraph.algorithms.searching import *
import pygame
from random import randrange,seed,sample
from copy import copy
from collections import Counter
seed(1301)


def dfs(starts,neighbors):
    to_do=starts
    done=set([])
    while to_do:
        a=to_do.pop()
        done.add(a)
        to_do.extend([n for n in neighbors(a) if not n in done])
        yield(a)

class Mygraph(graph):
    def __init__(self):
        graph.__init__(self)
    def is_connected(self,x,y):
        return (y in depth_first_search(self,x)[1])   

class EqMixin:
    def __eq__(self,other):
        if not type(other)==type(self):
            return False
        else:
            return self.__dict__==other.__dict__
class CheckInputMixin:
    def check(self):
        if self.game.display.get_input()=="undo":
            return "undo"
        if self.game.display.get_input()=="quit":
            return "quit"
        return None


class Color(EqMixin):
    def __init__(self,name,rgb):
        self.name=name
        self.rgb=rgb
    def __hash__(self):
        return hash(self.name)
    def __bool__(self):
    	return not self == empty
    	
def color_rgb_midpoint(color1,color2):
    x1,y1,z1 = color1.rgb
    x2,y2,z2 = color2.rgb
    return Color("midpoint",((x1+x2)//2,(y1+y2)//2,(z1+z2)//2))
    
empty=Color("empty",(255,255,255))
        
def standard_board_data(size):
    Player2=Color("blue",(100,100,255))
    Player1=Color("red",(255,100,100))
    #Player2=Color("blue",(250,250,100))
    #Player1=Color("red",(155,240,250))
    board_graph=Mygraph()
    for x,y in [(i,j) for i in range(size) for j in range(size)]:
        board_graph.add_node((x,y))
    for x,y in [(i,j) for i in range(size) for j in range(size)]:
        for w,z in [(x+1,y),(x,y+1),(x-1,y),(x,y-1),(x+1,y-1),(x-1,y+1)]:
            if board_graph.has_node((w,z)):
                if not board_graph.has_edge(((x,y),(w,z))):
                    board_graph.add_edge(((x,y),(w,z)))
    blue_start=[(0,i) for i in range(size)]
    blue_finish=[(size-1,i) for i in range(size)]
    red_start=[(i,0) for i in range(size)]
    red_finish=[(i,size-1) for i in range(size)]
    return (board_graph,[Player1,Player2], {Player1 : [blue_start,blue_finish], Player2 : [red_start,red_finish]})


class Player:
    def move(self,position):
        raise Exception("not implemented")

class Random_Player(Player,CheckInputMixin):
    def __init__(self,game):
        self.name="Random"
        self.display_name=self.name
        self.game=game
        self.size=self.game.board.size
    def move(self,position):
        if not position.color_winning():
            return (randrange(self.size),randrange(self.size))
        while True:
            a=self.check()
            if a:
                return a
                
class Dumb_Player(Player,CheckInputMixin):
    def __init__(self,game,tries):
        self.name="Dumb Player"
        self.display_name=self.name
        self.game=game
        self.size=self.game.board.size    
        self.tries=tries
    def move(self,position):
        if not position.color_winning():
            return CheckPosition(position,self.game).best2(self.tries)
        while True:
            a=self.check()
            if a:
                return a


class Human_Player(Player,CheckInputMixin):
    def __init__(self,game):
        self.game=game
        self.name="Human Player"
        self.display_name=self.name
    def move(self,position):
        a=False
        while not a:
            a=self.game.display.get_input()
        return a


class Board:
    def __init__(self,graph,colors,zones):
        self.graph=graph
        self.colors=colors
        self.zones=zones
    def adjacents(self,space):
        return self.graph.neighbors(space)
    def next_color(self,color):
        i=self.colors.index(color)
        return self.colors[(i+1)%len(self.colors)]
    def prev_color(self,color):
        i=self.colors.index(color)
        return self.colors[(i-1)%len(self.colors)]  
        
class Standard_Board(Board):
    def __init__(self,size):
        Board.__init__(self,*standard_board_data(size))
        self.size=size



class Move(EqMixin):
    def __init__(self,color,space):
        self.color=color
        self.space=space
    
        
class Graphical_Hex_Set:
    'This object is responsible for interfacing with the GUI'
    def __init__(self,game):
        self.game=game
        self.board=game.board
        self.size=game.board.size
        pygame.init()
        pygame.display.set_caption("Hex")
        self.clock = pygame.time.Clock()
        self.unit=16    #should be even
        self.border=2   
        self.right_margin=320
        self.right_max=self.unit*(self.size+2)*3 + self.unit*self.border
        self.bottom= self.unit*(self.size+2)*2 +  self.unit*self.border
        self.screen=pygame.display.set_mode((self.right_max+self.right_margin, self.bottom))
        self.draw_board()
        self.draw_margin()
        pygame.display.update()
    def draw(self,position):
        'draws a position for a standard board'
        if position.board !=self.board:
            raise Exception("board mismatch")
        self.draw_board()
        for color,spaces in position.pieces:
            for space in spaces:
                self.change(space,color)
    def draw_hex(self,coords,color):
        pygame.draw.polygon(self.screen, color.rgb, self.hex_poly_raw(*coords))
        pygame.draw.polygon(self.screen, (50,50,50), self.hex_poly_raw(*coords), 2)
    def draw_space(self,space,color):
        self.draw_hex(self.board_coords(*space) ,color)
    def change(self,space,color):
        'changes a space to a color'
        self.draw_space(space,color)
        pygame.display.update()
    def board_coords(self,x_hex,y_hex):
        x = self.unit + self.unit*(x_hex + y_hex + 2)*3//2 +self.unit*self.border//2
        y = self.unit*self.size + self.unit*(x_hex - y_hex +2 )+self.unit*self.border//2
        return (x,y)
    def draw_board(self):
        self.screen.fill(empty.rgb)
        for i in range(-1,self.size+1):
            for j in range(-1,self.size+1):
                color=empty
                if i == -1 or i == self.size:
                    if j== -1 or j== self.size:
                        color=color_rgb_midpoint(self.board.colors[0],self.board.colors[1])
                    else:
                        color=self.board.colors[0]
                elif  j== -1 or j== self.size:
                    color=self.board.colors[1]
                self.draw_space((i,j),color)
                
    def draw_name(self,player,is_bold): # player is 0 or 1, bold is boolean
        font= pygame.font.Font(None, 28,bold=is_bold)
        player_name = font.render(self.game.players[self.board.colors[player]].display_name, 1, (10,10,10))
        player_name_pos =player_name.get_rect()
        player_name_pos.center=(self.right_max+self.right_margin//2,(1+2*player)*self.bottom//4 +self.unit*3)
        pygame.draw.rect(self.screen,empty.rgb,player_name_pos.inflate(30,3))
        if is_bold:
            pygame.draw.rect(self.screen,(255,255,100),player_name_pos.inflate(3,3))
        self.screen.blit(player_name,player_name_pos )
    def draw_margin(self):
        self.draw_hex((self.right_max+self.right_margin//2,self.bottom//4),self.board.colors[0])
        self.draw_hex((self.right_max+self.right_margin//2,3*self.bottom//4),self.board.colors[1])
    def hex_poly_raw(self,x,y):
        return [(x - self.unit,  y),
            (x - self.unit//2, y - self.unit),
            (x + self.unit//2, y - self.unit),
            (x + self.unit,   y),
            (x + self.unit//2, y + self.unit),
            (x - self.unit//2, y + self.unit)]                
#    def hex_poly(self,x_hex,y_hex):
#        return self.hex_poly_raw(*self.board_coords(x_hex,y_hex))
    def hex_of(self,x,y):
        for x_hex in range(self.size):
            for y_hex in range(self.size):
                x1,y1=self.board_coords(x_hex,y_hex)
                if (x-x1)**2+(y-y1)**2 < self.unit ** 2 * .9:
                    return (x_hex,y_hex)
        return None
    def get_input(self): #this is the loop for pygame
        pygame.event.pump()
        self.clock.tick(40)
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    pos = event.pos #pygame.mouse.get_pos()
                    a=self.hex_of(*pos)
                    if a:
                        return a
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT,pygame.K_BACKSPACE]:
                    return "undo"
            elif event.type == pygame.QUIT:
                return "quit"
    def set_to_move(self,color): 
        if color==empty:
            self.draw_name(0,False)
            self.draw_name(1,False)
            return
        player=self.board.colors.index(color)
        self.draw_name(player,True)
        self.draw_name((player+1)%2,False)
        pygame.display.update()
    def show_winning(self,color):
        player=0
        if color==self.board.colors[1]:
            player=1
        font= pygame.font.Font(None, 96)
        one_text = font.render(" 1 ", 1, (10,150,10))
        zero_text = font.render(" 0 ", 1, (10,10,10))
        one_text_pos = one_text.get_rect()
        zero_text_pos = one_text.get_rect()
        one_text_pos.center=(self.right_max+4*self.right_margin//5,(1+2*player)*self.bottom//4 +self.unit)
        zero_text_pos.center=(self.right_max+4*self.right_margin//5,(1+2*((player+1)%2))*self.bottom//4 +self.unit)
        pygame.draw.rect(self.screen,empty.rgb,one_text_pos.inflate(10,3))
        pygame.draw.rect(self.screen,empty.rgb,zero_text_pos.inflate(10,3))
        if color:
            self.screen.blit(one_text,one_text_pos )
            self.screen.blit(zero_text,zero_text_pos )
            self.set_to_move(empty)
           
        pygame.display.update()
            
            
 
class Game:        
    def main(self):
        while True:
            won=self.position.color_winning()
            if won==empty:
                self.display.set_to_move(self.position.to_move)
            else:
                self.display.show_winning(won)
            space=self.players[self.position.to_move].move(self.position)
            if space=="quit":
                pygame.quit()
                return
            if space=="undo":
                self.undo()
            else:
                self.play(space)
    def undo(self):
        if not self.move_list:
            return
        move=self.move_list.pop()
        self.position.undo_piece(move.space)
        self.display.change(move.space,empty)  
        self.display.show_winning(empty)
    def play(self,space):
        color=self.position.to_move
        move = self.position.move_on(space)
        if move:
            self.display.change(move.space,move.color)
            self.move_list.append(move)
        
        
class Standard_Game(Game):
    def __init__(self,size):
        self.board=Standard_Board(size)
        self.position=Position(self.board)
        self.players={}
        self.move_list=[]
        for color in self.board.colors:
            self.players[color]=Human_Player(self)
        self.display=Graphical_Hex_Set(self)
        self.main()


        
class AI_Game(Game):
    def __init__(self,size):
        self.board=Standard_Board(size)
        self.position=Position(self.board)
        self.players={}
        self.move_list=[]
        self.players[self.board.colors[0]]= Dumb_Player(self,500)
        self.players[self.board.colors[1]]= Human_Player(self)
        self.display=Graphical_Hex_Set(self)
        self.main()   
        
    

class Position:
    'a position is a board, some pieces, and the identity of the color which moves next'
    def __init__(self,board,pieces_input={},to_move=0):
        if not to_move in board.colors:
            self.to_move=board.colors[0]
        else:
            self.to_move=to_move
        self.board=board
        self.pieces={}
        for color in self.board.colors:
            self.pieces[color]=set([])
            for space in pieces_input.get(color,[]):
                self.add_piece(color,space)
    def add_piece(self,color,space):
        'attempts to add a piece of color to space. Returns true if accomplished'
        if self.get_color(space)!=empty:
            return False
        self.pieces[color].add(space)
        return True

    def has_won(self,color):
        starts=[spacey for spacey in self.board.zones[color][0] if 
                                                spacey in self.pieces[color]]
        neighbors = lambda x : [x for x in self.board.adjacents(x) 
                                                  if x in self.pieces[color]]
        for space in dfs(starts,neighbors):
            if space in self.board.zones[color][1]:
                return True
        return False
    def move_on(self,space):
        'the current color moves on space if legal, updating the position and \
        returning a move object, if illegal returns None'
        color=self.to_move
        if self.get_color(space)!=empty:
            return None
        elif self.color_winning():
            return None
        else: 
            self.add_piece(color,space)
            self.to_move=self.board.next_color(color)
            return Move(color,space)
    def clear_piece(self,color,space):
        'removes a piece of color from space if present. Returns true if accomplished'
        for color in self.board.colors:
            if space in self.pieces[color]:
                self.pieces[color].discard(space)
                return True
        return False
    def undo_piece(self,space):
        'the current color takes a stone back from space'
        if self.clear_piece(self.to_move,space):
            self.to_move=self.board.prev_color(self.to_move)
            return "undo"
        return None
    def get_color(self,space):
        for color in self.board.colors:
            if space in self.pieces[color]:
                return color
        return empty
    def color_winning(self):
        for color in self.board.colors:
            if self.has_won(color):
                return color
        return empty
    def empties(self):
        guys=set(self.board.graph)
        for color in self.board.colors:
            guys-=self.pieces[color]
        return guys
    
class CheckPosition(CheckInputMixin):  #class for quickly simulating a random continuation
    def __init__(self,position,game):
        self.game=game
        self.empties=position.empties()
        self.empty_num=len(self.empties)
        self.size=position.board.size
        if position.to_move==position.board.colors[0]:
            self.to_move=0
        else:
            self.to_move=1
        self.reds=position.pieces[position.board.colors[self.to_move]]|set([])  #pieces of the players to move
    def sim(self,space,times): #simulates result if player (0 or 1) moves to space. number of times player wins
        empties = self.empties - set([space])
        reds=self.reds | set([])
        reds =reds | set([space])
        for i in range(times):
            red_try=reds | set(sample(empties,(self.empty_num-1)//2))
            #if space==(0,0) and i==0: 
                #print(reds)
                #print(empties)
                #print(red_try)
            if self.red_wins(red_try):
                red_wins+=1
        return red_wins
    def adjacents_in(self,space,reds):
        x,y=space[0],space[1]
        return [space for space in [(x+1,y),(x,y+1),(x-1,y),(x,y-1),(x+1,y-1),(x-1,y+1)] if self.valid(space) and space in reds]
    def valid(self,space):
        return space[0] >-1 and space[0]<self.size and space[1]>-1 and space[1]<self.size
    def red_wins(self,reds):
        for space in dfs([space for space in reds if space[0]==0], lambda x: (self.adjacents_in(x,reds)  ) ):
            if space[0]==self.size-1:
                return True
        return False
    def sim(self,times):
        count={}
        for space in self.empties:
            count[space]=self.sim(space,times)
            a=self.check()
            if a:
                return a
        #print(count)
        return max(count.keys(), key=( lambda key: count[key]))
    def best2(self,times):
        count_totals=Counter()
        count_wins=Counter()
        empties = self.empties | set([])
        reds=self.reds | set([])
        for i in range(times):
            new_reds=set(sample(empties,(self.empty_num+1)//2))
            red_try=reds | new_reds
            count_totals.update(new_reds)
            #if space==(0,0) and i==0: 
                #print(reds)
                #print(empties)
                #print(red_try)
            if self.red_wins(red_try):
                count_wins.update(new_reds)
            return max(count_totals.keys(), key=( lambda key: count_wins[key]/count_totals[key]))

AI_Game(13)

            
           

        
