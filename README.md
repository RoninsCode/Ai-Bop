# Ai-Bop  
Bebop-Style Quadcopter – High-Level Flight Controller (Genesis Simulation)

<img src="https://img.shields.io/badge/Status-Fully Working!-brightgreen" /> <img src="https://img.shields.io/badge/Genesis-0.3.4–0.3.6-blue" /> <img src="https://img.shields.io/badge/Control-Parrot Bebop Style-success" />

@misc{Genesis,
  author = {Genesis Authors},
  title = {Genesis: A Generative and Universal Physics Engine for Robotics and Beyond},
  month = {December},
  year = {2024},
  url = {https://github.com/Genesis-Embodied-AI/Genesis}
}


**A fully functional, PID-based, high-level flight controller that flies exactly like a real Parrot Bebop ** – with automatic hover, level-hold, yaw-rate control and vertical-velocity control – running in the Genesis simulator (CUDA).

This is the rock-solid foundation for the future **Ai-Bop** project: training autonomous policies (RL, IL, etc.) on a perfectly stable, Bebop-identical simulated drone.

**It works today. It flies beautifully. You can start training tomorrow.**

---

### Features (100 % working right now)

- True Parrot Bebop control scheme (no direct motor RPMs)  
- Full PID stack: Roll | Pitch | Yaw-Rate | Vertical Velocity  
- Automatic hover & perfect level-hold when no input  
- Smooth, realistic response (tuned for cf2x.urdf)  
- Keyboard control with WASD + Arrow keys (or any custom mapping)  
- Real-time debug output (attitude, targets, RPMs)  
- Tested and stable on Windows + CUDA + Genesis 0.3.4 – 0.3.6  

---

### Current Controls (WASD + Arrows)

| Key        | Action                     |
|------------|----------------------------|
| ↑          | Pitch forward              |
| ↓          | Pitch backward             |
| ←          | Roll left                  |
| →          | Roll right                 |
| **W**      | Climb (vertical velocity +)|
| **S**      | Descend (vertical velocity –)|
| **A**      | Yaw left                   |
| **D**      | Yaw right                  |
| **ESC**    | Quit simulation            |

*Releasing any key instantly returns that axis to neutral → PID holds level/hover automatically.*

---

### Why This Is the Perfect Starting Point for Ai-Bop

- Physics, mass, inertia, and motor mixing match the real Bebop as closely as possible in Genesis  
- High-level action space (roll, pitch, yaw_rate, vz) → identical to real Bebop firmware and most RL papers  
- Extremely stable baseline → ideal for RL training (no random crashes from bad low-level control)  
- Clean, modular code → easy to plug in your policy network later  

When you replace the keyboard controller with a neural network, the drone will behave exactly the same – because the low-level PID stack stays unchanged.

---

### Tested & Working Configuration (Genesis ≤ 0.3.6)


# Critical settings for old Genesis versions
self.hover_rpm = 22800.0
rpm = np.clip(rpm, 18000, 26000)
self.drone.set_propellels_rpm(rpm.tolist())   # yes, intentional typo in Genesis!

Uses direct Euler angles from get_dofs_position()[3:6] (no quaternion conversion needed)
CUDA tensors → .cpu().numpy() conversion
Correct indentation & threading model (no more frozen viewer)


Requirements

pip install pynput numpy scipy

# Genesis 0.3.4 – 0.3.6 (older versions with DOF API)
# Python 3.10 recommended

Future Roadmap (Ai-Bop)

Replace keyboard controller with trained policy (PPO, SAC, etc.)
Add FPV camera + image observations
Observation vector: attitude, velocities, height, optical flow
Reward shaping for patrol, landing, obstacle avoidance
Sim-to-real transfer experiments on the real Bebop
Integration with Benji project


Author & Support
Created by Envolate – with massive persistence and a very patient AI co-pilot.

If you like this project and want to see it become a full autonomous Bebop AI, give a shout on
X.com/envolate

Every star, follow, and retweet helps keep the dream alive.


Ai-Bop – the journey just began.
