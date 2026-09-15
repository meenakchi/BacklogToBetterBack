"""
Posture Dashboard
View and analyze posture session statistics
"""

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from datetime import datetime
from database import PostureDatabase
import json

class PostureDashboard:
    def __init__(self):
        """Initialize dashboard"""
        self.db = PostureDatabase()
    
    def plot_session(self, session_id):
        """Plot posture scores for a specific session"""
        session, frames = self.db.get_session_details(session_id)
        
        if not session or not frames:
            print("No data for this session")
            return
        
        # Extract data
        timestamps = []
        scores = []
        
        for timestamp, score in frames:
            dt = datetime.fromisoformat(timestamp)
            timestamps.append(dt)
            scores.append(score)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Posture score over time
        ax1.plot(timestamps, scores, linewidth=2, color='#2E86AB')
        ax1.fill_between(timestamps, scores, alpha=0.3, color='#2E86AB')
        ax1.axhline(y=60, color='red', linestyle='--', label='Alert threshold')
        ax1.axhline(y=80, color='green', linestyle='--', label='Good posture')
        ax1.set_ylabel('Posture Score', fontsize=12)
        ax1.set_title(f'Session #{session_id} - Posture Score Over Time', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        fig.autofmt_xdate(rotation=45)
        
        # Plot 2: Statistics
        ax2.axis('off')
        
        # Session stats
        session_id, start_time, end_time, duration, avg_score, min_score, max_score, alert_count = session
        
        avg_score = avg_score or 0
        min_score = min_score or 0
        max_score = max_score or 0
        alert_count = alert_count or 0
        duration = duration or 0
        
        stats_text = f"""
        SESSION STATISTICS
        
        Duration: {duration // 60}m {duration % 60}s
        Start: {start_time}
        
        Average Score: {avg_score:.1f}
        Max Score: {max_score:.1f}
        Min Score: {min_score:.1f}
        
        Alerts Triggered: {alert_count}
        Frames Recorded: {len(frames)}
        """
        
        ax2.text(0.5, 0.5, stats_text, 
                transform=ax2.transAxes,
                fontsize=11,
                verticalalignment='center',
                horizontalalignment='center',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()
    
    def plot_all_sessions(self, limit=20):
        """Plot all recent sessions"""
        sessions = self.db.get_latest_sessions(limit)
        
        if not sessions:
            print("No sessions found")
            return
        
        # Extract data
        dates = []
        avg_scores = []
        durations = []
        session_ids = []
        
        for session_id, start_time, duration, avg_score, alert_count in sessions:
            dt = datetime.fromisoformat(start_time)
            dates.append(dt)
            avg_scores.append(avg_score or 0)
            durations.append(duration or 0)
            session_ids.append(session_id)
        
        # Reverse for chronological order
        dates.reverse()
        avg_scores.reverse()
        durations.reverse()
        session_ids.reverse()
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Average posture scores
        colors = ['green' if s > 70 else 'orange' if s > 50 else 'red' for s in avg_scores]
        ax1.bar(range(len(avg_scores)), avg_scores, color=colors, alpha=0.7)
        ax1.axhline(y=70, color='green', linestyle='--', alpha=0.5, label='Good')
        ax1.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Fair')
        ax1.set_ylabel('Average Posture Score', fontsize=12)
        ax1.set_title('Average Posture Score by Session', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Session', fontsize=12)
        ax1.set_ylim(0, 100)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Session durations
        ax2.bar(range(len(durations)), [d/60 for d in durations], color='#2E86AB', alpha=0.7)
        ax2.set_ylabel('Duration (minutes)', fontsize=12)
        ax2.set_title('Session Duration', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Session', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add session IDs as labels
        ax1.set_xticks(range(len(session_ids)))
        ax1.set_xticklabels([f'S{i}' for i in session_ids], fontsize=9)
        ax2.set_xticks(range(len(session_ids)))
        ax2.set_xticklabels([f'S{i}' for i in session_ids], fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def print_sessions_table(self, limit=10):
        """Print sessions in table format"""
        sessions = self.db.get_latest_sessions(limit)
        
        print("\n" + "="*80)
        print(f"{'ID':<5} {'Start Time':<20} {'Duration':<12} {'Avg Score':<12} {'Alerts':<8}")
        print("="*80)
        
        for session_id, start_time, duration, avg_score, alert_count in sessions:
            duration_str = f"{duration//60}m {duration%60}s" if duration else "N/A"
            avg_score_str = f"{avg_score:.1f}" if avg_score else "N/A"
            alert_count_str = str(alert_count) if alert_count else "0"
            
            print(f"{session_id:<5} {start_time:<20} {duration_str:<12} {avg_score_str:<12} {alert_count_str:<8}")
        
        print("="*80 + "\n")

def main():
    """Dashboard CLI"""
    dashboard = PostureDashboard()
    
    print("""
╔════════════════════════════════════════╗
║    📊 POSTURE DASHBOARD 📊             ║
╚════════════════════════════════════════╝
    """)
    
    while True:
        print("\nOptions:")
        print("  1. View recent sessions")
        print("  2. Plot all sessions")
        print("  3. Plot specific session")
        print("  4. Clear old data (30+ days)")
        print("  5. Exit")
        
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == '1':
            dashboard.print_sessions_table(15)
        
        elif choice == '2':
            dashboard.plot_all_sessions(20)
        
        elif choice == '3':
            try:
                session_id = int(input("Enter session ID: "))
                dashboard.plot_session(session_id)
            except ValueError:
                print("Invalid ID")
        
        elif choice == '4':
            confirm = input("Delete data older than 30 days? (yes/no): ")
            if confirm.lower() == 'yes':
                dashboard.db.clear_old_data(30)
                print("✅ Old data cleared")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
