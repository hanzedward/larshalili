import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json

data = {'steps': 0, 'calories': 0, 'workouts': 0, 'daily': {'steps': 0, 'calories': 0, 'workouts': 0}, 'workout_log': []}

def show_login_screen():
    login_window = tk.Toplevel(root)
    login_window.title("Login")
    login_window.geometry("500x500")
    bg_image = Image.open("bg.jpg")
    bg_image = bg_image.resize((500, 500))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(login_window, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
    login_window.bg_photo = bg_photo

    username_entry = create_entry(login_window, "Username:", 150, 150)
    password_entry = create_password_entry(login_window, "Password:", 150, 200)

    loading_label = tk.Label(login_window, text="Loading...", font=("Arial", 12), fg="green")
    loading_label.place(x=200, y=400)
    loading_label.place_forget()

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if username == "user" and password == "password":
            loading_label.place(x=200, y=400)
            show_loading_screen(login_window)
            login_window.after(1000, lambda: (login_window.destroy(), show_main_screen()))
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    login_button = tk.Button(login_window, text="Login", font=("Arial", 12), command=login)
    login_button.place(x=150, y=250, width=200, height=40)

def show_loading_screen(window):
    window.update()

def create_entry(parent, placeholder, x, y, **kwargs):
    entry = tk.Entry(parent, font=("Arial", 12), **kwargs)
    entry.place(x=x, y=y, width=200, height=30)
    entry.insert(0, placeholder)
    entry.config(fg="gray")
    entry.bind("<FocusIn>", lambda event: on_focus_in(event, placeholder))
    entry.bind("<FocusOut>", lambda event: on_focus_out(event, placeholder))
    entry.config(borderwidth=2, relief="solid")
    return entry

def create_password_entry(parent, placeholder, x, y):
    password_entry = tk.Entry(parent, font=("Arial", 12), show="*")
    password_entry.place(x=x, y=y, width=200, height=30)
    password_entry.insert(0, placeholder)
    password_entry.config(fg="gray")
    password_entry.bind("<FocusIn>", lambda event: on_focus_in_password(event, placeholder))
    password_entry.bind("<FocusOut>", lambda event: on_focus_out_password(event, placeholder))
    password_entry.config(borderwidth=2, relief="solid")
    return password_entry

def on_focus_in(event, placeholder):
    current = event.widget.get()
    if current == placeholder:
        event.widget.delete(0, tk.END)
        event.widget.config(fg="black")

def on_focus_out(event, placeholder):
    current = event.widget.get()
    if current == "":
        event.widget.insert(0, placeholder)
        event.widget.config(fg="gray")

def on_focus_in_password(event, placeholder):
    current = event.widget.get()
    if current == placeholder:
        event.widget.delete(0, tk.END)
        event.widget.config(fg="black", show="*")

def on_focus_out_password(event, placeholder):
    current = event.widget.get()
    if current == "":
        event.widget.insert(0, placeholder)
        event.widget.config(fg="gray", show="")

def reset_entry(entry, placeholder):
    entry.delete(0, tk.END)
    entry.insert(0, placeholder)
    entry.config(fg="gray")

def show_main_screen():
    global data, main_window, listbox

    if 'main_window' in globals():
        main_window.destroy()

    main_window = tk.Toplevel(root)
    main_window.title("Byte Me Fitness Tracker")
    main_window.geometry("600x600")
    main_window.configure(bg="#f5f5f5")

    listbox_frame = tk.Frame(main_window, bg="#f5f5f5", bd=2, relief="solid")
    listbox_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

    listbox = tk.Listbox(listbox_frame, font=("Arial", 12), height=10, width=25, bg="#f9f9f9", selectmode=tk.SINGLE, bd=2, relief="solid")
    listbox.pack(fill=tk.BOTH, expand=True)

    update_listbox()

    steps_entry = create_entry(main_window, "Enter steps:", 20, 20)
    calories_entry = create_entry(main_window, "Enter calories:", 20, 80)
    workout_entry = create_entry(main_window, "Enter workout:", 20, 140)

    def update_steps():
        try:
            steps = int(steps_entry.get())
            if steps < 0:
                raise ValueError("Steps cannot be negative.")
            data['steps'] += steps
            data['daily']['steps'] += steps
            update_listbox()
            reset_entry(steps_entry, "Enter steps:")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for steps: {e}")

    def update_calories():
        try:
            calories = int(calories_entry.get())
            if calories < 0:
                raise ValueError("Calories cannot be negative.")
            data['calories'] += calories
            data['daily']['calories'] += calories
            update_listbox()
            reset_entry(calories_entry, "Enter calories:")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for calories: {e}")

    def log_workout():
        workout = workout_entry.get().strip()
        if workout == "" or workout == "Enter workout:":
            messagebox.showerror("Input Error", "Please enter a valid workout description.")
        else:
            data['workouts'] += 1
            data['daily']['workouts'] += 1
            data['workout_log'].append(workout)
            update_listbox()
            reset_entry(workout_entry, "Enter workout:")

    def edit_selected_entry():
        selected = listbox.curselection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select an item to edit.")
            return
        
        selected_index = selected[0]
        selected_item = listbox.get(selected_index)

        if selected_item.startswith("Total Steps:") or selected_item.startswith("Total Calories:"):
            current_value = int(selected_item.split(":")[1].strip())
            new_value = ask_for_edit_value("Edit Value", current_value)
            if new_value is not None:
                if selected_item.startswith("Total Steps:"):
                    data['steps'] = new_value
                    data['daily']['steps'] = new_value
                elif selected_item.startswith("Total Calories:"):
                    data['calories'] = new_value
                    data['daily']['calories'] = new_value
                update_listbox()

        elif selected_item.startswith(" - "):
            selected_workout = selected_item[3:]
            new_workout = ask_for_edit_value("Edit Workout", selected_workout, is_workout=True)
            if new_workout is not None:
                data['workout_log'][selected_index - 3] = new_workout
                update_listbox()

    def ask_for_edit_value(title, current_value, is_workout=False):
        edit_window = tk.Toplevel(main_window)
        edit_window.title(title)
        edit_window.geometry("300x200")

        edit_label = tk.Label(edit_window, text=f"Current value: {current_value}", font=("Arial", 12))
        edit_label.pack(pady=10)

        entry = tk.Entry(edit_window, font=("Arial", 12))
        entry.pack(pady=10)
        entry.insert(0, current_value)

        def save_edit():
            new_value = entry.get().strip()
            if is_workout and not new_value:
                messagebox.showerror("Input Error", "Workout cannot be empty.")
                return
            if not is_workout:
                try:
                    new_value = int(new_value)
                    if new_value < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid number.")
                    return
            edit_window.destroy()
            update_data(new_value, current_value, is_workout)

        save_button = tk.Button(edit_window, text="Save", font=("Arial", 12), command=save_edit)
        save_button.pack(pady=10)

        edit_window.mainloop()

    def update_data(new_value, current_value, is_workout):
        global data

        if isinstance(current_value, int):
            if current_value == data['steps']:
                data['steps'] = new_value
                data['daily']['steps'] = new_value
            elif current_value == data['calories']:
                data['calories'] = new_value
                data['daily']['calories'] = new_value
        else:
            workout_index = data['workout_log'].index(current_value)
            data['workout_log'][workout_index] = new_value

        update_listbox()

    def save_data():
        try:
            with open("fitness_data.json", "w") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Save Data", "Data has been saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {e}")

    update_steps_btn = tk.Button(main_window, text="Log Steps", font=("Arial", 12), command=update_steps, bg="#4CAF50", fg="white", relief="raised", width=20)
    update_steps_btn.grid(row=3, column=0, pady=10, padx=20, sticky="w")

    update_calories_btn = tk.Button(main_window, text="Log Calories", font=("Arial", 12), command=update_calories, bg="#FF5733", fg="white", relief="raised", width=20)
    update_calories_btn.grid(row=4, column=0, pady=10, padx=20, sticky="w")

    log_workout_btn = tk.Button(main_window, text="Log Workout", font=("Arial", 12), command=log_workout, bg="#2196F3", fg="white", relief="raised", width=20)
    log_workout_btn.grid(row=5, column=0, pady=10, padx=20, sticky="w")

    save_btn = tk.Button(main_window, text="Save Data", font=("Arial", 12), command=save_data, bg="#4CAF50", fg="white", relief="raised", width=20)
    save_btn.grid(row=8, column=0, pady=10, padx=20, sticky="w")

    edit_btn = tk.Button(main_window, text="Edit Selected", font=("Arial", 12), command=edit_selected_entry, bg="#FFC107", fg="white", relief="raised", width=20)
    edit_btn.grid(row=6, column=0, pady=10, padx=20, sticky="w")

    reset_btn = tk.Button(main_window, text="Reset Data", font=("Arial", 12), command=reset_data, bg="red", fg="white", relief="raised", width=20)
    reset_btn.grid(row=7, column=0, pady=10, padx=20, sticky="w")

def update_listbox():
    listbox.delete(0, tk.END)
    listbox.insert(tk.END, f"Total Steps: {data['steps']}")
    listbox.insert(tk.END, f"Total Calories: {data['calories']}")
    listbox.insert(tk.END, f"Workouts Logged: {len(data['workout_log'])}")
    for workout in data['workout_log']:
        listbox.insert(tk.END, f" - {workout}")

def reset_data():
    confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the data?")
    if confirm:
        global data
        data = {'steps': 0, 'calories': 0, 'workouts': 0, 'daily': {'steps': 0, 'calories': 0, 'workouts': 0}, 'workout_log': []}
        update_listbox()

root = tk.Tk()
root.withdraw()
show_login_screen()
root.mainloop()
