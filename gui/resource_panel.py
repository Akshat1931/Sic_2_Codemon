"""
gui/resource_panel.py - Tkinter view for stockpile management and greedy allocation.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.resource import ResourceInventory

class ResourcePanel(ttk.Frame):
    """
    Panel displaying global resource inventory and coordinating greedy resource dispatching.
    """
    def __init__(self, parent, platform):
        super().__init__(parent)
        self.platform = platform
        
        # Grid Configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Left Panel - Stockpile meters and restock controls
        self.left_frame = ttk.LabelFrame(self, text="Global Stockpile Inventory", padding=15)
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.setup_inventory_view()
        
        # Right Panel - Allocation triggering & log
        self.right_frame = ttk.LabelFrame(self, text="Resource Dispatch & Deficit Logs", padding=15)
        self.right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.setup_allocation_view()
        
        self.refresh()

    def setup_inventory_view(self):
        self.left_frame.columnconfigure(1, weight=1)
        
        # Stockpile Labels and Progress Indicators
        ttk.Label(self.left_frame, text="Resource Stockpile Status", font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky="w")
        
        # Food Packets
        ttk.Label(self.left_frame, text="Food Packets:").grid(row=1, column=0, sticky="w", pady=8)
        self.food_lbl = ttk.Label(self.left_frame, text="0 / 120,000", font=("Arial", 10, "bold"))
        self.food_lbl.grid(row=1, column=1, sticky="w", padx=10)
        self.food_bar = ttk.Progressbar(self.left_frame, length=180, mode="determinate", maximum=120000)
        self.food_bar.grid(row=1, column=2, sticky="ew", pady=8)
        
        # Drinking Water
        ttk.Label(self.left_frame, text="Drinking Water (L):").grid(row=2, column=0, sticky="w", pady=8)
        self.water_lbl = ttk.Label(self.left_frame, text="0 / 200,000", font=("Arial", 10, "bold"))
        self.water_lbl.grid(row=2, column=1, sticky="w", padx=10)
        self.water_bar = ttk.Progressbar(self.left_frame, length=180, mode="determinate", maximum=200000)
        self.water_bar.grid(row=2, column=2, sticky="ew", pady=8)
        
        # Medical Kits
        ttk.Label(self.left_frame, text="Medical Kits:").grid(row=3, column=0, sticky="w", pady=8)
        self.med_lbl = ttk.Label(self.left_frame, text="0 / 2,000", font=("Arial", 10, "bold"))
        self.med_lbl.grid(row=3, column=1, sticky="w", padx=10)
        self.med_bar = ttk.Progressbar(self.left_frame, length=180, mode="determinate", maximum=2000)
        self.med_bar.grid(row=3, column=2, sticky="ew", pady=8)
        
        # Rescue Teams
        ttk.Label(self.left_frame, text="Rescue Teams:").grid(row=4, column=0, sticky="w", pady=8)
        self.rescue_lbl = ttk.Label(self.left_frame, text="0 / 50", font=("Arial", 10, "bold"))
        self.rescue_lbl.grid(row=4, column=1, sticky="w", padx=10)
        self.rescue_bar = ttk.Progressbar(self.left_frame, length=180, mode="determinate", maximum=50)
        self.rescue_bar.grid(row=4, column=2, sticky="ew", pady=8)
        
        # Separator
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=5, column=0, columnspan=3, pady=15, sticky="ew")
        
        # Restock Section
        ttk.Label(self.left_frame, text="Replenish Supplies", font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=3, pady=(0, 10), sticky="w")
        
        # Restock Food
        ttk.Label(self.left_frame, text="Add Food:").grid(row=7, column=0, sticky="w", pady=4)
        self.restock_food = ttk.Entry(self.left_frame, width=10)
        self.restock_food.insert(0, "10000")
        self.restock_food.grid(row=7, column=1, columnspan=2, sticky="w", pady=4)
        
        # Restock Water
        ttk.Label(self.left_frame, text="Add Water (L):").grid(row=8, column=0, sticky="w", pady=4)
        self.restock_water = ttk.Entry(self.left_frame, width=10)
        self.restock_water.insert(0, "20000")
        self.restock_water.grid(row=8, column=1, columnspan=2, sticky="w", pady=4)
        
        # Restock Medical
        ttk.Label(self.left_frame, text="Add Med Kits:").grid(row=9, column=0, sticky="w", pady=4)
        self.restock_med = ttk.Entry(self.left_frame, width=10)
        self.restock_med.insert(0, "500")
        self.restock_med.grid(row=9, column=1, columnspan=2, sticky="w", pady=4)
        
        # Restock Rescue Teams
        ttk.Label(self.left_frame, text="Add Rescue Teams:").grid(row=10, column=0, sticky="w", pady=4)
        self.restock_rescue = ttk.Entry(self.left_frame, width=10)
        self.restock_rescue.insert(0, "5")
        self.restock_rescue.grid(row=10, column=1, columnspan=2, sticky="w", pady=4)
        
        # Restock Button
        self.restock_btn = ttk.Button(self.left_frame, text="📦 Restock Stockpile", command=self.restock_inventory)
        self.restock_btn.grid(row=11, column=0, columnspan=3, pady=12, sticky="ew")

    def setup_allocation_view(self):
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(2, weight=1)
        
        # Strategy selection dropdown (polymorphism toggle - Section 13 of PDF)
        strat_frame = ttk.Frame(self.right_frame)
        strat_frame.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        
        ttk.Label(strat_frame, text="Allocation Model:").pack(side="left", padx=5)
        self.strat_var = tk.StringVar(value="Greedy")
        self.strat_cb = ttk.Combobox(strat_frame, textvariable=self.strat_var, values=["Greedy", "Knapsack (DP)"], state="readonly", width=15)
        self.strat_cb.pack(side="left", padx=5)
        
        # Dispatch Trigger
        self.dispatch_btn = ttk.Button(
            self.right_frame, text="⚡ Run Allocation Engine", 
            command=self.run_allocation
        )
        self.dispatch_btn.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        
        # Log Table
        cols = ("Incident ID", "Food Allocated", "Water Allocated", "Meds Allocated", "Teams Allocated", "Status")
        self.tree = ttk.Treeview(self.right_frame, columns=cols, show="headings")
        self.tree.grid(row=2, column=0, sticky="nsew")
        
        widths = {
            "Incident ID": 80, 
            "Food Allocated": 100, 
            "Water Allocated": 100, 
            "Meds Allocated": 90, 
            "Teams Allocated": 100, 
            "Status": 90
        }
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], anchor="center")
            
        # Scrollbars
        scroll_y = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        scroll_y.grid(row=1, column=1, sticky="ns")
        self.tree.config(yscrollcommand=scroll_y.set)

    def restock_inventory(self):
        try:
            food = int(self.restock_food.get().strip() or "0")
            water = int(self.restock_water.get().strip() or "0")
            meds = int(self.restock_med.get().strip() or "0")
            teams = int(self.restock_rescue.get().strip() or "0")
            
            if food < 0 or water < 0 or meds < 0 or teams < 0:
                raise ValueError("Quantities cannot be negative.")
                
            self.platform.global_inventory.restock({
                "food": food,
                "water": water,
                "medical_kits": meds,
                "rescue_teams": teams
            })
            
            messagebox.showinfo("Success", "Global stockpile inventory replenished.")
            self.master.master.refresh_all_tabs()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid restocking quantities: {str(e)}")

    def run_allocation(self):
        try:
            strategy_name = "greedy" if "Greedy" in self.strat_var.get() else "knapsack"
            log = self.platform.greedy_allocate_resources(strategy=strategy_name)
            if not log:
                messagebox.showinfo("Allocation Status", "No active incidents pending resource allocation.")
                return
                
            # Log results details
            details = []
            for entry in log:
                alloc = entry["allocated"]
                rem = entry["remaining_stock"]
                details.append(
                    f"• {entry['incident_id']} ({entry['location']}):\n"
                    f"  Allocated: Food: {alloc['food']:,}, Water: {alloc['water']:,}, Med Kits: {alloc['medical_kits']:,}, Teams: {alloc['rescue_teams']:,}"
                )
            
            summary = f"{self.strat_var.get()} Allocation Complete!\n\n" + "\n".join(details)
            messagebox.showinfo("Resource Dispatch Summary", summary)
            
            # Broadcast refresh
            self.master.master.refresh_all_tabs()
        except Exception as e:
            messagebox.showerror("Allocation Error", f"Greedy allocation failed: {str(e)}")

    def refresh(self):
        inv = self.platform.global_inventory
        
        # Update labels and progress bars
        self.food_lbl.config(text=f"{inv.food:,} / 120,000")
        self.food_bar.config(value=inv.food)
        
        self.water_lbl.config(text=f"{inv.water:,} / 200,000")
        self.water_bar.config(value=inv.water)
        
        self.med_lbl.config(text=f"{inv.medical_kits:,} / 2,000")
        self.med_bar.config(value=inv.medical_kits)
        
        self.rescue_lbl.config(text=f"{inv.rescue_teams:,} / 50")
        self.rescue_bar.config(value=inv.rescue_teams)

        # Clear allocation log table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Repopulate log table based on incidents that have resources allocated
        for inc in self.platform.incidents:
            if inc.allocated_resources:
                alloc = inc.allocated_resources
                self.tree.insert(
                    "", "end",
                    values=(
                        inc.incident_id,
                        f"{alloc.food:,}",
                        f"{alloc.water:,}",
                        f"{alloc.medical_kits:,}",
                        f"{alloc.rescue_teams:,}",
                        "Dispatched"
                    )
                )
