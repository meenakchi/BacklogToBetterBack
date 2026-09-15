# 🧘 Posture Monitor - Real-time Posture Detection

A computer vision project using **MediaPipe** to monitor your posture in real-time. Get alerts when you slouch, track your posture metrics over time, and improve your ergonomics.

**Perfect for:** Hackathons, personal projects, learning OpenCV + MediaPipe

---

## 🎯 Features

✅ **Real-time pose detection** via webcam  
✅ **Posture scoring system** (0-100)  
✅ **Smart alerts** when you slouch (with cooldown)  
✅ **Session tracking** - records all monitoring data to SQLite  
✅ **Analytics dashboard** - visualize your posture trends  
✅ **Detailed metrics** - neck angle, shoulder level, forward head posture, etc.  
✅ **Screenshot capture** - save posture snapshots  

---

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- Webcam
- ~100MB disk space

### Installation

1. **Clone/extract this project**
   ```bash
   cd posture_monitor
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run it!**
   ```bash
   python main.py
   ```

---

## 🎮 Usage

### Start Monitoring
```bash
python main.py
```

The app will:
- Open your webcam
- Start detecting your pose
- Track posture score in real-time
- Save data to `posture_data.db`

### Keyboard Controls
| Key | Action |
|-----|--------|
| `q` | Quit monitoring |
| `s` | Save screenshot |
| `r` | Reset alert cooldown |

### View Analytics
```bash
python dashboard.py
```

Options in dashboard:
1. View recent sessions (table)
2. Plot all sessions (graphs)
3. Plot specific session (detailed)
4. Clear data older than 30 days

---

## 📊 Understanding Posture Metrics

### Posture Score (0-100)
- **80-100:** Excellent posture ✅
- **60-79:** Good, but room for improvement ⚠️
- **40-59:** Slouching - sit up! ❌
- **0-39:** Very bad posture 🚨

### Calculated Metrics
1. **Neck Angle** (ideal: 160-180°)
   - Detects forward head posture
   - Decreases when you lean forward
   
2. **Shoulder Level** (ideal: level)
   - Detects if shoulders are tilted
   - Higher = more uneven
   
3. **Forward Head Posture** (ideal: close to shoulder)
   - Distance from nose to shoulder
   - Larger distance = worse posture
   
4. **Back Curvature** (ideal: 160-180°)
   - Detects rounded/slouching back
   - Lower angle = more rounded

---

## 📁 Project Structure

```
posture_monitor/
├── main.py                  # Main monitoring app
├── detect_pose.py          # MediaPipe pose detection
├── posture_calculator.py   # Angle & score calculations
├── database.py             # SQLite storage
├── dashboard.py            # Analytics viewer
├── requirements.txt        # Dependencies
└── README.md              # This file

Generated files (during use):
├── posture_data.db        # SQLite database
└── posture_snapshot_*.jpg # Screenshots
```

---

## 💡 Code Walkthrough

### Core Concepts (Learn CV!)

#### 1. Pose Detection (`detect_pose.py`)
```python
# MediaPipe detects 33 body landmarks
landmarks = [
    NOSE, LEFT_EYE, RIGHT_EYE, LEFT_EAR, RIGHT_EAR,
    LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
    LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP,
    LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE,
    ...
]
```

Each landmark has: `x` (horizontal), `y` (vertical), `z` (depth), `visibility` (confidence)

#### 2. Angle Calculation (`posture_calculator.py`)
```python
# Calculate angle between 3 points using dot product
angle = arccos(dot_product / (mag_a * mag_c))
```

This is the core CV math - used everywhere!

#### 3. Scoring System
```python
# Combine multiple metrics into single score
score = 100
score -= (160 - neck_angle) * 0.5  # Penalize forward neck
score -= shoulder_level * 500        # Penalize uneven shoulders
# ... etc
score = clamp(score, 0, 100)
```

#### 4. Database Storage (`database.py`)
```sql
sessions:  [id, start_time, avg_score, alert_count, ...]
frames:    [id, session_id, timestamp, posture_score, ...]
```

Every frame's data is recorded for analysis!

---

## 🚀 Hackathon Tips

1. **Quick demo:** Just run `main.py` - slouch and watch score drop. Works great!
2. **Impressive stats:** Show off analytics dashboard with trends
3. **Custom alerts:** Modify alert thresholds in `main.py` for different sensitivity
4. **Export data:** Add CSV export to `database.py` for judges
5. **Mobile future:** Code is structured to add REST API easily

### Possible Extensions
- [ ] Web API (Flask) for multi-user tracking
- [ ] Mobile app (React Native)
- [ ] Discord bot for team posture stats
- [ ] Posture streak counter
- [ ] Custom workout suggestions based on metrics
- [ ] Integration with productivity apps (take breaks)

---

## ⚙️ Configuration

### Adjust These in `main.py`:
```python
# Alert threshold (lower = more sensitive)
alert_threshold = 60

# Seconds between repeated alerts
alert_cooldown = 2
```

### Adjust These in `detect_pose.py`:
```python
# Trade accuracy for speed
complexity = 1  # 0=fast, 1=accurate

# Detection confidence threshold
min_detection_confidence = 0.5
min_tracking_confidence = 0.5
```

---

## 📈 Database Queries

Access your data directly if needed:

```python
from database import PostureDatabase

db = PostureDatabase()

# Get last 10 sessions
sessions = db.get_latest_sessions(10)

# Get detailed session data
session, frames = db.get_session_details(session_id=1)
```

---

## 🎓 Learning Resources

### What You're Learning:
- **Computer Vision Basics:** Pose estimation, landmark detection
- **Python:** Real-time processing, file I/O, databases
- **Math:** Vector operations, angle calculations
- **Data Analysis:** Recording, storing, visualizing metrics

### Useful Resources:
- [MediaPipe Docs](https://mediapipe.dev/)
- [OpenCV Tutorials](https://docs.opencv.org/)
- [Pose Estimation Explained](https://www.youtube.com/watch?v=06FS7tPvSXE)

---

## ⚠️ Troubleshooting

### Camera won't open
```
Error: Could not open camera
```
- Check if camera is already in use
- Try `python main.py` with camera_id=1 or 2
- On Mac: Grant camera permissions in System Preferences

### MediaPipe slow
- Reduce complexity: `complexity=0` in detect_pose.py
- Lower resolution webcam feed
- Close other heavy apps

### No alerts triggering
- Lower `alert_threshold` in main.py
- Check posture feedback text to debug metrics

### Database issues
- Delete `posture_data.db` to reset
- Make sure you have write permissions

---

## 📝 License

Free to use for personal/educational projects!

---

## 🎉 Have Fun!

This is a learning project - experiment, break things, improve it. Posture monitor is just the foundation - imagine what else you can detect with pose estimation! 

Good luck at the hackathon! 🚀

---

**Questions?** Check the code comments - they explain the CV concepts!
