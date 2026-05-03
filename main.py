from __future__ import annotations

import copy
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import cv2
import mediapipe as mp
from PIL import Image, ImageTk

from src.config import DEFAULT_GESTURES, load_config, save_config
from src.gestures import (
    FINGER_ORDER,
    FingerState,
    describe_finger_state,
    extract_finger_state,
    find_matching_gesture,
)
from src.keyboard_controller import KeyboardGameController


CONFIG_PATH = Path("gesture_config.json")


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Custom CV Game Controller")
        self.root.geometry("1180x760")
        self.root.configure(bg="#f2efe8")

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam.")

        self.gestures = load_config(CONFIG_PATH)
        if not self.gestures:
            self.gestures = copy.deepcopy(DEFAULT_GESTURES)
            save_config(CONFIG_PATH, self.gestures)

        self.controller = KeyboardGameController()
        self.current_state: FingerState | None = None
        self.selected_index: int | None = None
        self.preview_image: ImageTk.PhotoImage | None = None

        self.status_var = tk.StringVar(value="Show your hand to the camera.")
        self.pose_var = tk.StringVar(value="Current pose: no hand detected")
        self.active_binding_var = tk.StringVar(value="Active key: none")
        self.name_var = tk.StringVar()
        self.key_var = tk.StringVar()
        self.finger_vars = {
            finger: tk.BooleanVar(value=False) for finger in FINGER_ORDER
        }

        self._build_ui()
        self._refresh_gesture_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._update_camera()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)

        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=2)
        outer.rowconfigure(0, weight=1)

        camera_card = ttk.Frame(outer, padding=12)
        camera_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        camera_card.columnconfigure(0, weight=1)

        self.video_label = ttk.Label(camera_card)
        self.video_label.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            camera_card,
            textvariable=self.pose_var,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(12, 0))
        ttk.Label(
            camera_card,
            textvariable=self.active_binding_var,
            font=("Segoe UI", 11),
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            camera_card,
            textvariable=self.status_var,
            wraplength=640,
            font=("Segoe UI", 10),
        ).grid(row=3, column=0, sticky="w", pady=(8, 0))

        right_panel = ttk.Frame(outer, padding=12)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)

        form_card = ttk.LabelFrame(right_panel, text="Create Or Edit Gesture", padding=12)
        form_card.grid(row=0, column=0, sticky="ew")
        form_card.columnconfigure(1, weight=1)

        ttk.Label(form_card, text="Gesture name").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(form_card, textvariable=self.name_var).grid(
            row=0, column=1, sticky="ew", pady=4
        )

        ttk.Label(form_card, text="Keyboard key").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form_card, textvariable=self.key_var).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        finger_frame = ttk.LabelFrame(form_card, text="Finger pattern", padding=8)
        finger_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 8))
        for index, finger in enumerate(FINGER_ORDER):
            ttk.Checkbutton(
                finger_frame,
                text=finger.title(),
                variable=self.finger_vars[finger],
            ).grid(row=index // 2, column=index % 2, sticky="w", padx=6, pady=4)

        buttons = ttk.Frame(form_card)
        buttons.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        ttk.Button(buttons, text="Use Current Pose", command=self.use_current_pose).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(buttons, text="Save Gesture", command=self.save_gesture).grid(
            row=0, column=1, sticky="ew"
        )

        buttons2 = ttk.Frame(form_card)
        buttons2.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        buttons2.columnconfigure(0, weight=1)
        buttons2.columnconfigure(1, weight=1)
        ttk.Button(buttons2, text="Clear Form", command=self.clear_form).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(buttons2, text="Delete Selected", command=self.delete_selected).grid(
            row=0, column=1, sticky="ew"
        )

        list_card = ttk.LabelFrame(right_panel, text="Saved Gestures", padding=12)
        list_card.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        self.gesture_list = tk.Listbox(
            list_card,
            height=16,
            activestyle="none",
            font=("Consolas", 10),
        )
        self.gesture_list.grid(row=0, column=0, sticky="nsew")
        self.gesture_list.bind("<<ListboxSelect>>", self.on_select_gesture)

        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.gesture_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.gesture_list.configure(yscrollcommand=scrollbar.set)

    def _refresh_gesture_list(self) -> None:
        self.gesture_list.delete(0, tk.END)
        for gesture in self.gestures:
            pose = describe_finger_state(gesture["pattern"])
            self.gesture_list.insert(
                tk.END,
                f"{gesture['name']:<18} -> {gesture['key']:<8} | {pose}",
            )

    def _update_camera(self) -> None:
        ok, frame = self.cap.read()
        if not ok:
            self.status_var.set("Unable to read a frame from the webcam.")
            self.root.after(30, self._update_camera)
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        matched_name = None
        matched_key = None
        self.current_state = None

        if results.multi_hand_landmarks and results.multi_handedness:
            hand_landmarks = results.multi_hand_landmarks[0]
            handedness = results.multi_handedness[0].classification[0].label
            self.current_state = extract_finger_state(hand_landmarks, handedness)
            matched = find_matching_gesture(self.current_state, self.gestures)

            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
            )

            self.pose_var.set(f"Current pose: {describe_finger_state(self.current_state)}")
            if matched:
                matched_name = matched["name"]
                matched_key = matched["key"]
                self.status_var.set(f"Matched gesture: {matched_name}")
                self.active_binding_var.set(f"Active key: {matched_key}")
            else:
                self.status_var.set("No saved gesture matches the current pose.")
                self.active_binding_var.set("Active key: none")
        else:
            self.pose_var.set("Current pose: no hand detected")
            self.status_var.set("Show your hand clearly to capture or trigger a gesture.")
            self.active_binding_var.set("Active key: none")

        self.controller.update(matched_key)

        cv2.putText(
            frame,
            matched_name or "No gesture",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (31, 163, 84),
            2,
        )
        cv2.putText(
            frame,
            "Capture a pose from the panel on the right",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        preview_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(preview_frame)
        image = image.resize((700, 520))
        self.preview_image = ImageTk.PhotoImage(image=image)
        self.video_label.configure(image=self.preview_image)

        self.root.after(15, self._update_camera)

    def use_current_pose(self) -> None:
        if self.current_state is None:
            messagebox.showwarning("No Hand Found", "Show a hand to the webcam first.")
            return

        for finger in FINGER_ORDER:
            self.finger_vars[finger].set(self.current_state[finger])
        self.status_var.set("Loaded the live hand pose into the gesture form.")

    def save_gesture(self) -> None:
        name = self.name_var.get().strip()
        key = self.key_var.get().strip()
        pattern = {finger: self.finger_vars[finger].get() for finger in FINGER_ORDER}

        if not name:
            messagebox.showerror("Missing Name", "Enter a gesture name.")
            return
        if not key:
            messagebox.showerror("Missing Key", "Enter a keyboard key such as a, d, or space.")
            return
        if not self.controller.is_supported(key):
            messagebox.showerror(
                "Unsupported Key",
                "Use one character like a or d, or a named key such as space, enter, up, down, left, or right.",
            )
            return

        gesture = {"name": name, "key": key, "pattern": pattern}

        if self.selected_index is None:
            self.gestures.append(gesture)
            self.status_var.set(f"Saved new gesture '{name}'.")
        else:
            self.gestures[self.selected_index] = gesture
            self.status_var.set(f"Updated gesture '{name}'.")

        save_config(CONFIG_PATH, self.gestures)
        self._refresh_gesture_list()
        self.clear_form(reset_selection=False)

    def clear_form(self, reset_selection: bool = True) -> None:
        self.name_var.set("")
        self.key_var.set("")
        for finger in FINGER_ORDER:
            self.finger_vars[finger].set(False)
        if reset_selection:
            self.selected_index = None
            self.gesture_list.selection_clear(0, tk.END)
        self.status_var.set("Gesture form cleared.")

    def delete_selected(self) -> None:
        if self.selected_index is None:
            messagebox.showinfo("No Selection", "Choose a gesture from the list first.")
            return

        gesture_name = self.gestures[self.selected_index]["name"]
        del self.gestures[self.selected_index]
        save_config(CONFIG_PATH, self.gestures)
        self._refresh_gesture_list()
        self.clear_form()
        self.status_var.set(f"Deleted gesture '{gesture_name}'.")

    def on_select_gesture(self, _event) -> None:
        selection = self.gesture_list.curselection()
        if not selection:
            return

        self.selected_index = selection[0]
        gesture = self.gestures[self.selected_index]
        self.name_var.set(gesture["name"])
        self.key_var.set(gesture["key"])
        for finger in FINGER_ORDER:
            self.finger_vars[finger].set(bool(gesture["pattern"].get(finger, False)))
        self.status_var.set(f"Editing gesture '{gesture['name']}'.")

    def on_close(self) -> None:
        self.controller.release_all()
        self.cap.release()
        self.hands.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
