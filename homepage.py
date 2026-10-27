# homepage.py
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import threading
import os

from detection_module import detect_hate_speech
from detection_image import analyze_image
from db import authenticate_user, create_user, add_text_submission, add_image_submission, get_user_history
from storage import save_image_file, save_pil_image

LANGS = [
    ("Auto", "auto"),
    ("English", "en"),
    ("Hindi", "hi"),
    ("Spanish", "es"),
    ("French", "fr"),
    ("Tamil","tl"),
    ("Marathi","mr")
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hate Speech Detection System")
        self.geometry("1150x750")
        self.configure(bg="#121212")
        self.current_user_id = None

        self.create_header()
        self.show_login_window()

    # ---------------- HEADER ----------------
    def create_header(self):
        header = tk.Frame(self, bg="#1f1f1f", pady=8)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🧠 Hate Speech Detection",
            font=("Montserrat", 18, "bold"),
            bg="#1f1f1f",
            fg="#00bfff"
        ).pack(side="left", padx=16)

        self.nav_frame = tk.Frame(header, bg="#1f1f1f")
        self.nav_frame.pack(side="right", padx=8)

    def update_nav(self):
        for w in self.nav_frame.winfo_children():
            w.destroy()

        if self.current_user_id:
            buttons = [
                ("Home", self.show_home),
                ("Text Detect", self.open_text_window),
                ("Image Detect", self.open_image_window),
                ("History", self.open_history_window),
                ("Logout", self.logout),
            ]
            for name, cmd in buttons:
                tk.Button(
                    self.nav_frame, text=name,
                    command=cmd, bg="#2d2d2d", fg="#00bfff"
                ).pack(side="left", padx=6)
        else:
            tk.Button(
                self.nav_frame, text="Login/Register",
                command=self.show_login_window,
                bg="#2d2d2d", fg="#00bfff"
            ).pack(side="left", padx=6)

    # ---------------- LOGIN PAGE ----------------
    def show_login_window(self):
        self.clear_body()

        frame = tk.Frame(self, bg="#121212")
        frame.pack(expand=True)

        tk.Label(
            frame, text="🔐 Login / Register",
            font=("Segoe UI", 18, "bold"), fg="#00bfff", bg="#121212"
        ).pack(pady=10)

        tk.Label(frame, text="Username", bg="#121212", fg="white").pack()
        username_entry = tk.Entry(frame, bg="#1e1e1e", fg="white")
        username_entry.pack(pady=6)

        tk.Label(frame, text="Password", bg="#121212", fg="white").pack()
        password_entry = tk.Entry(frame, bg="#1e1e1e", fg="white", show="*")
        password_entry.pack(pady=6)

        def do_login():
            u = username_entry.get().strip()
            p = password_entry.get().strip()
            if not u or not p:
                messagebox.showwarning("Error", "Enter username & password")
                return

            uid = authenticate_user(u, p)
            if uid:
                self.current_user_id = uid
                messagebox.showinfo("Welcome", f"Hello {u}!")
                self.update_nav()
                self.show_home()
            else:
                messagebox.showerror("Login failed", "Invalid credentials")

        def do_register():
            u = username_entry.get().strip()
            p = password_entry.get().strip()
            if not u or not p:
                messagebox.showwarning("Error", "Enter username & password")
                return
            try:
                create_user(u, p, None)
                messagebox.showinfo("Registered", "Account created. Please login.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(frame, text="Login", command=do_login, bg="#00bfff", fg="white").pack(pady=6)
        tk.Button(frame, text="Register", command=do_register, bg="#00ff99", fg="black").pack()

    # ---------------- HOME ----------------
    def show_home(self):
        self.clear_body()
        frame = tk.Frame(self, bg="#121212")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(
            frame,
            text="Welcome to the Hate Speech Detection System",
            font=("Segoe UI", 18, "bold"), fg="#00bfff", bg="#121212"
        ).pack(pady=10)

        tk.Label(
            frame,
            text="Use the navigation to detect text or images or check history.",
            fg="#cccccc", bg="#121212"
        ).pack(pady=6)

    # ---------------- TEXT DETECTION ----------------
    def open_text_window(self):
        if not self.current_user_id:
            messagebox.showwarning("Login", "Please login first.")
            self.show_login_window()
            return

        self.clear_body()

        frame = tk.Frame(self, bg="#121212")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(
            frame, text="📝 Text Detection",
            font=("Segoe UI", 16, "bold"),
            fg="#00bfff", bg="#121212"
        ).pack(pady=8)

        lang_frame = tk.Frame(frame, bg="#121212")
        lang_frame.pack(pady=6)

        tk.Label(lang_frame, text="Language:", bg="#121212", fg="white").pack(side="left")

        lang_menu = ttk.Combobox(
            lang_frame,
            values=[l[0] for l in LANGS],
            state="readonly",
            width=18
        )
        lang_menu.current(0)
        lang_menu.pack(side="left", padx=6)

        text_box = tk.Text(frame, height=6, width=80, bg="#1e1e1e", fg="white")
        text_box.pack(pady=8)

        result_label = tk.Label(frame, text="", bg="#121212", fg="white", font=("Segoe UI", 12, "bold"))
        result_label.pack(pady=8)

        def detect_text():
            txt = text_box.get("1.0", "end").strip()
            if not txt:
                messagebox.showwarning("Empty", "Please enter text.")
                return

            result_label.config(text="⏳ Detecting...")

            def worker():
                res = detect_hate_speech(txt)
                pred = str(res.get("predicted_label", "Error"))
                score = float(res.get("score", 0.0))
                sentiment = res.get("sentiment", "Neutral")
                sarcasm = res.get("sarcasm", "Not Detected")

                # Save to DB
                try:
                    add_text_submission(
                        self.current_user_id,
                        txt,
                        score,
                        pred,
                        sentiment,
                        1 if sarcasm == "Detected" else 0,
                        meta={"translated": txt}  # placeholder if translation needed
                    )
                except Exception as e:
                    print("DB save failed:", e)

                # Color code based on label
                color = "#00ff99" if "safe" in pred.lower() else ("#ff5555" if "hate" in pred.lower() else "#ffcc00")

                result_label.config(
                    text=f"Result: {pred} | Sentiment: {sentiment} | Sarcasm: {sarcasm}",
                    fg=color
                )

            threading.Thread(target=worker, daemon=True).start()

        tk.Button(frame, text="🔍 Detect", command=detect_text, bg="#00bfff", fg="white").pack(pady=6)

    # ---------------- IMAGE DETECTION ----------------
    def open_image_window(self):
        if not self.current_user_id:
            messagebox.showwarning("Login", "Please login first.")
            self.show_login_window()
            return

        self.clear_body()

        frame = tk.Frame(self, bg="#121212")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(frame, text="🖼 Image Detection", font=("Segoe UI", 16, "bold"), fg="#00bfff", bg="#121212").pack(pady=8)

        img_preview = tk.Label(frame, text="No image selected", bg="#1e1e1e", width=60, height=10)
        img_preview.pack(pady=8)

        result_label = tk.Label(frame, text="", bg="#121212", fg="white", font=("Segoe UI", 12, "bold"))
        result_label.pack(pady=10)

        def choose_file():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
            if not path:
                return
            saved = save_image_file(path)
            img_preview.filepath = saved
            try:
                img = Image.open(saved)
                img.thumbnail((420, 300))
                tk_img = ImageTk.PhotoImage(img)
                img_preview.img = tk_img
                img_preview.config(image=tk_img, text="")
            except:
                img_preview.config(text=os.path.basename(saved))

        def detect_image():
            path = getattr(img_preview, "filepath", None)
            if not path:
                messagebox.showwarning("No Image", "Select an image first.")
                return

            result_label.config(text="⏳ Detecting image...")

            def worker():
                res = analyze_image(path)
                pred = str(res.get("predicted_label", "Error"))
                score = float(res.get("score", 0.0))
                sentiment = res.get("sentiment", "Neutral")
                sarcasm = res.get("sarcasm", "Not Detected")
                extracted_text = res.get("extracted_text", "")

                # Save to DB
                try:
                    add_image_submission(
                        self.current_user_id,
                        path,
                        extracted_text,
                        score,
                        pred,
                        sentiment,
                        1 if sarcasm == "Detected" else 0,
                        meta=None
                    )
                except Exception as e:
                    print("DB save failed:", e)

                color = "#00ff99" if "safe" in pred.lower() else ("#ff5555" if "hate" in pred.lower() else "#ffcc00")
                result_label.config(
                    text=f"Result: {pred} | Sentiment: {sentiment} | Sarcasm: {sarcasm}",
                    fg=color
                )

            threading.Thread(target=worker, daemon=True).start()

        btn_frame = tk.Frame(frame, bg="#121212")
        btn_frame.pack()
        tk.Button(btn_frame, text="Select Image", command=choose_file, bg="#00bfff", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="🔍 Detect Image", command=detect_image, bg="#00bfff", fg="white").pack(side="left", padx=6)

    # ---------------- HISTORY WINDOW ----------------
    def open_history_window(self):
        if not self.current_user_id:
            messagebox.showwarning("Login", "Please login first.")
            self.show_login_window()
            return

        self.clear_body()

        outer_frame = tk.Frame(self, bg="#121212")
        outer_frame.pack(fill="both", expand=True)

        tk.Label(
            outer_frame,
            text="📜 Submission History",
            font=("Segoe UI", 20, "bold"),
            fg="#00bfff",
            bg="#121212"
        ).pack(pady=12)

        canvas = tk.Canvas(outer_frame, bg="#121212", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        scroll_frame = tk.Frame(canvas, bg="#121212")
        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

        rows = get_user_history(self.current_user_id, limit=200)
        if not rows:
            tk.Label(scroll_frame, text="No submissions yet.", bg="#121212", fg="white").pack()
            return

        for r in rows:
            box = tk.Frame(scroll_frame, bg="#1e1e1e", pady=10, padx=10)
            box.pack(fill="x", pady=8)

            tk.Label(
                box,
                text=f"{r.get('created_at')} — {r.get('prediction')} — {r.get('sentiment')}",
                bg="#1e1e1e", fg="#00bfff", font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", pady=(0, 4))

            t = r.get("content_text") or ""
            if t.strip():
                tk.Label(
                    box,
                    text=t[:800] + ("..." if len(t) > 800 else ""),
                    bg="#1e1e1e", fg="#ffffff",
                    wraplength=1200, justify="left"
                ).pack(anchor="w")

            imgp = r.get("image_path")
            if imgp:
                try:
                    img = Image.open(imgp)
                    img.thumbnail((300, 200))
                    tkimg = ImageTk.PhotoImage(img)
                    lbl_img = tk.Label(box, image=tkimg, bg="#1e1e1e")
                    lbl_img.image = tkimg
                    lbl_img.pack(anchor="w", pady=10)
                except:
                    tk.Label(box, text=f"[Image not found: {imgp}]", bg="#1e1e1e", fg="#cccccc").pack(anchor="w")

    # ---------------- LOGOUT ----------------
    def logout(self):
        self.current_user_id = None
        self.update_nav()
        self.show_login_window()

    # ---------------- CLEAR MAIN AREA ----------------
    def clear_body(self):
        for child in self.winfo_children():
            if isinstance(child, tk.Frame) and child != self.nav_frame.master:
                child.destroy()


if __name__ == "__main__":
    app = App()
    app.update_nav()
    app.show_home()
    app.mainloop()
