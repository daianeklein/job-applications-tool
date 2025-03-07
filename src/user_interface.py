import tkinter as tk
from tkinter import ttk

class UserInterface:
    def show_edit_dialog(self, field_name: str, current_value: str, new_value: str) -> str:
        dialog = tk.Tk()
        dialog.title(f"Review {field_name}")
        dialog.geometry("1000x600")

        tk.Label(dialog, text=f"Current {field_name}:", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Label(dialog, wraplength=500, text=current_value).pack(pady=5)

        tk.Label(dialog, text=f"Suggested {field_name}:", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Label(dialog, wraplength=500, text=new_value).pack(pady=5)

        tk.Label(dialog, text="Edit if needed:", font=("Arial", 10, "bold")).pack(pady=5)
        edit_field = tk.Text(dialog, width=80, height=15)
        edit_field.insert("1.0", new_value)
        edit_field.pack(pady=10)

        result = {"value": new_value}

        def on_accept():
            result["value"] = edit_field.get("1.0", "end-1c").strip()
            dialog.destroy()

        def on_cancel():
            result["value"] = current_value
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Accept", command=on_accept).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT)

        dialog.mainloop()
        return result["value"]
