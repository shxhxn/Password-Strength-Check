import re
import tkinter as tk
from tkinter import ttk

# --- Advanced Strength Scoring Logic ---

def calculate_strength_score(password):
    """
    Calculates a detailed score based on length, complexity, and patterns.
    Returns the score (0 to 100+).
    """
    score = 0
    length = len(password)

    if length == 0:
        return 0

    # 1. Length Bonus (Exponentially increasing points)
    # 8 chars = ~30 points, 12 chars = ~50 points, 20 chars = ~80 points
    score += min(80, length * 5 + (length - 8) * 2)
    score = max(0, score)

    # 2. Character Set Variety Bonus
    checks = {
        'lower': re.search(r"[a-z]", password) is not None,
        'upper': re.search(r"[A-Z]", password) is not None,
        'digits': re.search(r"\d", password) is not None,
        'symbols': re.search(r"[^a-zA-Z0-9\s]", password) is not None
    }

    unique_char_types = sum(checks.values())
    
    # Add points based on variety
    if unique_char_types == 2: score += 10
    if unique_char_types == 3: score += 15
    if unique_char_types == 4: score += 20
    
    # 3. Complexity Bonus (Ensuring mix and non-sequential use)
    if checks['digits'] and length > 6:
        # Bonus if digits are not only at the start/end
        if re.search(r"^[a-zA-Z].*\d.*[a-zA-Z]$", password): score += 5

    if checks['symbols'] and length > 6:
        # Bonus if symbols are not only at the start/end
        if re.search(r"^[a-zA-Z\d].*[^a-zA-Z0-9\s].*[a-zA-Z\d]$", password): score += 10

    # 4. Deduction for Repeated Characters (e.g., 'aaaaa' or '1111')
    repeat_match = re.findall(r"(.)\1{2,}", password)
    if repeat_match:
        score -= len(repeat_match) * 15 # Heavy deduction for repetition

    # 5. Deduction for Simple Patterns (e.g., '123' or 'abc')
    if re.search(r"(123|abc|xyz|qwerty)", password, re.IGNORECASE):
        score -= 15
    
    return max(0, round(score))


def get_strength_details(score, password):
    """Maps score to level, color, and feedback."""
    length = len(password)
    strength = "No Password"
    color = "#cccccc"
    percent = 0
    feedback = []

    # --- Level Classification ---
    if score > 100:
        strength = "Excellent (Unbreakable)"
        color = "#10B981"  # Emerald Green
        percent = 100
    elif score >= 76:
        strength = "Strong"
        color = "#059669"  # Dark Green
        percent = min(100, score)
    elif score >= 51:
        strength = "Moderate"
        color = "#F59E0B"  # Yellow/Amber
        percent = min(100, score)
    elif score >= 26:
        strength = "Weak"
        color = "#EF4444"  # Red
        percent = min(100, score)
    elif score > 0:
        strength = "Too Weak"
        color = "#B91C1C"  # Dark Red
        percent = min(100, score)

    # --- Detailed Feedback Generation ---
    if length == 0:
        return {"score": 0, "strength": "No Password", "color": "#cccccc", "percent": 0, "feedback": ["Please enter a password to check its strength."]}

    checks = {
        'Lowercase letters (a-z)': re.search(r"[a-z]", password),
        'Uppercase letters (A-Z)': re.search(r"[A-Z]", password),
        'Digits (0-9)': re.search(r"\d", password),
        'Symbols (!@#$)': re.search(r"[^a-zA-Z0-9\s]", password)
    }

    # Length Feedback
    if length < 8:
        feedback.append(f"❌ Length: Must be at least 8 characters. Currently {length}.")
    elif length < 12:
        feedback.append(f"🟡 Length: Good ({length} chars), but needs more for 'Strong'.")
    else:
        feedback.append(f"✅ Length: Excellent ({length} chars).")
    
    # Complexity Feedback
    for key, passed in checks.items():
        if not passed:
            feedback.append(f"❌ Missing: Include at least one {key}.")
        else:
            feedback.append(f"✅ Includes {key}.")

    # Pattern and Repetition Deduction Feedback
    if re.search(r"(.)\1{2,}", password):
        feedback.append("⚠️ Warning: Contains repetitive characters (e.g., 'aaa').")
    
    if re.search(r"(123|abc|xyz|qwerty)", password, re.IGNORECASE):
        feedback.append("⚠️ Warning: Contains simple sequential patterns ('123', 'abc').")


    return {"score": score, "strength": strength, "color": color, "percent": percent, "feedback": feedback}

# --- Tkinter GUI Application Class ---

class PasswordCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("Desktop Password Strength Checker")
        master.geometry("500x450")
        master.resizable(False, False)
        
        # Configure modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#F0F0F0')
        style.configure('TLabel', background='#F0F0F0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        style.configure('TEntry', padding=5)
        
        # Main Frame
        self.main_frame = ttk.Frame(master, padding="20 20 20 20")
        self.main_frame.pack(fill='both', expand=True)

        # Title
        ttk.Label(self.main_frame, text="Password Strength Analyzer", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Input Label and Field
        ttk.Label(self.main_frame, text="Enter Password:").pack(anchor='w', pady=(10, 2))
        self.password_entry = ttk.Entry(self.main_frame, show="*", width=50, font=('Arial', 12))
        self.password_entry.pack(fill='x', ipady=5)
        self.password_entry.bind('<KeyRelease>', self.check_strength_event)

        # Strength Bar Label and Progress Bar
        ttk.Label(self.main_frame, text="Strength Level:").pack(anchor='w', pady=(15, 2))
        
        self.strength_bar = ttk.Progressbar(self.main_frame, orient='horizontal', length=460, mode='determinate')
        self.strength_bar.pack(fill='x', pady=5)
        
        # Strength Text and Score
        self.strength_label = ttk.Label(self.main_frame, text="No Password", font=('Arial', 12, 'bold'), foreground='#444')
        self.strength_label.pack(anchor='w', pady=(0, 10))
        
        self.score_label = ttk.Label(self.main_frame, text="Score: 0 / 100+", font=('Arial', 9), foreground='#888')
        self.score_label.pack(anchor='e')

        # Feedback Section
        ttk.Label(self.main_frame, text="Checklist & Suggestions:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(10, 5))
        
        self.feedback_frame = ttk.Frame(self.main_frame)
        self.feedback_frame.pack(fill='both', expand=True)
        
        self.feedback_text = tk.Text(self.feedback_frame, height=10, width=50, state='disabled', wrap='word', borderwidth=1, relief="solid", font=('Arial', 10), padx=5, pady=5)
        self.feedback_text.pack(fill='both', expand=True)
        
        # Initial check
        self.check_strength_event(None)

    def check_strength_event(self, event):
        """Called on every key release in the password field."""
        password = self.password_entry.get()
        details = get_strength_details(calculate_strength_score(password), password)

        # Update Strength Label
        self.strength_label.config(text=details['strength'], foreground=details['color'])
        
        # Update Score Label
        self.score_label.config(text=f"Score: {details['score']} / 100+")

        # Update Progress Bar Color and Value
        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", foreground=details['color'], background=details['color'])
        self.strength_bar.config(style="green.Horizontal.TProgressbar", value=details['percent'])
        
        # Update Feedback Text Area
        self.feedback_text.config(state='normal')
        self.feedback_text.delete(1.0, tk.END)
        
        if password:
            for line in details['feedback']:
                self.feedback_text.insert(tk.END, line + '\n')
        else:
            self.feedback_text.insert(tk.END, "Start typing your password to see the analysis.")

        self.feedback_text.config(state='disabled')


if __name__ == "__main__":
    # The regex engine needs to be accessible in a Python environment
    # We define the regex patterns in global scope for efficiency (though repeated here for clarity)
    re.compile(r"[a-z]")
    re.compile(r"[A-Z]")
    re.compile(r"\d")
    re.compile(r"[^a-zA-Z0-9\s]")
    re.compile(r"(.)\1{2,}")
    re.compile(r"^[a-zA-Z].*\d.*[a-zA-Z]$")
    
    # Initialize the desktop window
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()