import os
import time
import threading
import genesis as gs
from pynput import keyboard
import numpy as np

print("Starting Bebop-Style Drone Simulation...")

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
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
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

        self.target_roll = 0.0
        self.target_pitch = 0.0
        self.target_yaw_rate = 0.0
        self.target_vertical_velocity = 0.0

        self.pid_roll  = PID(3.2, 0.08, 1.0, output_limit=15.0)
        self.pid_pitch = PID(3.2, 0.08, 1.0, output_limit=15.0)
        self.pid_yaw   = PID(2.5, 0.03, 0.5, output_limit=12.0)
        self.pid_vz    = PID(1100.0, 160.0, 380.0, output_limit=6500.0)

        self.hover_rpm = 14800.0
        self.rpm_scale = 900.0

    def update(self, dt):
        if dt <= 0:
            return

        # ========== FIX FÜR CUDA/TORCH TENSORS ==========
        pos_tensor = self.drone.get_dofs_position()
        vel_tensor = self.drone.get_dofs_velocity()

        pos = pos_tensor.cpu().numpy()
        vel = vel_tensor.cpu().numpy()

        position = pos[:3]
        roll, pitch, yaw = pos[3:6]        # <-- DIREKT EULER-WINKEL! Kein Quat!

        lin_vel = vel[:3]
        ang_vel = vel[3:6]

        vz = lin_vel[2]
        yaw_rate = ang_vel[2]

        vz = lin_vel[2]
        yaw_rate = ang_vel[2]

            # PID-Regelung
        roll_error  = self.target_roll  - roll
        pitch_error = self.target_pitch - pitch
        yaw_error   = self.target_yaw_rate - yaw_rate
        vz_error    = self.target_vertical_velocity - vz

        trq_roll  = self.pid_roll.update(roll_error, dt)
        trq_pitch = self.pid_pitch.update(pitch_error, dt)
        trq_yaw   = self.pid_yaw.update(yaw_error, dt)
        thrust_offset = self.pid_vz.update(vz_error, dt)

            # Motor-Mixing
        base_rpm = self.hover_rpm + thrust_offset
        rpm = np.array([base_rpm] * 4)

        rpm[0] += -trq_pitch + trq_roll - trq_yaw   # FR
        rpm[1] += -trq_pitch - trq_roll + trq_yaw   # FL
        rpm[2] +=  trq_pitch - trq_roll - trq_yaw   # BL
        rpm[3] +=  trq_pitch + trq_roll + trq_yaw   # BR

        rpm = np.clip(rpm, 9500, 24000)

        self.drone.set_propellels_rpm(rpm.tolist())

        print(f"R:{np.degrees(roll):+6.1f}° P:{np.degrees(pitch):+6.1f}° | "
            f"Target R:{np.degrees(self.target_roll):+6.1f}° P:{np.degrees(self.target_pitch):+6.1f}° | "
            f"Vz:{vz:+5.2f} | RPM: {rpm.astype(int)}")


# DroneController bleibt exakt wie vorher – NICHT ändern!
class DroneController:
    def __init__(self, flight_controller):
        self.fc = flight_controller
        self.running = True
        self.pressed_keys = set()

        self.roll_step = np.deg2rad(9.0)
        self.pitch_step = np.deg2rad(9.0)
        self.yaw_rate_step = 1.2
        self.vz_step = 1.5

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.running = False
            return False
        self.pressed_keys.add(key)

    def on_release(self, key):
        self.pressed_keys.discard(key)

    def update_targets(self):
        # Level Hold + Auto Hover, wenn Taste losgelassen
        if keyboard.Key.up not in self.pressed_keys:
            self.fc.target_pitch = 0.0
        if keyboard.Key.down not in self.pressed_keys:
            self.fc.target_pitch = 0.0
        if keyboard.Key.left not in self.pressed_keys:
            self.fc.target_roll = 0.0
        if keyboard.Key.right not in self.pressed_keys:
            self.fc.target_roll = 0.0
        if keyboard.KeyCode(char='a') not in self.pressed_keys and keyboard.KeyCode(char='d') not in self.pressed_keys:
            self.fc.target_yaw_rate = 0.0
        if keyboard.KeyCode(char='w') not in self.pressed_keys and keyboard.KeyCode(char='s') not in self.pressed_keys:
            self.fc.target_vertical_velocity = 0.0

        # Tasten drücken → Zielwerte setzen
        if keyboard.Key.up in self.pressed_keys:
            self.fc.target_pitch = +self.pitch_step
        if keyboard.Key.down in self.pressed_keys:
            self.fc.target_pitch = -self.pitch_step
        if keyboard.Key.left in self.pressed_keys:
            self.fc.target_roll = -self.roll_step
        if keyboard.Key.right in self.pressed_keys:
            self.fc.target_roll = +self.roll_step
        if keyboard.KeyCode(char='a') in self.pressed_keys:
            self.fc.target_yaw_rate = -self.yaw_rate_step
        if keyboard.KeyCode(char='d') in self.pressed_keys:
            self.fc.target_yaw_rate = +self.yaw_rate_step
        if keyboard.KeyCode(char='w') in self.pressed_keys:
            self.fc.target_vertical_velocity = +self.vz_step
        if keyboard.KeyCode(char='s') in self.pressed_keys:
            self.fc.target_vertical_velocity = -self.vz_step


def simulation_thread_func():
    global drone
    fc = FlightController(drone)
    ctrl = DroneController(fc)

    listener = keyboard.Listener(on_press=ctrl.on_press, on_release=ctrl.on_release)
    listener.start()

    print("Keyboard-Listener gestartet – drücke eine Taste und schau in die Konsole!")

    last = time.time()
    print("\n" + "="*85)
    print("   BEBOP-STYLE CONTROLLER LÄUFT AUF DEINER GENESIS VERSION – ABHEBEN!")
    print("   ↑↓←→ Neigen | A/D Drehen | W/S Hoch/Runter | ESC Beenden")
    print("="*85 + "\n")

    while ctrl.running:
        now = time.time()
        dt = now - last
        last = now

        ctrl.update_targets()
        fc.update(dt)
        scene.step()
        time.sleep(0.0008)   # Stabil & CPU-schonend

    listener.stop()


def main():
    gs.init(backend=gs.cuda, precision="32")
    global scene, drone

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.005, gravity=(0,0,-9.81)),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(0,-3,1.5), camera_lookat=(0,0,0.5), max_FPS=60
        ),
        show_viewer=True,
    )
    scene.add_entity(gs.morphs.Plane())
    drone = scene.add_entity(gs.morphs.Drone(file="urdf/drones/cf2x.urdf", pos=(0,0,0.6)))
    scene.viewer.follow_entity(drone)
    scene.build()

    threading.Thread(target=simulation_thread_func, daemon=True).start()

    print("Viewer läuft – ESC zum Beenden")
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
