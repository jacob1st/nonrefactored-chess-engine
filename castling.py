import time
import pygame
import math


# https://gist.github.com/peterellisjones/8c46c28141c162d1d8a0f0badbc9cff9 NODE 44 CASTLING IN FEN TEST
class board:
    # Holds the conversion from string to number for each piece and information about the board
    pieces = {'empty':0, 'p':1, 'r':2, 'n':3, 'b':4, 'k':5, 'q':6, 'white':8, 'black':16}
    reverse_pieces = {0:'empty', 1:'p', 2:'r', 3:'n', 4:'b', 5:'k', 6:'q', 8:'white', 16:'black'}
    def __init__(self, starting_board, turn, castling, passant, halfmove_clock, fullmove_clock):
        self.current_board = starting_board
        self.square_size = 0
        self.starting_pos = []
        self.turn = self.turn_from_string(turn)
        self.castling = castling
        self.passant = passant
        self.halfmove_clock = halfmove_clock
        self.fullmove_clock = fullmove_clock
    
    def turn_from_string(self, color):
        if color == "w":
            return 8
        else:
            return 16


def resize_screen(display, x, y):
    # Gets a new size and sets that as the new display
    display = pygame.display.set_mode((x, y), pygame.RESIZABLE)
    pygame.display.set_caption("Chess")
    return display

def num_to_piece(num):
    # Takes in a a number and returns the name of the piece, used to get the image files
    piece = num & 7
    color = num & 24
    if piece == 1:
        piece = "pawn"
    elif piece == 2:
        piece = "rook"
    elif piece == 3:
        piece = "knight"
    elif piece == 4:
        piece = "bishop"
    elif piece == 5:
        piece = "king"
    elif piece == 6:
        piece = "queen"
    else:
        return False
    
    if color == 8:
        return ("white_" + piece, num)
    else:
        return ("black_" + piece, num)
        
def draw_pieces(display, game_board):
    # loops through the list of pieces and gets the image file, then draws it, resizing it for the screen size
    image_dir = './images/'
    piece_pos_x = game_board.starting_pos[0] + .1*game_board.square_size
    piece_pos_y = game_board.starting_pos[1] + .1*game_board.square_size

    tile_num = 1
    for i in game_board.current_board:
        piece = num_to_piece(i)

        if piece:
            piece = piece[0]
            image = pygame.image.load(image_dir + piece + '.png')
            # adjust size
            image_size = game_board.square_size*.8
            image = pygame.transform.scale(image, (image_size, image_size))
            display.blit(image, (piece_pos_x, piece_pos_y))

        piece_pos_x += game_board.square_size
        if tile_num % 8 == 0 and tile_num >= 8:
            piece_pos_x = game_board.starting_pos[0] + .1*game_board.square_size
            piece_pos_y += game_board.square_size
        tile_num += 1

    return display

def draw_board(display, game_board):
    # Draw a grid of square with alternating colors
    # The board stays centered
    # Then draws all pieces
    screen_size = pygame.display.get_window_size()
    padding = 30

    if screen_size[0] < screen_size[1]:
        square_size = ((screen_size[0]-padding) - ((screen_size[0]-padding) % 8)) / 8
    else:
        square_size = ((screen_size[1]-padding) - ((screen_size[1]-padding) % 8)) / 8

    board_size = square_size*8
    
    square_x = (screen_size[0] - board_size)/2
    square_y = (screen_size[1] - board_size)/2

    game_board.square_size = square_size
    game_board.starting_pos = [square_x, square_y]

    for column in range(8):
        for row in range(8):
            if row % 2 == column % 2:
                color = (233, 209, 182) # light
            else:
                color = (161, 111, 90) # dark
            pygame.draw.rect(display, color, pygame.Rect(square_x, square_y, square_size, square_size))
            pygame.draw.rect(display, (0, 0, 0), pygame.Rect(square_x, square_y, square_size, square_size), 1)
            square_x += square_size

        square_y += square_size
        square_x = game_board.starting_pos[0]

    return game_board

def fen_to_list(fen):
    # Takes in a string in "FEN" format and returns a list of pieces
    portions = fen.split(' ')
    piece_pos = portions[0]
    turn = portions[1]
    castle_ability = portions[2]
    en_passant = portions[3]
    halfmove_clock = portions[4]
    fullmove_counter = portions[5]

    col = 0
    current_board = []
    for piece in piece_pos:
        if piece == '/':
            pass
        elif piece.isdigit():
            current_board += [board.pieces['empty'] for i in range(int(piece))]
            col += int(piece)
        else:
            if piece.isupper():
                piece_color = 'white'
            else:
                piece_color = 'black'
            
            piece_value = board.pieces[piece.lower()] | board.pieces[piece_color]
            current_board.append(piece_value)
    
    game_board = board(current_board, turn, castle_ability, en_passant, int(halfmove_clock), int(fullmove_counter))
    if en_passant != '-':
        columns = 'abcdefgh'
        col = 7-(columns.index(en_passant[0]))
        row = int(en_passant[1]) - 1
        game_board.passant = 63 - ((row*8) + col)
    return game_board

def pos_to_square(game_board, pos):
    # Takes a col x row and returns what number square it is
    x = pos[0]
    y = pos[1]
    col = int((x - game_board.starting_pos[0]) / (game_board.square_size))
    row = int((y - game_board.starting_pos[1]) / (game_board.square_size))
    return (row*8)+col

def draw_screen(display, game_board):
    # Draws everything, runs only on event (mouse click), doesn't update the window though
    display.fill((0, 0, 0))
    game_board = draw_board(display, game_board)
    display = draw_pieces(display, game_board)
    return game_board

def draw_screen_update(display, game_board):
    # Draws the screen and updates the window
    game_board = draw_screen(display, game_board)
    pygame.display.update()
    return game_board

def highlight_square(display, color, start_pos, size, square):
    # Takes a number in a list and colors the correct square
    row = int(square / 8)
    col = square % 8
    x = start_pos[0] + (col*size)
    y = start_pos[1] + (row*size)
    pygame.draw.rect(display, color, pygame.Rect(x, y, size, size))
    pygame.draw.rect(display, (0, 0, 0), pygame.Rect(x, y, size, size), 1)

def mark_square(display, color, start_pos, size, square):
    # Takes a number in a list and draws a circle on the correct square
    row = int(square / 8)
    col = square % 8
    x = (start_pos[0] + (col*size)) + (size/2)
    y = start_pos[1] + (row*size) + + (size/2)
    pygame.draw.circle(display, color, (x, y), 5)

def check_left_edge(square):
    # Return True if square is on left edge
    if square % 8 == 0:
        return True
    else: 
        return False

def check_right_edge(square):
    # Return True if square is on right edge
    if (square + 1) % 8 == 0:
        return True
    else: 
        return False

def validate_edge_move(square, offset):
    # If a move is faulty because the piece is on the edge this function returns false 
    # E.X the offset -7 return the square on the top right diagonal, but if the piece is on the right 
    # edge it will return the far left square instead (there is no top right diagonal square)
    # This will create errors for pieces like the bishop
    if check_right_edge(square):
        if offset == 1 or offset == -7 or offset == 9 or offset == 17 or offset == 10 or offset == -15 or offset == -6:
            return False
    if check_left_edge(square):
        if offset == -1 or offset == 7 or offset == -9 or offset == -17 or offset == -10 or offset == 15 or offset == 6:
            return False
    return True

def highlight_moves(game_board, piece, square, offset):
    # Takes an offset (straight, diagnonal, etc) and marks every square until it hits a piece
    # Pieces of different colors will be marked if they are hit
    # Returns a list of all marked squares
    available_moves = []
    if not validate_edge_move(square, offset):
        return available_moves
    square += offset
    while square <= 63 and square >= 0:
        if not validate_edge_move(square, offset):
            if game_board.current_board[square] & 24 != piece & 24:
                available_moves.append(square)
                return available_moves
        if game_board.current_board[square]: 
            if game_board.current_board[square] & 24 != piece & 24:
                available_moves.append(square)
                return available_moves
            else:
                return available_moves
        else:
            available_moves.append(square)

        square += offset

    return available_moves

def single_move(game_board, piece, square, offset):
    # Takes an offset (straight, diagnonal, etc) and marks the square it relates to if the move is valid
    # Pieces of different colors will be marked if they are hit
    # Returns the square if it was valid
    if not validate_edge_move(square, offset):
        return -1
    square += offset
    if square <= 63 and square >= 0:
        if game_board.current_board[square]: 
            if game_board.current_board[square] & 24 != piece & 24:              
                return square
        else:
            return square

def get_all_moves(game_board, piece, square):
    # Checks which piece is being held and marks all squares that it can move to
    # returns a list of all squares
    available_moves = []
    if piece & 7 == 1 and piece & 24 == 8: # White Pawn
        if square > 7:
            if not game_board.current_board[square - 8]:
                available_moves.append(single_move(game_board, piece, square, -8))
                if math.floor(square/8) == 6:
                    if not game_board.current_board[square - 16]:
                        available_moves.append(single_move(game_board, piece, square, -16))
            if game_board.current_board[square - 9] and game_board.current_board[square - 9] & 24 != piece & 24:
                available_moves.append(single_move(game_board, piece, square, -9))
            if game_board.current_board[square - 7] and game_board.current_board[square - 7] & 24 != piece & 24:
                available_moves.append(single_move(game_board, piece, square, -7))

            if square - 9 == game_board.passant and not check_left_edge(square):
                available_moves.append(game_board.passant)
            if square - 7 == game_board.passant and not check_right_edge(square):
                available_moves.append(game_board.passant)

    elif piece & 7 == 1 and piece & 24 == 16:
        if square < 56:
            if not game_board.current_board[square + 8]:    
                available_moves.append(single_move(game_board, piece, square, 8)) # Black Pawn
                if math.floor(square/8) == 1:
                    if not game_board.current_board[square + 16]:
                        available_moves.append(single_move(game_board, piece, square, 16))
            if game_board.current_board[square + 9] and game_board.current_board[square + 9] & 24 != piece & 24:
                available_moves.append(single_move(game_board, piece, square, 9))
            if game_board.current_board[square + 7] and game_board.current_board[square + 7] & 24 != piece & 24:
                available_moves.append(single_move(game_board, piece, square, 7))

            if square + 9 == game_board.passant and not check_right_edge(square):
                available_moves.append(game_board.passant)
            if square + 7 == game_board.passant and not check_left_edge(square):
                available_moves.append(game_board.passant)
    elif piece & 7 == 5: # King
        available_moves.append(single_move(game_board, piece, square, 8))
        available_moves.append(single_move(game_board, piece, square, -8))
        available_moves.append(single_move(game_board, piece, square, -1))
        available_moves.append(single_move(game_board, piece, square, 1))
        available_moves.append(single_move(game_board, piece, square, 9))
        available_moves.append(single_move(game_board, piece, square, -9))
        available_moves.append(single_move(game_board, piece, square, -7))
        available_moves.append(single_move(game_board, piece, square, 7))
        # if piece & 24 == 8:
        #     if game_board.castling[0] == 'K':
        #         available_moves.append(square + 2)
        #     if game_board.castling[1] == 'Q':
        #         available_moves.append(square - 3)
        # elif piece & 24 == 16:
        #     if game_board.castling[2] == 'k':
        #         available_moves.append(square + 2)
        #     if game_board.castling[3] == 'q':
        #         available_moves.append(square - 3)

    elif piece & 7 == 3: # Knight
        if not check_right_edge(square):
            available_moves.append(single_move(game_board, piece, square, -15)) 
            available_moves.append(single_move(game_board, piece, square, 17))
        if not check_right_edge(square + 1):
            available_moves.append(single_move(game_board, piece, square, -6))
            available_moves.append(single_move(game_board, piece, square, 10))
        if not check_left_edge(square):
            available_moves.append(single_move(game_board, piece, square, -17)) 
            available_moves.append(single_move(game_board, piece, square, 15))
        if not check_left_edge(square - 1):
            available_moves.append(single_move(game_board, piece, square, 6))
            available_moves.append(single_move(game_board, piece, square, -10))
    elif piece & 7 == 2 or piece & 7 == 6: # Rook/Queen
        available_moves += highlight_moves(game_board, piece, square, 8)
        available_moves += highlight_moves(game_board, piece, square, -8)
        available_moves += highlight_moves(game_board, piece, square, -1)
        available_moves += highlight_moves(game_board, piece, square, 1)
    if piece & 7 == 4 or piece & 7 == 6: # Bishop/Queen
        available_moves += highlight_moves(game_board, piece, square, -9)
        available_moves += highlight_moves(game_board, piece, square, 7)
        available_moves += highlight_moves(game_board, piece, square, 9)
        available_moves += highlight_moves(game_board, piece, square, -7)
    
    return [n for n in available_moves if n != None and n != -1]

def highlight_all_moves(display, game_board, available_moves):
    for i in available_moves:
        mark_square(display, (100, 170, 100), game_board.starting_pos, game_board.square_size, i)

def get_castle_moves(piece, game_board, square, turn):
    castle_moves = []
    attacked_squares = get_attacking_square(game_board, turn)
    if piece & 24 == 8:
        if game_board.castling[0] == 'K':
            if square not in attacked_squares and square + 1 not in attacked_squares and square + 2 not in attacked_squares:
                if game_board.current_board[square + 1] or game_board.current_board[square + 2]:
                    pass
                else:
                    castle_moves.append(square + 2)
        if game_board.castling[1] == 'Q':
            if square not in attacked_squares and square - 1 not in attacked_squares and square - 2 not in attacked_squares:
                if game_board.current_board[square - 1] or game_board.current_board[square - 2]:
                    pass
                else:
                    castle_moves.append(square - 2)
    elif piece & 24 == 16:
        if game_board.castling[2] == 'k':
            if square not in attacked_squares and square + 1 not in attacked_squares and square + 2 not in attacked_squares:
                if game_board.current_board[square + 1] or game_board.current_board[square + 2]:
                    pass
                else:
                    castle_moves.append(square + 2)
        if game_board.castling[3] == 'q':
            if square not in attacked_squares and square - 1 not in attacked_squares and square - 2 not in attacked_squares:
                if game_board.current_board[square - 1] or game_board.current_board[square - 2]:
                    pass
                else:
                    castle_moves.append(square - 2)

    return castle_moves

def get_attacking_square(game_board, color):
    attacking_moves = []
    i = 0
    while i <= 63:
        if game_board.current_board[i] and game_board.current_board[i] & 24 != color:
            piece = game_board.current_board[i]
            if piece & 7 == 1 and piece & 24 == 8: # White Pawn
                if game_board.current_board[i - 9] and game_board.current_board[i - 9] & 24 != piece & 24:
                    attacking_moves.append(single_move(game_board, piece, i, -9))
                if game_board.current_board[i - 7] and game_board.current_board[i - 7] & 24 != piece & 24:
                    attacking_moves.append(single_move(game_board, piece, i, -7))
            elif piece & 7 == 1 and piece & 24 == 16:
                if game_board.current_board[i + 9] and game_board.current_board[i + 9] & 24 != piece & 24:
                    attacking_moves.append(single_move(game_board, piece, i, 9))
                if game_board.current_board[i + 7] and game_board.current_board[i + 7] & 24 != piece & 24:
                    attacking_moves.append(single_move(game_board, piece, i, 7))
            else:
                attacking_moves += get_all_moves(game_board, game_board.current_board[i], i)
        i += 1

    return [n for n in attacking_moves if n != None]

def check_for_check(game_board, turn):
    attacking = get_attacking_square(game_board, turn)
    i = 0
    while i <= 63:
        if game_board.current_board[i] & 7 == 5 and game_board.current_board[i] & 24 == turn:
            if i in attacking:
                return i + 1
        i += 1
    
    return False

def check_for_checkmate(game_board, turn):
    board_state = game_board

    i = 0 
    while i <= 63:
        if game_board.current_board[i] and game_board.current_board[i] & 24 == turn:
            piece = game_board.current_board[i]
            new_moves = get_all_moves(game_board, piece, i)
            for move in new_moves:
                taken_piece = game_board.current_board[move]
                game_board.current_board[move] = piece
                game_board.current_board[i] = 0
                if check_for_check(game_board, piece & 24) == False:
                    game_board.current_board[i] = piece
                    game_board.current_board[move] = taken_piece
                    return False
                game_board.current_board[i] = piece
                game_board.current_board[move] = taken_piece
        i += 1
    game_board = board_state
    return True

def get_num_moves(display, game_board):
    board_state = game_board
    possible_moves = []
    i = 0 
    while i <= 63:
        if game_board.current_board[i]:
            piece = game_board.current_board[i]
            new_moves = get_all_moves(game_board, piece, i)
            for move in new_moves:
                taken_piece = game_board.current_board[move]
                game_board.current_board[move] = piece
                game_board.current_board[i] = 0
                game_board = draw_screen_update(display, game_board)
                if check_for_check(game_board, piece & 24) == False:
                    possible_moves.append(1)     
                game_board.current_board[i] = piece
                game_board.current_board[move] = taken_piece
                game_board = draw_screen_update(display, game_board)
        i += 1
    
    game_board = board_state
    print("FINAL LENGTH:", len(possible_moves))

def recursive_check(display, game_board, color):
    possible_moves = 0
    i = 0
    while i <= 63:
        if game_board.current_board[i] and game_board.current_board[i] & 24 == color:
            piece = game_board.current_board[i]
            new_moves = get_all_moves(game_board, piece, i)
            for move in new_moves:
                taken_piece = game_board.current_board[move]
                game_board.current_board[move] = piece
                game_board.current_board[i] = 0
                game_board = draw_screen_update(display, game_board)
                if check_for_check(game_board, piece & 24) == False:
                    possible_moves += 1     
                game_board.current_board[i] = piece
                game_board.current_board[move] = taken_piece 
                game_board = draw_screen_update(display, game_board) 
        i += 1
    
    return possible_moves     

def move_check_depth(display, game_board, depth):
    board_state = game_board

    possible_moves = 0
    i = 0 
    while i <= 63:
        if game_board.current_board[i] and game_board.current_board[i] & 24 == 8:
            piece = game_board.current_board[i]
            new_moves = get_all_moves(game_board, piece, i)
            for move in new_moves:
                    taken_piece = game_board.current_board[move]
                    game_board.current_board[move] = piece
                    game_board.current_board[i] = 0
                    game_board = draw_screen_update(display, game_board)
                    if check_for_check(game_board, piece & 24) == False:
                        possible_moves += recursive_check(display, game_board, 16)
                    game_board.current_board[i] = piece
                    game_board.current_board[move] = taken_piece
                    game_board = draw_screen_update(display, game_board)
        i += 1
    
    game_board = board_state
    print("FINAL LENGTH:", possible_moves)

def copied_test(game_board, depth, color):
    if depth == 0:
        return 1
    num_pos = 0
    i = 0
    while i <= 63:
        if game_board.current_board[i] and game_board.current_board[i] & 24 == color:
            piece = game_board.current_board[i] 
            moves = get_all_moves(game_board, piece, i)
            for move in moves:
                taken_piece = game_board.current_board[move]
                game_board.current_board[move] = piece
                game_board.current_board[i] = 0
                if check_for_check(game_board, color) != False:
                    game_board.current_board[i] = piece
                    game_board.current_board[move] = taken_piece
                    continue
                # game_board = draw_screen_update(display, game_board)
                if color == 8:
                    num_pos += copied_test(game_board, depth - 1, 16)
                else:
                    num_pos += copied_test(game_board, depth - 1, 8)
                game_board.current_board[i] = piece
                game_board.current_board[move] = taken_piece
                # game_board = draw_screen_update(display, game_board)
        i += 1

    return num_pos

def copied_test_draw(display, game_board, depth, color):
    if depth == 0:
        return 1
    num_pos = 0
    i = 0
    while i <= 63:
        if game_board.current_board[i] and game_board.current_board[i] & 24 == color:
            piece = game_board.current_board[i] 
            moves = get_all_moves(game_board, piece, i)
            for move in moves:
                taken_piece = game_board.current_board[move]
                game_board.current_board[move] = piece
                game_board.current_board[i] = 0
                if check_for_check(game_board, color):
                    game_board.current_board[i] = piece
                    game_board.current_board[move] = taken_piece
                    continue
                game_board = draw_screen_update(display, game_board)
                time.sleep(1)
                if color == 8:
                    num_pos += copied_test_draw(display, game_board, depth - 1, 16)
                else:
                    num_pos += copied_test_draw(display, game_board, depth - 1, 8)
                game_board.current_board[i] = piece
                game_board.current_board[move] = taken_piece
                game_board = draw_screen_update(display, game_board)
        i += 1

    return num_pos

def main():
    WIDTH = 770
    HEIGHT = 643
    # https://lichess.org/analysis/r1b1k2N/ppp1q1pp/5n2/3Pp3/2Bn4/8/PPPP1bPP/RNBQ1K1R_w_q_-_1_9
    fen =  'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'# Start: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    game_board = fen_to_list(fen)

    pygame.init()
    display = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    game_board = draw_screen_update(display, game_board)
    holding_piece = False
    available_moves = []
    turn = game_board.turn

    print(f"Turn {game_board.fullmove_clock}")
    if turn == 8:
        print("White's Turn")
    else:
        print("Black's Turn")
    run = True
    while run:
        # Program sleeps until event (mouseClick)
        for event in [pygame.event.wait()]+pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
            elif event.type == pygame.WINDOWRESIZED:
                # resize and redraw the screen
                display = resize_screen(display, event.x, event.y)
                game_board = draw_screen_update(display, game_board)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if you pressed a square with a piece on it
                # If you pressed your piece on your turn, it is considered "held"
                square = pos_to_square(game_board, event.pos)
                if square >= 0 and square <= 63:
                    picked_piece = num_to_piece(game_board.current_board[square])
                else:
                    picked_piece = 0
                if picked_piece and picked_piece[1] & 24 == turn:
                    holding_piece = picked_piece
                    available_moves = get_all_moves(game_board, holding_piece[1], square)
                    castle_moves = []
                    if picked_piece[1] & 7 == 5 and square == 60 or square == 4:
                        castle_moves = get_castle_moves(picked_piece[1], game_board, square, turn)
                    available_moves += castle_moves
                    game_board.current_board[square] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                print("Depth 1:", copied_test(game_board, 1, turn))
                print("Depth 2:", copied_test(game_board, 2, turn))
                print("Depth 3:", copied_test(game_board, 3, turn))
                # print("Depth 4:", copied_test(game_board, 4, 8))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and holding_piece:
                # If you let go, check which square you were on
                place_square = pos_to_square(game_board, event.pos)
                game_board = draw_screen(display, game_board)
                if place_square <= 63 and place_square in available_moves and place_square != square:
                    # If you were holding a piece and you let go on a valid move, move the piece
                    # Otherwise return the piece to its original position
                    if place_square in castle_moves:
                        if place_square > square:
                            game_board.current_board[place_square - 1] = game_board.current_board[place_square + 1]
                            game_board.current_board[place_square + 1] = 0
                        else:
                            game_board.current_board[place_square + 1] = game_board.current_board[place_square - 2]
                            game_board.current_board[place_square - 2] = 0

                    og_piece = game_board.current_board[place_square]
                    game_board.current_board[place_square] = picked_piece[1]

                    if picked_piece[1] & 7 == 1 and place_square == game_board.passant:
                        if turn == 8:
                            game_board.current_board[place_square + 8] = 0
                        else:
                            game_board.current_board[place_square - 8] = 0

                    game_board = draw_screen_update(display, game_board)
                    # Check if King is in check
                    check = check_for_check(game_board, turn)
                    if check: # Reset pieces to before move
                        print("CHECK")
                        check -= 1
                        game_board.current_board[square] = picked_piece[1]
                        game_board.current_board[place_square] = og_piece
                        if picked_piece[1] & 7 == 1 and place_square == game_board.passant: # Reset pawns if last move was an en passant
                            if turn == 8:
                                game_board.current_board[place_square + 8] = 17
                            else:
                                game_board.current_board[place_square - 8] = 9
                        available_moves = []
                        game_board = draw_screen_update(display, game_board)
                        highlight_square(display, (255, 0, 0), game_board.starting_pos, game_board.square_size, check)
                    else:
                        columns = 'abcdefgh'
                        row = str(8 - math.floor(place_square/8))
                        column = str(columns[place_square % 8])
                        print(f"{game_board.fullmove_clock}:{game_board.reverse_pieces[picked_piece[1] & 7]}{column}{row}")
                        # Make Move
                        if picked_piece[1] & 7 == 5:
                            if turn == 8:
                                game_board.castling = game_board.castling.replace('K', '-')
                                game_board.castling = game_board.castling.replace('Q', '-')
                            if turn == 16:
                                game_board.castling = game_board.castling.replace('k', '-')
                                game_board.castling = game_board.castling.replace('q', '-')
                        
                        if place_square == 0 or square == 0:
                            game_board.castling = game_board.castling.replace('q', '-')
                        if place_square == 7 or square == 7:
                            game_board.castling = game_board.castling.replace('k', '-')
                        if place_square == 56 or square == 56:
                            game_board.castling = game_board.castling.replace('Q', '-')
                        if place_square == 63 or square == 63:
                            game_board.castling = game_board.castling.replace('K', '-')
                        
                        highlight_square(display, (128, 255, 102), game_board.starting_pos, game_board.square_size, place_square)
                        if picked_piece[1] & 7 == 1:
                            # If a pawn advances to the final rank, make it a queen
                            if math.floor(place_square/8) == 0 or math.floor(place_square/8) == 7:
                                game_board.current_board[place_square] = turn + 6                        
                        
                        # Draw after 50 moves without capture or pawn piece
                        if og_piece or picked_piece[1] & 7 == 1:
                            game_board.halfmove_clock = 0
                        else:
                            if game_board.halfmove_clock == 50:
                                print("DRAW")
                            else:
                                game_board.halfmove_clock += 1

                        # Check for en passant availability
                        if picked_piece[1] & 7 == 1 and abs(place_square - square) > 15:
                            if picked_piece[1] & 24 == 16:
                                game_board.passant = place_square - 8
                            else:
                                game_board.passant = place_square + 8
                        else:
                            game_board.passant = '-'

                        # Change whose turn it is
                        if turn == 8:
                            turn = 16
                        else:
                            game_board.fullmove_clock += 1
                            turn = 8

                        #Check if that's checkmate
                        if check_for_checkmate(game_board, turn):
                            print("CheckMate")
                else:
                    game_board.current_board[square] = picked_piece[1]
                    available_moves = []

                holding_piece = False
                highlight_square(display, (30, 179, 0), game_board.starting_pos, game_board.square_size, square)
                display = draw_pieces(display, game_board)
                pygame.display.update()
        
        if holding_piece:
            # While holding a piece draw the screen every frame and highlight possible moves
            game_board = draw_screen(display, game_board)
            highlight_square(display, (30, 179, 0), game_board.starting_pos, game_board.square_size, square)
            # available_moves = get_all_moves(game_board, holding_piece[1], square)
            highlight_all_moves(display, game_board, available_moves)
            mouse_pos = pygame.mouse.get_pos()
            image = pygame.image.load('./images/' + holding_piece[0] + '.png')
            display.blit(image, (mouse_pos[0] - 30, mouse_pos[1] - 30))
            pygame.display.update()

    pygame.quit()


main()