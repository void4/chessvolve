## Evolving chess programs

A few times I created simulations which evolved small programs towards something, say, generate the most distinct colors with the least amount of resources.

This video: https://www.youtube.com/watch?v=DpXy041BIlA inspired me to create a small simulation where code to be evolved through genetic programming (selection, mutation, combination) runs on a very simple interpreter loop - at each turn/ply the code is executed with a max number of steps, it can execute a special instruction and return a number which will be used to index into a list of legal chess moves. If it doesn't return anything, it automatically loses the game and the code is discarded. https://github.com/void4/chessvolve This approach makes it more likely that the programs are valid (especially if the returned value is taken modulo the legal move list length, since then every number is a valid index), however the way the VM is structured is not too satisfying. It seems that this way, it is too easy to evolve good, static move lists without actually considering more of the game state at the turn the code is executed.

## Old stuff

Genetic algorithm chess with limited resources

better CLI, how to do 2d with python?
