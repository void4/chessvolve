from random import randint, choice
from copy import deepcopy

# Instruction numbers
NUMINSTR = 7
I_PUSH, I_ADD, I_PRINT, I_JUMP, I_SUB, I_IP, I_MEMREAD = range(NUMINSTR)#, I_MEMWRITE#I_RANDOM,

CELL_SIZE = 256
CELL_MAX = CELL_SIZE-1
CELL_MIN = 0

# indexes of the state components
NUMFIELDS = 4
F_GAS, F_IP, F_CODE, F_MEM = range(NUMFIELDS)

SC = 10

STARTGAS = 512*SC
CODEGEN = 256*SC

def execute(output, state):

	# Runtime stack for data manipulation
	stack = []

	start_steps = state[F_GAS]
	OUTPUT = False

	while True:

		if OUTPUT:
			break

		# Assuming no refills
		steps_done = start_steps - state[F_GAS]

		# pseudo-gravity
		"""
		if steps_done % 20 == 0:
			if state[F_Y] < H-1:
				state[F_Y] = (state[F_Y]+1)%H
		"""

		# Uncomment this to see the program state and stack each step
		#print("STATE:", state)
		#print("STACK:", stack)

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


		if instruction == I_PUSH:
			# Push the argument to the top of the stack
			stack.append(argument)
		elif instruction == I_ADD:
			# Pop the two topmost elements from the stack, add them and push the result back on the stack
			if len(stack) >= 2:
				stack.append(stack.pop(-1) + stack.pop(-1))
		elif instruction == I_SUB:
			# Pop the two topmost elements from the stack, subtract them and push the result back on the stack
			if len(stack) >= 2:
				stack.append(stack.pop(-1) - stack.pop(-1))
		elif instruction == I_MEMREAD:
			if len(stack) >= 1:
				stack.append(state[F_MEM][stack.pop(-1)%len(state[F_MEM])])
		#elif instruction == I_MEMWRITE:
		#	if len(stack) >= 2:
		#		state[F_MEM][stack.pop(-1)%len(state[F_MEM])] = stack.pop(-1)
		#TODO allow allocating memory? fixed size? read only area for input state?
		elif instruction == I_PRINT:
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

def code_to_state(code):
	return [STARTGAS, 0, code, []]

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
	for i in range(len(code)//10):
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

if __name__ == "__main__":
	# full runtime state of a process
	# number of remaining steps, instruction pointer, instruction list
	state_example = [100, 0, 0, 0, 0, [[I_PUSH, 1], [I_PUSH, 2], [I_ADD], [I_PRINT], [I_JUMP]]]

	execute(state_example)
