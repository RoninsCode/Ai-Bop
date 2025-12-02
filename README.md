# Ai-Bop

Bebop Drone – AI-Assisted Task Execution

This repository provides a modular and extensible framework for controlling a Parrot Bebop Drone using AI-driven autonomy. It combines reinforcement learning, computer vision, and simulation-based training to enable semi-autonomous or fully autonomous drone behavior.

Note: The codebase is currently under active development. Interfaces, modules, and workflows may change as the system evolves.

Overview

The framework implements an end-to-end reinforcement learning system for training and evaluating an autonomous agent that controls a Bebop drone inside a simulated environment.
It follows a clean architectural separation between:

Environment (state, actions, physics, transitions)

Agent (neural network, learning algorithm)

Training loop (episodes, reward, learning updates)

Simulation runtime (execution of trained policies)

This modularity ensures clarity, maintainability, and easy extension for new tasks or algorithms.

Project Structure
environment.py      # Simulation environment (state, actions, transitions)
training.py         # RL training loop, episodes, reward logic
agent.py            # Neural network policy and reinforcement learning algorithm
runSimulation.py    # Executes the simulation using a trained agent
README.md           # Project documentation

Module Overview
1. environment.py

Defines the complete simulation environment in which the Bebop drone operates.

Responsibilities:

Initialize the environment and scenario parameters

Generate observations (state representation) for the agent

Translate agent actions into drone state updates

Simulate physics, constraints, collisions, and boundaries

Return next_state, reward, done, and info at every step

This module forms the foundation for all learning and evaluation processes.

2. training.py

Implements the reinforcement learning loop that teaches the agent how to act autonomously.

Responsibilities:

Manage episodes and environment resets

Compute task-specific rewards

Execute the agent–environment interaction cycle

Log performance metrics and learning progress

Update the agent’s neural network and optimization steps

Running training.py trains the drone’s control policy using the defined environment.

3. agent.py

Encapsulates the reinforcement learning agent, including the underlying neural networks and algorithmic logic.

Responsibilities:

Define the neural network architecture for the policy or value function

Select actions (deterministic or using exploration strategies)

Perform algorithm-specific learning operations (loss computation, backpropagation)

Manage replay buffers, optimizers, and target networks (if required)

Save and load trained models

The agent implements all autonomous decision-making behavior.

4. runSimulation.py

Executes a simulation using a trained model to validate or demonstrate learned behavior.

Responsibilities:

Initialize both environment and trained agent

Load saved model checkpoints

Run real-time or step-wise simulations

Visualize and log agent performance and drone behavior

Operate strictly in inference mode (no learning happens here)

This script is ideal for evaluation and demonstration purposes.

Workflow
Training Workflow

Initialize the environment and agent

Run episodes defined in training.py

The agent interacts with the environment and learns from rewards

Model checkpoints are saved for later simulation or fine-tuning

Simulation Workflow

Load a trained policy via runSimulation.py

The agent selects actions using the learned policy

The environment updates its state based on these actions

Behavior is visualized or otherwise analyzed

Requirements

Adjust as needed based on your implementation.

Python 3.9+

NumPy, SciPy

PyTorch or TensorFlow

OpenCV

Matplotlib (optional, for debugging or visualization)

Install all dependencies using:

pip install -r requirements.txt

Purpose of the Framework

This system enables the development, training, and validation of autonomous drone behaviors through reinforcement learning.
By separating environment, agent, training logic, and simulation runtime, the framework provides:

Clear architecture

High maintainability

Simplified experimentation

Easy integration of new tasks or RL algorithms

It is well suited for research, prototyping, and future deployment on a real Bebop drone.
