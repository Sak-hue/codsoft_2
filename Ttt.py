from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
import copy
import math

X = 'X'
O = 'O'

app = Flask(__name__)
CORS(app)

def player(board):
    countX = 0
    countO = 0
    for row in board:
        for cell in row:
            if cell == X:
                countX += 1
            elif cell == O:
                countO += 1
    return O if countX > countO else X

def actions(board):
    possibleActions = set()
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] is None:
                possibleActions.add((row, col))
    return possibleActions

def result(board, action):
    if action not in actions(board):
        raise Exception("Not valid action")
    row, col = action
    board_copy = copy.deepcopy(board)
    board_copy[row][col] = player(board)
    return board_copy

def checkRow(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    return False

def checkCol(board, player):
    for col in range(len(board[0])):
        if all(board[row][col] == player for row in range(len(board))):
            return True
    return False

def diagonalL(board, player):
    return all(board[i][i] == player for i in range(len(board)))

def diagonalR(board, player):
    return all(board[i][len(board) - i - 1] == player for i in range(len(board)))

def winner(board):
    if checkRow(board, X) or checkCol(board, X) or diagonalR(board, X) or diagonalL(board, X):
        return X
    elif checkRow(board, O) or checkCol(board, O) or diagonalR(board, O) or diagonalL(board, O):
        return O
    else:
        return None

def terminal(board):
    return winner(board) is not None or all(cell is not None for row in board for cell in row)

def utility(board):
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0

def maximising(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, minimising(result(board, action)))
    return v

def minimising(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, maximising(result(board, action)))
    return v

def minimax(board):
    if terminal(board):
        return None
    if player(board) == X:
        plays = [[minimising(result(board, action)), action] for action in actions(board)]
        return max(plays, key=lambda x: x[0])[1]
    else:
        plays = [[maximising(result(board, action)), action] for action in actions(board)]
        return min(plays, key=lambda x: x[0])[1]

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    board = data['board']
    move = minimax(board)
    return jsonify({'row': move[0], 'col': move[1]})

if __name__ == '__main__':
    app.run(debug=True)
