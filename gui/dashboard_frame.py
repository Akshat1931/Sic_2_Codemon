"""
gui/dashboard_frame.py - Tkinter view embedding Matplotlib charts.
"""
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class DashboardFrame(ttk.Frame):
    """
    Panel rendering Matplotlib data charts directly inside the Tkinter GUI.
    """
    def __init__(self, parent, platform):
        super().__init__(parent)
        self.platform = platform
        
        # Configure 2x2 Grid Layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.canvas_widgets = []
        self.refresh()

    def clear_canvas(self):
        """Destroys previous canvas widgets to avoid layering plots on refresh."""
        for widget in self.canvas_widgets:
            widget.destroy()
        self.canvas_widgets.clear()
        plt.close("all")  # Close all matplotlib figures to free memory

    def refresh(self):
        """Re-aggregates platform data and draws the 4 charts."""
        self.clear_canvas()
        
        incidents = self.platform.incidents
        if not incidents:
            # Show empty state label
            lbl = ttk.Label(self, text="No incident data available. Please register incidents first.", font=("Arial", 12))
            lbl.grid(row=0, column=0, columnspan=2, rowspan=2, pady=50)
            self.canvas_widgets.append(lbl)
            return

        # Prepare dark styles
        plt.style.use("dark_background")
        bg_color = "#080c14"  # Match Tkinter dark window background
        card_color = "#131a2c" # Match card background
        text_color = "#f8fafc"
        accent_colors = ["#6366f1", "#10b981", "#eab308", "#ef4444", "#8b5cf6", "#06b6d4"]
        
        # 1. CHART 1: Population Impact by Area (Horizontal Bar Chart)
        df = pd.DataFrame([i.to_dict() for i in incidents])
        df["population_affected"] = pd.to_numeric(df["population_affected"])
        
        active_df = df[df["status"].str.lower() != "resolved"]
        if not active_df.empty:
            loc_impact = active_df.groupby("location_id")["population_affected"].sum().sort_values(ascending=True)
            
            fig1, ax1 = plt.subplots(figsize=(4, 3), facecolor=bg_color)
            ax1.set_facecolor(card_color)
            
            y_pos = np.arange(len(loc_impact))
            bars = ax1.barh(y_pos, loc_impact.values, color=accent_colors[:len(loc_impact)], height=0.55)
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(loc_impact.index, color="#9ca3af", fontsize=8)
            
            for bar, val in zip(bars, loc_impact.values):
                ax1.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2, 
                         f"{val:,}", va="center", color=text_color, fontsize=8)
            
            ax1.set_title("Population Impact by Zone", color=text_color, fontsize=9, fontweight="bold")
            ax1.tick_params(colors="#9ca3af", labelsize=8)
            for spine in ax1.spines.values():
                spine.set_visible(False)
            ax1.grid(axis="x", color="#374151", linewidth=0.5)
            fig1.tight_layout()
            
            self.embed_chart(fig1, 0, 0)

        # 2. CHART 2: Disaster Type Distribution (Pie Chart)
        type_counts = df["disaster_type"].value_counts()
        if not type_counts.empty:
            fig2, ax2 = plt.subplots(figsize=(4, 3), facecolor=bg_color)
            ax2.set_facecolor(bg_color)
            
            wedges, texts, autotexts = ax2.pie(
                type_counts.values, labels=type_counts.index, autopct="%1.0f%%",
                colors=accent_colors[:len(type_counts)],
                wedgeprops={"edgecolor": bg_color, "linewidth": 1.5},
                pctdistance=0.7, startangle=140
            )
            for text in texts:
                text.set(color="#9ca3af", fontsize=8)
            for at in autotexts:
                at.set(color="#111827", fontsize=8, fontweight="bold")
                
            ax2.set_title("Disaster Types", color=text_color, fontsize=9, fontweight="bold")
            fig2.tight_layout()
            
            self.embed_chart(fig2, 0, 1)

        # 3. CHART 3: Resource Stockpile Utilization (Bar Chart)
        inv = self.platform.global_inventory
        # Base capacities
        base = {"food": 120000, "water": 200000, "medical_kits": 2000, "rescue_teams": 50}
        labels = ["Food", "Water", "Medical", "Rescue"]
        current_vals = [inv.food, inv.water, inv.medical_kits, inv.rescue_teams]
        max_vals = [base["food"], base["water"], base["medical_kits"], base["rescue_teams"]]
        used_pcts = [((m - c) / m * 100) if m > 0 else 0 for c, m in zip(current_vals, max_vals)]
        
        fig3, ax3 = plt.subplots(figsize=(4, 3), facecolor=bg_color)
        ax3.set_facecolor(card_color)
        
        bars3 = ax3.bar(labels, used_pcts, color=["#3b82f6", "#10b981", "#ef4444", "#fbbf24"], edgecolor="none", width=0.45)
        for bar, pct in zip(bars3, used_pcts):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                     f"{pct:.0f}%", ha="center", color=text_color, fontsize=8, fontweight="bold")
                     
        ax3.set_ylabel("Stock Utilized (%)", color="#9ca3af", fontsize=8)
        ax3.set_title("Resource Stockpile Utilization", color=text_color, fontsize=9, fontweight="bold")
        ax3.tick_params(colors="#9ca3af", labelsize=8)
        for spine in ax3.spines.values():
            spine.set_visible(False)
        ax3.set_ylim(0, 110)
        ax3.grid(axis="y", color="#374151", linewidth=0.5)
        fig3.tight_layout()
        
        self.embed_chart(fig3, 1, 0)

        # 4. CHART 4: Incident Severity breakdown (Bar Chart)
        sev_counts = df["severity"].value_counts()
        if not sev_counts.empty:
            order = ["Critical", "High", "Medium", "Low"]
            sev_col = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#fbbf24", "Low": "#10b981"}
            
            # Map index values (Low/Critical string representation)
            cats = [c for c in order if c in sev_counts.index]
            vals = [sev_counts[c] for c in cats]
            cols = [sev_col[c] for c in cats]
            
            fig4, ax4 = plt.subplots(figsize=(4, 3), facecolor=bg_color)
            ax4.set_facecolor(card_color)
            
            bars4 = ax4.bar(cats, vals, color=cols, edgecolor="none", width=0.45)
            for bar, val in zip(bars4, vals):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         str(val), ha="center", color=text_color, fontsize=8, fontweight="bold")
                         
            ax4.set_ylabel("Number of Incidents", color="#9ca3af", fontsize=8)
            ax4.set_title("Incidents by Severity", color=text_color, fontsize=9, fontweight="bold")
            ax4.tick_params(colors="#9ca3af", labelsize=8)
            for spine in ax4.spines.values():
                spine.set_visible(False)
            ax4.set_ylim(0, max(vals, default=0) + 1.2)
            ax4.grid(axis="y", color="#374151", linewidth=0.5)
            fig4.tight_layout()
            
            self.embed_chart(fig4, 1, 1)

        # 5. CHART 5: Incident Timeline (Cumulative surge over time - Section 10.1 of PDF)
        try:
            fig5, ax5 = plt.subplots(figsize=(8, 2.5), facecolor=bg_color)
            ax5.set_facecolor(card_color)
            sorted_incidents = sorted(incidents, key=lambda x: x.timestamp)
            times = [pd.to_datetime(x.timestamp) for x in sorted_incidents]
            counts = np.arange(1, len(sorted_incidents) + 1)
            ax5.plot(times, counts, color="#06b6d4", marker="o", markersize=4, linewidth=2)
            ax5.fill_between(times, counts, color="#06b6d4", alpha=0.15)
            ax5.set_ylabel("Total Incidents", color="#9ca3af", fontsize=8)
            ax5.set_title("Incident Timeline Surge", color=text_color, fontsize=9, fontweight="bold")
            ax5.tick_params(colors="#9ca3af", labelsize=8)
            for spine in ax5.spines.values():
                spine.set_visible(False)
            fig5.autofmt_xdate()
            ax5.grid(axis="y", color="#374151", linewidth=0.5)
            fig5.tight_layout()
            
            self.embed_chart(fig5, 2, 0, columnspan=2)
        except Exception:
            pass

    def embed_chart(self, fig, row, col, columnspan=1):
        """Helper to render Matplotlib figure inside Tkinter Grid."""
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.config(bg="#080c14", highlightbackground="#080c14", highlightcolor="#080c14")
        widget.grid(row=row, column=col, columnspan=columnspan, padx=10, pady=10, sticky="nsew")
        self.canvas_widgets.append(widget)
