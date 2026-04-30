 Astar Pathfinder

A* pathfinding on a 10×10 grid with a Manhattan distance heuristic. Interactive tkinter visualization where you click to place start and end points, then watch the algorithm find the shortest path around obstacles.

## How It Works

A* is an informed search algorithm that finds the shortest path between two nodes by combining:

- **g(n)** — the actual cost from the start to node `n`
- **h(n)** — a heuristic estimate of the cost from `n` to the goal

At each step, A* expands the node with the lowest **f(n) = g(n) + h(n)**. With an admissible heuristic (one that never overestimates), A* is guaranteed to find the shortest path.

This implementation uses **Manhattan distance** as the heuristic, which is admissible for 4-directional grid movement:
The open list is a min-heap (`heapq`) keyed on f-score, giving O(log n) insertion and extraction.

## Controls

- **Left click** — place the start (green), then the end (red), then trigger pathfinding (blue)
- **Right click** — toggle obstacles (black) on or off

## Run It

```bash
python main.py
```

Requires Python 3.x. No dependencies beyond the standard library (`tkinter`, `heapq`).

## Files

- `main.py` — A* implementation and tkinter UI
- `testing.py` — algorithm tests
- `debugging.py` — debugging scratchpad

## Why I Built It

To get the algorithm in my hands. Reading about A* and implementing it are different things, and the visualization made it obvious where the heuristic helps versus where it's misled by obstacles. Next iterations would add diagonal movement (which would require a different heuristic, since Manhattan stops being admissible) and weighted terrain.****
