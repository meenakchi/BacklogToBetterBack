# Fix your posture, not your backlog
## Posture Monitor - Real-time Posture Detection

A computer vision project using **MediaPipe** to monitor your posture in real-time. Get alerts when you slouch, track your posture metrics over time, and improve your ergonomics. Made for corporate techy people who spend more time in front of screens than grass!

---

## Features

* Real-time pose detection via webcam
* Posture scoring system (0-100)
* Smart alerts when you slouch, with cooldown
* Session tracking with SQLite
* Analytics dashboard for visualizing posture trends
* Detailed posture metrics including neck angle, shoulder level, and forward head posture
* Screenshot capture for posture snapshots

---

## Setup

### Prerequisites

* Python 3.8+
* Webcam
* Approximately 100MB of disk space

### Installation

1. **Clone or extract this project**

```bash
cd posture_monitor
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
python main.py
```

---

## Usage

### Start Monitoring

```bash
python main.py
```

The application will:

* Open your webcam
* Detect your pose in real-time
* Calculate and display your posture score
* Save monitoring data to `posture_data.db`

### Keyboard Controls

| Key | Action               |
| --- | -------------------- |
| `q` | Quit monitoring      |
| `s` | Save screenshot      |
| `r` | Reset alert cooldown |

### View Analytics

```bash
python dashboard.py
```

The dashboard provides the following options:

1. View recent sessions in a table
2. Plot data from all sessions
3. Plot detailed data from a specific session
4. Clear data older than 30 days

---

## Understanding Posture Metrics

### Posture Score (0-100)

| Score  | Rating                                  |
| ------ | --------------------------------------- |
| 80-100 | Excellent posture                       |
| 60-79  | Good posture, with room for improvement |
| 40-59  | Slouching detected                      |
| 0-39   | Poor posture                            |

### Calculated Metrics

#### 1. Neck Angle

**Ideal range:** 160-180°

* Detects forward head posture
* The angle decreases when you lean forward

#### 2. Shoulder Level

**Ideal:** Shoulders remain level

* Detects whether your shoulders are tilted
* A higher value indicates greater shoulder imbalance

#### 3. Forward Head Posture

**Ideal:** Head remains close to shoulder alignment

* Measures the distance between the nose and shoulder
* A larger distance indicates greater forward head posture

#### 4. Back Curvature

**Ideal range:** 160-180°

* Detects rounded or slouched posture
* A lower angle indicates greater curvature

---

## Project Structure

```text
posture_monitor/
├── main.py                  # Main monitoring application
├── detect_pose.py           # MediaPipe pose detection
├── posture_calculator.py    # Angle and score calculations
├── database.py              # SQLite storage
├── dashboard.py             # Analytics viewer
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation

Generated files:
├── posture_data.db          # SQLite database
└── posture_snapshot_*.jpg   # Saved posture screenshots
```

---

## Code Walkthrough

### Core Concepts

#### 1. Pose Detection (`detect_pose.py`)

MediaPipe detects 33 body landmarks, including:

```python
landmarks = [
    NOSE, LEFT_EYE, RIGHT_EYE, LEFT_EAR, RIGHT_EAR,
    LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
    LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP,
    LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE,
    ...
]
```

Each landmark contains:

* `x`: Horizontal position
* `y`: Vertical position
* `z`: Depth position
* `visibility`: Landmark detection confidence

#### 2. Angle Calculation (`posture_calculator.py`)

The project calculates angles between body landmarks using vector mathematics and the dot product:

```python
angle = arccos(dot_product / (mag_a * mag_c))
```

This forms the mathematical foundation for several posture measurements.

#### 3. Scoring System

Multiple posture metrics are combined into a single score:

```python
score = 100
score -= (160 - neck_angle) * 0.5
score -= shoulder_level * 500
# ... additional penalties
score = clamp(score, 0, 100)
```

The final score is constrained between 0 and 100.

#### 4. Database Storage (`database.py`)

Posture data is stored in SQLite using session and frame records:

```sql
sessions: [id, start_time, avg_score, alert_count, ...]
frames:   [id, session_id, timestamp, posture_score, ...]
```

Frame-level posture data can then be used to analyze trends across monitoring sessions.

---

## Hackathon Tips

1. **Quick demo:** Run `main.py`, then demonstrate how the posture score changes when you slouch.
2. **Analytics:** Use the dashboard to demonstrate posture trends across sessions.
3. **Custom alerts:** Modify the alert threshold in `main.py` to adjust sensitivity.
4. **Data export:** Add CSV export functionality to `database.py` for easier analysis and presentation.
5. **Future expansion:** The project structure can be extended with a REST API for additional applications.

### Possible Extensions

* [ ] Web API using Flask for multi-user tracking
* [ ] Mobile application using React Native
* [ ] Discord bot for team posture statistics
* [ ] Posture streak counter
* [ ] Personalized exercise suggestions based on posture metrics
* [ ] Integration with productivity applications for break reminders

---

## Configuration

### Settings in `main.py`

```python
# Alert threshold (lower = more sensitive)
alert_threshold = 60

# Seconds between repeated alerts
alert_cooldown = 2
```

### Settings in `detect_pose.py`

```python
# Trade accuracy for speed
complexity = 1  # 0 = fast, 1 = accurate

# Detection confidence thresholds
min_detection_confidence = 0.5
min_tracking_confidence = 0.5
```

---

## Database Queries

You can access posture data directly through the `PostureDatabase` class:

```python
from database import PostureDatabase

db = PostureDatabase()

# Get the last 10 sessions
sessions = db.get_latest_sessions(10)

# Get detailed data for a specific session
session, frames = db.get_session_details(session_id=1)
```

---

## Learning Resources

### What You're Learning

* **Computer Vision:** Pose estimation and landmark detection
* **Python:** Real-time processing, file I/O, and databases
* **Mathematics:** Vector operations and angle calculations
* **Data Analysis:** Recording, storing, and visualizing posture metrics

### Useful Resources

* [MediaPipe Documentation](https://mediapipe.dev/)
* [OpenCV Documentation](https://docs.opencv.org/)
* [Pose Estimation Explained](https://www.youtube.com/watch?v=06FS7tPvSXE)

---

## Troubleshooting

### Camera Will Not Open

```text
Error: Could not open camera
```

Possible solutions:

* Check whether another application is using the camera
* Try running `main.py` with `camera_id=1` or `camera_id=2`
* On Mac, grant camera access through System Settings

### MediaPipe Is Slow

* Reduce `complexity` to `0` in `detect_pose.py`
* Lower the webcam resolution
* Close other resource-intensive applications

### Alerts Are Not Triggering

* Lower `alert_threshold` in `main.py`
* Check the posture feedback text to verify the calculated metrics

### Database Issues

* Delete `posture_data.db` to reset the database
* Make sure the application has permission to write to the project directory

---

## License

Free to use for personal and educational projects.

---

## About the Project

This project is designed as a foundation for experimenting with pose estimation and real-time computer vision. The same techniques can be extended to other applications involving human movement, activity recognition, and ergonomic analysis.

## Questions

Check the comments throughout the source code for explanations of the computer vision concepts and implementation details.
