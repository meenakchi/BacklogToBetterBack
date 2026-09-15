# ⚡ Quick Start (5 Minutes)

## Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py

# 3. Watch your posture score change in real-time!
```

That's it! 🎉

---

## What to Try

1. **Sit up straight** → Your score goes UP ⬆️
2. **Slouch forward** → Your score goes DOWN ⬇️ (Alert triggers!)
3. **Tilt shoulders** → Score decreases
4. **Press 's'** → Save a screenshot
5. **Press 'q'** → Quit (saves stats to database)

---

## View Your Stats

```bash
python dashboard.py

# Then choose option 1 to see your sessions
```

---

## Next Steps

1. Read the full `README.md` for all features
2. Check out `posture_calculator.py` to learn the math
3. Modify thresholds in `main.py` to make it more/less sensitive
4. Add your own features!

---

## For Hackathon

- **Day 1:** Get it running, collect 10+ sessions
- **Day 2:** Build cool visualizations with dashboard
- **Day 3:** Add new features (breaks, stretches, teams, etc.)

---

## Common Issues

**Camera won't open?**
- Check camera is not in use elsewhere
- Try different `camera_id` in `main.py`

**Too many/few alerts?**
- Change `alert_threshold` in `main.py`

**Want to reset?**
- Delete `posture_data.db` and start fresh

---

Have fun! 🚀
