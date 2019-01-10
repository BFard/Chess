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

def out_of_bounds(square):
	row, col = square
	return row < 0 or row > 7 or col < 0 or col > 7

class Piece():
	def __init__(self, piece_type, piece_color):
		self.type = piece_type
		self.color = piece_color

	def get_attacked_squares(self, board, row, col):
		attacked_squares = []

		def fan_out(row_dir, col_dir, limit):
			for i in range(1, limit + 1):
				new_row, new_col = row + i * row_dir, col + i * col_dir
				square = (new_row, new_col)
				if out_of_bounds(square):
					break
				piece = board[new_row][new_col]
				if piece is not None:
					if piece.color == self.color:
						break
					else:
						attacked_squares.append(square)
						break
				else:
					attacked_squares.append(square)

		def fan_diagonal(limit):
			fan_out(1, 1, limit)
			fan_out(1, -1, limit)
			fan_out(-1, 1, limit)
			fan_out(-1, -1, limit)

		def fan_horizontal(limit):
			fan_out(1, 0, limit)
			fan_out(0, 1, limit)
			fan_out(-1, 0, limit)
			fan_out(0, -1, limit)

		if self.type == "P":
			direction = -self.color
			fan_out(direction, 1, 1)
			fan_out(direction, -1, 1)

		elif self.type == "B":
			fan_diagonal(7)

		elif self.type == "R":
			fan_horizontal(7)

		elif self.type == "Q":
			fan_diagonal(7)
			fan_horizontal(7)

		elif self.type == "K":
			fan_diagonal(1)
			fan_horizontal(1)

		elif self.type == "N":
			fan_out(1, 2, 1)
			fan_out(1, -2, 1)
			fan_out(-1, 2, 1)
			fan_out(-1, -2, 1)
			fan_out(2, 1, 1)
			fan_out(2, -1, 1)
			fan_out(-2, 1, 1)
			fan_out(-2, -1, 1)

		return attacked_squares

	def get_potential_moves(self, board, row, col):
		potential_moves = self.get_attacked_squares()

		if self.type == "P":
			direction = -self.color
			front = (row + direction, col)
			if board[row + direction][col] is None:
				potential_moves.append(front)
				special_rows = {-1: 1, 1: 6}
				if row = special_rows[piece.color] and board[row + 2 * direction][col] is None:
					potential_moves.append((row + 2 * direction, col))
			left = (row + direction, col - 1)
			right = (row + direction, col + 1)
			if not out_of_bounds(left):
				piece = board[row + direction, col - 1]
				if piece is None or piece.color == self.color:
					potential_moves.remove(left)
			if not out_of_bounds(right):
				piece = board[row + direction, col + 1]
				if piece is None or piece.color == self.color:
					potential_moves.remove(left)

		return potential_moves

class Game():
	def __init__(self):
		self.curr_board = self.create_board()
		self.curr_player = 1
		self.is_over = False
		self.king_positions = {1: (7, 4), -1: (0, 4)}
		self.valid_moves = None #self.get_valid_moves()

	def get_valid_moves(self):
		valid_moves = {}

		for row in range(8):
			for col in range(8):
				piece = self.curr_board[row][col]
				if piece is None or piece.color != self.curr_player:
					continue
				for move in self.get_potential_moves(self.curr_board, piece, row, col):
					new_row, new_col = move
					board_cpy = copy.deepcopy(self.curr_board)
					board_cpy[new_row][new_col] = board_cpy[row][col]
					board_cpy[row][col] = None
					if not self.in_check(board_cpy, piece.color):
						alg_notation = piece.type + square_name(row, col) + square_name(new_row, new_col)
						valid_moves[alg_notation] = ((row, col), move)


		return valid_moves

	def transfer(self, start_square, end_square):
		self.curr_board[end_square[0]][end_square[1]] = self.curr_board[start_square[0]][start_square[1]]
		self.curr_board[start_square[0]][start_square[1]] = None

	def make_move(self, move):
		start_square, end_square = self.valid_moves[move]
		self.transfer(start_square, end_square)
		self.curr_player *= -1
		self.is_over = self.get_game_status()
		self.valid_moves = self.get_valid_moves()

	def in_check(self, board, player):
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if piece is not None and piece.color != player:
					attacked_squares = piece.get_attacked_squares(board, row, col)
					if self.king_positions[player] in attacked_squares:
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
				piece = self.curr_board[row][col]
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