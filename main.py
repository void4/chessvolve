import os
from time import time
from random import random, choice
from collections import Counter
from trueskill import Rating, rate_1vs1
from vm import execute, generate_random, mutate, F_GAS, splice, F_MEM, STARTGAS, F_IP

import chess

numbers = ".PNBRQKpnbrqk"

def num(board):
	return [numbers.find(p) for p in str(board).replace("\n","").replace(" ","")]

index = 0



pool = {}
best = None
queue = []

def get_player():
    global queue
    if random() < len(queue)/30 and len(queue) > 0:
        state = queue.pop(0)
    else:
        state = generate_random()
    return state

while True:
    print("queue", len(queue))

    p1 = get_player()
    p2 = get_player()

    board = chess.Board()

    while not board.is_game_over():
        #print(board)
        legal = sorted([x.uci() for x in list(board.generate_legal_moves())])
        mem = [len(legal)] + num(board)
        active = p1 if board.turn == chess.WHITE else p2

        active[F_MEM] = mem

        has_output = False

        def output(value):
            global has_output
            #print("OUTPUT", value)
            board.push(chess.Move.from_uci(legal[value%len(legal)]))
            has_output = True

        startgas = active[F_GAS]

        execute(output, active)

        if not has_output:
            #print("NO OUTPUT")
            break

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
        else:
            if res == "1-0":
                winner = p2
                loser = p1
            else:
                winner = p1
                loser = p2

    if draw:
        pass
    else:
        winner[F_IP] = 0
        winner[F_GAS] = STARTGAS
        #if random() > len(queue)/30:
        queue.append(winner)
        if random() > len(queue)/30:
            queue.append(mutate(winner))
        if has_output:
            if random() > len(queue)/30:
                queue.append(mutate(loser))

    gasdelta = winner[F_GAS] - STARTGAS
    """
    score = diffcolors# - gasdelta

    if best is None or score > pool[best]:
        print("New best: ", score, "Queue length: ", len(queue))
        key = str(state)
        pool[key] = score
        best = key

        for i in range(50):
            if random() > len(queue)/50:
                if len(queue) > 0:
                    other = choice(queue)
                else:
                    other = generate_random()

                newstate = mutate(splice(other, state))
                newstate[F_X] = state[F_X]
                newstate[F_Y] = state[F_Y]
                newstate[F_R] = state[F_R]
                queue.append(newstate)
    """
