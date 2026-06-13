"""
gui/main_window.py - Main Tkinter window with tabbed notebook layout and custom dark theme.
"""
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from modules.platform_orchestrator import DisasterPlatform

# Import custom frames
from gui.incident_form import IncidentForm
from gui.resource_panel import ResourcePanel
from gui.dashboard_frame import DashboardFrame

class MainWindow(tk.Tk):
    """
    Main Tkinter application window for DisasterOS.
    Implements a custom dark theme and tabbed layout.
    """
    def __init__(self, platform=None):
        super().__init__()
        self.platform = platform or DisasterPlatform(bootstrap=True)
        
        # State variables for mapping
        self.highlight_path = None
        self.highlight_shelters = None
        
        # Setup Window Title & Geometry
        self.title("DisasterOS -- Smart Emergency Management Center")
        self.geometry("1024x720")
        self.minsize(800, 600)
        
        # Apply Dark Theme Styles
        self.apply_dark_styles()
        self.configure(background="#080c14")
        
        # Top Header Banner
        header = tk.Frame(self, bg="#0e1320", height=50)
        header.pack(fill="x", side="top")
        header_lbl = tk.Label(
            header, text="🚨 Smart Disaster Response & Resource Allocation Control Center", 
            font=("Arial", 12, "bold"), fg="#10b981", bg="#0e1320", pady=10
        )
        header_lbl.pack(side="left", padx=15)
        
        pdf_btn = ttk.Button(
            header, text="📝 Export PDF Report", 
            command=self.export_pdf_report
        )
        pdf_btn.pack(side="right", padx=15, pady=8)
        
        # Create Notebook (Tab Container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Incidents Form
        self.incident_form = IncidentForm(self.notebook, self.platform)
        self.notebook.add(self.incident_form, text="📝 Incidents Registry")
        
        # Tab 2: Resource Allocations
        self.resource_panel = ResourcePanel(self.notebook, self.platform)
        self.notebook.add(self.resource_panel, text="📦 Resource Inventory")
        
        # Tab 3: Shelter Recommendation
        self.shelter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.shelter_tab, text="🏥 Shelter Recommendation")
        self.setup_shelter_tab()
        
        # Tab 4: Route Planning
        self.route_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.route_tab, text="🗺️ Rescue Route Planner")
        self.setup_route_tab()
        
        # Tab 5: Analytics Charts
        self.charts_frame = DashboardFrame(self.notebook, self.platform)
        self.notebook.add(self.charts_frame, text="📊 Analytics Dashboard")
        
        # Initial refresh
        self.refresh_all_tabs()

    def apply_dark_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        bg_dark = "#080c14"
        bg_card = "#131a2c"
        fg_light = "#f8fafc"
        accent_indigo = "#6366f1"
        
        style.configure(".", background=bg_dark, foreground=fg_light, fieldbackground=bg_card)
        style.configure("TLabel", background=bg_dark, foreground=fg_light)
        style.configure("TButton", background=bg_card, foreground=fg_light, borderwidth=0, padding=6)
        style.map("TButton", background=[("active", accent_indigo)])
        style.configure("TCombobox", background=bg_card, foreground=fg_light, fieldbackground=bg_card)
        style.configure("TNotebook", background=bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_card, foreground=fg_light, borderwidth=0, padding=(12, 5))
        style.map("TNotebook.Tab", background=[("selected", bg_dark)], foreground=[("selected", "#6366f1")])
        style.configure("Treeview", background=bg_card, foreground=fg_light, fieldbackground=bg_card, rowheight=24)
        style.configure("Treeview.Heading", background="#1e293b", foreground=fg_light)

    # ── BFS Shelter Tab UI ─────────────────────────────────────────
    def setup_shelter_tab(self):
        self.shelter_tab.columnconfigure(0, weight=1)
        self.shelter_tab.rowconfigure(1, weight=1)
        
        control_frame = ttk.LabelFrame(self.shelter_tab, text="Select Affected Zone Incident", padding=10)
        control_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        
        ttk.Label(control_frame, text="Incident:").pack(side="left", padx=5)
        self.shelter_inc_var = tk.StringVar()
        self.shelter_inc_cb = ttk.Combobox(control_frame, textvariable=self.shelter_inc_var, state="readonly", width=40)
        self.shelter_inc_cb.pack(side="left", padx=5)
        
        recommend_btn = ttk.Button(control_frame, text="🏥 Run BFS Shelter Recommendation", command=self.run_shelter_bfs)
        recommend_btn.pack(side="left", padx=15)
        
        # Results table
        cols = ("Shelter Name", "Hops", "Distance", "Vacancy", "Occupancy Pct", "Navigable Route")
        self.shelter_tree = ttk.Treeview(self.shelter_tab, columns=cols, show="headings")
        self.shelter_tree.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        widths = {"Shelter Name": 180, "Hops": 60, "Distance": 90, "Vacancy": 90, "Occupancy Pct": 100, "Navigable Route": 300}
        for col in cols:
            self.shelter_tree.heading(col, text=col)
            self.shelter_tree.column(col, width=widths[col], anchor="w" if col == "Navigable Route" or col == "Shelter Name" else "center")
            
        action_frame = ttk.Frame(self.shelter_tab)
        action_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        
        map_btn = ttk.Button(action_frame, text="🗺️ Open Shelter Map in Browser", command=self.open_interactive_map)
        map_btn.pack(side="left", padx=5)
        
        admit_btn = ttk.Button(action_frame, text="✓ Evacuate and Admit to Selected Shelter", command=self.admit_to_shelter)
        admit_btn.pack(side="right", padx=5)

    def run_shelter_bfs(self):
        inc_str = self.shelter_inc_var.get()
        if not inc_str:
            messagebox.showwarning("Warning", "Please select an incident first.")
            return
            
        inc_id = inc_str.split(" | ")[0]
        
        try:
            recs = self.platform.recommend_shelters(inc_id)
            # Clear table
            for item in self.shelter_tree.get_children():
                self.shelter_tree.delete(item)
                
            self.highlight_shelters = [r["node_id"] for r in recs]
            
            # Repopulate
            for r in recs:
                path_str = " ➔ ".join(r["path"])
                self.shelter_tree.insert(
                    "", "end",
                    values=(
                        f"{r['shelter_id']} - {r['name']}",
                        r["bfs_hops"],
                        f"{r['distance_km']} km",
                        f"{r['available_capacity']:,}",
                        f"{r['occupancy_pct']}%",
                        path_str
                    )
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to recommend shelters: {str(e)}")

    def admit_to_shelter(self):
        selected = self.shelter_tree.selection()
        inc_str = self.shelter_inc_var.get()
        if not selected or not inc_str:
            messagebox.showwarning("Selection Required", "Please select an incident and a recommended shelter.")
            return
            
        inc_id = inc_str.split(" | ")[0]
        shelter_val = self.shelter_tree.item(selected[0], "values")[0]
        shelter_id = shelter_val.split(" - ")[0]  # SH001
        
        incident = self.platform.get_incident(inc_id)
        # Find shelter node in platform
        shelter_node = None
        for s in self.platform.shelters.values():
            if s.shelter_id == shelter_id:
                shelter_node = s
                break
                
        if not incident or not shelter_node:
            messagebox.showerror("Error", "Could not locate incident or shelter node.")
            return
            
        # Admit population
        admitted = shelter_node.update_occupancy(incident.population_affected)
        incident.assigned_shelter = shelter_node.name
        
        # If population is fully evacuated, we resolve it
        if admitted >= incident.population_affected:
            incident.status = "Resolved"
            messagebox.showinfo("Evacuation Success", f"Successfully evacuated {admitted:,} citizens to {shelter_node.name}. Incident marked as Resolved!")
        else:
            incident.population_affected -= admitted
            messagebox.showinfo("Partial Evacuation", f"Admitted {admitted:,} citizens to {shelter_node.name}. Shelter is now full! {incident.population_affected:,} citizens still need shelter.")
            
        self.refresh_all_tabs()

    # ── Dijkstra Route Tab UI ──────────────────────────────────────
    def setup_route_tab(self):
        self.route_tab.columnconfigure(0, weight=1)
        self.route_tab.rowconfigure(1, weight=1)
        
        controls = ttk.LabelFrame(self.route_tab, text="Route Parameters", padding=10)
        controls.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)
        
        ttk.Label(controls, text="Source Node:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.src_var = tk.StringVar()
        self.src_cb = ttk.Combobox(controls, textvariable=self.src_var, state="readonly")
        self.src_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(controls, text="Target Node:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.dst_var = tk.StringVar()
        self.dst_cb = ttk.Combobox(controls, textvariable=self.dst_var, state="readonly")
        self.dst_cb.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        plan_btn = ttk.Button(controls, text="⚡ Run Dijkstra Route Planner", command=self.run_route_dijkstra)
        plan_btn.grid(row=0, column=4, padx=15, pady=5)
        
        # Results frame
        self.route_res_frame = ttk.LabelFrame(self.route_tab, text="Calculated Route Details", padding=15)
        self.route_res_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        self.route_res_frame.columnconfigure(0, weight=1)
        
        self.route_summary_lbl = ttk.Label(
            self.route_res_frame, text="Select source and target nodes to plan dispatch route.", 
            font=("Arial", 11, "bold"), wraplength=700, justify="left"
        )
        self.route_summary_lbl.grid(row=0, column=0, sticky="w", pady=5)
        
        self.route_text = tk.Text(self.route_res_frame, height=10, wrap="word", font=("Courier New", 10))
        self.route_text.grid(row=1, column=0, sticky="nsew", pady=10)
        self.route_text.config(state="disabled")
        
        map_btn = ttk.Button(self.route_res_frame, text="🗺️ Open Rescue Route in Web Browser", command=self.open_interactive_map)
        map_btn.grid(row=2, column=0, sticky="w")

    def run_route_dijkstra(self):
        src = self.src_var.get()
        dst = self.dst_var.get()
        
        if not src or not dst:
            messagebox.showwarning("Warning", "Please select both source and target nodes.")
            return
            
        src_id = src.split(" | ")[0]
        dst_id = dst.split(" | ")[0]
        
        try:
            route = self.platform.plan_rescue_route(src_id, dst_id)
            if "error" in route:
                messagebox.showerror("No Path", "No route found between selected nodes.")
                return
                
            self.highlight_path = route["path_ids"]
            
            # Format text
            self.route_summary_lbl.config(
                text=f"Shortest Safest Route: {route['source']} ➔ {route['target']}\n"
                     f"Distance: {route['total_cost']} km | Hops: {route['hops']}"
            )
            
            path_names_str = " ➔ ".join(route["path_names"])
            nodes_details = []
            for nid in route["path_ids"]:
                node = self.platform.graph.nodes[nid]
                nodes_details.append(f"  • {nid}: {node.name} ({node.loc_type})")
                
            details_str = (
                f"RESCUE ROUTE DISPATCH SCHEDULE\n"
                f"========================================\n"
                f"Source:      {route['source']} ({src_id})\n"
                f"Destination: {route['target']} ({dst_id})\n"
                f"Cost (km):   {route['total_cost']} km\n"
                f"Total Hops:  {route['hops']}\n\n"
                f"Routing path:\n{path_names_str}\n\n"
                f"Stop Details:\n" + "\n".join(nodes_details)
            )
            
            self.route_text.config(state="normal")
            self.route_text.delete("1.0", "end")
            self.route_text.insert("1.0", details_str)
            self.route_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Routing calculation failed: {str(e)}")

    # ── Map launcher ───────────────────────────────────────────────
    def open_interactive_map(self):
        """Generates the Folium map and opens it in default web browser."""
        try:
            html_content = self.platform.generate_map(
                highlight_path=self.highlight_path, 
                highlight_shelters=self.highlight_shelters
            )
            os.makedirs("outputs/maps", exist_ok=True)
            map_path = os.path.abspath("outputs/maps/map.html")
            with open(map_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            webbrowser.open("file://" + map_path)
        except Exception as e:
            messagebox.showerror("Map Error", f"Could not launch browser map: {str(e)}")

    # ── Refresh Coordination ───────────────────────────────────────
    def refresh_all_tabs(self):
        """Broadcasts refresh command to all sub-tabs to keep data synchronized."""
        # 1. Update registries
        nodes_list = sorted([f"{nid} | {n.name}" for nid, n in self.platform.graph.nodes.items()])
        self.src_cb["values"] = nodes_list
        self.dst_cb["values"] = nodes_list
        
        inc_list = sorted([
            f"{i.incident_id} | {self.platform.graph.nodes[i.location].name} ({i.disaster_type})" 
            for i in self.platform.incidents if i.status.lower() != "resolved"
        ])
        self.shelter_inc_cb["values"] = inc_list
        
        # Set selection values if empty
        if not self.src_var.get() and nodes_list:
            self.src_cb.current(0)
        if not self.dst_var.get() and nodes_list:
            self.dst_cb.current(0)
        if not self.shelter_inc_var.get() and inc_list:
            self.shelter_inc_cb.current(0)

        # 2. Refresh frames
        self.incident_form.refresh()
        self.resource_panel.refresh()
        self.charts_frame.refresh()

    def export_pdf_report(self):
        try:
            import os
            os.makedirs("outputs/reports", exist_ok=True)
            path = os.path.abspath("outputs/reports/incident_report.pdf")
            self.platform.export_pdf_report(path)
            messagebox.showinfo("Export Success", f"Successfully exported PDF report to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF report: {str(e)}")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
