🔫 Weapon Detection System (YOLOv8)
📌 Overview

The Weapon Detection System is an AI-powered computer vision project that uses YOLOv8 to detect weapons such as Guns and Knives from images and video feeds.
This project is designed to help enhance public safety and security monitoring by providing real-time alerts and automated detection, reducing the reliance on manual CCTV monitoring.

Key highlights:

🚀 Built using YOLOv8 (Ultralytics)

📷 Detects two classes: Gun, Knife

🧠 Trained on 4000–5000 images

⚡ Supports real-time inference (images or CCTV feed)

🖥️ Beginner-friendly setup for reproducibility

👥 Team Details

Team Name: AI Defenders

Team Members:

Vineet Unde

[Member 2 Name]

[Member 3 Name]

🚨 Problem Statement

Security systems today heavily rely on manual CCTV monitoring. This comes with challenges:

👀 Human operators often miss critical moments due to fatigue or distractions.

⏳ Delayed detection of weapons can escalate into serious incidents.

🔒 There is a need for a fast, automated, and reliable system that can detect weapons in real time.

💡 Proposed Solution

We propose a YOLOv8-based solution that automatically detects weapons (Gun & Knife) in CCTV footage or images.
The model is trained on thousands of labeled images to ensure high accuracy.

System features:

✅ Detects Guns and Knives with bounding boxes and confidence scores.

✅ Provides real-time inference from webcam/CCTV.

✅ Lightweight models (YOLOv8n/m) for faster training & inference.

✅ Scalable for more classes in the future.

🏗️ System Architecture
Input (Image/Video/CCTV)
        │
        ▼
Preprocessing (resize, augment, normalize)
        │
        ▼
YOLOv8 Model (Gun/Knife detection)
        │
        ▼
Bounding Boxes + Confidence Scores
        │
        ▼
Alert System (future scope: notifications, dashboards)


📌 A clean architecture diagram (recommended: eraser.io, draw.io, or PPT export) should be placed in docs/architecture.png.

🛠️ Tech Stack

Languages & Frameworks:

Python 3.12

PyTorch (Deep Learning Framework)

Ultralytics YOLOv8

Libraries:

OpenCV → for image/video handling

NumPy, Matplotlib → for visualization

Pandas → dataset management

Tools:

Jupyter Notebook (training & experimentation)

VS Code (development)

GitHub (version control & collaboration)

📂 Dataset

Total images: 4000–5000

Classes:

Gun

Knife

Annotation format: YOLO TXT format (class_id x_center y_center width height)

Data split:

Train: 80%

Validation: 20%

Test: Empty (future use)

Folder Structure:

Weapon_Detection_System/
└── dataset/
    ├── train/
    │   ├── images/
    │   │   ├── Gun/
    │   │   └── Knife/
    │   └── labels/
    │       ├── Gun/
    │       └── Knife/
    ├── val/
    │   ├── images/
    │   │   ├── Gun/
    │   │   └── Knife/
    │   └── labels/
    │       ├── Gun/
    │       └── Knife/
    └── test/   # empty

📑 Data.yaml File
# Dataset configuration for YOLOv8
path: D:/ASSIGNMENTS VIIT/SEM 5/AISSMS HACKATHON/Weapon_Detection_System/dataset

train: train/images
val: val/images
test: test/images  # currently empty

# Number of classes
nc: 2

# Class names
names: ["Gun", "Knife"]

⚙️ Installation & Setup
🔹 1. Clone Repository
git clone https://github.com/your-username/weapon-detection-system.git
cd weapon-detection-system

🔹 2. Create Virtual Environment
python -m venv yolov8env
yolov8env\Scripts\activate   # (Windows)

🔹 3. Install Dependencies
pip install ultralytics opencv-python matplotlib numpy pandas

🔹 4. Open Jupyter Lab
jupyter lab

🏋️ Training the Model
from ultralytics import YOLO

# Load YOLOv8n (fast and lightweight)
model = YOLO("yolov8n.pt")

# Train
model.train(
    data="D:/ASSIGNMENTS VIIT/SEM 5/AISSMS HACKATHON/Weapon_Detection_System/dataset/data.yaml",
    epochs=30,       # number of epochs
    imgsz=640,       # image size
    batch=16,        # batch size
    name="weapon_detection",
    workers=4        # workers for dataloading
)

🔍 Inference (Prediction)

Run inference on an image:

results = model.predict("test_image.jpg", show=True)


Run inference on webcam:

results = model.predict(source=0, show=True)  # 0 = default webcam

📊 Results & Metrics

Training Dataset: 4000+ images

Validation Dataset: 1000+ images

Classes: Gun, Knife

Expected results:

mAP50 ≈ 0.75–0.85 (depends on training)

High precision on clear images

Some false positives on complex backgrounds (limitation)

(Insert screenshots of training curves and detection outputs here)

🚀 Future Scope

Add more weapon types (rifles, bombs, etc.)

Real-time notification system (SMS/Email/Telegram alerts)

Deployment as Flask/Django web app

Optimize for edge devices (Jetson Nano, Raspberry Pi)

📜 License

This project is developed for educational and hackathon purposes only.
Not intended for deployment in real-world critical surveillance without security evaluation.

🙌 Acknowledgements

Ultralytics YOLOv8

OpenCV Community

Hackathon Organizers
