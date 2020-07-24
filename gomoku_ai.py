#coding=gbk
#2020/7/23
import numpy as np
import os
from pygame import *
from sys import exit
from pygame.locals import *
import random

SCREEN_SIZE = (800,600)
WHITE = (255,255,255)
BLACK = (0,0,0)
INF = 10000

SCORE = [[0,5,25,125,1000,INF,1000,125,25,5],
        [0,0,5,25,125,INF,125,25,5,0],
        [0,0,1,5,25,INF,25,5,1,0]]


def scoreit(l):
    score = 0
    state = 0
    subclass = 0
    for i in range(len(l)):
        piece = l[i]
        if piece == 0:
            if state == 0:
                continue
            elif state > 0:
                score += SCORE[subclass][state]
            elif state < 0:
                score -= SCORE[subclass][state]
            state = 0
            subclass = 0
        elif piece == 1:
            if state > 0:
                state += 1
            elif state == 0:
                if l[i-1] == 2 or l[i-1] == -1:
                    subclass += 1
                state += 1
            elif state < 0:
                score -= SCORE[subclass+1][state]
                state = 1
                subclass = 1
        elif piece == 2:
            if state < 0:
                state -= 1
            elif state == 0:
                if l[i-1] == 1 or l[i-1] == -1:
                    subclass += 1
                state -= 1
            elif state > 0:
                score += SCORE[subclass+1][state]
                state = -1
                subclass = 1
        elif piece == -1:
            if state == 0:
                continue
            elif state > 0:
                score += SCORE[subclass+1][state]
            elif state < 0:
                score -= SCORE[subclass+1][state]
    return score

def dummy_gameboard():
    a = np.zeros([19,19])
    a[:2,:] = -np.ones([2,19])
    a[-2:,:] = -np.ones([2,19])
    a[:,:2] = -np.ones([19,2])
    a[:,-2:] = -np.ones([19,2])
    return a

class node:
    def __init__(self,max_min,move=(-1,-1)):
        self.a = -INF
        self.b = +INF
        self.move = move
        self.nextmove = (-1,-1)
        self.max_min = max_min
        self.children = []
        self.parent = None
        if max_min:
            self.v = -INF
        else:
            self.v = +INF
    
    def addchild(self,child):
        self.children.append(child)
        child.parent = self                

    def alpha_beta_pruning(self,v,a,b,g,layer):
        if self.move[0] != -1:
            g.flip_side()
            g.set_piece(self.move[0],self.move[1])
        cur_v = g.evaluate()
        if (self.max_min and cur_v < -500) or (not self.max_min and cur_v > 500):
            g.flip_side()
            g.pick_piece(self.move[0],self.move[1])
            return [cur_v,self.move]
        self.v = v
        self.a = a
        self.b = b
        if layer == 1:
            self.v = g.evaluate()
            g.flip_side()
            g.pick_piece(self.move[0],self.move[1])
            # print(layer,self.v,self.a,self.b,'return')
            return [self.v,self.move]
        else:
            g.find_pos()
            for step in g.golden:
                self.children.append(node(not self.max_min,move=step))
            for head_node in self.children:
                if self.max_min:
                    tmpv,tmpm = head_node.alpha_beta_pruning(head_node.v,self.a,self.b,g,layer-1)
                    if tmpv > self.v:
                        self.nextmove = tmpm
                        self.v = tmpv
                        self.a = self.v
                        # print(layer,self.v,self.a,self.b,'modify')
                    if self.a > self.b or self.v > 500:
                        print('pruning!!!')
                        break
                else:
                    tmpv,tmpm = head_node.alpha_beta_pruning(head_node.v,self.a,self.b,g,layer-1)
                    if tmpv < self.v:
                        self.nextmove = tmpm
                        self.v = tmpv
                        self.b = self.v
                        # print(layer,self.v,self.a,self.b,'modify')
                    if self.a > self.b or self.v < -500:
                        print('pruning!!!')
                        break
        g.flip_side()
        g.pick_piece(self.move[0],self.move[1])
        # print(layer,self.v,self.a,self.b,'return')
        return [self.v,self.move]

class gomoku:
    def __init__(self):
        init()
        self.screen = display.set_mode(SCREEN_SIZE,0,32)
        display.set_caption('Gomoku')
        self.background = image.load('board.jpg')
        self.background = transform.scale(self.background,(600,600))
        self.game_board = dummy_gameboard()
        self.side = 1
        self.layer = 4
        self.golden = []
        self.sliver = []
        self.tree = None
        self.sit = 0

    def display(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.background,(0,0))
        for i in range(2,17):
            for j in range(2,17):
                if self.game_board[i][j] == 1:
                    draw.circle(self.screen,BLACK,(40*j-60,40*i-60),16)
                elif self.game_board[i][j] == 2:
                    draw.circle(self.screen,WHITE,(40*j-60,40*i-60),16)
        # myCfont = font.SysFont('stfangsong',20)
        # text = myCfont.render(f'当前局面分数：{self.sit}',True,BLACK)
        # self.screen.blit(text,(620,20))
        display.update()

    def set_piece(self,row,col):
        if self.game_board[row,col] > 0:
            return False
        self.game_board[row][col] = self.side
        return True
    
    def pick_piece(self,row,col):
        self.game_board[row][col] = 0

    def get_pos(self,pos):
        if abs(pos[0] % 40 - 20) > 15 or abs(pos[1] % 40 - 20) > 15 or pos[0] > 615:
            return False
        return self.set_piece(round((pos[1]-20)/40)+2,round((pos[0]-20)/40)+2)

    def flip_side(self):
        self.side = (2,1)[self.side-1]
    
    def find_pos(self):
        self.golden = []
        self.sliver = []
        for i in range(2,17):
            for j in range(2,17):
                if self.game_board[i][j] == 0:
                    if self.game_board[i+1][j-1] > 0 or self.game_board[i+1][j+1] > 0 \
                        or self.game_board[i][j-1] > 0 or self.game_board[i][j+1] > 0 \
                        or self.game_board[i-1][j-1] > 0 or self.game_board[i-1][j+1] > 0 \
                        or self.game_board[i+1][j] > 0 or self.game_board[i-1][j] > 0:
                        self.golden.append((i,j))
                    elif self.game_board[i+2][j-2] > 0 or self.game_board[i+2][j+2] > 0 \
                        or self.game_board[i+1][j-2] > 0 or self.game_board[i+1][j+2] > 0 \
                        or self.game_board[i][j-2] > 0 or self.game_board[i][j+2] > 0 \
                        or self.game_board[i-1][j-2] > 0 or self.game_board[i-1][j+2] > 0 \
                        or self.game_board[i-2][j-2] > 0 or self.game_board[i-2][j+2] > 0 \
                        or self.game_board[i-2][j-1] > 0 or self.game_board[i+2][j-1] > 0 \
                        or self.game_board[i-2][j] > 0 or self.game_board[i+2][j] > 0 \
                        or self.game_board[i-2][j+1] > 0 or self.game_board[i+2][j+1] > 0:
                        self.sliver.append((i,j))

    def preprocess_evaluate(self):
        ll = []
        ll.append([self.game_board[i,i] for i in range(19)])
        ll.append([self.game_board[i,18-i] for i in range(19)])
        for i in range(1,11):
            l1 = []
            l2 = []
            for j in range(19):
                if i+j<19:
                    l1.append(self.game_board[i+j,j])
                    l2.append(self.game_board[j,i+j])
                else:
                    break
            ll.append(l1)
            ll.append(l2)
        for i in range(8,18):
            l1 = []
            l2 = []
            for j in range(19):
                if i-j>=0 and 18-j>=0:
                    l1.append(self.game_board[i-j,j])
                    l2.append(self.game_board[18-j,18-i+j])
                else:
                    break
            ll.append(l1)
            ll.append(l2)
        for i in range(2,17):
            ll.append(self.game_board[i,:])
            ll.append(self.game_board[:,i])
        return ll

    def evaluate(self):
        score = 0
        for l in self.preprocess_evaluate():
            score += scoreit(l)
        return score

    def aiplaying(self):
        if self.side == 1:
            max_min = True
        else:
            max_min = False
        self.tree = node(max_min)
        self.flip_side()
        score,move = self.tree.alpha_beta_pruning(self.tree.v,self.tree.a,self.tree.b,self,self.layer)
        self.set_piece(self.tree.nextmove[0],self.tree.nextmove[1])

if __name__ == "__main__":
    G = gomoku()
    flag = random.choice([True,False])
    if flag:
        G.set_piece(7+2,7+2)
        G.sit = G.evaluate()
        G.flip_side()
        flag = False
    while True:
        for e in event.get():
            if e.type==QUIT or (e.type==KEYDOWN and e.key==K_ESCAPE):
                exit()
            elif e.type==MOUSEBUTTONDOWN and e.button==BUTTON_LEFT and not flag:
                if G.get_pos(e.pos):
                    G.sit = G.evaluate()
                    print(G.sit)
                    if abs(G.sit) > INF/2:
                        print('Win!!!')
                        exit()
                    G.flip_side()
                    flag = True
        G.display()
        if flag:
            G.aiplaying()
            G.sit = G.evaluate()
            print(G.sit)
            if abs(G.sit) > INF/2:
                print('Lose~~')
                exit()
            G.flip_side()
            flag = False
        