import random
import copy

max_depth = 1

def get_move(initial_state):
	next_states = successors(initial_state)
	values = [value(state, 0, -1000, 1000) for state in next_states]
	if initial_state.curr_player == 1:
		max_val = max(values)
		options = [i for i in range(len(next_states)) if values[i] == max_val]
	else:
		min_val = min(values)
		options = [i for i in range(len(next_states)) if values[i] == min_val]
	move_list = list(initial_state.valid_moves.keys())
	return move_list[random.choice(options)]

def value(state, depth, alpha, beta):
	if depth == max_depth:
		return evaluation(state.curr_board)
	elif state.curr_player == 1:
		return max_value(state, depth, alpha, beta)
	else:
		return min_value(state, depth, alpha, beta)

def max_value(state, depth, alpha, beta):
	max_val = -1000
	for next_state in successors(state):
		max_val = max(max_val, value(next_state, depth + 1, alpha, beta))
		if max_val >= beta:
			return max_val
		alpha = max(max_val, alpha)
	return max_val

def min_value(state, depth, alpha, beta):
	min_val = 1000
	for next_state in successors(state):
		min_val = min(min_val, value(next_state, depth + 1, alpha, beta))
		if min_val <= alpha:
			return min_val
		beta = min(min_val, beta)
	return min_val

def evaluation(board):
	piece_values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}
	total_value = 0
	for row in range(8):
		for col in range(8):
			piece = board[row][col]
			if piece is not None:
				total_value += piece.color * piece_values[piece.type]
	return total_value

def successors(state):
	successors = []
	for move in state.valid_moves:
		state_copy = copy.deepcopy(state)
		state_copy.make_move(move)
		successors.append(state_copy)
	return successors