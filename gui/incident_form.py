"""
gui/incident_form.py - Tkinter view for incident registration and management.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.incident import DisasterIncident

class IncidentForm(ttk.Frame):
    """
    Form to register new disaster incidents and log table to display reported incidents.
    """
    def __init__(self, parent, platform):
        super().__init__(parent)
        self.platform = platform
        
        # Configure Grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        
        # Style Definitions
        self.dark_bg = "#080c14"
        self.card_bg = "#131a2c"
        self.text_color = "#f8fafc"
        self.accent_indigo = "#6366f1"
        self.accent_green = "#10b981"
        self.accent_red = "#ef4444"
        
        # Left Panel - Form Container
        self.left_frame = ttk.LabelFrame(self, text="Report New Incident", padding=15)
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.setup_form()
        
        # Right Panel - Log Table Container
        self.right_frame = ttk.LabelFrame(self, text="Incident Log", padding=15)
        self.right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.setup_table()
        
        self.refresh()

    def setup_form(self):
        # Grid config
        self.left_frame.columnconfigure(1, weight=1)
        
        # 1. Location Selection
        ttk.Label(self.left_frame, text="Location:").grid(row=0, column=0, sticky="w", pady=6)
        self.loc_var = tk.StringVar()
        self.loc_cb = ttk.Combobox(self.left_frame, textvariable=self.loc_var, state="readonly")
        # Populate with graph node IDs
        self.loc_cb["values"] = sorted(list(self.platform.graph.nodes.keys()))
        self.loc_cb.grid(row=0, column=1, sticky="ew", pady=6)
        if self.loc_cb["values"]:
            self.loc_cb.current(0)

        # 2. Disaster Type Selection
        ttk.Label(self.left_frame, text="Disaster Type:").grid(row=1, column=0, sticky="w", pady=6)
        self.type_var = tk.StringVar()
        self.type_cb = ttk.Combobox(self.left_frame, textvariable=self.type_var, state="readonly")
        self.type_cb["values"] = ["Flood", "Earthquake", "Cyclone", "Tsunami", "Fire", "Wildfire", "Landslide"]
        self.type_cb.grid(row=1, column=1, sticky="ew", pady=6)
        self.type_cb.current(0)

        # 3. Severity Level
        ttk.Label(self.left_frame, text="Severity Level (Auto):").grid(row=2, column=0, sticky="w", pady=6)
        self.sev_var = tk.StringVar()
        self.sev_cb = ttk.Combobox(self.left_frame, textvariable=self.sev_var, state="disabled")
        self.sev_cb["values"] = ["Low", "Medium", "High", "Critical"]
        self.sev_cb.grid(row=2, column=1, sticky="ew", pady=6)

        # 4. Population Affected
        ttk.Label(self.left_frame, text="Population Affected:").grid(row=3, column=0, sticky="w", pady=6)
        self.pop_entry = ttk.Entry(self.left_frame)
        self.pop_entry.insert(0, "1000")
        self.pop_entry.grid(row=3, column=1, sticky="ew", pady=6)
        
        # Bind events for real-time severity calculation
        self.pop_entry.bind("<KeyRelease>", self.update_severity_from_population)
        self.update_severity_from_population()

        # 5. Reporter
        ttk.Label(self.left_frame, text="Reporter:").grid(row=4, column=0, sticky="w", pady=6)
        self.rep_entry = ttk.Entry(self.left_frame)
        self.rep_entry.insert(0, "Field Unit")
        self.rep_entry.grid(row=4, column=1, sticky="ew", pady=6)

        # 6. Description
        ttk.Label(self.left_frame, text="Description:").grid(row=5, column=0, sticky="nw", pady=6)
        self.desc_text = tk.Text(self.left_frame, height=5, wrap="word", width=25)
        self.desc_text.grid(row=5, column=1, sticky="ew", pady=6)

        # 7. Submit Button
        self.submit_btn = ttk.Button(self.left_frame, text="⚠️ Register Incident", command=self.submit_incident)
        self.submit_btn.grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

    def setup_table(self):
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(self.right_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(self.right_frame, orient="horizontal")
        
        # Treeview
        cols = ("ID", "Location", "Type", "Severity", "Population", "Status")
        self.tree = ttk.Treeview(
            self.right_frame, columns=cols, show="headings", 
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )
        
        # Scrollbars layout
        scroll_y.config(command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.config(command=self.tree.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns
        widths = {"ID": 70, "Location": 130, "Type": 90, "Severity": 80, "Population": 90, "Status": 90}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], anchor="center")
            
        # Resolve Button
        self.resolve_btn = ttk.Button(self.right_frame, text="✓ Resolve Selected Incident", command=self.resolve_incident)
        self.resolve_btn.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

    def update_severity_from_population(self, event=None):
        pop_str = self.pop_entry.get().strip()
        if not pop_str.isdigit():
            return
        pop = int(pop_str)
        if pop < 1000:
            sev = "Low"
        elif pop < 5000:
            sev = "Medium"
        elif pop < 20000:
            sev = "High"
        else:
            sev = "Critical"
        self.sev_var.set(sev)

    def submit_incident(self):
        # Retrieve values
        loc_id = self.loc_var.get()
        dtype = self.type_var.get()
        sev = self.sev_var.get()
        pop_str = self.pop_entry.get().strip()
        reporter = self.rep_entry.get().strip()
        desc = self.desc_text.get("1.0", "end-1c").strip()
        
        # Validation
        if not pop_str.isdigit() or int(pop_str) <= 0:
            messagebox.showerror("Validation Error", "Population affected must be a positive integer.")
            return
            
        pop = int(pop_str)
        if not reporter:
            reporter = "Anonymous"
            
        try:
            # Report using platform orchestrator
            self.platform.report_incident(
                location_id=loc_id,
                disaster_type=dtype,
                severity=sev,
                population_affected=pop,
                description=desc,
                reporter=reporter
            )
            messagebox.showinfo("Success", f"Incident registered successfully!")
            self.desc_text.delete("1.0", "end")
            
            # Broadcast refresh to parent window (which updates other tabs)
            self.master.master.refresh_all_tabs()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register incident: {str(e)}")

    def resolve_incident(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an incident from the log table.")
            return
            
        item_values = self.tree.item(selected[0], "values")
        incident_id = item_values[0]
        
        if self.platform.resolve_incident(incident_id):
            messagebox.showinfo("Resolved", f"Incident '{incident_id}' has been marked as Resolved.")
            self.master.master.refresh_all_tabs()
        else:
            messagebox.showerror("Error", "Could not resolve incident.")

    def refresh(self):
        # Update locations dropdown just in case
        self.loc_cb["values"] = sorted(list(self.platform.graph.nodes.keys()))
        
        # Clear log treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Repopulate table
        for inc in self.platform.incidents:
            node = self.platform.graph.nodes.get(inc.location)
            loc_name = node.name if node else inc.location
            self.tree.insert(
                "", "end", 
                values=(
                    inc.incident_id, 
                    f"{inc.location} ({loc_name})", 
                    inc.disaster_type, 
                    inc.severity_level_str, 
                    f"{inc.population_affected:,}", 
                    inc.status
                )
            )
