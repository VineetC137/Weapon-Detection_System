# 🔫 Weapon Detection System using YOLOv8

An AI-powered real-time weapon detection system that identifies **Guns and Knives** from images, videos, and live CCTV feeds using **YOLOv8**.

---

## 📌 Overview

Manual CCTV monitoring is error-prone and slow. This system automates the detection of weapons to improve surveillance response time and public safety using deep learning.

---

## ✨ Features

- Detects **Gun** and **Knife** with bounding boxes & confidence scores  
- Real-time webcam / CCTV feed detection  
- YOLOv8 lightweight architecture for faster inference  
- Scalable for additional weapon classes  

---

## 👥 Team Details

**Team Name:** AI Defenders  

| Name |
|------|
| Vineet Unde |
| Shraddha Bhadane |
---

## 🚨 Problem Statement

Traditional surveillance depends on human operators who may miss critical events due to fatigue or distractions, causing delayed reactions to violent incidents.

---

## 💡 Proposed Solution

A YOLOv8-based automated detection system trained on thousands of weapon images to identify guns and knives instantly in real-time.

---

## 🏗️ System Architecture
Input (Image / Video / CCTV)
│
▼
Preprocessing (Resize, Normalize, Augmentation)
│
▼
YOLOv8 Model
│
▼
Bounding Boxes + Confidence Scores
│
▼
Alert System (Future Scope)


---

## 🛠️ Tech Stack

| Component | Tools |
|---------|------|
| Language | Python 3.12 |
| Framework | PyTorch |
| Model | YOLOv8 (Ultralytics) |
| Libraries | OpenCV, NumPy, Pandas, Matplotlib |
| Tools | Jupyter Notebook, VS Code, GitHub |

---

## 📂 Dataset

| Category | Details |
|--------|--------|
| Total Images | 4000–5000 |
| Classes | Gun, Knife |
| Split | 80% Train / 20% Validation |
| Format | YOLO TXT |

---

## 📁 Dataset Structure

Weapon_Detection_System/
└── dataset/
├── train/
│ ├── images/
│ └── labels/
├── val/
│ ├── images/
│ └── labels/
└── test/
---

## 📑 data.yaml

```yaml
path: dataset
train: train/images
val: val/images
test: test/images
nc: 2
names: ["Gun", "Knife"]
⚙️ Installation
```bash
Copy code
git clone https://github.com/VineetC137/Weapon-Detection_System.git
cd Weapon-Detection_System
python -m venv yolov8env
yolov8env\Scripts\activate
pip install ultralytics opencv-python matplotlib numpy pandas
🏋️ Training
```bash
python
Copy code
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="dataset/data.yaml",
    epochs=30,
    imgsz=640,
    batch=16,
    name="weapon_detection"
)
-----

🔍 Inference
```bash
Run on Image
python
Copy code
model.predict("test.jpg", show=True)
Run on Webcam
python
Copy code
model.predict(source=0, show=True)
-------
📊 Results
Metric	Value
mAP50	0.75 – 0.85
Precision	High
Limitation	False positives on cluttered backgrounds
-------
🚀 Future Enhancements
Add detection for more weapon classes

Integrate real-time alert notifications

Deploy as a Flask/Django web application

Optimize model for edge devices
-------
📜 License
This project is for educational and hackathon use only.
--------
🙌 Acknowledgements
Ultralytics YOLOv8

OpenCV Community

Hackathon Organizers
