# startet Simulation - verbindet Agent und Environment

import os
import genesis as gs
from .Environment import create_scene

# --- Stabilitätsflags für Windows + CUDA ---
os.environ["TI_DEBUG"] = "0"         
os.environ["TI_ARCH"] = "cuda"        
os.environ["TI_DEVICE_MEMORY_GB"] = "3"  
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TI_DEBUG"] = "1"

# --- Genesis initialisieren ---
gs.init(backend=gs.cuda, precision="32", logging_level="info", debug=False)
print("[Genesis] ✅ Initialized with Taichi CUDA backend (Windows + NVIDIA)")

def run_simulation(steps: int = 600):
    """Run the simulation loop using the scene created by create_scene."""
    scene, camera, camera_pov = create_scene()
    for _ in range(steps):
        scene.step()
        camera.render()
        camera_pov.render()

if __name__ == "__main__":
    run_simulation()


