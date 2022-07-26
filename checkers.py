import pygame
from copy import deepcopy

#music
pygame.mixer.init()
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play()


#constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH//COLS

#COLORS
CREAM = (255, 211, 155)
BLACK = (0, 0, 0)
BROWN = (138, 54, 15)
ORANGE = (255, 97, 3)
GREY = (128,128,128)
CROWN = pygame.transform.scale(pygame.image.load('photo/crown.jpg'), (40, 20))


#taw
class Taw:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True
    
    def draw(self, win):
        radius = SQUARE_SIZE//2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width()//2, self.y - CROWN.get_height()//2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)



#board
class Board:
    def __init__(self):
        self.board = []
        self.cream_left = self.black_left = 12
        self.cream_kings = self.black_kings = 0
        self.create_board()
    
    def draw_squares(self, win):
        win.fill(BROWN)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, CREAM, (row*SQUARE_SIZE, col *SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.black_left - self.cream_left + (self.black_kings * 0.5 - self.cream_kings * 0.5)

    def get_all_taws(self, color):
        taws = []
        for row in self.board:
            for taw in row:
                if taw != 0 and taw.color == color:
                    taws.append(taw)
        return taws

    def move(self, taw, row, col):
        self.board[taw.row][taw.col], self.board[row][col] = self.board[row][col], self.board[taw.row][taw.col]
        taw.move(row, col)

        if row == ROWS - 1 or row == 0:
            taw.make_king()
            if taw.color == BLACK:
                self.black_kings += 1
            else:
                self.cream_kings += 1 

    def get_taw(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row +  1) % 2):
                    if row < 3:
                        self.board[row].append(Taw(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Taw(row, col, CREAM))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                taw = self.board[row][col]
                if taw != 0:
                    taw.draw(win)

    def remove(self, taws):
        for taw in taws:
            self.board[taw.row][taw.col] = 0
            if taw != 0:
                if taw.color == CREAM:
                    self.cream_left -= 1
                else:
                    self.black_left -= 1
    
    def winner(self):
        if self.cream_left <= 0:
            return BLACK
        elif self.black_left <= 0:
            return CREAM
        
        return None 
    
    def get_valid_moves(self, taw):
        moves = {}
        left = taw.col - 1
        right = taw.col + 1
        row = taw.row

        if taw.color == CREAM or taw.king:
            moves.update(self._traverse_left(row -1, max(row-3, -1), -1, taw.color, left))
            moves.update(self._traverse_right(row -1, max(row-3, -1), -1, taw.color, right))
        if taw.color == BLACK or taw.king:
            moves.update(self._traverse_left(row +1, min(row+3, ROWS), 1, taw.color, left))
            moves.update(self._traverse_right(row +1, min(row+3, ROWS), 1, taw.color, right))
    
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, left-1,skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1,skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves


#game
class Game:
    def __init__(self, win):
        self._init()
        self.win = win
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = CREAM
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        taw = self.board.get_taw(row, col)
        if taw != 0 and taw.color == self.turn:
            self.selected = taw
            self.valid_moves = self.board.get_valid_moves(taw)
            return True
            
        return False

    def _move(self, row, col):
        taw = self.board.get_taw(row, col)
        if self.selected and taw == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, ORANGE, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == CREAM:
            self.turn = BLACK
        else:
            self.turn = CREAM

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()



#minmax
def minimax(position, depth, max_player, game):
    if depth == 0 or position.winner() != None:
        return position.evaluate(), position
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(position, BLACK, game):
            evaluation = minimax(move, depth-1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, CREAM, game):
            evaluation = minimax(move, depth-1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        
        return minEval, best_move


def simulate_move(taw, move, board, game, skip):
    board.move(taw, move[0], move[1])
    if skip:
        board.remove(skip)

    return board


def get_all_moves(board, color, game):
    moves = []

    for taw in board.get_all_taws(color):
        valid_moves = board.get_valid_moves(taw)
        for move, skip in valid_moves.items():
            draw_moves(game, board, taw)
            temp_board = deepcopy(board)
            temp_taw = temp_board.get_taw(taw.row, taw.col)
            new_board = simulate_move(temp_taw, move, temp_board, game, skip)
            moves.append(new_board)
    
    return moves


def draw_moves(game, board, taw):
    valid_moves = board.get_valid_moves(taw)
    board.draw(game.win)
    pygame.draw.circle(game.win, (0,255,0), (taw.x, taw.y), 50, 5)
    game.draw_valid_moves(valid_moves.keys())
    pygame.display.update()



#main
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')
def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(60)
        
        if game.turn == BLACK:
            value, new_board = minimax(game.get_board(), 4, BLACK, game)
            game.ai_move(new_board)

        if game.winner() != None:
            print(game.winner())
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        game.update()
    pygame.quit()
main()