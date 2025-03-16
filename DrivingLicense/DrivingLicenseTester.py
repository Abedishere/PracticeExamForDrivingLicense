import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
import os
from datetime import timedelta


def resize_image(img, max_size):
    """Resize image maintaining aspect ratio."""
    width, height = img.size
    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)

    return img.resize((new_width, new_height), Image.LANCZOS)


class ModernQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Driving Exam Quiz")
        self.geometry("1000x750")

        # Set application icon (if available)
        try:
            self.iconphoto(True, tk.PhotoImage(file="icon.png"))
        except:
            pass

        # Custom colors - Dark mode
        self.colors = {
            "primary": "#3498db",  # Blue
            "secondary": "#2ecc71",  # Green
            "accent": "#e74c3c",  # Red
            "bg": "#1e1e2e",  # Dark background
            "card_bg": "#2d2d3f",  # Slightly lighter background for cards
            "text": "#ffffff",  # White text
            "light_text": "#a0a0a0",  # Light gray text
            "border": "#3d3d4f"  # Slightly lighter border
        }

        # Configure root window background
        self.configure(bg=self.colors["bg"])

        # Custom font styles
        self.fonts = {
            "heading": ("Helvetica", 20, "bold"),
            "subheading": ("Helvetica", 16),
            "body": ("Helvetica", 14),
            "small": ("Helvetica", 12)
        }

        # 1) Get our 30 random questions (10 from each category)
        self.questions = get_questions()

        self.current_question = 0
        self.user_answers = []  # store the user's selected answer indices
        self.score = 0
        self.time_left = 15 * 60  # 15 minutes in seconds

        # Keep references to PhotoImages to avoid garbage collection
        self.photos = []

        self.create_widgets()
        self.display_question()
        self.update_timer()

    def create_widgets(self):
        """Create all UI widgets with dark mode styling"""
        # Create main container frame
        self.main_frame = tk.Frame(self, bg=self.colors["bg"], padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # Header frame with timer and progress info
        self.header_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        self.header_frame.pack(fill="x", pady=(0, 20))

        # Quiz title
        self.title_label = tk.Label(
            self.header_frame,
            text="Driving License Exam",
            font=self.fonts["heading"],
            bg=self.colors["bg"],
            fg=self.colors["primary"]
        )
        self.title_label.pack(side="left")

        # Timer display with icon
        self.timer_frame = tk.Frame(self.header_frame, bg=self.colors["bg"])
        self.timer_frame.pack(side="right")

        self.timer_label = tk.Label(
            self.timer_frame,
            text="15:00",
            font=self.fonts["subheading"],
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        self.timer_label.pack(side="right")

        self.timer_icon_label = tk.Label(
            self.timer_frame,
            text="⏱️ ",
            font=self.fonts["subheading"],
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        self.timer_icon_label.pack(side="right", padx=(0, 5))

        # Progress bar and question counter
        self.progress_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        self.progress_frame.pack(fill="x", pady=(0, 15))

        self.question_counter = tk.Label(
            self.progress_frame,
            text="Question 1/30",
            font=self.fonts["small"],
            bg=self.colors["bg"],
            fg=self.colors["light_text"]
        )
        self.question_counter.pack(side="left", anchor="w", pady=(0, 5))

        # Configure dark theme for ttk widgets (progressbar)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar",
                        thickness=10,
                        background=self.colors["primary"],
                        troughcolor=self.colors["border"])

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=960,
            mode="determinate",
            style="TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))

        # Question card with shadow effect
        self.card_frame = tk.Frame(
            self.main_frame,
            bg=self.colors["card_bg"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            padx=25,
            pady=25
        )
        self.card_frame.pack(fill="both", expand=True)

        # Category label
        self.category_label = tk.Label(
            self.card_frame,
            text="Category: Signs",
            font=self.fonts["small"],
            bg=self.colors["card_bg"],
            fg=self.colors["light_text"]
        )
        self.category_label.pack(anchor="w")

        # Question text
        self.question_label = tk.Label(
            self.card_frame,
            text="",
            font=self.fonts["subheading"],
            wraplength=900,
            justify="left",
            bg=self.colors["card_bg"],
            fg=self.colors["text"]
        )
        self.question_label.pack(pady=(10, 20), anchor="w")

        # Image frame (for sign images)
        self.image_frame = tk.Frame(self.card_frame, bg=self.colors["card_bg"])
        self.image_frame.pack(fill="x", pady=(0, 20))

        self.image_label = tk.Label(self.image_frame, bg=self.colors["card_bg"])
        self.image_label.pack()

        # Options frame
        self.options_frame = tk.Frame(self.card_frame, bg=self.colors["card_bg"])
        self.options_frame.pack(fill="x", pady=(0, 20))

        # Radio button variable
        self.var = tk.IntVar(value=-1)  # -1 = no selection

        # Custom radio buttons with modern styling
        self.radio_buttons = []
        for i in range(3):
            option_frame = tk.Frame(
                self.options_frame,
                bg=self.colors["card_bg"],
                highlightbackground=self.colors["border"],
                highlightthickness=1,
                padx=15,
                pady=15,
                cursor="hand2"  # Hand cursor to indicate clickable
            )
            option_frame.pack(fill="x", pady=8)

            # Store the option index for click events
            option_frame.option_index = i

            # Bind click event to the entire frame
            option_frame.bind("<Button-1>", self.option_frame_clicked)

            rb = tk.Radiobutton(
                option_frame,
                variable=self.var,
                value=i,
                bg=self.colors["card_bg"],
                activebackground=self.colors["card_bg"],
                fg=self.colors["text"],
                selectcolor=self.colors["card_bg"]
            )
            rb.pack(side="left", padx=(0, 10))

            # Also bind the radiobutton to update the parent frame
            rb.bind("<Button-1>", lambda event, idx=i: self.option_frame_clicked(event, idx))

            option_text = tk.Label(
                option_frame,
                text="Option text goes here",
                font=self.fonts["body"],
                wraplength=850,
                justify="left",
                bg=self.colors["card_bg"],
                fg=self.colors["text"],
                cursor="hand2"  # Hand cursor to indicate clickable
            )
            option_text.pack(side="left", fill="x", expand=True)

            # Also bind the label to update the parent frame
            option_text.bind("<Button-1>", lambda event, idx=i: self.option_frame_clicked(event, idx))

            self.radio_buttons.append((rb, option_text, option_frame))

        # Navigation buttons frame
        self.button_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        self.button_frame.pack(fill="x", pady=(20, 0))

        # Next button
        self.next_button = tk.Button(
            self.button_frame,
            text="Next Question",
            font=self.fonts["body"],
            bg=self.colors["primary"],
            fg=self.colors["text"],
            activebackground=self.colors["primary"],
            activeforeground=self.colors["text"],
            padx=20,
            pady=10,
            bd=0,
            cursor="hand2",
            command=self.next_question,
            state="disabled"
        )
        self.next_button.pack(side="right")

    def option_frame_clicked(self, event, idx=None):
        """Handle clicks on the option frame, label, or radio button"""
        # If idx is provided directly, use it, otherwise get it from the widget
        if idx is None:
            # Get the option index from the clicked widget or its parent
            widget = event.widget
            if hasattr(widget, 'option_index'):
                idx = widget.option_index
            else:
                # Try to find parent with option_index
                for parent in (widget.master, widget.master.master):
                    if hasattr(parent, 'option_index'):
                        idx = parent.option_index
                        break

        # Set the radio button value
        self.var.set(idx)

        # Update the UI
        self.option_selected()

    def update_timer(self):
        """Updates the countdown timer every second with format MM:SS."""
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

        # Change timer color to red when less than 2 minutes remaining
        if self.time_left <= 120:
            self.timer_label.config(fg=self.colors["accent"])
            self.timer_icon_label.config(fg=self.colors["accent"])

        if self.time_left <= 0:
            messagebox.showinfo("Time's Up!", "Your time is up! Let's see how you did.")
            self.finish_quiz(time_up=True)
        else:
            self.time_left -= 1
            self.after(1000, self.update_timer)

    def display_question(self):
        """Displays the current question with modern styling."""
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]

            # Update progress indicators
            progress_percent = (self.current_question / len(self.questions)) * 100
            self.progress_bar["value"] = progress_percent
            self.question_counter.config(text=f"Question {self.current_question + 1}/{len(self.questions)}")

            # Update category
            self.category_label.config(text=f"Category: {q['category']}")

            # Clear previous selection
            self.var.set(-1)
            self.next_button.config(state="disabled")

            # Reset option styling - both frame border and text color
            for rb, label, frame in self.radio_buttons:
                frame.config(highlightbackground=self.colors["border"])
                label.config(fg=self.colors["text"])

            # Show question text
            self.question_label.config(text=q["question"])

            # Show sign image if category is "Signs" and image path is set
            if q["category"] == "Signs" and q["image"]:
                if os.path.exists(q["image"]):
                    try:
                        img = Image.open(q["image"])
                        # Resize image maintaining aspect ratio
                        img = resize_image(img, 300)
                        photo = ImageTk.PhotoImage(img)
                        self.photos.append(photo)  # store reference
                        self.image_label.config(image=photo)
                        self.image_label.pack(pady=(0, 20))
                    except Exception as e:
                        self.image_label.config(image="", text=f"Error loading image")
                        print(f"Image error: {e}")
                else:
                    self.image_label.config(image="", text="")
                    self.image_label.pack_forget()
            else:
                # No image for this question
                self.image_label.config(image="", text="")
                self.image_label.pack_forget()

            # Update the radio button text
            for i, (rb, label, frame) in enumerate(self.radio_buttons):
                label.config(text=q["options"][i])

        else:
            # No more questions
            self.finish_quiz()

    def option_selected(self):
        """Highlights the selected option and enables Next button."""
        selected = self.var.get()
        if selected >= 0:
            # Highlight selected option
            for i, (rb, label, frame) in enumerate(self.radio_buttons):
                if i == selected:
                    frame.config(highlightbackground=self.colors["primary"])
                    label.config(fg=self.colors["primary"])
                else:
                    frame.config(highlightbackground=self.colors["border"])
                    label.config(fg=self.colors["text"])

            self.next_button.config(state="normal")

    def next_question(self):
        """Saves answer, checks correctness, and goes to next question."""
        selected = self.var.get()
        self.user_answers.append(selected)

        # Check if correct
        correct_index = self.questions[self.current_question]["correct"]
        if selected == correct_index:
            self.score += 1

        self.current_question += 1
        self.display_question()

    def finish_quiz(self, time_up=False):
        """Shows results page with dark mode styling."""
        # Remove all existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Update statistics for multiple attempts
        if not hasattr(self, 'total_attempts'):
            self.total_attempts = 1
            self.successful_attempts = 1 if self.score >= len(self.questions) * 0.8 else 0
        else:
            self.total_attempts += 1
            if self.score >= len(self.questions) * 0.8:
                self.successful_attempts += 1

        # Create results container
        results_frame = tk.Frame(self, bg=self.colors["bg"], padx=30, pady=30)
        results_frame.pack(fill="both", expand=True)

        # Results header
        header_frame = tk.Frame(results_frame, bg=self.colors["bg"])
        header_frame.pack(fill="x", pady=(0, 30))

        # Pass/Fail status
        pass_threshold = 0.8  # 24/30
        passed = self.score >= len(self.questions) * pass_threshold

        status_text = "PASSED" if passed else "FAILED"
        status_color = self.colors["secondary"] if passed else self.colors["accent"]

        status_label = tk.Label(
            header_frame,
            text=status_text,
            font=("Helvetica", 24, "bold"),
            bg=self.colors["bg"],
            fg=status_color
        )
        status_label.pack(anchor="center")

        # Score display
        score_label = tk.Label(
            header_frame,
            text=f"Your Score: {self.score}/{len(self.questions)} ({int(self.score / len(self.questions) * 100)}%)",
            font=self.fonts["heading"],
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        score_label.pack(anchor="center", pady=(10, 0))

        # Display session statistics only if there's been more than one attempt
        if self.total_attempts > 1:
            success_rate = (self.successful_attempts / self.total_attempts) * 100
            stats_label = tk.Label(
                header_frame,
                text=f"Session Statistics: {self.successful_attempts} passed out of {self.total_attempts} attempts ({int(success_rate)}%)",
                font=self.fonts["body"],
                bg=self.colors["bg"],
                fg=self.colors["text"]
            )
            stats_label.pack(anchor="center", pady=(5, 0))

        if time_up:
            time_label = tk.Label(
                header_frame,
                text="Time Expired",
                font=self.fonts["small"],
                bg=self.colors["bg"],
                fg=self.colors["accent"]
            )
            time_label.pack(anchor="center", pady=(5, 0))

        # Score visualization
        vis_frame = tk.Frame(results_frame, bg=self.colors["card_bg"], padx=20, pady=20)
        vis_frame.pack(fill="x", pady=(0, 20))

        # Create custom progress bar for score visualization
        vis_canvas = tk.Canvas(
            vis_frame,
            width=900,
            height=30,
            bg=self.colors["border"],
            highlightthickness=0
        )
        vis_canvas.pack(fill="x", pady=(10, 20))

        # Draw score bar
        score_width = int((self.score / len(self.questions)) * 900)
        vis_canvas.create_rectangle(0, 0, score_width, 30, fill=status_color, outline="")

        # Draw passing threshold marker
        threshold_pos = int(pass_threshold * 900)
        vis_canvas.create_line(threshold_pos, 0, threshold_pos, 30, fill="#ffffff", width=2, dash=(5, 5))

        # Results breakdown - create a scrollable area for missed questions
        results_label = tk.Label(
            results_frame,
            text="Questions Review (Incorrect First)",
            font=self.fonts["subheading"],
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        results_label.pack(anchor="w", pady=(10, 5))

        # Create scrollable canvas for review of questions
        canvas_frame = tk.Frame(results_frame, bg=self.colors["card_bg"], bd=1, relief="solid")
        canvas_frame.pack(fill="both", expand=True)

        # Add scrollbar with dark styling
        style = ttk.Style()
        style.configure("Dark.Vertical.TScrollbar",
                        background=self.colors["primary"],
                        troughcolor=self.colors["card_bg"],
                        arrowcolor=self.colors["text"])

        # Add scrollbar
        scrollbar = ttk.Scrollbar(canvas_frame, style="Dark.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")

        # Create canvas
        canvas = tk.Canvas(
            canvas_frame,
            bg=self.colors["card_bg"],
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        # Configure scrollbar
        scrollbar.config(command=canvas.yview)

        # Create frame inside canvas for questions
        inner_frame = tk.Frame(canvas, bg=self.colors["card_bg"], padx=20, pady=20)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Add mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows and MacOS
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux

        # Sort questions: incorrect first, then correct
        question_indices = list(range(len(self.questions)))

        # Function to determine if question was answered correctly
        def was_correct(idx):
            if idx >= len(self.user_answers):
                return False  # Unanswered questions are treated as incorrect
            return self.user_answers[idx] == self.questions[idx]['correct']

        # Sort indices by correctness (incorrect first)
        question_indices.sort(key=lambda idx: was_correct(idx))

        # Add all questions to the review section in the sorted order
        for idx in question_indices:
            q = self.questions[idx]
            i = idx  # Preserve original question number

            question_card = tk.Frame(
                inner_frame,
                bg=self.colors["card_bg"],
                bd=0,
                highlightbackground=self.colors["border"],
                highlightthickness=1,
                padx=15,
                pady=15
            )
            question_card.pack(fill="x", pady=10)

            # Question header with number and category
            header_frame = tk.Frame(question_card, bg=self.colors["card_bg"])
            header_frame.pack(fill="x")

            q_num = tk.Label(
                header_frame,
                text=f"Question {i + 1}",
                font=self.fonts["body"],
                bg=self.colors["card_bg"],
                fg=self.colors["primary"]
            )
            q_num.pack(side="left")

            category = tk.Label(
                header_frame,
                text=f"{q['category']}",
                font=self.fonts["small"],
                bg=self.colors["card_bg"],
                fg=self.colors["light_text"]
            )
            category.pack(side="right")

            # Status indicator
            if i < len(self.user_answers):
                selected = self.user_answers[i]
                is_correct = selected == q['correct']
                status_text = "✓ Correct" if is_correct else "✗ Incorrect"
                status_color = self.colors["secondary"] if is_correct else self.colors["accent"]
            else:
                status_text = "Not Answered"
                status_color = self.colors["accent"]  # Treat unanswered as incorrect

            status = tk.Label(
                question_card,
                text=status_text,
                font=self.fonts["small"],
                bg=self.colors["card_bg"],
                fg=status_color
            )
            status.pack(anchor="w", pady=(5, 10))

            # Question text
            q_text = tk.Label(
                question_card,
                text=q["question"],
                font=self.fonts["body"],
                wraplength=800,
                justify="left",
                bg=self.colors["card_bg"],
                fg=self.colors["text"]
            )
            q_text.pack(anchor="w", pady=(0, 10))

            # Show image if there was one
            if q["category"] == "Signs" and q["image"] and os.path.exists(q["image"]):
                try:
                    img = Image.open(q["image"])
                    img = self.resize_image(img, 150)  # Smaller for review
                    photo = ImageTk.PhotoImage(img)
                    self.photos.append(photo)
                    img_label = tk.Label(question_card, image=photo, bg=self.colors["card_bg"])
                    img_label.pack(anchor="w", pady=(0, 10))
                except Exception:
                    pass

            # Show all answer options, highlighting correct and user answers
            for j, option_text in enumerate(q["options"]):
                # Determine option styling based on correctness
                if j == q["correct"]:
                    # Correct answer
                    bg_color = "#1e392a"  # Dark green
                    fg_color = self.colors["secondary"]
                    prefix = "✓ "
                elif i < len(self.user_answers) and j == self.user_answers[i] and j != q["correct"]:
                    # User's incorrect answer
                    bg_color = "#3d1e1e"  # Dark red
                    fg_color = self.colors["accent"]
                    prefix = "✗ "
                else:
                    # Other options
                    bg_color = self.colors["card_bg"]
                    fg_color = self.colors["text"]
                    prefix = ""

                option_frame = tk.Frame(
                    question_card,
                    bg=bg_color,
                    padx=10,
                    pady=5
                )
                option_frame.pack(fill="x", pady=2)

                option_label = tk.Label(
                    option_frame,
                    text=f"{prefix}{option_text}",
                    font=self.fonts["small"],
                    wraplength=800,
                    justify="left",
                    bg=bg_color,
                    fg=fg_color,
                    padx=5,
                    pady=5
                )
                option_label.pack(anchor="w")

        # Update the canvas scroll region after all items added
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Unbind mousewheel on exit
        def _on_frame_destroy(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        results_frame.bind("<Destroy>", _on_frame_destroy)

        # Create button frame at the bottom
        button_frame = tk.Frame(results_frame, bg=self.colors["bg"])
        button_frame.pack(pady=20, fill="x")

        # Try Again button (same questions) - LEFT SIDE
        retry_button = tk.Button(
            button_frame,
            text="Retry These Questions",
            font=self.fonts["body"],
            bg=self.colors["primary"],
            fg=self.colors["text"],
            activebackground=self.colors["primary"],
            activeforeground=self.colors["text"],
            padx=20,
            pady=10,
            bd=0,
            cursor="hand2",
            command=self.retry_quiz
        )
        retry_button.pack(side="left", padx=(0, 10))

        # New Test button (new questions) - RIGHT SIDE
        # Check if restart_quiz exists first and use that directly if it does
        new_quiz_command = self.restart_quiz if hasattr(self, 'restart_quiz') else self.new_quiz

        new_test_button = tk.Button(
            button_frame,
            text="Start New Quiz",
            font=self.fonts["body"],
            bg=self.colors["secondary"],
            fg=self.colors["text"],
            activebackground=self.colors["secondary"],
            activeforeground=self.colors["text"],
            padx=20,
            pady=10,
            bd=0,
            cursor="hand2",
            command=new_quiz_command
        )
        new_test_button.pack(side="right", padx=(10, 0))

    def retry_quiz(self):
        """Restart the quiz with the same questions."""
        # Destroy all widgets first
        for widget in self.winfo_children():
            widget.destroy()

        # Reset variables but keep the same questions
        self.current_question = 0
        self.user_answers = []
        self.score = 0
        self.time_left = 15 * 60
        self.photos = []

        # Recreate UI and start again
        self.create_widgets()
        self.display_question()
        self.update_timer()

    def new_quiz(self):
        """Start a fresh quiz with new questions."""
        try:
            # Destroy all widgets first
            for widget in self.winfo_children():
                widget.destroy()

            # Reset all variables
            self.current_question = 0
            self.user_answers = []
            self.score = 0
            self.time_left = 15 * 60
            self.photos = []

            # Rather than directly calling load_questions, use restart_quiz if it exists
            # This is likely what the New Test button was originally using
            if hasattr(self, 'restart_quiz'):
                self.restart_quiz()
            else:
                # Fallback if restart_quiz doesn't exist
                self.questions = self.get_new_questions()  # TODO: MAKE THIS METHOD
                self.create_widgets()
                self.display_question()
                self.update_timer()
        except Exception as e:
            # Show error message instead of blank screen
            error_label = tk.Label(
                self,
                text=f"Error starting new quiz: {str(e)}\nPlease restart the application.",
                font=("Helvetica", 14),
                bg=self.colors["bg"],
                fg=self.colors["accent"],
                padx=20,
                pady=20
            )
            error_label.pack(expand=True)

    def get_new_questions(self):
        """
        Generates a new set of random questions for the quiz.
        Returns a list of question dictionaries.
        """
        # This method will call the existing get_questions() function
        # which appears to be a standalone function that returns all available questions

        # Get all available questions
        all_questions = get_questions()

        # Determine how many questions the quiz should have
        # Using the length of the previous quiz if available
        target_question_count = len(self.questions) if hasattr(self, 'questions') else 30

        # Import random for shuffling
        import random

        # Create a copy of all questions and shuffle them
        available_questions = all_questions.copy()
        random.shuffle(available_questions)

        # Select questions up to the target count
        # If there aren't enough questions, take all available ones
        new_questions = available_questions[:target_question_count]

        # If we need to maintain category distribution similar to the original quiz:
        # (This is optional but would make the quiz structure more consistent)
        if hasattr(self, 'questions') and len(new_questions) < len(available_questions):
            # Count categories in the original quiz
            original_categories = {}
            for q in self.questions:
                category = q['category']
                if category not in original_categories:
                    original_categories[category] = 0
                original_categories[category] += 1

            # Try to match the original distribution
            selected_questions = []
            remaining_by_category = original_categories.copy()

            # First pass: select questions by category to match distribution
            for q in available_questions:
                category = q['category']
                if category in remaining_by_category and remaining_by_category[category] > 0:
                    selected_questions.append(q)
                    remaining_by_category[category] -= 1

                # Stop if we've selected enough questions
                if len(selected_questions) >= target_question_count:
                    break

            # If we still need more questions, add random ones
            if len(selected_questions) < target_question_count:
                # Get questions not already selected
                unused_questions = [q for q in available_questions if q not in selected_questions]
                random.shuffle(unused_questions)
                selected_questions.extend(unused_questions[:target_question_count - len(selected_questions)])

            # If we've successfully created a category-balanced set, use it
            if len(selected_questions) == target_question_count:
                new_questions = selected_questions

        return new_questions


def get_questions():
    """
    Returns 30 questions total by randomly sampling:
      - 10 from the 'Signs' pool
      - 10 from the 'Safety' pool
      - 10 from the 'Law' pool
    Then shuffles them.

    Make sure each pool has at least 10 questions.
    Update the 'image' paths to match your actual file structure (e.g. 'images/17.jpg').
    """
    # ---------------------- SIGN QUESTIONS POOL ----------------------
    # You can keep expanding this list with the rest of your sign questions (IDs 120+).
    sign_pool = [
        # Example from earlier IDs (1,3,4,5,6,...):
        {
            # ID 120 (Sign 1)
            "question": "What does this sign mean? - C:\\DTA\\signs\\1.jpg",
            "options": [
                "Caution, slippery road ahead",
                "Caution, speed bumps ahead",
                "Caution, uneven road ahead"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/1.jpg"
        },
        # ID 121 (Sign 3)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\3.jpg",
            "options": [
                "Roundabout ahead",
                "Caution, left bend ahead",
                "Caution, right bend ahead"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/3.jpg"
        },
        # ID 122 (Sign 4)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\4.jpg",
            "options": [
                "Vehicles can go left",
                "Caution, left bend ahead",
                "Caution, right bend ahead"
            ],
            "correct": 1,
            "category": "Signs",
            "image": "images/4.jpg"
        },
        # ID 123 (Sign 5)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\5.jpg",
            "options": [
                "Caution, double lane road",
                "Caution, double bend ahead, first one to the left",
                "Caution, double bend ahead, first one to the right"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/5.jpg"
        },
        # ID 124 (Sign 6)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\6.jpg",
            "options": [
                "Caution, double lane road",
                "Caution, double bend ahead, first one to the left",
                "Caution, double bend ahead, first one to the right"
            ],
            "correct": 1,
            "category": "Signs",
            "image": "images/6.jpg"
        },
        # ID 125 (Sign 10)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\10.jpg",
            "options": [
                "Caution, narrow road ahead",
                "Caution, dangerous slope",
                "Caution, slippery road ahead"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/10.jpg"
        },
        # ID 126 (Sign 11)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\11.jpg",
            "options": [
                "Unsecure crossing",
                "No entry",
                "Caution, students or school"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/11.jpg"
        },
        # ID 127 (Sign 13)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\13.jpg",
            "options": [
                "Stray animals",
                "Animals not allowed",
                "Caution, animals"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/13.jpg"
        },
        # ID 128 (Sign 14)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\14.jpg",
            "options": [
                "Travel on the right side of the road",
                "Caution, intersection without right of way",
                "Caution, double lane road"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/14.jpg"
        },
        # ID 129 (Sign 15)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\15.jpg",
            "options": [
                "Caution, various dangers",
                "You cannot turn",
                "Caution, roundabout ahead"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/15.jpg"
        },
        # ID 130 (Sign 17)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\17.jpg",
            "options": [
                "Caution, intersection with no right of way",
                "Caution, vehicles coming from the opposite direction have the right of way",
                "Caution, intersection ahead"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/17.jpg"
        },
        # ID 131 (Sign 18)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\18.jpg",
            "options": [
                "Merging with a freeway",
                "Caution, intersection with no right of way",
                "Caution, vehicles coming from the opposite direction have the right of way"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/18.jpg"
        },
        # ID 132 (Sign 19)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\19.jpg",
            "options": [
                "Caution, intersection on the right",
                "Caution, intersection with no right of way",
                "Caution, vehicles coming from the opposite direction have the right of way"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/19.jpg"
        },
        # ID 133 (Sign 24)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\24.jpg",
            "options": [
                "One-minute parking",
                "End of speed limit",
                "Road with priority right of way"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/24.jpg"
        },
        # ID 134 (Sign 25)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\25.jpg",
            "options": [
                "Not reserved for pedestrians",
                "No entry for pedestrians",
                "Caution, pedestrian crossing"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/25.jpg"
        },
        # ID 135 (Sign 26)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\26.jpg",
            "options": [
                "Trolley crossing",
                "No entry for bikes",
                "Caution, cycles crossing"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/26.jpg"
        },
        # ID 136 (Sign 29)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\29.jpg",
            "options": [
                "Caution, wide road",
                "Caution, narrow road on the left",
                "Caution, narrow road ahead"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/29.jpg"
        },
        # ID 137 (Sign 30)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\30.jpg",
            "options": [
                "Priority to the right",
                "Narrow road on the right",
                "Caution, narrow road on the left"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/30.jpg"
        },
        # ID 138 (Sign 31)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\31.jpg",
            "options": [
                "End of priority",
                "Caution, narrow road on the right",
                "Caution, vehicles coming from the opposite direction have the right of way"
            ],
            "correct": 1,
            "category": "Signs",
            "image": "images/31.jpg"
        },
        # ID 139 (Sign 32)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\32.jpg",
            "options": [
                "Mountainous area",
                "Caution, falling or fallen rocks ahead",
                "Caution, narrow road ahead"
            ],
            "correct": 1,
            "category": "Signs",
            "image": "images/32.jpg"
        },
        # ID 140 (Sign 33)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\33.jpg",
            "options": [
                "No entry to all types of motor vehicles",
                "Caution, electrical signs",
                "Caution, roundabout ahead"
            ],
            "correct": 0,
            "category": "Signs",
            "image": "images/33.jpg"
        },
        # ID 141 (Sign 37)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\37.jpg",
            "options": [
                "No entry",
                "Give way - priority road ahead",
                "Caution, various dangers"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/37.jpg"
        },
        # ID 142 (Sign 38)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\38.jpg",
            "options": [
                "No entry",
                "Give way - priority road ahead",
                "Caution, various dangers"
            ],
            "correct": 1,
            "category": "Signs",
            "image": "images/38.jpg"
        },
        # ID 143 (Sign 39)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\39.jpg",
            "options": [
                "No entry",
                "End of priority",
                "Caution, vehicles coming from the opposite direction have the right of way"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/39.jpg"
        },
        # ID 144 (Sign 40)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\40.jpg",
            "options": [
                "No overtaking for all kinds of vehicles",
                "End of priority",
                "Caution, vehicles coming from the opposite direction have the right of way"
            ],
            "correct": 0,
            "category": "Signs",
            "image": "images/40.jpg"
        },
        # ID 145 (Sign 41)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\41.jpg",
            "options": [
                "One lane road",
                "No entry",
                "Stop"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/41.jpg"
        },
        # ID 146 (Sign 42)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\42.jpg",
            "options": [
                "One Lane road",
                "No parking",
                "No entry for all motor vehicles"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/42.jpg"
        },
        # ID 147 (Sign 43)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\43.jpg",
            "options": [
                "Various dangers",
                "No parking",
                "No entry"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/43.jpg"
        },
        # ID 148 (Sign 44)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\44.jpg",
            "options": [
                "No overtaking allowed for trucks",
                "No overtaking allowed for all kinds of vehicles",
                "No entry"
            ],
            "correct": 0,
            "category": "Signs",
            "image": "images/44.jpg"
        },
        # ID 149 (Sign 45)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\45.jpg",
            "options": [
                "Upper speed limit: 30 km/hour",
                "Lower Speed limit: 80 km/hour",
                "Give way - priority road ahead"
            ],
            "correct": 0,
            "category": "Signs",
            "image": "images/45.jpg"
        },
        # ID 150 (Sign 46)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\46.jpg",
            "options": [
                "Theatre",
                "No parking",
                "You are not allowed to sound your horn"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/46.jpg"
        },
        # ID 151 (Sign 47)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\47.jpg",
            "options": [
                "Road reserved for trucks",
                "Trucks can overtake",
                "Trucks cannot overtake"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/47.jpg"
        },
        # ID 152 (Sign 48)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\48.jpg",
            "options": [
                "Animal carts allowed",
                "No entry for pedestrians",
                "No entry for animal carts"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/48.jpg"
        },
        # ID 153 (Sign 49)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\49.jpg",
            "options": [
                "No entry to all types of motor vehicles",
                "Caution, Lane reserved for pedestrians",
                "No entry for pedestrians"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/49.jpg"
        },
        # ID 154 (Sign 50)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\50.jpg",
            "options": [
                "Compulsory path for motor vehicles",
                "Lane reserved for bikes",
                "No entry for bikes"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/50.jpg"
        },
        # ID 155 (Sign 51)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\51.jpg",
            "options": [
                "Cycles crossing",
                "Motorbikes Lane",
                "No entry for motorbikes"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/51.jpg"
        },
        # ID 156 (Sign 52)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\52.jpg",
            "options": [
                "Trolleys cannot be parked here",
                "Lane reserved for trolleys",
                "No entry for trolleys"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/52.jpg"
        },
        # ID 157 (Sign 53)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\53.jpg",
            "options": [
                "No parking",
                "Road reserved for motor vehicles",
                "No entry to all types of motor vehicles"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/53.jpg"
        },
        # ID 158 (Sign 55)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\55.jpg",
            "options": [
                "No entry to trucks exceeding 2.3m in height",
                "No entry for trucks",
                "No entry to cars exceeding 2.3m in width"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/55.jpg"
        },
        # ID 159 (Sign 56)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\56.jpg",
            "options": [
                "Compulsory direction for trucks",
                "No entry to trucks exceeding 3.5 tons in weight",
                "No entry to trucks exceeding 3.5 m in height"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/56.jpg"
        },
        # ID 160 (Sign 57)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\57.jpg",
            "options": [
                "Cargo cannot exceed 10m",
                "No entry to trucks carrying more than 6.5 tons of cargo",
                "No entry to trucks exceeding 10m in height"
            ],
            "correct": 2,
            "category": "Signs",
            "image": "images/57.jpg"
        },
        # ... [Continuing for all IDs up to 220] ...
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\58.jpg",
            "options": [
                "No entry to trucks exceeding 7m in height",
                "No entry to trucks exceeding 7 tons/wheel",
                "No entry to trucks carrying more than 7 tons of cargo"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/58.jpg"
        },
        # ID 162 (Sign 60)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\60.jpg",
            "options": [
                "Start of restriction signs",
                "No speeding",
                "End of restriction sign"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/60.jpg"
        },
        # ID 163 (Sign 61)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\61.jpg",
            "options": [
                "Speed limit",
                "Start of speed limit",
                "End of speed limit"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/61.jpg"
        },
        # ID 164 (Sign 62)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\62.jpg",
            "options": [
                "Compulsory direction to the left",
                "You cannot turn right",
                "Turn right"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/62.jpg"
        },
        # ID 165 (Sign 63)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\63.jpg",
            "options": [
                "You can go straight or turn right",
                "You cannot turn left",
                "Turn left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/63.jpg"
        },
        # ID 166 (Sign 64)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\64.jpg",
            "options": [
                "You cannot go right or left",
                "You must go straight or left",
                "You can turn right or left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/64.jpg"
        },
        # ID 167 (Sign 65)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\65.jpg",
            "options": [
                "Trucks must go right",
                "You cannot turn left",
                "You can go straight or turn right"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/65.jpg"
        },
        # ID 168 (Sign 66)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\66.jpg",
            "options": [
                "You cannot go left",
                "Compulsory direction to the left",
                "You can go straight or turn left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/66.jpg"
        },
        # ID 169 (Sign 67)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\67.jpg",
            "options": [
                "You can go right",
                "Freeway lane",
                "Compulsory direction to the left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/67.jpg"
        },
        # ID 170 (Sign 68)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\68.jpg",
            "options": [
                "You must go straight",
                "You cannot turn right",
                "Compulsory direction to the right"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/68.jpg"
        },
        # ID 171 (Sign 69)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\69.jpg",
            "options": [
                "You cannot turn right or left",
                "Vehicle can only turn right",
                "Compulsory direction to the right or the left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/69.jpg"
        },
        # ID 172 (Sign 71)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\71.jpg",
            "options": [
                "Lane reserved for pedestrians and bicycles",
                "Lane reserved for bicycles",
                "End of bicycle track"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/71.jpg"
        },
        # ID 173 (Sign 72)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\72.jpg",
            "options": [
                "No entry for pedestrians and bicycles",
                "Lane reserved for pedestrians and bicycles",
                "End of bicycle track"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/72.jpg"
        },
        # ID 174 (Sign 75)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\75.jpg",
            "options": [
                "Compulsory direction to the right",
                "Traffic direction",
                "You cannot turn right"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/75.jpg"
        },
        # ID 175 (Sign 76)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\76.jpg",
            "options": [
                "Compulsory turn",
                "Traffic direction",
                "You cannot turn"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/76.jpg"
        },
        # ID 176 (Sign 77)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\77.jpg",
            "options": [
                "End of no bus overtaking zone",
                "Lane reserved for buses",
                "No entry to buses"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/77.jpg"
        },
        # ID 177 (Sign 78)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\78.jpg",
            "options": [
                "No entry to trucks exceeding 6.5 tons in weight",
                "Lane reserved for trucks",
                "No entry to trucks"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/78.jpg"
        },
        # ID 178 (Sign 79)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\79.jpg",
            "options": [
                "Compulsory direction for trucks",
                "Trucks cannot park here",
                "No entry to trucks carrying more than 6.5 tons of cargo"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/79.jpg"
        },
        # ID 179 (Sign 80)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\80.jpg",
            "options": [
                "Compulsory direction for trucks",
                "No entry for trucks carrying Hazardous Material",
                "No entry to trailer trucks"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/80.jpg"
        },
        # ID 180 (Sign 81)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\81.jpg",
            "options": [
                "One-minute parking for agricultural machinery",
                "Road reserved for agricultural machinery",
                "Agricultural machinery not allowed"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/81.jpg"
        },
        # ID 181 (Sign 84)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\84.jpg",
            "options": [
                "End of no overtaking for trucks",
                "End of no overtaking zone",
                "Caution, two-lane road"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/84.jpg"
        },
        # ID 182 (Sign 85)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\85.jpg",
            "options": [
                "Trucks only",
                "End of no overtaking for trucks",
                "Caution, two lane road"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/85.jpg"
        },
        # ID 183 (Sign 86)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\86.jpg",
            "options": [
                "No parking",
                "No overtaking for all kinds of vehicles",
                "No entry"
            ],
            "correct": 0,  # Status 1 = TRUE
            "category": "Signs",
            "image": "images/86.jpg"
        },
        # ID 184 (Sign 87)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\87.jpg",
            "options": [
                "No stopping and no parking",
                "No parking",
                "No entry"
            ],
            "correct": 0,  # Status 1 = TRUE
            "category": "Signs",
            "image": "images/87.jpg"
        },
        # ID 185 (Sign 88)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\88.jpg",
            "options": [
                "No parking in this zone",
                "No entry in this direction",
                "You must go straight"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/88.jpg"
        },
        # ID 186 (Sign 89)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\89.jpg",
            "options": [
                "No parking on the left",
                "You cannot turn left",
                "Direction to the left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/89.jpg"
        },
        # ID 187 (Sign 90)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\90.jpg",
            "options": [
                "No parking on the right",
                "You cannot turn right",
                "Direction to the right"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/90.jpg"
        },
        # ID 188 (Sign 91)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\91.jpg",
            "options": [
                "Parking zone",
                "Roundabout ahead",
                "You cannot turn"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/91.jpg"
        },
        # ID 189 (Sign 92)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\92.jpg",
            "options": [
                "You cannot park for more than 30 minutes",
                "Mandatory upper speed",
                "Mandatory lower speed"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/92.jpg"
        },
        # ID 190 (Sign 93)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\93.jpg",
            "options": [
                "Maximum speed: 30 km/h",
                "You cannot park for more than 30 minutes",
                "End of mandatory lower speed"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/93.jpg"
        },
        # ID 191 (Sign 94)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\94.jpg",
            "options": [
                "Caution, slippery road ahead",
                "Tyre chains must be removed",
                "Vehicles equipped with metal chains only"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/94.jpg"
        },
        # ID 192 (Sign 95)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\95.jpg",
            "options": [
                "Park",
                "No entry for pedestrians",
                "Lane reserved for pedestrians"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/95.jpg"
        },
        # ID 193 (Sign 96)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\96.jpg",
            "options": [
                "Lane reserved for pedestrians",
                "Upper ground pedestrian crossing",
                "End of pedestrian Lane"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/96.jpg"
        },
        # ID 194 (Sign 97)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\97.jpg",
            "options": [
                "No parking for bicycles",
                "No entry for bicycles",
                "Bicycles track"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/97.jpg"
        },
        # ID 195 (Sign 98)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\98.jpg",
            "options": [
                "Compulsory direction to the left",
                "No parking on the left",
                "Cannot turn left"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/98.jpg"
        },
        # ID 196 (Sign 99)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\99.jpg",
            "options": [
                "Caution, moving bridge ahead",
                "Two-lane road connected to a bridge",
                "Hospital"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/99.jpg"
        },
        # ID 197 (Sign 100)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\100.jpg",
            "options": [
                "Caution, no entry to pedestrians",
                "End of pedestrian lane",
                "Caution, pedestrian crossing"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/100.jpg"
        },
        # ID 198 (Sign 104)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\104.jpg",
            "options": [
                "No entry for bicycles",
                "Lane reserved for bikes",
                "Bicycle track"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/104.jpg"
        },
        # ID 199 (Sign 106)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\106.jpg",
            "options": [
                "Lanes merge ahead",
                "Merger with a freeway ahead",
                "Dead end road"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/106.jpg"
        },
        # ID 200 (Sign 107)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\107.jpg",
            "options": [
                "Caution, airport runway",
                "Caution, bridge",
                "Highway"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/107.jpg"
        },

        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\108.jpg",
            "options": [
                "Bridge above the road",
                "End of freeway",
                "Caution, narrow road ahead"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/108.jpg"
        },
        # ID 202 (Sign 109)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\109.jpg",
            "options": [
                "Bridge",
                "Tunnel",
                "Caution, rough road ahead"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/109.jpg"
        },
        # ID 203 (Sign 111)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\111.jpg",
            "options": [
                "For doctors only",
                "Parking for the disabled",
                "Help center"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/111.jpg"
        },
        # ID 204 (Sign 112)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\112.jpg",
            "options": [
                "No parking for the disabled",
                "One-minute parking",
                "Parking reserved for the disabled"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/112.jpg"
        },
        # ID 205 (Sign 113)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\113.jpg",
            "options": [
                "Parking",
                "One-minute parking",
                "Parking not allowed"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/113.jpg"
        },
        # ID 206 (Sign 116)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\116.jpg",
            "options": [
                "Parking for all - not more than two taxi cars allowed",
                "Taxis not allowed to park here",
                "Taxi stop"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/116.jpg"
        },
        # ID 207 (Sign 117)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\117.jpg",
            "options": [
                "Remove immediately",
                "Inquiries",
                "Police"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/117.jpg"
        },
        # ID 208 (Sign 118)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\118.jpg",
            "options": [
                "Internet Center",
                "Petrol station",
                "Inquiries"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/118.jpg"
        },
        # ID 209 (Sign 119)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\119.jpg",
            "options": [
                "Parking reserved for the police",
                "Fire Brigade",
                "Municipality police"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/119.jpg"
        },
        # ID 210 (Sign 121)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\121.jpg",
            "options": [
                "Dangerous intersection ahead",
                "Indirect turn to the left",
                "Freeway"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/121.jpg"
        },
        # ID 211 (Sign 127)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\127.jpg",
            "options": [
                "Parking",
                "One-minute parking",
                "No parking"
            ],
            "correct": 0,  # Status 1 = TRUE
            "category": "Signs",
            "image": "images/127.jpg"
        },
        # ID 212 (Sign 128)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\128.jpg",
            "options": [
                "Repair Center",
                "Restaurant",
                "Hotel"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/128.jpg"
        },
        # ID 213 (Sign 129)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\129.jpg",
            "options": [
                "Refreshments",
                "Restaurant",
                "Inquiries"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/129.jpg"
        },
        # ID 214 (Sign 132)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\132.jpg",
            "options": [
                "Petrol station",
                "Public phone",
                "Restaurant"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/132.jpg"
        },
        # ID 215 (Sign 133)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\133.jpg",
            "options": [
                "Petrol station",
                "Repair Center",
                "Restaurant"
            ],
            "correct": 0,  # Status 1 = TRUE
            "category": "Signs",
            "image": "images/133.jpg"
        },
        # ID 216 (Sign 134)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\134.jpg",
            "options": [
                "Lane reserved for buses",
                "Buses are not allowed to stop here",
                "Bus parking"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/134.jpg"
        },
        # ID 217 (Sign 136)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\136.jpg",
            "options": [
                "Help Center",
                "Camping & camping cars zone",
                "No parking"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/136.jpg"
        },
        # ID 218 (Sign 139)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\139.jpg",
            "options": [
                "Reduce Speed",
                "Indirect bend to the left",
                "Bend ahead"
            ],
            "correct": 2,  # Status 3 = TRUE
            "category": "Signs",
            "image": "images/139.jpg"
        },
        # ID 219 (Sign 141)
        {
            "question": "What does this sign mean? - C:\\DTA\\signs\\141.jpg",
            "options": [
                "Reduce Speed",
                "Indirect bend to the left",
                "Bend ahead"
            ],
            "correct": 1,  # Status 2 = TRUE
            "category": "Signs",
            "image": "images/141.jpg"
        },

    ]

    # If you have 80+ sign questions, keep adding them the same way above!

    # ------------- SAFETY QUESTIONS POOL (Fill with real data as needed) -------------

    safety_pool = [
        {
            "question": "When entering a tunnel during daytime, the driver should:",
            "options": [
                "Turn on the regular headlights (low beam) and speed up",
                "Turn on the regular headlights (low beam) and slow down",
                "Sound the horn"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "At night, when driving behind another vehicle, you should:",
            "options": [
                "Turn on the normal headlights (low beam)",
                "Turn on the high beam",
                "Not use car headlights"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If a car approaches from the other direction while your high beam is on, you should:",
            "options": [
                "Switch to normal headlights (low beam) immediately",
                "Turn off lights",
                "Switch between high and low beam repetitively"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "When filling up your car with gas, you should:",
            "options": [
                "Keep the engine running",
                "Not care as it does not pose any threat",
                "Turn off the engine"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If you feel sleepy while driving, you should:",
            "options": [
                "Take amphetamines and continue driving",
                "Not be concerned as it will pass",
                "Stop immediately at the side of the road to get some rest"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "It is okay while driving for the driver to:",
            "options": [
                "Read the newspaper",
                "Use the phone",
                "Listen to the radio at a low volume"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The driver and passengers should fasten their seat belt:",
            "options": [
                "Before turning on the car engine",
                "Prior to setting off",
                "After a minute from setting off"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The driver’s ability to focus is impaired during driving due to:",
            "options": [
                "Having an abundance in energy",
                "Being sleepy and tired",
                "Driving inside the city"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Using a cell phone while driving impacts the drivers’ ability to drive in a:",
            "options": [
                "Positive way",
                "Negative way",
                "Both positive and negative way"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The first advice for a driver that assumed some alcohol is to:",
            "options": [
                "Drive at low speeds",
                "Refrain from driving until the side effects of alcohol have disappeared",
                "Not to be bothered"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Driving under the influence of sleeping medication is:",
            "options": [
                "Delightful",
                "Not dangerous",
                "Dangerous"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If the gas pedal gets stuck while driving, the driver should immediately:",
            "options": [
                "Pull the handbrake up",
                "Change to a lower gear",
                "Put the gear on neutral, turn off the engine and stop on the side of the road"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If the car hood accidentally releases while driving down the road, you should immediately:",
            "options": [
                "Increase your speed a little",
                "Reduce your speed gradually and pull to the side of the road",
                "Press firmly on the brakes"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "To avoid being late during heavy rain, the driver should start his journey:",
            "options": [
                "A bit earlier than usual",
                "A bit later than usual",
                "With good spirits"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Before stepping into the vehicle, the driver should:",
            "options": [
                "Make sure he has enough time on his hands",
                "Look around and under the vehicle",
                "Fasten the seatbelt"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "While driving in heavy traffic, the driver should glance at his mirrors every:",
            "options": [
                "45 seconds",
                "30 seconds",
                "4 to 8 seconds"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Before turning right, the driver should glance at:",
            "options": [
                "The left-side mirror only",
                "The right-side mirror only",
                "All the mirrors, especially the right-side mirror and blind spots"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The biggest threat that vehicles parked on the right-side pavement pose to drivers passing close to them is:",
            "options": [
                "Pedestrians, and children, appearing suddenly from between these parked vehicles",
                "Trash being thrown from them towards the passing vehicles",
                "Loud sounds from the radios of these vehicles"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The threat that vehicles parked on the right-side pavement bring to drivers passing close to them is:",
            "options": [
                "The alarm that would go off as the drivers cross next to these vehicles",
                "The opening of a car trunk",
                "The fact that any of these parked vehicles could take off and join traffic at any time"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "As a cautious driver, you should:",
            "options": [
                "Take the right of way by force as it is your right",
                "Yield the right of way to prevent road collisions",
                "Never yield your right of way"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "While driving and prior to hitting your brakes, you should first look:",
            "options": [
                "In the mirrors, namely the rear-view mirror",
                "To your right",
                "To your left"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "When strong braking is applied, ABS in modern vehicles:",
            "options": [
                "Should not make noise or cause the brake pedal to pulsate",
                "Would normally make noise and cause the brake pedal to pulsate",
                "Would normally cause the brake pedal to pulsate"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "One of the benefits of ABS in modern vehicles when strong braking is applied, is:",
            "options": [
                "Preventing brakes from locking-up and allows the driver to maintain steering control of the vehicle",
                "Preventing brakes locking-up only",
                "Not preventing brakes locking-up and not helping the driver maintain steering control of the vehicle"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If your vehicle is beginning to lose traction on a slippery surface, you should spontaneously:",
            "options": [
                "Press on the brakes and steer your vehicle in the opposite direction to your vehicle's rear",
                "Get your foot off the accelerator (don't press on the brakes) and steer your vehicle in the same direction",
                "Increase your speed"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If you leave a safe distance between your vehicle and the vehicle in front, you will be able to:",
            "options": [
                "Avoid a collision with that vehicle should it make a sudden stoop",
                "Enjoy the view surrounding you",
                "Read the plate number of that vehicle"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If your vehicle suddenly malfunctions while driving on a highway, you should:",
            "options": [
                "Leave the highway from the nearest exit",
                "Stop the car immediately in the place your at",
                "Keep on driving to your destination"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The driver should hold the steering wheel:",
            "options": [
                "With one hand",
                "With both hands",
                "With his fingertips"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "By law, the driver should yield the right of way to:",
            "options": [
                "Speeding vehicles",
                "Bus Schools flashing their hazard lights",
                "Slow vehicles"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Excessive eating:",
            "options": [
                "Helps the driver drive more safely",
                "Will impair the driver's ability to react properly and make the right decisions",
                "Will allow the driver to maintain control of his vehicle while driving at very high speeds"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Insufficient sleeping:",
            "options": [
                "Helps improve reaction",
                "Slows down his reactions during driving and causes him a slight loss of memory",
                "Helps him to be alert"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "In long trips, the driver must stop for rest every:",
            "options": [
                "10 hours",
                "8 hours",
                "4 hours"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "In long trips, the driver must stop for rest around every:",
            "options": [
                "250 kilometers",
                "750 kilometers",
                "900 kilometers"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Driving under the influence of alcohol:",
            "options": [
                "Endangers driver’s life as well as the lives of others",
                "Endangers others’ lives only",
                "Endangers the driver"
            ],
            "correct": 0,
            "category": "Safety",
            "image": None
        },
        {
            "question": "During very long trips, the driver should:",
            "options": [
                "Consume amphetamines regularly",
                "Continue driving without rest",
                "Never consume amphetamines to stay awake"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The best way for a driver to know how a medical drug affects his driving is to:",
            "options": [
                "Check with another driver",
                "Check with his physician",
                "Test it on another driver"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Driving under the influence of alcohol or drugs causes the driver a false feeling of:",
            "options": [
                "Fear",
                "Courage and boldness",
                "Outrage"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "When you are about to overtake another vehicle, you should:",
            "options": [
                "Rely on that vehicle light signals",
                "Never depend on that vehicle’s driver hand gestures",
                "Check the signals od the driver behind you"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If you have a flat tyre while you're traveling:",
            "options": [
                "Let the steering wheel take the reigns",
                "Release the accelerator to allow the vehicle to slow down, keep the steering wheel straight, and pull off the road",
                "Press on the brakes to slow down, and pull off the road"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If the lights of the vehicle traveling on the opposite direction are bothering you, you should:",
            "options": [
                "Look towards the middle of the road",
                "Look towards the left side of the road",
                "Look down, and towards the right side of the road"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "In case of vehicle break-down on the highway",
            "options": [
                "Wait inside the vehicle until the road assistance vehicle reaches you",
                "Place the warning triangle and turn on the headlights to warn other drivers",
                "Place the warning triangle and activate all four signal lights to warn other drivers"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "If your brakes stops working while you are on the road, you should:",
            "options": [
                "Turn off the engine",
                "Head directly to a repair shop",
                "Quickly press on the brakes with high frequency"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "In case of bad weather, the driver should:",
            "options": [
                "Drive at the upper speed limit",
                "Drive below the upper speed limit so as to accommodate road conditions",
                "Drive at the upper speed limit and turn on the lights"
            ],
            "correct": 1,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The driver needs a bigger 'safe distance':",
            "options": [
                "Where there are other cars in front",
                "On dry roads",
                "On wet roads"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "Ice forms quickly on roads that:",
            "options": [
                "Are plane",
                "Have an uneven surface, with lots of bends",
                "Are shaded"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        },
        {
            "question": "The shelf life of tyres does not exceed:",
            "options": [
                "4 years from manufacturing date or 1.6 mm thread thickness, whichever comes first",
                "5 years from manufacturing date or 1.6 mm thread thickness, whichever comes last",
                "6 years from manufacturing date or 1.6 mm thread thickness, whichever comes first"
            ],
            "correct": 2,
            "category": "Safety",
            "image": None
        }
    ]

    law_pool = [
        {
            "question": "If the traffic light turns yellow when your vehicle has already entered the intersection, you should:",
            "options": [
                "Stop immediately in the middle of the intersection",
                "Continue forward cautiously",
                "Stare at the traffic light"
            ],
            "correct": 1,
            "category": "Law",
            "image": None
        },
        {
            "question": "When approaching an intersection that has a traffic policeman regulating traffic and an active traffic light and fixed traffic sign, you should:",
            "options": [
                "Follow the traffic policeman’s instructions",
                "Follow the traffic lights",
                "Heed the fixed traffic sign"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "When the vehicle in front immediately takes off the moment a red light turns green, you should:",
            "options": [
                "Take off immediately after it and fast",
                "Sound your horn",
                "Make sure the road is empty then take off"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When approaching an intersection with a flashing yellow traffic light, you should:",
            "options": [
                "Provide right of way",
                "Stop",
                "Fasten the seatbelt"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "The seat belt must be used:",
            "options": [
                "By all passengers",
                "By front-seat passengers only",
                "Not absolutely necessary"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "By law, the driver should yield the right of way to:",
            "options": [
                "Vehicles that are already in the roundabout",
                "Vehicles that are entering a roundabout",
                "Vehicles located to the right of the vehicle"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "It is legal to parallel park a vehicle to the pavement on a single-lane two-way street:",
            "options": [
                "To the right of the direction of driving for the vehicle",
                "Doesn't matter as long as it doesn't hinder traffic",
                "To the left of the road"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "If the road is divided into two lanes with solid lines or other lane separator, the driver:",
            "options": [
                "Should travel in the opposite direction",
                "Should cross these lines and drive on it",
                "Should not cross these lines or other lane separators"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "In case of normal traffic, the driver should:",
            "options": [
                "Keep to the left side of the road",
                "Cross the dividing lines to overtake",
                "Keep to the right side of the road"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Pavements are intended:",
            "options": [
                "To park vehicles, when parking is allowed",
                "To put anything that obstructs the use of the pavement",
                "To be used by pedestrians, children trolleys, the sick , and the disabled"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When drastically changing speed or direction, the driver should:",
            "options": [
                "Cross the solid line if the solid line is on his left",
                "Cross the broken line without any signaling",
                "Check there is no danger, and give appropriate signals to other road users"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Sudden braking is allowed only:",
            "options": [
                "If the driver needs to stop the car",
                "If the driver needs to test the brakes",
                "In case of danger"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "The driver should keep to:",
            "options": [
                "The left, when another driver is overtaking him",
                "The left, when another vehicle is heading towards him way from the opposite direction",
                "The right, when another vehicle is heading towards him way from the opposite direction"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers are strictly prohibited to:",
            "options": [
                "Overtake from the left when there is enough visibility",
                "Travel on the right side of the road when another vehicle is heading towards him from the opposite direction",
                "Overtake traveling military or police motorcades, or other processions"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers are strictly prohibited to:",
            "options": [
                "Move slowly on the left side of the road",
                "Travel in the designated direction",
                "Drive in neutral with the intention to drive the vehicle solely through downforce"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers are strictly prohibited to:",
            "options": [
                "Check there is no danger before overtaking",
                "Travel in the designated direction",
                "Make a U-turn in the middle of the road in a populated area"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers are strictly prohibited to:",
            "options": [
                "Check there is no danger before overtaking",
                "Travel in the designated direction",
                "Travel in other than the designated direction"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "The driver:",
            "options": [
                "Should not take into consideration the condition of the road or the traffic density",
                "Should increase his speed when visibility is low",
                "Should reduce his speed or stop completely when the conditions surrounding him dictate so, especially when visibility is really bad"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Before overtaking, the driver should:",
            "options": [
                "Should not take into consideration driving decorum when in populated areas",
                "Overtake, even if the driver behind have have already initiated a similar overtake",
                "Check that drivers behind him have not initiated a similar overtake"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When overtaking, the driver should:",
            "options": [
                "Not keep to the right immediately before overtaking",
                "Use the left side of the road, even if it disaccommodate drivers traveling on the opposite direction",
                "Use the left side of the road without disaccommodating drivers traveling on the opposite direction"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "It is prohibited to overtake:",
            "options": [
                "On bends",
                "From the right, whatever the case may be",
                "On bridges and in tunnels"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "If a police car, ambulance, or fire truck gives a signal of approaching, other road users should:",
            "options": [
                "Stop immediately where they are so as to ease the movement of such vehicle",
                "Increase their speed so as to ease the movement of such vehicle",
                "Reduce their speed, and if need be, stop or move aside so as to ease the movement of such vehicle"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "It is best to keep a 'safe Distance':",
            "options": [
                "From the left and the right sides only",
                "From the front and the end sides only",
                "From all sides of the vehicle"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "A solid green light at the intersection means:",
            "options": [
                "You should stop and check traffic in the other direction before you carry on",
                "You cannot turn right",
                "You can cross the intersection if it is possible"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "A flashing yellow light means:",
            "options": [
                "You can carry on if the road is clear",
                "You should stop and carry on only when the road is clear",
                "Reduce your speed and carry on cautiously"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "A yellow light on the intersection means:",
            "options": [
                "Go ahead",
                "Reduce your speed and be ready to stop",
                "Stop"
            ],
            "correct": 1,
            "category": "Law",
            "image": None
        },
        {
            "question": "When you enter a highway, you should:",
            "options": [
                "Slow down",
                "Drive below the speed limit",
                "Drive within the highway traffic speed"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "If a vehicle is pressing behind you, and you are on the left lane on a freeway, you should:",
            "options": [
                "Speed up",
                "Press the brakes intermittently to drive the other vehicle to move away",
                "Move to the right lane, and adjust your speed to the traffic speed on that lane"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Rear brake lights alert other drivers that you are:",
            "options": [
                "Entering a bend",
                "Changing lanes",
                "Slowing down or stopping"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "On a four-way intersection, the vehicle that goes first is:",
            "options": [
                "The vehicle that arrived first",
                "The vehicle that is turning right",
                "The vehicle that arrived first and already entered the intersection"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "You should stop when you see:",
            "options": [
                "A solid yellow light",
                "A flashing yellow light",
                "A flashing red light"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When you are sharing the road with a truck, it would be good to remember that trucks:",
            "options": [
                "Require a smaller turning radius",
                "Require less time to overtake in descents",
                "Need a bigger safe distance with other vehicles to be able to stop"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When turning right at the green light, you should:",
            "options": [
                "Slow down to be able to make the turn",
                "Carry on on the same lane",
                "Give way to pedestrians"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "You can refrain from taking the drug or alcohol test:",
            "options": [
                "In emergency cases",
                "If you are under 21",
                "No, you cannot in any case it may be"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When driving in the fog, you should turn on the:",
            "options": [
                "High beam",
                "Hazard lights, and/or low beam",
                "Hazard lights, and/or high beam"
            ],
            "correct": 1,
            "category": "Law",
            "image": None
        },
        {
            "question": "When overtaking on a multiple-lane highway:",
            "options": [
                "No need to give a signal",
                "Keep your eyes on the parallel lane",
                "Make sure there is enough gap in the lane you want to move to"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When you are taking a curve:",
            "options": [
                "Maintain the speed of your vehicle",
                "Increase the speed of your vehicle",
                "Decrease the speed of your vehicle"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "If the traffic lights are not working:",
            "options": [
                "Give the right of way to the driver on the left",
                "Stop and wait until the police gets to the intersection",
                "Act as if you are at an intersection without traffic lights"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When a truck is trying to overtake your vehicle:",
            "options": [
                "Change lanes",
                "Increase your speed",
                "Maintain or decrease your speed"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "If two drivers are approaching an intersection from opposite directions",
            "options": [
                "Each will go on his way without giving priority to the other",
                "The driver coming from the left should give the right of way to the other driver",
                "The driver coming from the right should give the right of way to the other driver"
            ],
            "correct": 1,
            "category": "Law",
            "image": None
        },
        {
            "question": "Before overtaking, entering a curve, or being overtaken, you should",
            "options": [
                "Reduce your speed, give a signal to other drivers, and check the mirrors",
                "Reduce your speed, give a signal as you take the other lane",
                "Slow down, give enough signal to other road users, and check the mirrors and the blind spots"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When a vehicle is turning and a pedestrian is crossing the street, and there is no traffic light, who has the right of way?",
            "options": [
                "Whomever goes faster and reachs first",
                "The vehicle",
                "The pedestrian"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers are strictly prohibited to:",
            "options": [
                "Travel in other than the designated direction",
                "Stay awake and in control of their vehicles",
                "Check there is no danger before overtaking"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "Common logic dictates that you should not:",
            "options": [
                "Go beyond the upper speed limit of 80 km/hour",
                "Go beyond the indicated speed limit",
                "Go faster than what is appropriate to the road you are traveling on"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "You can carry on on a yellow light if you are:",
            "options": [
                "Behind a vehicle that has the right of way (ambulance, civil defence, firetruck)",
                "Turning right",
                "Already in the intersection"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers who have had their drivers' license for more than three years, should not drive under the influence of alcohol where the level of alcohol in their blood exceeds:",
            "options": [
                "0.3 grams/liter",
                "0.4 grams/liter",
                "0.5 grams/liter"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "In the first three years of having a drivers' license, the level of alcohol in the blood should not exceed:",
            "options": [
                "0 grams/liter",
                "0.3 grams/liter",
                "0.5 grams/liter"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "It is strictly prohibited for drivers to:",
            "options": [
                "Use any communication devices",
                "Use one hand to drive and the other to answer the phone",
                "Use both hands to drive, and answer the call using bluetooth technology"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "Where there is no speed limit signs, the upper speed limit on the freeway is:",
            "options": [
                "80 km/hour",
                "100 km/hour",
                "120 km/hour"
            ],
            "correct": 1,
            "category": "Law",
            "image": None
        },
        {
            "question": "Where there is no speed limit signs, the upper speed limit outside populated areas is:",
            "options": [
                "50 km/hour",
                "60 km/hour",
                "70 km/hour"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Where there is no speed limit signs, the upper speed limit inside populated areas is:",
            "options": [
                "40 km/hour",
                "50 km/hour",
                "60 km/hour"
            ],
            "correct": 1,
            "category": "Law",
            "image": None
        },
        {
            "question": "When the driver causes an accident, and even if damages are material damages only:",
            "options": [
                "The driver has the right to flee the scene and avoid responsibility",
                "The driver should carry on driving",
                "The driver should stop and take care of the victim"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "If the brake lights are down:",
            "options": [
                "The car may be impounded",
                "This is a Class 2 violation",
                "All of the above"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When the traffic light is green, but traffic is congested, road users should:",
            "options": [
                "Move slowly so as not to obstruct traffic",
                "Cross the green light quickly",
                "Refrain from crossing the green light if it would obstruct traffic"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "A broken line on the road means:",
            "options": [
                "You can travel on the line",
                "You cannot cross the line",
                "You can cross the line"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Vehicles of all types cannot be fitted in the front with lights other than:",
            "options": [
                "Blue or yellow",
                "White or blue",
                "White or yellow"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "The driver should give the right of way to:",
            "options": [
                "Vehicles",
                "Trucks",
                "Pedestrians"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Inside cities, you should always keep a safe distance of:",
            "options": [
                "1 second",
                "2 meters",
                "2 seconds"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "In entering a roundabout, the right of way is for:",
            "options": [
                "The vehicle on the left",
                "The vehicle on the right",
                "The vehicle that is already in the roundabout"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "In case of road works, the driver should:",
            "options": [
                "Turn on his vehicle lights",
                "Drive fast",
                "Reduce speed"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Children below the age of five should be seated:",
            "options": [
                "In their parents laps",
                "In the back seats",
                "In child seats"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When vehicles are still approaching an intersection, the right of way is always for the driver coming from:",
            "options": [
                "Inside the intersection",
                "The left",
                "The right"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers are prohibited to obstruct traffic by:",
            "options": [
                "Stopping slowly",
                "Travelling below the lower speed limit",
                "Stopping suddenly without a valid reason to do so"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Who has the right of way on a three forked road?",
            "options": [
                "The driver who proceeds cautiously",
                "The driver on the right side",
                "The driver who is on the straight lane"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When the traffic policeman lifts his hand vertically, it means:",
            "options": [
                "You have to slow down",
                "Traffic ahead has come to a halt",
                "\"Careful and stop\" to all road users"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Every vehicle should be fitted with",
            "options": [
                "A registration plate at the back side of the vehicle",
                "Two registration plates with the vehicle number, at front or back side of the vehicles",
                "Two registration plates with the vehicle number, at the front and back sides of the vehicles"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Warning sounds can be used only:",
            "options": [
                "To alert other drivers that they should move quickly",
                "To escape heavy traffic",
                "To alarm other road users so as to avoid accidents"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "When the driver streches his hand horizontally, it means the driver is:",
            "options": [
                "Reversing",
                "Slowing down",
                "Turning left"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Children under ____ cannot sit in the front seat:",
            "options": [
                "10 years",
                "12 years",
                "8 years"
            ],
            "correct": 0,
            "category": "Law",
            "image": None
        },
        {
            "question": "It is strictly prohibited to throw stuff from the vehicle as this would:",
            "options": [
                "Obstruct policemen",
                "Cause road markings to fade away",
                "Cause accidents, and clog water drainage system"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "What is the difference between yellow lines and white lines when they are in the middle of the road?",
            "options": [
                "Yellow lines are used on road sides only, whereas white lines are used to mark vehicle lanes",
                "Yellow lines are used for one-way roads whereas white lines are used for two-way streets",
                "White lines demarcate lanes that go in the same direction, yellow lines are demarcate lanes that go in opposite directions"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        },
        {
            "question": "Drivers should stop and park:",
            "options": [
                "On white pedestrian crossing stripes",
                "After white pedestrian crossing stripes",
                "Before white pedestrian crossing stripes"
            ],
            "correct": 2,
            "category": "Law",
            "image": None
        }
    ]

    # Ensure at least 10 in safety_pool
    while len(safety_pool) < 10:
        safety_pool.append(safety_pool[0])

    # Ensure at least 10 in law_pool
    while len(law_pool) < 10:
        law_pool.append(law_pool[0])

    # Randomly pick 10 from each
    chosen_signs = random.sample(sign_pool, 10)
    chosen_safety = random.sample(safety_pool, 10)
    chosen_law = random.sample(law_pool, 10)

    # Combine them and shuffle
    questions = chosen_signs + chosen_safety + chosen_law
    random.shuffle(questions)
    return questions


if __name__ == "__main__":
    app = ModernQuizApp()
    app.mainloop()
