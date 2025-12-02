# Ai-Bop
Bebop Drone – AI-Assisted Task Execution

This repository contains an in-development framework for controlling a Parrot Bebop Drone using AI-driven autonomy. The project integrates computer vision, sensor data processing, and task-oriented decision-making to enable semi-autonomous or fully autonomous drone operations.

Note: The codebase is under active development. Interfaces, modules, and workflows may change as features mature.

This repository contains an end-to-end reinforcement learning framework designed to train and evaluate an autonomous agent that controls a Bebop drone inside a simulated environment. The system is modular, separating environment logic, agent logic, training processes, and simulation execution.

Project Structure
environment.py      # Simulation environment (state, actions, transitions)
training.py         # RL training loop, episodes, reward logic
agent.py            # Neural network policy and reinforcement learning algorithm
runSimulation.py    # Executes a simulation using a trained agent
README.md

Module Overview
1. environment.py

Defines the simulated world in which the Bebop drone operates.

Key responsibilities:

Environment initialization and scenario definition

State and observation generation

Handling agent actions and physics updates

Collision detection, boundaries, and rule enforcement

Producing step outputs: next_state, reward, done, info

This module serves as the foundation for both training and simulation.

2. training.py

Implements the reinforcement learning training loop.

Key responsibilities:

Episode management and environment resets

Reward computation based on task goals

Agent–environment interaction cycle

Logging training metrics

Updating the agent’s neural network and learning policy

Executing training.py trains the drone’s control policy using the defined environment.

3. agent.py

Contains the autonomous agent based on a reinforcement learning architecture.

Key responsibilities:

Neural network model for policy or value estimation

Action selection (deterministic or exploration-based)

Algorithm-specific training logic (loss, backprop, updates)

Replay buffers, optimizers, target networks (depending on algorithm)

Saving and loading trained models

The agent encapsulates all intelligence and decision-making logic.

4. runSimulation.py

Runs the simulation using a trained agent inside the environment.

Key responsibilities:

Initializing environment and agent

Loading trained model weights

Running step-by-step or real-time simulations

Visualizing, logging, and evaluating agent behavior

No learning occurs here; this is purely inference mode

This script allows you to test and demonstrate the trained drone behavior.

Workflow
Training Workflow

Initialize environment and agent

Run episodes defined in training.py

Agent learns from rewards and transitions

Model checkpoints are saved

Simulation Workflow

Load trained model via runSimulation.py

Agent selects actions based on learned policy

Environment executes actions and updates state

Behavior can be monitored, visualized, or analyzed

Requirements

(Adjust according to your implementation.)

Python 3.9+

NumPy, SciPy

PyTorch or TensorFlow

OpenCV

Matplotlib (optional for debugging)

Install dependencies:

pip install -r requirements.txt

Purpose of the Framework

This system enables development and evaluation of autonomous drone behaviors using reinforcement learning. The separation of modules ensures clean architecture, flexibility for extending tasks, and the ability to swap environments, agents, or RL algorithms without rewriting the entire system.
