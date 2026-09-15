"""
Database Module
SQLite storage for posture sessions and metrics
"""

import sqlite3
from datetime import datetime
import json
import os

class PostureDatabase:
    def __init__(self, db_name='posture_data.db'):
        """Initialize database connection"""
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Sessions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                avg_posture_score REAL,
                min_posture_score REAL,
                max_posture_score REAL,
                alert_count INTEGER
            )
        ''')
        
        # Frames table (stores individual frame data)
        c.execute('''
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP,
                posture_score REAL,
                metrics TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self):
        """Start a new posture monitoring session"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        start_time = datetime.now()
        c.execute('''
            INSERT INTO sessions (start_time, duration_seconds, alert_count)
            VALUES (?, ?, ?)
        ''', (start_time, 0, 0))
        
        session_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def end_session(self, session_id):
        """End current session and calculate stats"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Get all frames for this session
        c.execute('''
            SELECT posture_score FROM frames WHERE session_id = ?
        ''', (session_id,))
        
        scores = [row[0] for row in c.fetchall()]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
        else:
            avg_score = min_score = max_score = 0
        
        end_time = datetime.now()
        
        # Get start time
        c.execute('SELECT start_time FROM sessions WHERE id = ?', (session_id,))
        start_time = c.fetchone()[0]
        start_dt = datetime.fromisoformat(start_time)
        duration = int((end_time - start_dt).total_seconds())
        
        # Update session
        c.execute('''
            UPDATE sessions 
            SET end_time = ?, duration_seconds = ?, 
                avg_posture_score = ?, min_posture_score = ?, max_posture_score = ?
            WHERE id = ?
        ''', (end_time, duration, avg_score, min_score, max_score, session_id))
        
        conn.commit()
        conn.close()
        
        return {
            'duration': duration,
            'avg_score': avg_score,
            'min_score': min_score,
            'max_score': max_score
        }
    
    def record_frame(self, session_id, posture_score, metrics):
        """Record a single frame's posture data"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        timestamp = datetime.now()
        metrics_json = json.dumps(metrics) if metrics else '{}'
        
        c.execute('''
            INSERT INTO frames (session_id, timestamp, posture_score, metrics)
            VALUES (?, ?, ?, ?)
        ''', (session_id, timestamp, posture_score, metrics_json))
        
        conn.commit()
        conn.close()
    
    def record_alert(self, session_id):
        """Increment alert count for session"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''
            UPDATE sessions SET alert_count = alert_count + 1 WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_latest_sessions(self, limit=10):
        """Get latest sessions"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, start_time, duration_seconds, avg_posture_score, alert_count
            FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        ''', (limit,))
        
        sessions = c.fetchall()
        conn.close()
        
        return sessions
    
    def get_session_details(self, session_id):
        """Get detailed data for a specific session"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Session info
        c.execute('''
            SELECT * FROM sessions WHERE id = ?
        ''', (session_id,))
        
        session = c.fetchone()
        
        # Frames
        c.execute('''
            SELECT timestamp, posture_score FROM frames WHERE session_id = ?
            ORDER BY timestamp
        ''', (session_id,))
        
        frames = c.fetchall()
        conn.close()
        
        return session, frames
    
    def clear_old_data(self, days=30):
        """Delete data older than N days (cleanup)"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        c.execute('DELETE FROM frames WHERE session_id IN (SELECT id FROM sessions WHERE start_time < ?)', (cutoff_date,))
        c.execute('DELETE FROM sessions WHERE start_time < ?', (cutoff_date,))
        
        conn.commit()
        conn.close()
