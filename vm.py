from random import randint, choice
from collections import Counter
from copy import deepcopy

# Instruction numbers
NUMINSTR = 16
I_PUSH, I_ADD, I_MOVE, I_JUMP, I_SUB, I_MUL, I_IP, I_GAMEREAD, I_MEMREAD, I_MEMWRITE, I_LSHIFT, I_RSHIFT, I_AND, I_OR, I_NOT, I_MOD = range(NUMINSTR)#I_RANDOM,

INSTR = "PUSH ADD MOVE JUMP SUB MUL IP GAMEREAD MEMREAD MEMWRITE LSHIFT RSHIFT AND OR NOT MOD".split()

WORDSIZE = 16
CELL_SIZE = 2**WORDSIZE
CELL_MAX = CELL_SIZE-1
CELL_MIN = 0

# indexes of the state components
NUMFIELDS = 5
F_GAS, F_IP, F_CODE, F_MEM, F_GAMEMEM = range(NUMFIELDS)

SC = 2

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

		instruction_length = 1

		instr = code[ip]

		stats[instr] += 1

		if instr == I_PUSH:
			# Push the argument to the top of the stack
			if ip + 1 < len(code):
				instruction_length = 2
				stack.append(code[ip+1])
		elif instr == I_ADD:
			# Pop the two topmost elements from the stack, add them and push the result back on the stack
			if len(stack) >= 2:
				stack.append((stack.pop(-1) + stack.pop(-1))&CELL_MAX)
		elif instr == I_SUB:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append((stack.pop(-1) - stack.pop(-1))&CELL_MAX)
		elif instr == I_MUL:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append((stack.pop(-1) * stack.pop(-1))&CELL_MAX)
		elif instr == I_MOD:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				mod = stack.pop(-1)
				if mod > 0:
					stack.append(stack.pop(-1) % mod)
		elif instr == I_AND:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append(stack.pop(-1) & stack.pop(-1))
		elif instr == I_OR:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append(stack.pop(-1) | stack.pop(-1))
		elif instr == I_NOT:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 1:
				stack.append((~stack.pop(-1))&CELL_MAX)
		elif instr == I_LSHIFT:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				shift = stack.pop(-1)
				if 0 < shift <= WORDSIZE:
					stack.append((stack.pop(-1) << shift)&CELL_MAX)
		elif instr == I_RSHIFT:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				shift = stack.pop(-1)
				if shift > 0:
					stack.append(stack.pop(-1) >> shift)
		elif instr == I_GAMEREAD:
			if len(stack) >= 1:
				stack.append(state[F_GAMEMEM][stack.pop(-1)%len(state[F_GAMEMEM])])
		elif instr == I_MEMWRITE:
			if len(stack) >= 2:
				state[F_MEM][stack.pop(-1)%len(state[F_MEM])] = stack.pop(-1)
		elif instr == I_MEMREAD:
			if len(stack) >= 1:
				stack.append(state[F_MEM][stack.pop(-1)%len(state[F_MEM])])
		#TODO allow allocating memory? fixed size? read only area for input state?
		elif instr == I_MOVE:
			# Pop the topmost element from the stack and print it
			#print("OUTPUT:", stack.pop(-1))
			if len(stack) >= 1:
				if not output(stack.pop(-1)):
					break
				OUTPUT = True
		elif instr == I_JUMP:
			if len(stack) >= 1:
				state[F_IP] = stack.pop(-1)
		elif instr == I_IP:
			stack.append(ip)
		#elif instr == I_RANDOM:
		#	stack.append(randint(0,255))
		# Move the instr pointer one step forward to point to the next instr
		state[F_IP] += instruction_length

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
		block = (I_PUSH, randint(0,CELL_MAX))
	else:
		block = (instr,)
	return block

def generate_random():
	code = []
	for i in range(CODEGEN):
		code += random_instruction()

	code = tuple(code)

	return code_to_state(code)

def mutate(code):
	for i in range(randint(0,len(code)-1)):
		random_index = randint(0, len(code)-1)
		code = code[:random_index] + random_instruction() + code[random_index+1:]
	# Replenish, reset
	return code

def splice(code1, code2):
	code1 = deepcopy(code1)
	code2 = deepcopy(code2)
	index = randint(0, min(len(code1), len(code2))-1)
	first, second = (code1, code2) if randint(0,1) == 0 else (code2, code1)
	code = first[:index] + second[index:]
	return code
