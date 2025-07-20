import tkinter as tk
from PIL import Image, ImageTk
import cv2
from concurrent.futures import ThreadPoolExecutor

from gui_settings_window import SettingsWindow
from config_utils import load_config, save_config
from gui_util_camera import detect_cameras


class WALDOApp(tk.Tk):
    """Main W.A.L.D.O. GUI window."""
    def __init__(self, router, camera_count=None):
        super().__init__()
        self.router = router
        self.title("W.A.L.D.O. - Vision AI Interface")
        self.geometry("1480x900")
        self.configure(bg="#1e1e1e")

        # Executor keeps UI responsive while AI / networking runs
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Config -----------------------------------------------------------------
        self.config = load_config()

        # Camera discovery -------------------------------------------------------
        self.camera_indices = detect_cameras()
        self.camera_count = len(self.camera_indices)
        self.latest_frames = {}

        # Sidebar ----------------------------------------------------------------
        self.sidebar = tk.Frame(self, width=200, bg="#2e2e2e")
        self.sidebar.pack(side="left", fill="y")
        tk.Label(self.sidebar, text="W.A.L.D.O.", fg="#ffffff", bg="#2e2e2e",
                 font=("Consolas", 18, "bold")).pack(pady=20)
        tk.Button(self.sidebar, text="⚙️ Settings", bg="#444", fg="white",
                  command=self.open_settings, relief="flat").pack(pady=10, fill="x", padx=10)

        # Main area --------------------------------------------------------------
        self.main_area = tk.Frame(self, bg="#1e1e1e")
        self.main_area.pack(side="right", expand=True, fill="both")

        self.status_box = tk.Text(self.main_area, height=8, bg="#121212", fg="white",
                                  font=("Consolas", 11))
        self.status_box.pack(fill="x", padx=20, pady=(20, 10))
        self.status_box.insert("end", "Welcome to W.A.L.D.O. Interface\n")

        self.input_field = tk.Entry(self.main_area, bg="#2e2e2e", fg="white",
                                    insertbackground="white", font=("Consolas", 11))
        self.input_field.pack(fill="x", padx=20, pady=(0, 10))
        self.input_field.bind("<Return>", self.send_prompt)

        # Camera grid ------------------------------------------------------------
        self.camera_grid_frame = tk.Frame(self.main_area, bg="#181818")
        self.camera_grid_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.camera_labels, self.camera_caps = [], []
        self.setup_camera_grid()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------------------------------------------------- #
    def setup_camera_grid(self):
        for lbl in self.camera_labels:
            lbl.destroy()
        self.camera_labels.clear()
        for cap in self.camera_caps:
            if cap:
                cap.release()
        self.camera_caps.clear()

        cols = min(2, self.camera_count) or 1
        for idx, cam_idx in enumerate(self.camera_indices):
            frame = tk.Frame(self.camera_grid_frame, bg="#252525", bd=2, relief="groove")
            frame.grid(row=idx // cols, column=idx % cols, padx=12, pady=12, sticky="nsew")

            cam_name = self.config.get(f"camera_name_{cam_idx}", f"Camera {cam_idx+1}")
            tk.Label(frame, text=cam_name, bg="#181818", fg="cyan",
                     font=("Consolas", 15, "bold")).pack(fill="x", pady=(4,0))

            cam_label = tk.Label(frame, bg="black")
            cam_label.pack(padx=2, pady=2)
            self.camera_labels.append(cam_label)

            cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_caps.append(cap)

        self.update_camera_feeds()

    # ---------------------------------------------------------------------- #
    def update_camera_feeds(self):
        min_delay_ms = 1000  # will be lowered per camera FPS
        for idx, cap in enumerate(self.camera_caps):
            ret, frame = cap.read()
            if ret:
                # Resize for preview
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb).resize((480, 320))
                imgtk = ImageTk.PhotoImage(image=img)
                lbl = self.camera_labels[idx]
                lbl.imgtk = imgtk
                lbl.configure(image=imgtk)

                cam_idx = self.camera_indices[idx]
                self.latest_frames[cam_idx] = frame.copy()

                fps = int(self.config.get(f"fps_{cam_idx}", 30))
                delay = max(1, int(1000 / fps))
                min_delay_ms = min(min_delay_ms, delay)

        self.after(min_delay_ms, self.update_camera_feeds)

    # ---------------------------------------------------------------------- #
    def open_settings(self):
        SettingsWindow(self, self.camera_indices, self.config, self.on_settings_saved)

    def on_settings_saved(self):
        save_config(self.config)
        if self.router:
            self.router.config_data = self.config
        self.setup_camera_grid()
        self._status("[System] Settings applied live.")

    # ---------------------------------------------------------------------- #
    def send_prompt(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        self._status(f"> {user_input}")
        self.input_field.delete(0, "end")

        # Offload heavy processing
        def _work():
            try:
                response = self.router.process_prompt(user_input) if self.router else "[No router]"
            except Exception as e:
                response = f"[Error]: {e}"
            self.after(0, lambda: self._status(response))

        self.executor.submit(_work)

    # ---------------------------------------------------------------------- #
    def _status(self, text: str):
        self.status_box.insert("end", f"{text}\n")
        self.status_box.see("end")

    # ---------------------------------------------------------------------- #
    def on_close(self):
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass
        for cap in self.camera_caps:
            if cap:
                cap.release()
        self.destroy()