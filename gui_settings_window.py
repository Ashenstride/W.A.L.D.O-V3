import tkinter as tk
from tkinter import ttk
from config_utils import save_config

class SettingsWindow(tk.Toplevel):
    def __init__(self, master, camera_indices, config, live_update_callback):
        super().__init__(master)
        self.title("Settings")
        self.geometry("1000x700")
        self.configure(bg="#1e1e1e")
        self.config = config
        self.camera_indices = camera_indices
        self.live_update_callback = live_update_callback
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        self.tab_styles = ttk.Style()
        self.tab_styles.theme_use('default')
        self.tab_styles.configure('TNotebook.Tab', background="#2e2e2e", foreground="white")
        self.tab_styles.map("TNotebook.Tab", background=[("selected", "#444")])
        self.widget_refs = {}

        # Camera tabs
        for cam_idx in self.camera_indices:
            tab = tk.Frame(self.tab_control, bg="#1e1e1e")
            self.tab_control.add(tab, text=f"Camera {cam_idx+1}")
            self.create_camera_settings(tab, cam_idx)

        # Interface AI tab
        interface_tab = tk.Frame(self.tab_control, bg="#1e1e1e")
        self.tab_control.add(interface_tab, text="Interface AI")
        self.create_interface_ai_settings(interface_tab)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_camera_settings(self, tab, cam_idx):
        canvas = tk.Canvas(tab, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        row = 0

        def add_labeled_entry(label, key, show=None):
            nonlocal row
            tk.Label(scrollable_frame, text=label, fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(scrollable_frame, width=60, show=show)
            entry.grid(row=row, column=1, padx=10, pady=5)
            value = self.config.get(key, "")
            entry.insert(0, value)
            self.widget_refs[key] = entry
            row += 1

        add_labeled_entry("API Endpoint", f"llava_endpoint_{cam_idx}")
        add_labeled_entry("Camera Name", f"camera_name_{cam_idx}")
        add_labeled_entry("AI Model", f"model_{cam_idx}")
        add_labeled_entry("Personality", f"personality_{cam_idx}")
        add_labeled_entry("API Key", f"apikey_{cam_idx}", show="*")
        tk.Button(scrollable_frame, text="Apply API Key", command=lambda: self.widget_refs[f"apikey_{cam_idx}"].config(show="*")).grid(row=row-1, column=2, padx=5, pady=5)

        tk.Label(scrollable_frame, text="FPS", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        fps_spin = tk.Spinbox(scrollable_frame, from_=1, to=60, width=10)
        fps_val = self.config.get(f"fps_{cam_idx}", "10")
        fps_spin.delete(0, "end")
        fps_spin.insert(0, fps_val)
        fps_spin.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs[f"fps_{cam_idx}"] = fps_spin
        row += 1

        autoprompt_var = tk.BooleanVar()
        autoprompt_var.set(bool(self.config.get(f"autoprompt_{cam_idx}", False)))
        toggle = tk.Checkbutton(scrollable_frame, text="Auto-Prompt Enabled", variable=autoprompt_var, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e")
        toggle.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.widget_refs[f"autoprompt_{cam_idx}"] = autoprompt_var
        row += 1

        tk.Label(scrollable_frame, text="Auto-Prompt Interval (s)", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        interval_spin = tk.Spinbox(scrollable_frame, from_=1, to=300, width=10)
        interval_val = self.config.get(f"autointerval_{cam_idx}", "10")
        interval_spin.delete(0, "end")
        interval_spin.insert(0, interval_val)
        interval_spin.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs[f"autointerval_{cam_idx}"] = interval_spin
        row += 1

        tk.Label(scrollable_frame, text="Roles & Responsibilities", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="nw", padx=10, pady=5)
        roles_text = tk.Text(scrollable_frame, width=60, height=4, wrap="word")
        roles_val = self.config.get(f"roles_{cam_idx}", "")
        roles_text.insert("1.0", roles_val)
        roles_text.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs[f"roles_{cam_idx}"] = roles_text
        row += 1

        tk.Label(scrollable_frame, text="Bounding Box Labels (comma separated)", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="nw", padx=10, pady=5)
        bbox_entry = tk.Entry(scrollable_frame, width=60)
        bbox_val = self.config.get(f"bbox_labels_{cam_idx}", "")
        bbox_entry.insert(0, bbox_val)
        bbox_entry.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs[f"bbox_labels_{cam_idx}"] = bbox_entry
        row += 1

        tk.Label(scrollable_frame, text="Min Box Confidence (0.0 - 1.0)", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        conf_spin = tk.Spinbox(scrollable_frame, from_=0.0, to=1.0, increment=0.05, width=10)
        conf_val = self.config.get(f"bbox_conf_{cam_idx}", "0.5")
        conf_spin.delete(0, "end")
        conf_spin.insert(0, conf_val)
        conf_spin.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs[f"bbox_conf_{cam_idx}"] = conf_spin
        row += 1

        tk.Label(scrollable_frame, text="Target Behavior (e.g. follow, ignore)", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        behavior_entry = tk.Entry(scrollable_frame, width=60)
        behavior_val = self.config.get(f"bbox_behavior_{cam_idx}", "")
        behavior_entry.insert(0, behavior_val)
        behavior_entry.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs[f"bbox_behavior_{cam_idx}"] = behavior_entry
        row += 1

        save_btn = tk.Button(scrollable_frame, text="Save Settings", bg="#333", fg="white",
                             command=lambda cam_idx=cam_idx: self.save_camera_settings(cam_idx))
        save_btn.grid(row=row, column=0, columnspan=2, pady=15)

    def create_interface_ai_settings(self, tab):
        canvas = tk.Canvas(tab, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        row = 0

        def add_labeled_entry(label, key, show=None):
            nonlocal row
            tk.Label(scrollable_frame, text=label, fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(scrollable_frame, width=60, show=show)
            entry.grid(row=row, column=1, padx=10, pady=5)
            value = self.config.get(key, "")
            entry.insert(0, value)
            self.widget_refs[key] = entry
            row += 1

        add_labeled_entry("Interface Model", "interface_model")
        add_labeled_entry("Personality", "interface_personality")
        add_labeled_entry("API Key", "interface_apikey", show="*")
        tk.Button(scrollable_frame, text="Apply API Key", command=lambda: self.widget_refs["interface_apikey"].config(show="*")).grid(row=row-1, column=2, padx=5, pady=5)
        tk.Label(scrollable_frame, text="Roles & Responsibilities", fg="white", bg="#1e1e1e").grid(row=row, column=0, sticky="nw", padx=10, pady=5)
        roles_text = tk.Text(scrollable_frame, width=60, height=4, wrap="word")
        roles_val = self.config.get("interface_roles", "")
        roles_text.insert("1.0", roles_val)
        roles_text.grid(row=row, column=1, padx=10, pady=5)
        self.widget_refs["interface_roles"] = roles_text
        row += 1

        verbose_var = tk.BooleanVar()
        verbose_var.set(bool(self.config.get("interface_verbose", False)))
        verbose_toggle = tk.Checkbutton(scrollable_frame, text="Verbose Mode (Show all camera AI responses)",
                                       variable=verbose_var, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e")
        verbose_toggle.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.widget_refs["interface_verbose"] = verbose_var
        row += 1

        save_btn = tk.Button(scrollable_frame, text="Save Settings", bg="#333", fg="white",
                             command=self.save_interface_settings)
        save_btn.grid(row=row, column=0, columnspan=2, pady=15)

    def save_camera_settings(self, cam_idx):
        for key in [f"llava_endpoint_{cam_idx}", f"camera_name_{cam_idx}", f"model_{cam_idx}", f"personality_{cam_idx}", f"apikey_{cam_idx}", f"fps_{cam_idx}",
                    f"autoprompt_{cam_idx}", f"autointerval_{cam_idx}", f"roles_{cam_idx}", f"bbox_labels_{cam_idx}",
                    f"bbox_conf_{cam_idx}", f"bbox_behavior_{cam_idx}"]:
            widget = self.widget_refs[key]
            if isinstance(widget, tk.Entry) or isinstance(widget, tk.Spinbox):
                self.config[key] = widget.get()
            elif isinstance(widget, tk.BooleanVar):
                self.config[key] = widget.get()
            elif isinstance(widget, tk.Text):
                self.config[key] = widget.get("1.0", "end-1c")
        save_config(self.config)
        self.live_update_callback()
        self.show_toast(f"Camera {cam_idx+1} settings saved")

    def save_interface_settings(self):
        for key in ["interface_model", "interface_personality", "interface_apikey", "interface_roles", "interface_verbose"]:
            widget = self.widget_refs[key]
            if isinstance(widget, tk.Entry):
                self.config[key] = widget.get()
            elif isinstance(widget, tk.BooleanVar):
                self.config[key] = widget.get()
            elif isinstance(widget, tk.Text):
                self.config[key] = widget.get("1.0", "end-1c")
        save_config(self.config)
        self.live_update_callback()
        self.show_toast("Interface AI settings saved")

    def show_toast(self, message="Settings Saved"):
        toast = tk.Toplevel(self)
        toast.configure(bg="black")
        toast.geometry("220x50+{}+{}".format(self.winfo_x() + 400, self.winfo_y() + 300))
        tk.Label(toast, text=message, fg="white", bg="black", font=("Consolas", 12)).pack(expand=True)
        toast.after(1200, toast.destroy)

    def on_close(self):
        self.destroy()
