from subprocess import Popen, PIPE
import time

def square_name(square):
	return chr(97 + square[1]) + str(8 - square[0])

def get_move(game):
	stockfish = Popen(["stockfish_10_x32"], stdin=PIPE, stdout=PIPE)
	fen = game.fen().encode("utf-8")
	stockfish.stdin.write(b'position fen "' + fen + b'"\n')
	stockfish.stdin.flush()
	stockfish.stdin.write(b'go\n')
	stockfish.stdin.flush()
	time.sleep(0.5)
	response = str(stockfish.communicate()[0])
	index = response.index("bestmove")
	choice_start = response[index + 9: index + 11]
	choice_end = response[index + 11: index + 13]
	promotion = response[index + 13]
	for move in game.valid_moves:
		start_square = square_name(game.valid_moves[move][0])
		end_square = square_name(game.valid_moves[move][1])
		if choice_start == start_square and choice_end == end_square:
			if promotion not in ["n", "b", "r", "q"] or "=" in move and promotion.upper() == move[move.index("=") + 1]:
				return move