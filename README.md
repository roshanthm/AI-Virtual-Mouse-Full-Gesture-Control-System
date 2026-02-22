# 🖐️ AI Virtual Mouse & Full Gesture Control System

An AI-powered virtual mouse system that enables **hands-free computer control**
using real-time hand gesture recognition. The system leverages computer vision
and machine learning to translate hand movements and gestures into mouse actions
such as cursor movement, clicking, dragging, scrolling, and voice feedback.

---

## 🚀 Project Overview

Traditional mouse-based interaction is not always accessible or convenient.
This project provides a **touchless human–computer interaction system** using
a standard webcam and hand gestures.

By combining **MediaPipe hand tracking** with real-time gesture interpretation,
the system allows users to control the mouse cursor naturally, without any
physical input devices.

---

## ✨ Key Features

- Real-time hand tracking using a webcam
- Smooth cursor movement with motion filtering
- Gesture-based mouse actions:
  - Left click
  - Double click
  - Right click
  - Click-and-drag
  - Vertical scrolling
- Optional voice feedback (Text-to-Speech)
- Toggle mouse control and visual overlay
- FPS monitoring and on-screen status display

---

## 🧠 Gesture Controls

| Gesture | Action |
|------|------|
| Index finger movement | Move cursor |
| Thumb + Index finger pinch | Click / Drag |
| Quick double pinch | Double click |
| Index + Middle finger pinch | Right click |
| Two fingers open + vertical motion | Scroll |
| `M` key | Toggle mouse control |
| `V` key | Toggle overlay |
| `Q` or `ESC` | Exit application |

---

## 🛠️ Technologies Used

- **Python**
- **OpenCV** – Video capture and rendering
- **MediaPipe** – Hand landmark detection
- **PyAutoGUI** – Mouse and scroll control
- **NumPy** – Mathematical operations
- **pyttsx3** (optional) – Voice feedback

---

