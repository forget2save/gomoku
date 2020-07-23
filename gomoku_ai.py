#coding=gbk
#2020/7/23
import numpy as np
import colorama
import os

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
        self.v = v
        self.a = a
        self.b = b
        if layer == 1:
            self.v = g.evaluate()
            g.flip_side()
            g.pick_piece(self.move[0],self.move[1])
            return [self.v,self.move]
        else:
            g.find_pos()
            for step in g.golden:
                self.children.append(node(not self.max_min,move=step))
            for head_node in self.children:
                if self.max_min:
                    tmpv,tmpm = head_node.alpha_beta_pruning(head_node.v,head_node.a,head_node.b,g,layer-1)
                    if tmpv > self.v:
                        self.nextmove = tmpm
                        self.v = tmpv
                        self.a = self.v
                    if self.a > self.b:
                        break
                else:
                    tmpv,tmpm = head_node.alpha_beta_pruning(head_node.v,head_node.a,head_node.b,g,layer-1)
                    if tmpv < self.v:
                        self.nextmove = tmpm
                        self.v = tmpv
                        self.b = self.v
                    if self.a > self.b:
                        break
        g.flip_side()
        g.pick_piece(self.move[0],self.move[1])
        return [self.v,self.move]

class gomoku:
    def __init__(self):
        colorama.init()
        self.game_board = dummy_gameboard()
        self.side = 1
        self.layer = 3
        self.golden = []
        self.sliver = []
        self.tree = None

    def display(self):
        os.system('cls')
        print(self.evaluate())
        print(f'  ',end='')
        for i in range(15):
            if i<=9:
                print(f'  {i} ',end='')
            else:
                print(f' {i} ',end='')
        print('')
        for i, row in enumerate(self.game_board[2:17,2:17]):
            colored_row = ""
            for item in row:
                if item == 0:
                    colored_row += colorama.Fore.WHITE + "  + " + colorama.Style.RESET_ALL
                elif item == 1:
                    colored_row += colorama.Fore.GREEN + "  X " + colorama.Style.RESET_ALL
                elif item  == 2:
                    colored_row += colorama.Fore.MAGENTA + "  O " + colorama.Style.RESET_ALL
            print('{:2d}'.format(i),end='')
            print(colored_row)

    def set_piece(self,row,col):
        self.game_board[row][col] = self.side
    
    def pick_piece(self,row,col):
        self.game_board[row][col] = 0

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
    player_side = eval(input('which side: 1 or 2?'))
    if player_side == 2:
        G.set_piece(7+2,7+2)
        G.flip_side()
    while True:
        G.display()
        print('It is Player\'s turn!')
        try:
            r = eval(input('which row?'))
            c = eval(input('which column?'))
        except:
            os.system('cls')
            print('ERROR: Invalid inputs!!!')
            if input('exit?(e)') == 'e':
                break
            continue
        G.set_piece(r+2,c+2)
        if abs(G.evaluate()) > INF/2:
            print('Win!!!')
            break
        G.flip_side()
        G.display()
        G.aiplaying()
        if abs(G.evaluate()) > INF/2:
            print('Lose~~')
            break
        G.flip_side()

        