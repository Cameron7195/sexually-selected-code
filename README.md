# sexually-selected-code

This project is a pioneering attempt to blur the line between the digital and biological realms. I present an approach to optimizing computer programs using evolutionary algorithms by recombining their instructions in the same way that DNA is recombined through sexual selection. Each instruction is a subleq instruction, which is Turing complete and is repeated on each row of the DNA array. Agents possess this DNA and use it to perform simple tasks such as reading and writing integers.

The project measures the distance between the actual output and the desired output of some computational task to assign a fitness score to each agent. Males and females are then selected and paired based on their fitness scores to produce offspring that possess their parents DNA, recombined by crossing over, just like in meiosis. A low-frequency random mutation rate—higher in males—is also included to generate new agent abilities. The offspring are then used to repeat the experiment and see if the agents can evolve DNA that solves the given task.

The results of the project demonstrate the potential of evolutionary principles in optimizing computer programs and highlight the similarities between DNA and code. The agents were successfully able to learn to read and write 50 input integers to the correct 50 output locations, showcasing the deep connection between the digital and biological.