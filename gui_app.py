import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, Text

import grpc
import notes_pb2
import notes_pb2_grpc

# --- 1. Define Color Palette & Fonts ---
COLOR_PRIMARY_DARK = "#001f3f"
COLOR_PRIMARY_LIGHT = "#003366"
COLOR_SECONDARY_LIGHT = "#f4f7fa"
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_TEXT_DARK = "#333333"
COLOR_TEXT_MUTED = "#b0bec5"
COLOR_SUCCESS = "#28a745"
COLOR_DANGER = "#dc3545"
FONT_PRIMARY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")


class NoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("gRPC Note App (Python GUI)")
        self.geometry("800x600")
        self.configure(bg=COLOR_SECONDARY_LIGHT)
        self.setup_styles()

        try:
            self.channel = grpc.insecure_channel('localhost:50051')
            self.stub = notes_pb2_grpc.NoteServiceStub(self.channel)
            self.stub.ListNotes(notes_pb2.ListNotesRequest(), timeout=1.0)
        except grpc.RpcError as e:
            messagebox.showerror("Connection Error",
                                 f"Could not connect to gRPC server...\n"
                                 f"Please ensure Docker is running.\n\nError: {e.details()}")
            self.destroy()
            return

        self.create_widgets()
        self.list_all_notes()

    def setup_styles(self):
        """Creates all the custom styles for our ttk widgets."""
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TFrame', background=COLOR_SECONDARY_LIGHT)
        style.configure('Sidebar.TFrame', background=COLOR_PRIMARY_DARK)

        style.configure('TLabel', background=COLOR_SECONDARY_LIGHT, foreground=COLOR_TEXT_DARK, font=FONT_PRIMARY)
        style.configure('H1.TLabel', font=FONT_TITLE, background=COLOR_SECONDARY_LIGHT)
        style.configure('Sidebar.TLabel', background=COLOR_PRIMARY_DARK, foreground=COLOR_TEXT_LIGHT, font=FONT_PRIMARY)

        style.configure('TButton', font=FONT_PRIMARY, padding=6)
        style.configure('Sidebar.TButton', font=FONT_PRIMARY, background=COLOR_PRIMARY_DARK,
                        foreground=COLOR_TEXT_LIGHT, padding=10)
        style.map('Sidebar.TButton', background=[('active', COLOR_PRIMARY_LIGHT)],
                  foreground=[('active', COLOR_TEXT_LIGHT)])
        style.configure('Success.TButton', background=COLOR_SUCCESS, foreground=COLOR_TEXT_LIGHT)
        style.map('Success.TButton', background=[('active', '#218838')])
        style.configure('Danger.TButton', background=COLOR_DANGER, foreground=COLOR_TEXT_LIGHT)
        style.map('Danger.TButton', background=[('active', '#c82333')])

        style.configure('TEntry', font=FONT_PRIMARY, padding=5)

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Left Frame (Sidebar) ---
        sidebar_frame = ttk.Frame(self, width=220, style='Sidebar.TFrame')
        sidebar_frame.grid(row=0, column=0, sticky="nsw")
        sidebar_frame.grid_propagate(False)

        ttk.Button(sidebar_frame, text="Create New Note", command=self.open_create_note_window,
                   style='Sidebar.TButton').pack(fill="x", pady=10, padx=10)
        ttk.Button(sidebar_frame, text="List All Notes", command=self.list_all_notes, style='Sidebar.TButton').pack(
            fill="x", pady=10, padx=10)

        # --- Search Frame REMOVED ---

        # --- Get/Delete by ID ---
        id_frame = ttk.Frame(sidebar_frame, style='Sidebar.TFrame')
        id_frame.pack(fill="x", pady=20, padx=10)
        ttk.Label(id_frame, text="Enter Note ID:", style='Sidebar.TLabel').pack()
        self.id_entry = ttk.Entry(id_frame)
        self.id_entry.pack(fill="x", pady=5)
        ttk.Button(id_frame, text="Get by ID", command=self.get_note_by_id, style='Sidebar.TButton').pack(fill="x",
                                                                                                          pady=5)
        ttk.Button(id_frame, text="Delete by ID", command=self.delete_note_by_id, style='Danger.TButton').pack(fill="x",
                                                                                                               pady=5)

        # --- Right Frame (Main Content) ---
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="Notes List:", style='H1.TLabel').grid(row=0, column=0, sticky="w", pady=5)

        list_frame = ttk.Frame(main_frame, style='TFrame')
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.notes_listbox = tk.Listbox(list_frame,
                                        yscrollcommand=scrollbar.set,
                                        font=("Courier", 11),
                                        height=25,
                                        background="white",
                                        foreground=COLOR_TEXT_DARK,
                                        borderwidth=0,
                                        highlightthickness=0,
                                        selectbackground=COLOR_PRIMARY_LIGHT,
                                        selectforeground=COLOR_TEXT_LIGHT)
        scrollbar.config(command=self.notes_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.notes_listbox.grid(row=0, column=0, sticky="nsew")
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

    # --- gRPC Handler Functions ---

    def list_all_notes(self):
        self.notes_listbox.delete(0, tk.END)
        try:
            response = self.stub.ListNotes(notes_pb2.ListNotesRequest())
            if not response.notes:
                self.notes_listbox.insert(tk.END, "  No notes found.")

            for note in response.notes:
                # --- FIX for parenthesis bug ---
                self.notes_listbox.insert(tk.END, f"  {note.title:<30} | ID: {note.id}")
        except grpc.RpcError as e:
            messagebox.showerror("Server Error", f"Could not list notes: {e.details()}")

    # --- search_by_title function REMOVED ---

    def get_note_by_id(self):
        note_id = self.id_entry.get()
        if not note_id:
            messagebox.showwarning("Input Error", "Please enter a Note ID.")
            return
        try:
            request = notes_pb2.GetNoteRequest(id=note_id)
            response = self.stub.GetNote(request)
            if not response.note.id:
                messagebox.showerror("Not Found", f"Note with ID '{note_id}' not found.")
                return
            self.show_note_details(response.note)
        except grpc.RpcError as e:
            messagebox.showerror("Server Error", f"Could not get note: {e.details()}")

    def delete_note_by_id(self):
        note_id = self.id_entry.get()
        if not note_id:
            messagebox.showwarning("Input Error", "Please enter a Note ID.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete note {note_id}?"):
            return
        try:
            request = notes_pb2.DeleteNoteRequest(id=note_id)
            response = self.stub.DeleteNote(request)
            if response.success:
                messagebox.showinfo("Success", response.message)
                self.id_entry.delete(0, tk.END)
                self.list_all_notes()
            else:
                messagebox.showerror("Error", response.message)
        except grpc.RpcError as e:
            messagebox.showerror("Server Error", f"Could not delete note: {e.details()}")

    def open_create_note_window(self):
        create_window = Toplevel(self)
        create_window.title("Create New Note")
        create_window.geometry("400x350")
        create_window.configure(bg=COLOR_SECONDARY_LIGHT)
        create_window.resizable(False, False)

        form_frame = ttk.Frame(create_window, padding=10)
        form_frame.pack(fill="both", expand=True)

        def submit_create():
            title = title_entry.get()
            content = content_text.get("1.0", tk.END).strip()
            if not title:
                messagebox.showwarning("Input Error", "Title is required.", parent=create_window)
                return
            request = notes_pb2.CreateNoteRequest(title=title, content=content)
            try:
                response = self.stub.CreateNote(request)
                messagebox.showinfo("Success", f"Note created with ID: {response.id}", parent=create_window)
                create_window.destroy()
                self.list_all_notes()
            except grpc.RpcError as e:
                messagebox.showerror("Server Error", f"Could not create note: {e.details()}", parent=create_window)

        # --- FIX for create button ---
        submit_button = ttk.Button(form_frame, text="Create", command=submit_create, style='Success.TButton')
        submit_button.pack(side=tk.BOTTOM, pady=(10, 0))

        ttk.Label(form_frame, text="Title:").pack(anchor='w')
        title_entry = ttk.Entry(form_frame, width=50)
        title_entry.pack(fill="x", pady=(5, 10))

        ttk.Label(form_frame, text="Content:").pack(anchor='w')
        content_text = Text(form_frame, height=10, width=50,
                            background="white", foreground=COLOR_TEXT_DARK,
                            borderwidth=0, highlightthickness=1,
                            font=FONT_PRIMARY)
        content_text.pack(fill="both", expand=True)

    def on_note_select(self, event):
        selected_indices = self.notes_listbox.curselection()
        if not selected_indices:
            return
        selected_line = self.notes_listbox.get(selected_indices[0])
        try:
            # --- FIX for parenthesis bug ---
            note_id = selected_line.split("ID: ")[1].strip()
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, note_id)
        except IndexError:
            pass

    def show_note_details(self, note):
        details_window = Toplevel(self)
        details_window.title(f"Details for: {note.title}")
        details_window.geometry("400x300")
        details_window.configure(bg=COLOR_SECONDARY_LIGHT)
        text_widget = Text(details_window, height=15, width=50,
                           font=("Helvetica", 10),
                           background="white", foreground=COLOR_TEXT_DARK,
                           borderwidth=0, highlightthickness=0,
                           padx=10, pady=10)
        text_widget.pack(pady=10, padx=10, fill="both", expand=True)
        text_widget.insert(tk.END, f"ID:\n{note.id}\n\n")
        text_widget.insert(tk.END, f"TITLE:\n{note.title}\n\n")
        text_widget.insert(tk.END, f"CONTENT:\n{note.content}")
        text_widget.config(state="disabled")


if __name__ == "__main__":
    app = NoteApp()
    app.mainloop()