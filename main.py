import os
import hashlib
from time import time
from random import random, choice
from collections import Counter, defaultdict

import chess
from trueskill import Rating, rate_1vs1

from vm import execute, generate_random, mutate, F_GAS, splice, F_MEM, F_GAMEMEM, STARTGAS, F_IP, F_CODE, code_to_state


numbers = ".PNBRQKpnbrqk"

def num(board):
	return [numbers.find(p) for p in str(board).replace("\n","").replace(" ","")]

index = 0

MAXPOOL = 30

pool = {}
best = None
queue = []

def get_player2():
	global queue
	if random() < len(queue)/30 and len(queue) > 0:
		state = queue.pop(0)
	else:
		state = generate_random()
	return state

def get_player():
	if random() < 0.5 and len(pool) > 0:
		return code_to_state(choice(list(pool.keys())))
	else:
		if random() < 0.5 and len(pool) > 2:
			return code_to_state(mutate(splice(list(choice(list(pool.keys()))), list(choice(list(pool.keys()))))))
		else:
			return generate_random()

games = 0

try:
	while True:

		p1 = get_player()
		p2 = get_player()

		board = chess.Board()



		out = defaultdict(list)

		while not board.is_game_over():
			#print(board)
			legal = sorted([x.uci() for x in list(board.generate_legal_moves())])
			mem = [len(legal)] + num(board)
			active = p1 if board.turn == chess.WHITE else p2

			active[F_GAMEMEM] = mem

			has_output = False


			def output(value):
				#XXX use uci coordinates instead of index into legal?
				global has_output, pool
				#print("OUTPUT", value)
				#out.append(value)
				#out[entuple(active[F_CODE])].append(value)
				board.push(chess.Move.from_uci(legal[value%len(legal)]))
				has_output = True

			startgas = active[F_GAS]

			stats = execute(output, active)
			out[tuple(active[F_CODE])] = stats

			if not has_output:
				#print("NO OUTPUT")
				break

		#print(out)

		draw = False
		if not has_output:
			if board.turn == chess.WHITE:
				winner = p2
				loser = p1
			else:
				winner = p1
				loser = p2
		else:
			res = board.result()
			if res == "1/2-1/2":
				draw = True
				winner = p1
				loser = p2
			else:
				if res == "1-0":
					winner = p2
					loser = p1
				else:
					winner = p1
					loser = p2

		# TODO
		gasdelta = winner[F_GAS] - STARTGAS

		winnercode = tuple(winner[F_CODE])
		losercode = tuple(loser[F_CODE])

		#win, draw, loss
		winnerdata = pool.get(winnercode, [Rating(), 0, 0, 0, []])
		loserdata = pool.get(losercode, [Rating(), 0, 0, 0, []])

		if draw:
			winnerdata[2] += 1
			loserdata[2] += 1
		else:
			winnerdata[1] += 1
			loserdata[3] += 1


		winnerrating, loserrating = rate_1vs1(winnerdata[0], loserdata[0], drawn=draw)
		winnerdata[0] = winnerrating
		loserdata[0] = loserrating
		winnerdata[4] = out[winnercode]
		loserdata[4] = out[losercode]
		pool[winnercode] = winnerdata
		pool[losercode] = loserdata

		if not has_output:
			del pool[losercode]


		os.system("clear")
		toplist = sorted(pool.items(), key=lambda kv:kv[1][0].mu, reverse=True)
		for k,v in toplist[MAXPOOL:]:
			del pool[k]

		toplist = toplist[:MAXPOOL]
		for k,v in toplist:
			print(hashlib.sha256(str(k).encode("ascii")).hexdigest()[:6], v)#, k[:10])

		games += 1
		print(games)#, toplist[0] if toplist else None)
except KeyboardInterrupt:
	pass

toplist = sorted(pool.items(), key=lambda kv:kv[1][0].mu, reverse=True)
top = toplist[0]

playercolor = chess.WHITE
npc = code_to_state(top[0])

board = chess.Board()
while not board.is_game_over():
	print(board)
	if board.turn == playercolor:
		while True:
			try:
				board.push(chess.Move.from_uci(input()))
				break
			except ValueError:
				pass
	else:
		#print(board)
		legal = sorted([x.uci() for x in list(board.generate_legal_moves())])
		mem = [len(legal)] + num(board)
		active[F_GAMEMEM] = mem

		has_output = False


		def output(value):
			#XXX use uci coordinates instead of index into legal?
			global has_output, pool
			print("OUTPUT", value)
			#out.append(value)
			board.push(chess.Move.from_uci(legal[value%len(legal)]))
			has_output = True

		startgas = active[F_GAS]

		execute(output, active)

		if not has_output:
			#print("NO OUTPUT")
			break
