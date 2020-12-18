import os
from time import time
from random import random, choice
from collections import Counter
from trueskill import Rating, rate_1vs1
from vm import execute, generate_random, mutate, F_GAS, splice, F_MEM, STARTGAS, F_IP, F_CODE, code_to_state
import hashlib

import chess

numbers = ".PNBRQKpnbrqk"

def num(board):
	return [numbers.find(p) for p in str(board).replace("\n","").replace(" ","")]

index = 0

MAXPOOL = 30

pool = {}
best = None
queue = []

def detuple(tt):
    return [list(t) for t in tt]

def entuple(ll):
    return tuple(tuple(l) for l in ll)

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
            return code_to_state(mutate(splice(detuple(choice(list(pool.keys()))), detuple(choice(list(pool.keys()))))))
        else:
            return generate_random()


while True:

    p1 = get_player()
    p2 = get_player()

    board = chess.Board()



    #out = []

    while not board.is_game_over():
        #print(board)
        legal = sorted([x.uci() for x in list(board.generate_legal_moves())])
        mem = [len(legal)] + num(board)
        active = p1 if board.turn == chess.WHITE else p2

        active[F_MEM] = mem

        has_output = False


        def output(value):
            #XXX use uci coordinates instead of index into legal?
            global has_output, pool
            #print("OUTPUT", value)
            #out.append(value)
            board.push(chess.Move.from_uci(legal[value%len(legal)]))
            has_output = True

        startgas = active[F_GAS]

        execute(output, active)

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

    if draw:
        pass
    else:
        """
        winner[F_IP] = 0
        winner[F_GAS] = STARTGAS
        #if random() > len(queue)/30:
        queue.append(winner)
        if random() > len(queue)/30:
            queue.append(mutate(winner))
        if has_output:
            if random() > len(queue)/30:
                queue.append(mutate(loser))
        """

    gasdelta = winner[F_GAS] - STARTGAS

    winnercode = entuple(winner[F_CODE])
    losercode = entuple(loser[F_CODE])

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