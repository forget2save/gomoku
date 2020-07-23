import colorama
import os

def create_game_board(s=15):
    if s < 5:
        s = 5
    if s > 30:
        s = 30
    return [[0 for i in range(s)] for j in range(s)]

current_player = 1
colorama.init()
game_board = create_game_board()
# try:
#     board_size = eval(input('What board size?'))
#     game_board = create_game_board(board_size)
# except:
#     game_board = create_game_board()

def display_game_board():
    print(f'  ',end='')
    for i in range(len(game_board)):
        if i<=9:
            print(f'  {i} ',end='')
        else:
            print(f' {i} ',end='')
    print('')
    for i, row in enumerate(game_board):
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

def set_piece(row,col):
    try:
        if game_board[row][col] == 0:
            game_board[row][col] = current_player
            return True
        else:
            print('ERROR: Piece Collision!!')
            return False
    except:
        print('ERROR: Out of range!!!')
        return False

def next_player():
    global current_player
    current_player = (2,1)[current_player-1]

def check_five(inlist):
    inlist = [str(x) for x in inlist]
    str1 = ''.join(inlist)
    str2 = str(current_player) * 5
    if str1.find(str2) != -1:
        return True
    else:
        return False

def whether_win(row,col):
    l1 = game_board[row]
    l2 = []
    l3 = []
    l4 = []
    for i,rr in enumerate(game_board):
        if col-abs(i-row) >= 0:
            l3.append(rr[col-abs(i-row)])
        if col+abs(i-row) < len(game_board):
            l4.append(rr[col+abs(i-row)])
        l2.append(rr[col])
    return check_five(l1) or check_five(l2) or check_five(l3) or check_five(l4)

os.system('cls')

while True:
    display_game_board()
    print(f'It is Player{current_player}\'s turn!')
    try:
        r = eval(input('which row?'))
        c = eval(input('which column?'))
    except:
        os.system('cls')
        print('ERROR: Invalid inputs!!!')
        if input('exit?(e)') == 'e':
            break
        continue
    os.system('cls')
    
    if set_piece(r,c):
        if whether_win(r,c):
            print(f'Winner : Player{current_player}!')
            break
        next_player()
        
