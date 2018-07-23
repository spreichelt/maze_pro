# Maze Pro
A game experience designed for use in teaching programming concepts from basic programming to training AI's, an advanced path finding algorithms.

### Current State of the Project:
The project is in an early stage where the basic building blocks are still under construction. 

#### Demo
A rudimentary demo is available on the DEMO branch that displays a randomly constructed maze, then shows a simple agent (near-aimlessly) traversing the maze.
In order to use the demo:

1. Clone repository
2. Navigate to the top level directory of the repository
3. Run the test script, maze_pro.py:

    ```python maze_pro.py```    

Use the provided requirements.txt to ensure all dependencies are captured

#### Independent usage
The master branch contains the most recent working version of the project. The **maze.py** and **maze_player.py** classes contain the basic functionality of the project. A **maze_player.Player()** can interact with a **maze.Maze()** through the **maze.PlayerInterface()**.

### TODO
- Refactor **maze_player.Player()** to allow for a parameterized step function. The step function should implement everything required to return the next tile an agent will move to when queried, using only the information available through the maze.PlayerInterface().

- Create step() functions that implement more intelligent traversals, including interaction with maze resources (mining / returning to home)

- Implement a resource collection point where the player can deposit collected resources

- Improve the demo animation color scheme using a custom color map.

- Create a demo that uses Jupyter Notebooks, specifically make google colab use seamless