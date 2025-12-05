import os
import genesis as gs

print("Starting Simulation...")
# --- Stabilitätsflags für Windows + CUDA --- 

os.environ["TI_DEBUG"] = "0"          # kein Debug-Modus, sonst langsam
os.environ["TI_ARCH"] = "cuda"        # erzwingt CUDA statt CPU/OpenGL
os.environ["TI_DEVICE_MEMORY_GB"] = "3"  # Taichi darf max. 3 GB GPU-RAM nutzen
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TI_DEBUG"] = "1"


# --- Genesis initialisieren ---
gs.init(backend=gs.cuda, precision="32", logging_level="info", debug=False)
print("[Genesis] ✅ Initialized with Taichi CUDA backend (Windows + NVIDIA)")

# --- Szene ---
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(enable_collision=True, gravity=(0, 0, -9.8)),
    viewer_options=gs.options.ViewerOptions(
        res=(960, 540),
        camera_pos=(0.6, 0.0, 0.6),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=55,
    ),
    renderer=gs.renderers.Rasterizer(),  # OpenGL-basiertes Rendering
)

# --- Objekte ---
scene.add_entity(
    morph=gs.morphs.Plane(pos=(0, 0, -0.5)),
    surface=gs.surfaces.Rough(color=(0.8, 0.8, 0.8)),
)
scene.add_entity(
    morph=gs.morphs.URDF(file="urdf/drones/cf2x.urdf", pos=(0, 0, 0.5), fixed=True),
)

# --- Kamera ---
camera = scene.add_camera(
    res=(960, 540),
    pos=(0.6, 0.0, 0.6),
    lookat=(0.0, 0.0, 0.5),
    fov=55,
    GUI=True,
    spp=16,
)

# --- POV Kamera ---
camera_pov = scene.add_camera(
    res=(480, 270),
    pos=(0.1, 0.0, 0.55),
    lookat=(1.0, 0.0, 0.55),
    fov=70,
    GUI=True,
    spp=16,
)

# --- Simulation ---
scene.build()
scene.reset()

for i in range(600):
    scene.step()
    camera.render()
    camera_pov.render()
