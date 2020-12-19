from random import randint, choice
from collections import Counter
from copy import deepcopy

# Instruction numbers
NUMINSTR = 16
I_PUSH, I_ADD, I_MOVE, I_JUMP, I_SUB, I_MUL, I_IP, I_GAMEREAD, I_MEMREAD, I_MEMWRITE, I_LSHIFT, I_RSHIFT, I_AND, I_OR, I_NOT, I_MOD = range(NUMINSTR)#I_RANDOM,

WORDSIZE = 16
CELL_SIZE = 2**WORDSIZE
CELL_MAX = CELL_SIZE-1
CELL_MIN = 0

# indexes of the state components
NUMFIELDS = 5
F_GAS, F_IP, F_CODE, F_MEM, F_GAMEMEM = range(NUMFIELDS)

SC = 10

STARTGAS = 512*SC
CODEGEN = 256*SC
MEMSIZE = STARTGAS//10

def execute(output, state):

	# Runtime stack for data manipulation
	stack = []

	start_steps = state[F_GAS]
	OUTPUT = False

	stats = Counter()

	while True:

		if OUTPUT:
			break

		# Assuming no refills
		steps_done = start_steps - state[F_GAS]

		steps = state[F_GAS]
		ip = state[F_IP]
		code = state[F_CODE]

		# We are out of steps, stop the process
		if steps <= 0:
			break

		# No instructions are left, stop the process
		if ip >= len(code) or ip < 0:
			break

		if len(code[ip]) == 2:
			# Some instructions have an argument, unpack that as well
			instruction, argument = code[ip]
		else:
			instruction = code[ip][0]
			argument = None

		stats[instruction] += 1

		if instruction == I_PUSH:
			# Push the argument to the top of the stack
			stack.append(argument)
		elif instruction == I_ADD:
			# Pop the two topmost elements from the stack, add them and push the result back on the stack
			if len(stack) >= 2:
				stack.append((stack.pop(-1) + stack.pop(-1))&CELL_MAX)
		elif instruction == I_SUB:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append((stack.pop(-1) - stack.pop(-1))&CELL_MAX)
		elif instruction == I_MUL:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append((stack.pop(-1) * stack.pop(-1))&CELL_MAX)
		elif instruction == I_MOD:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				mod = stack.pop(-1)
				if mod > 0:
					stack.append(stack.pop(-1) % mod)
		elif instruction == I_AND:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append(stack.pop(-1) & stack.pop(-1))
		elif instruction == I_OR:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append(stack.pop(-1) | stack.pop(-1))
		elif instruction == I_NOT:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 1:
				stack.append((~stack.pop(-1))&CELL_MAX)
		elif instruction == I_LSHIFT:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				shift = stack.pop(-1)
				if 0 < shift <= WORDSIZE:
					stack.append((stack.pop(-1) << shift)&CELL_MAX)
		elif instruction == I_RSHIFT:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				shift = stack.pop(-1)
				if shift > 0:
					stack.append(stack.pop(-1) >> shift)
		elif instruction == I_GAMEREAD:
			if len(stack) >= 1:
				stack.append(state[F_GAMEMEM][stack.pop(-1)%len(state[F_GAMEMEM])])
		elif instruction == I_MEMWRITE:
			if len(stack) >= 2:
				state[F_MEM][stack.pop(-1)%len(state[F_MEM])] = stack.pop(-1)
		elif instruction == I_MEMREAD:
			if len(stack) >= 1:
				stack.append(state[F_MEM][stack.pop(-1)%len(state[F_MEM])])
		#TODO allow allocating memory? fixed size? read only area for input state?
		elif instruction == I_MOVE:
			# Pop the topmost element from the stack and print it
			#print("OUTPUT:", stack.pop(-1))
			if len(stack) >= 1:
				output(stack.pop(-1))
				OUTPUT = True
		elif instruction == I_JUMP:
			if len(stack) >= 1:
				state[F_IP] = stack.pop(-1)
		elif instruction == I_IP:
			stack.append(ip)
		#elif instruction == I_RANDOM:
		#	stack.append(randint(0,255))
		# Move the instruction pointer one step forward to point to the next instruction
		state[F_IP] += 1

		# Reduce the number of remaining steps by one
		state[F_GAS] -= 1

		# Print a newline after each iteration
		#print("")

	return stats

def code_to_state(code):
	return [STARTGAS, 0, code, [0 for i in range(MEMSIZE)], []]

def random_instruction():
	instr = randint(0, NUMINSTR-1)
	if instr == I_PUSH:
		block = [I_PUSH, randint(0,CELL_MAX)]
	else:
		block = [instr]
	return block

def generate_random():
	code = []
	for i in range(CODEGEN):
		code.append(random_instruction())

	return code_to_state(code)

def mutate(code):
	for i in range(randint(0,len(code)-1)):
		random_index = randint(0, len(code)-1)
		code[random_index] = random_instruction()
	# Replenish, reset
	return code

def splice(code1, code2):
	code1 = deepcopy(code1)
	code2 = deepcopy(code2)
	index = randint(0, min(len(code1), len(code2))-1)
	first, second = (code1, code2) if randint(0,1) == 0 else (code2, code1)
	code = first[:index] + second[index:]
	return code
