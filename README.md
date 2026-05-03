# 🎮 Computer Vision Game Controller

Control your games using **hand gestures captured via webcam**.  
This project converts real-time hand poses into keyboard inputs with a customizable desktop interface.

> 🚀 **No setup required — just download and run the `.exe` file**

---

## 📥 Download

You can download the application here:

👉 [Download CV Game Controller](https://drive.google.com/drive/folders/1wzbmrS9IYrOLbOYQZE-6hD4ayM1-fZOL?usp=sharing)

### ⚠️ Important Notes
- This is a Windows executable (`.exe`)
- You may see a **Windows SmartScreen warning** → Click *"More info → Run anyway"*
- Ensure your **webcam is connected** before running

---

## 🚀 Features

- ✋ Real-time **hand tracking** using MediaPipe  
- 🎥 Live webcam preview  
- 🎯 Capture and save custom hand gestures  
- ⌨️ Map gestures to keyboard inputs (`W`, `A`, `D`, `Space`, etc.)  
- 💾 Persistent gesture bindings via JSON  
- ⚡ Real-time keypress simulation for seamless gameplay  

---

## 🎛️ Custom Gesture UI

Easily create and manage gesture bindings:

1. Enter a **gesture name**
2. Assign a **keyboard key**
3. Define finger states:
   - Manually select finger positions  
   - OR click **"Use Current Pose"**
4. Save the gesture  
5. Edit or delete existing gestures anytime  

---

## ⚙️ Setup (For Developers)

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📁 Configuration

Gesture mappings are stored in:

```bash
gesture_config.json
```

---

## 🎮 Usage Notes

- Click on your **game window** to ensure it receives inputs  
- Ensure **good lighting** for accurate hand tracking  
- Keep **one hand clearly visible** to the camera  
- Close the app window to stop the controller  

---

## 💡 Future Improvements

- ✌️ Support for **two-hand gestures**  
- 🧠 Gesture **calibration wizard**  
- 🎮 Replace keyboard input with **virtual gamepad support**  
- 🤖 Train a **custom gesture classifier** for higher accuracy  

---

## 📌 Tech Stack

- Python  
- MediaPipe  
- OpenCV  
- PyAutoGUI / keyboard input simulation  

---


## 🙌 Acknowledgements

- MediaPipe for hand tracking  
- OpenCV for computer vision utilities  
- Python ecosystem for development  