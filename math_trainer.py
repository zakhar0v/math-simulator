#!/usr/bin/env python3
"""
Math Trainer - Multiplication of two-digit numbers by one-digit numbers
GUI application with SQLite statistics storage
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import time
from datetime import datetime
from abc import ABC, abstractmethod


# ==================== Database Module ====================
class DatabaseManager:
    """Manages SQLite database for storing statistics"""
    
    def __init__(self, db_path="math_trainer.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for topics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for attempts/statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                problem TEXT NOT NULL,
                user_answer TEXT,
                correct_answer TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                time_taken REAL NOT NULL,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        ''')
        
        # Insert default topic if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO topics (name, description) 
            VALUES (?, ?)
        ''', ("multiplication_2digit_1digit", "Умножение двузначных чисел на однозначное"))
        
        conn.commit()
        conn.close()
    
    def get_topic_id(self, topic_name):
        """Get topic ID by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def add_topic(self, name, description=""):
        """Add a new topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO topics (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            topic_id = cursor.lastrowid
            return topic_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_all_topics(self):
        """Get all available topics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM topics")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def save_attempt(self, topic_id, problem, user_answer, correct_answer, is_correct, time_taken):
        """Save an attempt to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attempts (topic_id, problem, user_answer, correct_answer, is_correct, time_taken)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (topic_id, problem, str(user_answer), str(correct_answer), is_correct, time_taken))
        conn.commit()
        conn.close()
    
    def get_statistics(self, topic_id=None, days=7):
        """Get statistics for a topic or all topics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if topic_id:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_attempts,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                    AVG(time_taken) as avg_time,
                    MIN(time_taken) as min_time,
                    MAX(time_taken) as max_time
                FROM attempts
                WHERE topic_id = ?
                AND attempted_at >= datetime('now', '-' || ? || ' days')
            ''', (topic_id, days))
        else:
            cursor.execute('''
                SELECT 
                    t.name,
                    COUNT(a.id) as total_attempts,
                    SUM(CASE WHEN a.is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                    AVG(a.time_taken) as avg_time
                FROM topics t
                LEFT JOIN attempts a ON t.id = a.topic_id
                AND a.attempted_at >= datetime('now', '-' || ? || ' days')
                GROUP BY t.id
            ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        return results


# ==================== Problem Generator Module ====================
class ProblemGenerator(ABC):
    """Abstract base class for problem generators"""
    
    @abstractmethod
    def generate_problem(self):
        """Generate a new problem, returns (problem_text, correct_answer)"""
        pass
    
    @abstractmethod
    def get_name(self):
        """Get the name of this problem type"""
        pass
    
    @abstractmethod
    def get_description(self):
        """Get description of this problem type"""
        pass


class Multiplication2Digit1Digit(ProblemGenerator):
    """Generator for multiplication of two-digit by one-digit numbers"""
    
    def generate_problem(self):
        """Generate multiplication problem: 2-digit × 1-digit"""
        num1 = random.randint(10, 99)  # Two-digit number
        num2 = random.randint(2, 9)    # One-digit number (excluding 1 for more practice)
        problem = f"{num1} × {num2}"
        answer = num1 * num2
        return problem, answer
    
    def get_name(self):
        return "multiplication_2digit_1digit"
    
    def get_description(self):
        return "Умножение двузначных чисел на однозначное"


# ==================== Main Application ====================
class MathTrainerApp:
    """Main GUI Application for Math Trainer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Математический тренажер")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize components
        self.db = DatabaseManager()
        self.generators = {
            "multiplication_2digit_1digit": Multiplication2Digit1Digit()
        }
        
        self.current_generator = self.generators["multiplication_2digit_1digit"]
        self.current_topic_id = self.db.get_topic_id("multiplication_2digit_1digit")
        self.current_problem = None
        self.current_answer = None
        self.start_time = None
        
        self._setup_ui()
        self._load_new_problem()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Тренажер по математике", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Topic selector frame
        topic_frame = ttk.LabelFrame(main_frame, text="Выберите тему", padding="5")
        topic_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        topic_frame.columnconfigure(1, weight=1)
        
        self.topic_var = tk.StringVar(value="multiplication_2digit_1digit")
        self.topic_combo = ttk.Combobox(
            topic_frame, 
            textvariable=self.topic_var,
            values=list(self.generators.keys()),
            state="readonly",
            width=40
        )
        self.topic_combo.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.topic_combo.bind("<<ComboboxSelected>>", self._on_topic_change)
        
        # New topic button
        new_topic_btn = ttk.Button(
            topic_frame, 
            text="+ Новая тема", 
            command=self._add_new_topic
        )
        new_topic_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        
        # Statistics button
        stats_btn = ttk.Button(
            topic_frame, 
            text="📊 Статистика", 
            command=self._show_statistics
        )
        stats_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Problem display frame
        problem_frame = ttk.LabelFrame(main_frame, text="Задача", padding="10")
        problem_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        problem_frame.columnconfigure(0, weight=1)
        
        self.problem_label = ttk.Label(
            problem_frame, 
            text="", 
            font=("Arial", 24, "bold"),
            justify=tk.CENTER
        )
        self.problem_label.grid(row=0, column=0, pady=20)
        
        # Answer input frame
        answer_frame = ttk.Frame(main_frame)
        answer_frame.grid(row=3, column=0, columnspan=3, pady=10)
        answer_frame.columnconfigure(1, weight=1)
        
        ttk.Label(answer_frame, text="Ваш ответ:", font=("Arial", 12)).grid(
            row=0, column=0, padx=5, sticky=tk.E
        )
        
        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(
            answer_frame, 
            textvariable=self.answer_var, 
            font=("Arial", 14),
            width=15,
            justify=tk.CENTER
        )
        self.answer_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.answer_entry.bind("<Return>", lambda e: self._check_answer())
        self.answer_entry.focus_set()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.check_btn = ttk.Button(
            buttons_frame, 
            text="Проверить", 
            command=self._check_answer,
            width=15
        )
        self.check_btn.grid(row=0, column=0, padx=10)
        
        self.skip_btn = ttk.Button(
            buttons_frame, 
            text="Пропустить", 
            command=self._skip_problem,
            width=15
        )
        self.skip_btn.grid(row=0, column=1, padx=10)
        
        # Result label
        self.result_label = ttk.Label(
            main_frame, 
            text="", 
            font=("Arial", 12),
            foreground="green"
        )
        self.result_label.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Timer label
        self.timer_label = ttk.Label(
            main_frame, 
            text="Время: 0.0 сек", 
            font=("Arial", 10),
            foreground="blue"
        )
        self.timer_label.grid(row=6, column=0, columnspan=3)
        
        # Progress label
        self.progress_label = ttk.Label(
            main_frame, 
            text="", 
            font=("Arial", 10)
        )
        self.progress_label.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        # Update timer periodically
        self._update_timer()
    
    def _load_new_problem(self):
        """Load a new problem"""
        self.current_problem, self.current_answer = self.current_generator.generate_problem()
        self.problem_label.config(text=self.current_problem)
        self.answer_var.set("")
        self.result_label.config(text="")
        self.start_time = time.time()
        self.answer_entry.focus_set()
    
    def _check_answer(self):
        """Check the user's answer"""
        user_input = self.answer_var.get().strip()
        
        if not user_input:
            messagebox.showwarning("Предупреждение", "Введите ответ!")
            return
        
        try:
            user_answer = int(user_input)
        except ValueError:
            messagebox.showerror("Ошибка", "Ответ должен быть числом!")
            return
        
        # Calculate time taken
        time_taken = time.time() - self.start_time
        
        # Check if correct
        is_correct = (user_answer == self.current_answer)
        
        # Save to database
        self.db.save_attempt(
            topic_id=self.current_topic_id,
            problem=self.current_problem,
            user_answer=user_answer,
            correct_answer=self.current_answer,
            is_correct=is_correct,
            time_taken=time_taken
        )
        
        # Display result
        if is_correct:
            self.result_label.config(
                text=f"✓ Правильно! Ответ: {self.current_answer}", 
                foreground="green"
            )
        else:
            self.result_label.config(
                text=f"✗ Неправильно. Правильный ответ: {self.current_answer}", 
                foreground="red"
            )
        
        # Disable check button temporarily and load new problem after delay
        self.check_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        self.root.after(1500, self._after_check)
    
    def _after_check(self):
        """Called after checking answer"""
        self._load_new_problem()
        self.check_btn.config(state="normal")
        self.skip_btn.config(state="normal")
    
    def _skip_problem(self):
        """Skip the current problem"""
        time_taken = time.time() - self.start_time
        
        # Save skipped attempt
        self.db.save_attempt(
            topic_id=self.current_topic_id,
            problem=self.current_problem,
            user_answer="skipped",
            correct_answer=self.current_answer,
            is_correct=False,
            time_taken=time_taken
        )
        
        self.result_label.config(
            text=f"Пропущено. Правильный ответ: {self.current_answer}", 
            foreground="orange"
        )
        
        self.check_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        self.root.after(1500, self._after_check)
    
    def _update_timer(self):
        """Update the timer display"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"Время: {elapsed:.1f} сек")
        self.root.after(100, self._update_timer)
    
    def _on_topic_change(self, event=None):
        """Handle topic change"""
        selected = self.topic_var.get()
        if selected in self.generators:
            self.current_generator = self.generators[selected]
            self.current_topic_id = self.db.get_topic_id(selected)
            self._load_new_problem()
    
    def _add_new_topic(self):
        """Open dialog to add a new topic"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить новую тему")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Название темы:", font=("Arial", 11)).pack(pady=10)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.focus_set()
        
        ttk.Label(dialog, text="Описание:", font=("Arial", 11)).pack(pady=10)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.pack(pady=5)
        
        def save_topic():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Предупреждение", "Введите название темы!")
                return
            
            topic_id = self.db.add_topic(name, desc)
            if topic_id:
                # Note: To fully support new topics, you would need to create
                # a corresponding ProblemGenerator. This is a placeholder.
                messagebox.showinfo(
                    "Успех", 
                    f"Тема '{name}' добавлена в базу данных.\n"
                    f"Для полноценной работы необходимо добавить генератор задач."
                )
                # Refresh topic list
                topics = self.db.get_all_topics()
                topic_names = [t[1] for t in topics]
                self.topic_combo['values'] = topic_names
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Тема с таким названием уже существует!")
        
        ttk.Button(dialog, text="Сохранить", command=save_topic).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack()
    
    def _show_statistics(self):
        """Show statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика")
        stats_window.geometry("500x400")
        stats_window.transient(self.root)
        
        main_frame = ttk.Frame(stats_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_window.columnconfigure(0, weight=1)
        stats_window.rowconfigure(0, weight=1)
        
        ttk.Label(
            main_frame, 
            text="Статистика за последние 7 дней", 
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Get statistics
        stats = self.db.get_statistics(days=7)
        
        # Create treeview for statistics
        columns = ("topic", "total", "correct", "accuracy", "avg_time")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
        
        tree.heading("topic", text="Тема")
        tree.heading("total", text="Всего")
        tree.heading("correct", text="Правильно")
        tree.heading("accuracy", text="Точность %")
        tree.heading("avg_time", text="Ср. время (сек)")
        
        tree.column("topic", width=200)
        tree.column("total", width=80, anchor=tk.CENTER)
        tree.column("correct", width=80, anchor=tk.CENTER)
        tree.column("accuracy", width=100, anchor=tk.CENTER)
        tree.column("avg_time", width=120, anchor=tk.CENTER)
        
        tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Populate data
        for stat in stats:
            if len(stat) == 5:  # All topics query
                topic_name, total, correct, avg_time = stat
                accuracy = (correct / total * 100) if total > 0 else 0
                tree.insert("", tk.END, values=(
                    topic_name,
                    total or 0,
                    correct or 0,
                    f"{accuracy:.1f}%",
                    f"{avg_time:.2f}" if avg_time else "N/A"
                ))
            elif len(stat) == 5:  # Single topic query
                total, correct, avg_time, min_time, max_time = stat
                accuracy = (correct / total * 100) if total > 0 else 0
                tree.insert("", tk.END, values=(
                    self.current_generator.get_description(),
                    total or 0,
                    correct or 0,
                    f"{accuracy:.1f}%",
                    f"{avg_time:.2f}" if avg_time else "N/A"
                ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        
        # Close button
        ttk.Button(
            main_frame, 
            text="Закрыть", 
            command=stats_window.destroy
        ).grid(row=2, column=0, columnspan=2, pady=20)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MathTrainerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
