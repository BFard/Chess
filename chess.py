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

	def get_potential_squares(self, board, row, col, ep_square, castle_privileges):
		potential_squares = self.get_attacked_squares(board, row, col)

		if self.type == "P":
			direction = -self.color
			front = (row + direction, col)
			if board[row + direction][col] is None:
				potential_squares.append(front)
				special_rows = {-1: 1, 1: 6}
				if row == special_rows[self.color] and board[row + 2 * direction][col] is None:
					potential_squares.append((row + 2 * direction, col))
			left = (row + direction, col - 1)
			right = (row + direction, col + 1)
			if not out_of_bounds(left):
				piece = board[row + direction][col - 1]
				if piece is None:
					potential_squares.remove(left)
				if left == ep_square:
					potential_squares.append((row + direction, col - 1, "en_passant"))
			if not out_of_bounds(right):
				piece = board[row + direction][col + 1]
				if piece is None:
					potential_squares.remove(right)
				if right == ep_square:
					potential_squares.append((row + direction, col + 1, "en_passant"))

		elif self.type == "K":
			if "long" in castle_privileges[self.color] and \
			board[row][col - 1] == board[row][col - 2] == board[row][col - 3] is None:
				potential_squares.append((row, col - 2, "long_castle"))
			if "short" in castle_privileges[self.color] and \
			board[row][col + 1] == board[row][col + 2] is None:
				potential_squares.append((row, col + 2, "short_castle"))

		return potential_squares

class Game():
	def __init__(self):
		self.curr_board = self.create_board()
		self.curr_player = 1
		self.result = None
		self.ep_square = None
		self.fifty_move_counter = 0
		self.king_positions = {1: (7, 4), -1: (0, 4)}
		self.castle_privileges = {1: ["long", "short"], -1: ["long", "short"]}
		self.valid_moves = self.get_valid_moves(self.curr_board, self.curr_player, self.king_positions, self.ep_square, self.castle_privileges)

	def get_valid_moves(self, board, player, king_positions, ep_square, castle_privileges, stop_early=False):
		valid_moves = {}

		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if piece is None or piece.color != player:
					continue
				for square in piece.get_potential_squares(board, row, col, ep_square, castle_privileges):
					new_row, new_col = square[0], square[1]
					board_copy = copy.deepcopy(board)
					board_copy[row][col] = None
					new_king_positions = king_positions.copy()
					if len(square) == 3 and square[2] == "en_passant":
						board_copy[row][new_col] = None
					elif len(square) == 3 and square[2] == "long_castle":
						board_copy[row][col - 1] = piece
						new_king_positions[piece.color] = (row, col - 1)
						if self.in_check(board, piece.color, king_positions) or \
						self.in_check(board_copy, piece.color, new_king_positions):
							continue
						board_copy[row][col - 1] = board_copy[row][0]
					elif len(square) == 3 and square[2] == "short_castle":
						board_copy[row][col + 1] == piece
						new_king_positions[piece.color] = (row, col + 1)
						if self.in_check(board, piece.color, king_positions) or \
						self.in_check(board_copy, piece.color, new_king_positions):
							continue
						board_copy[row][col + 1] = board_copy[row][7]
					board_copy[new_row][new_col] = piece
					if piece.type == "K":
						new_king_positions[piece.color] = (new_row, new_col)
					if not self.in_check(board_copy, piece.color, new_king_positions):
						if stop_early:
							return "nonempty"
						move = ((row, col), square)
						if piece.type == "P":
							if new_col == col:
								alg_notation = square_name(new_row, new_col)
							else:
								alg_notation = chr(97 + col) + "x" + square_name(new_row, new_col)
							promotion_rows = {1: 0, -1: 7}
							if new_row == promotion_rows[piece.color]:
								promotions = [alg_notation + "=N", alg_notation + "=B", alg_notation + "=R", alg_notation + "=Q"]
								for i in range(4):
									option = promotions[i]
									board_copy[new_row][new_col] = Piece(option[-1], piece.color)
									checks_opp = self.in_check(board_copy, -player, new_king_positions)
									mates_opp = checks_opp and \
									len(self.get_valid_moves(board_copy, -player, new_king_positions, None, castle_privileges, True)) == 0 
									if mates_opp:
										promotions[i] += "#"
									elif checks_opp:
										promotions[i] += "+"
									valid_moves[promotions[i]] = move
								continue
						elif piece.type == "K":
							if len(square) == 3 and square[2] == "long_castle":
								alg_notation = "O-O-O"
							elif len(square) == 3 and square[2] == "short_castle":
								alg_notation = "O-O"
							else:
								alg_notation = piece.type + square_name(new_row, new_col)
						else:
							alg_notation = piece.type + square_name(row, col) + square_name(new_row, new_col)
						if board[new_row][new_col] is not None and piece.type != "P":
							alg_notation = alg_notation[:-2] + "x" + alg_notation[-2:]
						if piece.type == "P" and abs(new_row - row) == 2:
							new_ep_square = (row, col - piece.color)
						else:
							new_ep_square = None
						checks_opp = self.in_check(board_copy, -player, new_king_positions)
						mates_opp = checks_opp and \
						len(self.get_valid_moves(board_copy, -player, new_king_positions, new_ep_square, castle_privileges, True)) == 0
						if mates_opp:
							alg_notation += "#"
						elif checks_opp:
							alg_notation += "+"
						valid_moves[alg_notation] = move

		replacements = {}
		for alg_move in valid_moves.keys():
			piece_type = alg_move[0]
			if piece_type not in ["N", "B", "R", "Q"]:
				continue
			file = alg_move[1]
			rank = alg_move[2]
			def dest(move):
				if "x" in move:
					return move[4:6]
				else:
					return move[3:5]
			rank_duplicated = False
			file_duplicated = False
			duplicates = [move for move in valid_moves.keys() if move[0] == piece_type and dest(move) == dest(alg_move) and move != alg_move]
			for other_move in duplicates:
				if other_move[1] == file:
					file_duplicated = True
				if other_move[2] == rank:
					rank_duplicated = True
			if rank_duplicated and file_duplicated:
				continue
			elif file_duplicated:
				new_notation = piece_type + alg_move[2:]
			elif duplicates:
				new_notation = piece_type + file + alg_move[3:]
			else:
				new_notation = piece_type + alg_move[3:]
			replacements[alg_move] = new_notation
		
		for to_replace in replacements:
			replacement = replacements[to_replace]
			valid_moves[replacement] = valid_moves[to_replace]
			valid_moves.pop(to_replace)

		return valid_moves

	def transfer(self, start_square, end_square):
		self.curr_board[end_square[0]][end_square[1]] = self.curr_board[start_square[0]][start_square[1]]
		self.curr_board[start_square[0]][start_square[1]] = None

	def make_move(self, move):
		move_data = self.valid_moves[move]
		start_square = move_data[0]
		end_square = move_data[1]
		row, col = start_square
		new_row, new_col = end_square[0], end_square[1]
		piece = self.curr_board[row][col]
		if len(end_square) == 3 and end_square[2] == "en_passant":
			self.curr_board[row][new_col] = None
		elif len(end_square) == 3 and end_square[2] == "long_castle":
			self.curr_board[row][col - 1] = self.curr_board[row][0]
			self.curr_board[row][0] = None
		elif len(end_square) == 3 and end_square[2] == "short_castle":
			self.curr_board[row][col + 1] = self.curr_board[row][7]
			self.curr_board[row][7] = None
		self.transfer(start_square, end_square)
		if "=" in move:
			if move[-1] in ["+", "#"]:
				new_type = move[-2]
			else:
				new_type = move[-1]
			self.curr_board[new_row][new_col] = Piece(new_type, piece.color)
		elif piece.type == "P" and abs(new_row - row) == 2:
			self.ep_square = (row - piece.color, col)
		elif piece.type == "K":
			self.king_positions[piece.color] = (new_row, new_col)
			self.castle_privileges[piece.color] = []
		elif piece.type == "R":
			starting_rows = {-1: 0, 1: 7}
			left_square = (starting_rows[piece.color], 0)
			right_square = (starting_rows[piece.color], 7)
			if start_square == left_square and "long_castle" in self.castle_privileges:
				self.castle_privileges[piece.color].remove("long_castle")
			elif start_square == right_square and "short_castle" in self.castle_privileges:
				self.castle_privileges[piece.color].remove("short_castle")
		if piece.type == "P" or "x" in move:
			self.fifty_move_counter = 0
		else:
			self.fifty_move_counter += 1
		self.curr_player *= -1
		self.valid_moves = self.get_valid_moves(self.curr_board, self.curr_player, self.king_positions, self.ep_square, self.castle_privileges)
		if "#" in move:
			self.result = piece.color
		elif not self.valid_moves or self.fifty_move_counter == 100 or self.insufficient_material():
			self.result = 0

	def insufficient_material(self):
		num_pieces = 0
		for row in range(8):
			for col in range(8):
				piece = self.curr_board[row][col]
				if piece is not None and piece.type in ["P", "R", "Q"]:
					return False
				elif piece is not None:
					num_pieces += 1
		return num_pieces <= 3

	def in_check(self, board, player, king_positions):
		for row in range(8):
			for col in range(8):
				piece = board[row][col]
				if piece is not None and piece.color != player:
					attacked_squares = piece.get_attacked_squares(board, row, col)
					if king_positions[player] in attacked_squares:
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
				print("\nInvalid move entered. Valid moves: " + str(list(game.valid_moves.keys())).replace("'", "")[1:-1] + "\n")
				move = input(message)
		else:
			print("The computer will make a move for " + player_map[game.curr_player] + ".")
			move = ai.get_move(game)
		return move

	while game.result is None:
		game.print_board(game.curr_player)
		next_move = get_move()
		game.make_move(next_move)
		moves_played += 1

	game.print_board(game.curr_player)
	if game.result == 0:
		print("The game is a draw.")
	else:
		winner = player_map[game.result]
		winner = winner[0].upper() + winner[1:]
		print(winner + " wins.")
	print("Thanks for playing chess.")

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print('\nPlease enter a mode. Try "human" or "computer".')
	elif len(sys.argv) == 2:
		play(sys.argv[1], None)
	else:
		play(sys.argv[1], sys.argv[2])