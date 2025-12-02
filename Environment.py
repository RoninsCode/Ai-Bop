#Umgebungsdaten - Drohne und Umgebung

#Umgebungsdaten - Drohne und Umgebung
import os
import genesis as gs

def create_scene():
    """Create and return a fully configured Genesis scene.

    Returns
    -------
    tuple
        (scene, camera, camera_pov)
    """
    # --- Szene ---
    scene = gs.Scene(
        rigid_options=gs.options.RigidOptions(enable_collision=True, gravity=(0, 0, -9.8)),
        viewer_options=gs.options.ViewerOptions(
            res=(960, 540),
            camera_pos=(0.6, 0.0, 0.6),
            camera_lookat=(0.0, 0.0, 0.5),
            camera_fov=55,
        ),
        renderer=gs.renderers.Rasterizer(),
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

    # Build and reset the scene before returning
    scene.build()
    scene.reset()

    return scene, camera, camera_pov

if __name__ == "__main__":
    # Optional demo: run the scene directly
    gs.init(backend=gs.cuda, precision="32", logging_level="info", debug=False)
    print("[Genesis] ✅ Initialized with Taichi CUDA backend (Windows + NVIDIA)")
    scene, cam, cam_pov = create_scene()
    for _ in range(600):
        scene.step()
        cam.render()
        cam_pov.render()
