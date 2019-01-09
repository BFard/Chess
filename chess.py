import random
import copy
import sys

ai_module = "ai"
if ai_module:
	try:
		exec("import " + ai_module + " as ai")
	except:
		print("\nError: The given ai module could not be found.")
		exit()

def square_name(row, col):
	return chr(97 + col) + str(8 - row)

class Piece():
	def __init__(self, piece_type, piece_color):
		self.type = piece_type
		self.color = piece_color

class Game():
	def __init__(self):
		self.board = self.create_board()
		self.curr_player = 1
		self.is_over = False
		self.valid_moves = self.get_valid_moves()

	def get_potential_moves(self, board, piece, row, col):
		potential_moves = []

		if piece.type == "P":
			direction = -piece.color
			special_rows = {-1: 1, 1: 6}
			if board[row + direction][col] is None:
				potential_moves.append((row + direction, col))
				if row == special_rows[piece.color] and board[row + 2 * direction][col] is None:
					potential_moves.append((row - 2, col))
			left = board[row + direction][col - 1]
			if left is not None and left.color != piece.color:
				potential_moves.append((row + direction, col - 1))
			right = board[row + direction][col + 1]
			if right is not None and right.color != piece.color:
				potential_moves.append((row + direction, col + 1))

		return potential_moves

	def get_valid_moves(self):
		valid_moves = {}
		for row in range(8):
			for col in range(8):
				piece = self.board[row][col]
				if piece is None or piece.color != self.curr_player:
					continue
				for move in self.get_potential_moves(self.board, piece, row, col):
					new_row, new_col = move
					board_cpy = copy.deepcopy(self.board)
					board_cpy[new_row][new_col] = board_cpy[row][col]
					board_cpy[row][col] = None
					if not self.in_check(board_cpy, piece.color):
						alg_notation = piece.type + square_name(row, col) + square_name(new_row, new_col)
						valid_moves[alg_notation] = ((row, col), move)


		return valid_moves

	def make_move(self, move):
		start_square, end_square = self.valid_moves[move]
		board[end_square[0]][end_square[1]] = board[start_square[0]][start_square[1]]
		board[start_square[0]][start_square[1]] = None
		self.curr_player *= -1
		self.is_over = self.get_game_status()
		self.valid_moves = self.get_valid_moves()

	def in_check(self, board, player):
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if piece is None:
					continue
				if piece.type == "K" and piece.color == player:
					king_row, king_col = row, col
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if piece is None:
					continue
				potential_moves = self.get_potential_moves(board, piece, row, col)
				if (king_row, king_col) in potential_moves:
					return True
		return False

	def create_board(self):
		board = [[None for _ in range(8)] for _ in range(8)]
		colors = {0: -1, 1: -1, 6: 1, 7: 1}
		for row in [0, 7]:
			board[row][0] = Piece("R", colors[row])
			board[row][1] = Piece("N", colors[row])
			board[row][2] = Piece("B", colors[row])
			board[row][3] = Piece("Q", colors[row])
			board[row][4] = Piece("K", colors[row])
			board[row][5] = Piece("B", colors[row])
			board[row][6] = Piece("N", colors[row])
			board[row][7] = Piece("R", colors[row])
		for row in [1, 6]:
			for col in range(8):
				board[row][col] = Piece("P", colors[row])
		return board

	def print_board(self, perspective):
		board_str = "\n"
		line = "---------------------------------\n"
		for row in range(8)[::perspective]:
			board_str += line
			for col in range(8)[::perspective]:
				piece = self.board[row][col]
				if piece is None:
					board_str += "|   "
				elif piece.color == -1:
					board_str += "| " + piece.type.lower() + " "
				else:
					board_str += "| " + piece.type + " "
			board_str += "|\n"
		board_str += line
		print(board_str)

def play(mode, color):
	if mode not in ["human", "computer"]:
		print('\nError: The given mode does not exist. Try "human" or "computer".')
		exit()
	elif mode == "human":
		computer_player = None
	elif color is None:
		computer_player = random.choice([-1, 1])
	elif color == "white":
		computer_player = -1
	elif color == "black":
		computer_player = 1
	else:
		print('\nError: Invalid color choice. Try "white" or "black".')
		exit()

	print("\nWelcome to chess.")
	print("Please enter moves in standard algebraic notation.\n")
	input("Press Enter to start...")

	game = Game()
	moves_played = 0
	player_map = {1: "white", -1: "black"}

	def get_move():
		if mode == "human" or game.curr_player != computer_player:
			message = "Please enter a move for " + player_map[game.curr_player] + ": "
			move = input(message)
			while move not in game.valid_moves:
				print("\nInvalid move entered. Valid moves:", game.valid_moves, "\n")
				move = input(message)
		else:
			print("The computer will make a move for " + player_map[game.curr_player] + ".")
			move = ai.get_move(game)
		return move

	while not game.is_over:
		game.print_board(game.curr_player)
		next_move = get_move()
		game.make_move(next_move)
		moves_played += 1

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print('\nPlease enter a mode. Try "human" or "computer".')
	elif len(sys.argv) == 2:
		play(sys.argv[1], None)
	else:
		play(sys.argv[1], sys.argv[2])