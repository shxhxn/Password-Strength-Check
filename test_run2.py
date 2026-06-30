import re
import tkinter as tk
from tkinter import ttk

# --- Advanced Strength Scoring Logic (UNCHANGED from user's request) ---

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
    color = "#D1D5DB"  # Gray for empty state
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
        return {"score": 0, "strength": "No Password", "color": "#D1D5DB", "percent": 0, "feedback": ["Please enter a password to check its strength."]}

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

# --- Tkinter GUI Application Class (Improved Aesthetics) ---

class PasswordCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("Password Strength Analyzer")
        master.geometry("500x470") # Slightly taller window
        master.resizable(False, False)
        master.configure(background='#F0F0F0') # Light background for the window

        # Configure modern styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Customizing the Frame and Labels for a cleaner look
        style.configure('Main.TFrame', background='#FFFFFF', borderwidth=1, relief="flat") # White background for content area
        style.configure('TLabel', background='#FFFFFF', font=('Segoe UI', 10), foreground='#333333')
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#2563EB') # Blue accent for title
        style.configure('Bold.TLabel', font=('Segoe UI', 11, 'bold'))
        
        # Customizing the Progressbar for a sleek appearance
        style.layout('Custom.Horizontal.TProgressbar', 
                     [('Horizontal.Progressbar.trough', 
                       {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nsew'})])
        style.configure('Custom.Horizontal.TProgressbar', troughcolor='#E5E7EB', borderwidth=0, thickness=12)


        # Main Frame (Container for content)
        self.main_frame = ttk.Frame(master, style='Main.TFrame', padding="25 20 25 20")
        self.main_frame.pack(fill='both', expand=True, padx=15, pady=15) # Add margin around the main content

        # Title
        ttk.Label(self.main_frame, text="Password Strength Analyzer", style='Title.TLabel').pack(pady=(0, 15))
        
        # Input Label and Field
        ttk.Label(self.main_frame, text="Enter Password:").pack(anchor='w', pady=(5, 2))
        self.password_entry = ttk.Entry(self.main_frame, show="*", width=50, font=('Consolas', 12), foreground='#222')
        self.password_entry.pack(fill='x', ipady=8)
        self.password_entry.bind('<KeyRelease>', self.check_strength_event)

        # Strength Bar Label and Progress Bar
        ttk.Label(self.main_frame, text="Strength Level:").pack(anchor='w', pady=(15, 5))
        
        self.strength_bar = ttk.Progressbar(self.main_frame, orient='horizontal', length=450, mode='determinate', style='Custom.Horizontal.TProgressbar')
        self.strength_bar.pack(fill='x', pady=0)
        
        # Strength Text and Score Container
        score_container = ttk.Frame(self.main_frame, style='Main.TFrame')
        score_container.pack(fill='x', pady=(5, 15))

        # Strength Text (Left aligned and prominent)
        self.strength_label = ttk.Label(score_container, text="No Password", font=('Segoe UI', 14, 'bold'), foreground='#444')
        self.strength_label.pack(side='left')
        
        # Score (Right aligned and subtle)
        self.score_label = ttk.Label(score_container, text="Score: 0 / 100+", font=('Segoe UI', 10), foreground='#888')
        self.score_label.pack(side='right')

        # Feedback Section
        ttk.Label(self.main_frame, text="Checklist & Suggestions:", style='Bold.TLabel').pack(anchor='w', pady=(10, 5))
        
        self.feedback_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.feedback_frame.pack(fill='both', expand=True)
        
        # Using a slightly styled Text widget for feedback
        self.feedback_text = tk.Text(self.feedback_frame, height=10, width=50, state='disabled', wrap='word', 
                                     borderwidth=1, relief="solid", font=('Consolas', 10), padx=8, pady=8, 
                                     background='#F9F9F9', foreground='#333333', selectbackground='#C3D9FF')
        self.feedback_text.pack(fill='both', expand=True)
        
        # Initial check to set the default state
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
        # Dynamic style update is necessary to change the progress bar color
        style = ttk.Style()
        style_name = f"{details['color']}.Custom.Horizontal.TProgressbar"
        style.configure(style_name, background=details['color'])
        self.strength_bar.config(style=style_name, value=details['percent'])
        
        # Update Feedback Text Area
        self.feedback_text.config(state='normal')
        self.feedback_text.delete(1.0, tk.END)
        
        # Insert feedback lines
        if password:
            for line in details['feedback']:
                self.feedback_text.insert(tk.END, line + '\n')
        else:
            self.feedback_text.insert(tk.END, "Start typing your password to see the analysis.")

        self.feedback_text.config(state='disabled')


if __name__ == "__main__":
    # Compile regex patterns for efficiency (as in the original code)
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