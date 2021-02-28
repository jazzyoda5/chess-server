import random
import chess
import copy
import evaluation_tables as eval_tables
# For now only returns a random move

w_pawns = ['wR', 'wK', 'wB', 'wQ', 'wKn', 'wP']
b_pawns = ['bR', 'bK', 'bB', 'bQ', 'bKn', 'bP']

def get_move(data):
    # Get the data
    game_state = data['game_state']
    comp_color = data['comp_color']
    board = chess.Board(convert_format(game_state, comp_color))

    global COUNT
    COUNT = 0

    print('[ENGINE] Board recieved:')
    print(board)

    # Check if game if already over
    if board.is_checkmate():
        print('[ENGINE] Computer lost. Checkmate.')
        return None

    # Get all possible moves and evaluate them
    moves = board.generate_legal_moves()

    # Best move
    max_eval = -10000

    for uci_move in moves:
        move = chess.Move.from_uci(str(uci_move))
        board.push(move)
        eval_of_board = minimax(board, 2, -10000, 10000, True)

        if eval_of_board > max_eval:
            max_eval = eval_of_board
            best_pos = copy.deepcopy(board)

        board.pop()

    # Set third arg to false if convert back from fen
    new_state = convert_format(best_pos.fen(), comp_color, False)
    print('[ENGINE] Board emitted: ')
    print(best_pos)

    obj = {'game_state': new_state}

    del board

    return obj


def minimax(board, depth, alpha, beta, maximizing_player):
    if board.is_checkmate() and maximizing_player:
        # If computer can win, return a big evaluation like a thousand
        return 200000

    if depth == 0:
        evaluation = board_evaluation(board)
        return evaluation

    if maximizing_player:
        max_eval = -10000
        # Get all possible moves
        moves = board.generate_legal_moves()

        for uci_move in moves:
            move = chess.Move.from_uci(str(uci_move))
            board.push(move)
            evaluation = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break

        return max_eval

    else:
        min_eval = 10000
        moves = board.generate_legal_moves()

        for uci_move in moves:
            move = chess.Move.from_uci(str(uci_move))
            board.push(move)
            evaluation = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break

        return min_eval


# Convert front end board representation into FEN
# Or from FEN to frontend representation
# Too lazy to translate my own chess logic from js to python
# So using python-chess here
def convert_format(game_state, comp_color, to_fen=True):

    if to_fen:
        pychess_pawns = ['r', 'k', 'b', 'q', 'n', 'p']

        # Board is a python-chess representation of a chess board
        board = ''

        for i in range(8):
            for j in range(8):
                pawn = game_state[i][j]

                if pawn in w_pawns:
                    index = w_pawns.index(pawn)
                    new_pawn = pychess_pawns[index].upper()
                    board += new_pawn

                elif pawn in b_pawns:
                    index = b_pawns.index(pawn)
                    new_pawn = pychess_pawns[index]
                    board += new_pawn

                else:
                    # Num of empty squares on the end of board string
                    try:
                        prev_square = board[len(board) - 1]

                        # If previous square was also empty
                        if prev_square.isnumeric():
                            square = str(int(prev_square) + 1)
                            board = board[:-1]
                            board += square

                        else:
                            board += '1'

                    # If it is top left square on the board it throws an error
                    except IndexError:
                        board += '1'

                if j == 7 and i != 7:
                    board += '/'

        board += ' ' + comp_color

    else:
        pychess_pawns_b = ['r', 'k', 'b', 'q', 'n', 'p']
        pychess_pawns_w = ['R', 'K', 'B', 'Q', 'N', 'P']

        board = [[]]

        # Here board arrives as a fen string
        # start on row 0
        row = 0
        for letter in game_state:
            if letter == '/':
                board.append([])
                row += 1

            elif letter == ' ':
                return board

            elif letter in pychess_pawns_b:
                index = pychess_pawns_b.index(letter)
                pawn = b_pawns[index]
                board[row].append(pawn)

            elif letter in pychess_pawns_w:
                index = pychess_pawns_w.index(letter)
                pawn = w_pawns[index]
                board[row].append(pawn)

            elif letter.isnumeric():
                for i in range(int(letter)):
                    board[row].append('')

    return board


def board_evaluation(board):
    evaluation = 0

    board_str = board.fen()

    i = 0
    y = 0
    x = 0
    while True:
        piece = board_str[i]
        if piece == ' ':
            break
        elif piece == '/':
            y += 1
            x = 0
        elif piece.isdigit():
            num = int(piece)
            x += (num - 1)

        else: 

            value = eval_tables.eval_list[piece]
            evaluation += value

            # Position evaluation
            eval_table = getattr(eval_tables, piece.lower())

            # If piece is black invert the table
            if piece.islower() and piece != 'q':
                inv_table = list(reversed(eval_table))
                # Get the proper eval table
                evaluation += inv_table[y][x]

            else:
                evaluation += eval_table[y][x]
        
        if piece != '/':
            x += 1
        i += 1

    return evaluation
