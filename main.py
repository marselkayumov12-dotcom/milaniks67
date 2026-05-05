import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        # Predefined tasks database
        self.tasks_db = [
            {"name": "Read a technical article", "category": "study"},
            {"name": "Complete one coding exercise", "category": "study"},
            {"name": "Watch a tutorial video", "category": "study"},
            {"name": "Review yesterday's notes", "category": "study"},
            {"name": "Learn 10 new words in a foreign language", "category": "study"},
            {"name": "Do 20 push-ups", "category": "sport"},
            {"name": "Go for a 15-minute walk", "category": "sport"},
            {"name": "Do morning stretching", "category": "sport"},
            {"name": "Take 1000 steps", "category": "sport"},
            {"name": "Do a 5-minute plank", "category": "sport"},
            {"name": "Reply to important emails", "category": "work"},
            {"name": "Plan tomorrow's schedule", "category": "work"},
            {"name": "Update project documentation", "category": "work"},
            {"name": "Organize your workspace", "category": "work"},
            {"name": "Make a to-do list for the week", "category": "work"},
            {"name": "Call a family member", "category": "other"},
            {"name": "Meditate for 10 minutes", "category": "other"},
            {"name": "Read a book for pleasure", "category": "other"},
            {"name": "Listen to a podcast", "category": "other"},
            {"name": "Write down three things you're grateful for", "category": "other"}
        ]

        # History file
        self.history_file = "tasks_history.json"
        self.history = self.load_history()
        self.current_filter = "all"

        # Build GUI
        self.create_widgets()
        self.update_history_display()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="🎲 Random Task Generator", font=("Arial", 20, "bold"), fg="#2E7D32")
        title.pack(pady=15)

        # Current task display frame
        display_frame = tk.Frame(self.root, bg="#F0F0F0", relief=tk.RAISED, bd=2)
        display_frame.pack(pady=20, padx=20, fill=tk.X)

        self.current_task_label = tk.Label(display_frame, text="Click 'Generate Task' to start!", 
                                           font=("Arial", 14), bg="#F0F0F0", wraplength=600, height=4)
        self.current_task_label.pack(pady=30, padx=20)

        # Generate button
        self.generate_btn = tk.Button(self.root, text="🎯 Generate Random Task", 
                                      command=self.generate_random_task,
                                      bg="#4CAF50", fg="white", font=("Arial", 14, "bold"),
                                      width=25, height=2)
        self.generate_btn.pack(pady=10)

        # Add new task section
        add_frame = tk.LabelFrame(self.root, text="➕ Add New Task", font=("Arial", 12, "bold"), padx=10, pady=10)
        add_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(add_frame, text="Task Name:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_task_entry = tk.Entry(add_frame, width=40, font=("Arial", 10))
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Category:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar(value="other")
        category_menu = ttk.Combobox(add_frame, textvariable=self.category_var, 
                                     values=["study", "sport", "work", "other"], width=15)
        category_menu.grid(row=0, column=3, padx=5, pady=5)

        self.add_btn = tk.Button(add_frame, text="Add Task", command=self.add_new_task,
                                 bg="#2196F3", fg="white", font=("Arial", 10))
        self.add_btn.grid(row=0, column=4, padx=10, pady=5)

        # Filter section
        filter_frame = tk.LabelFrame(self.root, text="🔍 Filter History", font=("Arial", 12, "bold"), padx=10, pady=10)
        filter_frame.pack(pady=10, padx=20, fill=tk.X)

        self.filter_var = tk.StringVar(value="all")
        filter_all = tk.Radiobutton(filter_frame, text="All Tasks", variable=self.filter_var, 
                                    value="all", command=self.apply_filter)
        filter_study = tk.Radiobutton(filter_frame, text="📚 Study", variable=self.filter_var, 
                                      value="study", command=self.apply_filter)
        filter_sport = tk.Radiobutton(filter_frame, text="🏃 Sport", variable=self.filter_var, 
                                      value="sport", command=self.apply_filter)
        filter_work = tk.Radiobutton(filter_frame, text="💼 Work", variable=self.filter_var, 
                                     value="work", command=self.apply_filter)
        filter_other = tk.Radiobutton(filter_frame, text="🎨 Other", variable=self.filter_var, 
                                      value="other", command=self.apply_filter)

        filter_all.pack(side=tk.LEFT, padx=10)
        filter_study.pack(side=tk.LEFT, padx=10)
        filter_sport.pack(side=tk.LEFT, padx=10)
        filter_work.pack(side=tk.LEFT, padx=10)
        filter_other.pack(side=tk.LEFT, padx=10)

        # History section
        history_frame = tk.LabelFrame(self.root, text="📜 Task History", font=("Arial", 12, "bold"), padx=10, pady=10)
        history_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # History listbox with scrollbar
        listbox_frame = tk.Frame(history_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                          font=("Courier", 10), height=12)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # History control buttons
        btn_frame = tk.Frame(history_frame)
        btn_frame.pack(pady=10)

        self.save_btn = tk.Button(btn_frame, text="💾 Save History", command=self.save_history,
                                  bg="#FF9800", fg="white", font=("Arial", 10), width=15)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.load_btn = tk.Button(btn_frame, text="📂 Load History", command=self.load_history_from_file,
                                  bg="#9C27B0", fg="white", font=("Arial", 10), width=15)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(btn_frame, text="🗑️ Clear History", command=self.clear_history,
                                   bg="#F44336", fg="white", font=("Arial", 10), width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Statistics label
        self.stats_label = tk.Label(self.root, text="", font=("Arial", 9), fg="gray")
        self.stats_label.pack(pady=5)

    def generate_random_task(self):
        """Generate a random task from the database"""
        if not self.tasks_db:
            messagebox.showwarning("No Tasks", "No tasks available! Please add some tasks first.")
            return

        # Filter tasks by current filter for generation
        if self.current_filter != "all":
            available_tasks = [task for task in self.tasks_db if task["category"] == self.current_filter]
            if not available_tasks:
                messagebox.showinfo("No Tasks", f"No tasks available in '{self.current_filter}' category. Generating from all tasks.")
                available_tasks = self.tasks_db
        else:
            available_tasks = self.tasks_db

        selected_task = random.choice(available_tasks)
        
        # Update display
        category_emoji = {
            "study": "📚", "sport": "🏃", "work": "💼", "other": "🎨"
        }
        emoji = category_emoji.get(selected_task["category"], "📌")
        self.current_task_label.config(text=f"{emoji} {selected_task['name']}\n\nCategory: {selected_task['category'].upper()}", 
                                       font=("Arial", 14, "bold"), fg="#2E7D32")

        # Add to history
        self.add_to_history(selected_task["name"], selected_task["category"])

    def add_to_history(self, task_name, category):
        """Add generated task to history"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": task_name,
            "category": category
        }
        self.history.append(entry)
        self.update_history_display()
        self.save_history()  # Auto-save

    def update_history_display(self):
        """Update the history listbox based on current filter"""
        self.history_listbox.delete(0, tk.END)
        
        filtered_history = self.history
        if self.current_filter != "all":
            filtered_history = [h for h in self.history if h["category"] == self.current_filter]
        
        # Reverse to show newest first
        for entry in reversed(filtered_history):
            display_text = f"[{entry['date']}] {entry['category'].upper()}: {entry['task']}"
            self.history_listbox.insert(tk.END, display_text)
        
        # Update statistics
        total_count = len(self.history)
        filtered_count = len(filtered_history)
        
        if self.current_filter == "all":
            self.stats_label.config(text=f"Total tasks generated: {total_count}")
        else:
            self.stats_label.config(text=f"Showing {filtered_count} of {total_count} tasks (filter: {self.current_filter})")

    def apply_filter(self):
        """Apply the selected filter"""
        self.current_filter = self.filter_var.get()
        self.update_history_display()

    def add_new_task(self):
        """Add a new task to the database"""
        task_name = self.new_task_entry.get().strip()
        category = self.category_var.get()
        
        # Validation
        if not task_name:
            messagebox.showerror("Input Error", "Task name cannot be empty!")
            return
        
        if not category or category not in ["study", "sport", "work", "other"]:
            messagebox.showerror("Input Error", "Please select a valid category!")
            return
        
        # Add to database
        self.tasks_db.append({"name": task_name, "category": category})
        self.new_task_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Task '{task_name}' added to '{category}' category!")

    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save history: {str(e)}")

    def load_history_from_file(self):
        """Load history from JSON file"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            self.update_history_display()
            messagebox.showinfo("Success", f"History loaded from {self.history_file}")
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "No history file found. Starting empty.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load history: {str(e)}")

    def load_history(self):
        """Load initial history from file if exists"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all task history?"):
            self.history = []
            self.update_history_display()
            self.save_history()
            messagebox.showinfo("Success", "History cleared!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()
