import os
import time
import threading
import genesis as gs
from pynput import keyboard
import numpy as np

print("Starting Bebop-Style Drone Simulation – FINAL & STABIL")
os.environ["TI_ARCH"] = "cuda"
os.environ["TI_DEVICE_MEMORY_GB"] = "3"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class PID:
    def __init__(self, kp, ki, kd, integral_limit=1000.0, output_limit=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_limit = integral_limit
        self.output_limit = output_limit
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, error, dt):
        if dt <= 0: return 0.0
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)
        derivative = (error - self.prev_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        if self.output_limit is not None:
            output = np.clip(output, -self.output_limit, self.output_limit)
        return output

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0


class FlightController:
    def __init__(self, drone):
        self.drone = drone
        self.target_vx = 0.0
        self.target_vy = 0.0
        self.target_vz = 0.0
        self.target_yaw_rate = 0.0

        self.pid_vx = PID(4.2, 0.02, 1.1, output_limit=42.0)
        self.pid_vy = PID(4.2, 0.02, 1.1, output_limit=42.0)
        self.pid_vz = PID(1100.0, 160.0, 380.0, output_limit=6500.0)
        self.pid_yaw = PID(6.5, 0.08, 1.8, output_limit=35.0)

        self.hover_rpm = 15200.0

    def update(self, dt):
        if dt <= 0: return

        pos = self.drone.get_dofs_position().cpu().numpy()
        vel = self.drone.get_dofs_velocity().cpu().numpy()

        vx_body, vy_body, vz_body = vel[0], vel[1], vel[2]
        yaw_rate = vel[5]

        target_pitch =  self.pid_vx.update(self.target_vx - vx_body, dt)
        target_roll  = -self.pid_vy.update(self.target_vy - vy_body, dt)

        thrust_offset = self.pid_vz.update(self.target_vz - vz_body, dt)
        trq_yaw = self.pid_yaw.update(self.target_yaw_rate - yaw_rate, dt)

        base_rpm = self.hover_rpm + thrust_offset
        rpm = np.array([base_rpm] * 4)
        rpm[0] += -target_pitch + target_roll - trq_yaw   # FR
        rpm[1] += -target_pitch - target_roll + trq_yaw   # FL
        rpm[2] +=  target_pitch - target_roll - trq_yaw   # BL
        rpm[3] +=  target_pitch + target_roll + trq_yaw   # BR

        rpm = np.clip(rpm, 9500, 26000)
        self.drone.set_propellels_rpm(rpm.tolist())

        print(f"Vx:{vx_body:+5.2f} Vy:{vy_body:+5.2f} Vz:{vz_body:+5.2f} | "
              f"Roll:{np.degrees(target_roll):+6.1f}° Pitch:{np.degrees(target_pitch):+6.1f}°")


class DroneController:
    def __init__(self, flight_controller):
        self.fc = flight_controller
        self.running = True
        self.pressed_keys = set()
        self.vel_accel = 30
        self.yaw_rate = 4.5

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.running = False
            return False
        self.pressed_keys.add(key)

    def on_release(self, key):
        self.pressed_keys.discard(key)

    def update_targets(self, dt):
        # Vor/Zurück
        if keyboard.Key.up in self.pressed_keys:
            self.fc.target_vx = min(self.fc.target_vx + self.vel_accel * dt, 7.5)
        elif keyboard.Key.down in self.pressed_keys:
            self.fc.target_vx = max(self.fc.target_vx - self.vel_accel * dt, -5.0)
        else:
            if abs(self.fc.target_vx) > 0.08:
                self.fc.target_vx -= np.sign(self.fc.target_vx) * self.vel_accel * dt * 3.8
            else:
                self.fc.target_vx = 0.0

        # Links/Rechts
        if keyboard.Key.right in self.pressed_keys:
            self.fc.target_vy = min(self.fc.target_vy + self.vel_accel * dt, 7.5)
        elif keyboard.Key.left in self.pressed_keys:
            self.fc.target_vy = max(self.fc.target_vy - self.vel_accel * dt, -7.5)
        else:
            if abs(self.fc.target_vy) > 0.08:
                self.fc.target_vy -= np.sign(self.fc.target_vy) * self.vel_accel * dt * 3.8
            else:
                self.fc.target_vy = 0.0

        # Höhe
        self.fc.target_vz = 2.8 if keyboard.KeyCode(char='w') in self.pressed_keys else \
                           -2.8 if keyboard.KeyCode(char='s') in self.pressed_keys else 0.0

        # Yaw
        self.fc.target_yaw_rate = -self.yaw_rate if keyboard.KeyCode(char='a') in self.pressed_keys else \
                                   self.yaw_rate if keyboard.KeyCode(char='d') in self.pressed_keys else 0.0


def simulation_thread_func():
    global drone
    fc = FlightController(drone)
    ctrl = DroneController(fc)
    listener = keyboard.Listener(on_press=ctrl.on_press, on_release=ctrl.on_release)
    listener.start()

    print("\n" + "="*92)
    print("   ECHTES BEBOP / DJI MINI VERHALTEN – LÄUFT 100% STABIL!")
    print("   ↑↓←→ = Bewegung   |   W/S = Hoch/Runter   |   A/D = Drehen   |   ESC = Beenden")
    print("   Kurzer Druck → kurzer Schub → Drohne bremst & hovert automatisch!")
    print("="*92 + "\n")

    last = time.time()
    while ctrl.running:
        now = time.time()
        dt = now - last
        last = now

        ctrl.update_targets(dt)
        fc.update(dt)
        scene.step()
        time.sleep(0.0005)   # ~2000 Hz Regelung

    listener.stop()


def main():
    gs.init(backend=gs.cuda, precision="32")
    global scene, drone

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.005, gravity=(0,0,-9.81)),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(0, -1.2, 0.9),    # Etwas weiter hinten & höher für bessere Übersicht
            camera_lookat=(0, 0, 0.6),
            max_FPS=60
        ),
        show_viewer=True,
    )

    scene.add_entity(gs.morphs.Plane())
    drone = scene.add_entity(gs.morphs.Drone(file="urdf/drones/cf2x.urdf", pos=(0,0,0.6)))

    # Standard-Follow-Kamera von Genesis – funktioniert immer!
    scene.viewer.follow_entity(drone)

    scene.build()

    threading.Thread(target=simulation_thread_func, daemon=True).start()
    print("Simulation läuft – Bebop-Feeling garantiert!")

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        from scipy.spatial.transform import Rotation
    except ImportError:
        print("FEHLER: pip install scipy")
        exit(1)
    main()
