"""
modules/analytics.py - Data visualization and analytics dashboard.
"""
import base64
import io
import folium
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class AnalyticsDashboard:
    """
    Module E: Dashboard & Visualization.
    Aggregates incident and resource statistics using Pandas and NumPy,
    and renders Folium maps and Matplotlib charts.
    """
    def __init__(self):
        self.incident_df = None
        self.resource_df = None

    def show_stats(self, incidents, global_inventory) -> dict:
        """Returns aggregated statistical summaries of the active disaster response operations."""
        if not incidents:
            return {}

        # Convert to Pandas DataFrame
        df = pd.DataFrame([i.to_dict() for i in incidents])
        df["population_affected"] = pd.to_numeric(df["population_affected"])
        df["priority_index"] = pd.to_numeric(df["priority_index"])
        
        self.incident_df = df

        # Most affected areas
        loc_impact = (df[df["status"].str.lower() != "resolved"]
                      .groupby("location_id")["population_affected"].sum()
                      .sort_values(ascending=False))
                      
        most_affected = []
        for lid, pop in loc_impact.items():
            most_affected.append({
                "location_id": lid,
                "population": int(pop)
            })

        # Distributions
        sev_counts = df["severity"].value_counts().to_dict()
        type_counts = df["disaster_type"].value_counts().to_dict()
        status_counts = df["status"].value_counts().to_dict()

        # Resource Utilization
        # Using base starting capacities to calculate utilization
        orig_food = 120000
        orig_water = 200000
        orig_med = 2000
        orig_rescue = 50
        
        resource_util = {
            "food": {"used": orig_food - global_inventory.food, "remaining": global_inventory.food, "total": orig_food},
            "water": {"used": orig_water - global_inventory.water, "remaining": global_inventory.water, "total": orig_water},
            "medical_kits": {"used": orig_med - global_inventory.medical_kits, "remaining": global_inventory.medical_kits, "total": orig_med},
            "rescue_teams": {"used": orig_rescue - global_inventory.rescue_teams, "remaining": global_inventory.rescue_teams, "total": orig_rescue},
        }

        total_pop = int(df["population_affected"].sum())
        active_count = int((df["status"].str.lower() == "active").sum())

        return {
            "total_incidents": len(incidents),
            "active_incidents": active_count,
            "resolved_incidents": int((df["status"].str.lower() == "resolved").sum()),
            "total_population": total_pop,
            "most_affected": most_affected,
            "severity_dist": sev_counts,
            "type_dist": type_counts,
            "status_dist": status_counts,
            "resource_util": resource_util,
        }

    def render_charts(self, incidents, global_inventory) -> dict[str, str]:
        """Generates Matplotlib analytics charts as base64 PNG strings with transparent backgrounds."""
        analytics = self.show_stats(incidents, global_inventory)
        charts = {}
        if not analytics:
            return charts

        plt.style.use("dark_background")
        CARD_BG = "#080c16"  # matching the new tactical card base
        ACCENT_COLORS = ["#6366f1", "#10b981", "#eab308", "#ef4444", "#8b5cf6", "#06b6d4"]

        def fig_to_b64(fig):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=110)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()

        # Chart 1: Population Impact Bar Chart
        if analytics.get("most_affected"):
            fig, ax = plt.subplots(figsize=(7, 3.8), facecolor="none")
            ax.set_facecolor("none")
            items = analytics["most_affected"][:6]
            names = [i["location_id"] for i in items]  # Node IDs
            pops = [i["population"] for i in items]
            bars = ax.barh(names, pops, color=ACCENT_COLORS[:len(names)], edgecolor="none", height=0.55)
            
            for bar, pop in zip(bars, pops):
                ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
                        f"{pop:,}", va="center", color="#ccddee", fontsize=9)
            ax.set_xlabel("People Affected", color="#94a3b8", fontsize=9)
            ax.set_title("Population Impact by Area", color="#f8fafc", fontsize=11, fontweight="bold", pad=10)
            ax.tick_params(colors="#94a3b8", labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.grid(axis="x", color="#1e293b", linewidth=0.5)
            fig.tight_layout()
            charts["population_impact"] = fig_to_b64(fig)
            plt.close(fig)

        # Chart 2: Disaster Type Donut
        if analytics.get("type_dist"):
            fig, ax = plt.subplots(figsize=(5, 4), facecolor="none")
            ax.set_facecolor("none")
            labels = list(analytics["type_dist"].keys())
            sizes = list(analytics["type_dist"].values())
            wedges, texts, autotexts = ax.pie(
                sizes, labels=None, autopct="%1.0f%%",
                colors=ACCENT_COLORS[:len(labels)],
                wedgeprops={"edgecolor": CARD_BG, "linewidth": 2},
                pctdistance=0.78, startangle=90
            )
            for at in autotexts:
                at.set(color="#030712", fontsize=8, fontweight="bold")
            centre = plt.Circle((0, 0), 0.55, fc=CARD_BG)
            ax.add_patch(centre)
            ax.text(0, 0, "Types", ha="center", va="center", color="#94a3b8", fontsize=9, fontweight="bold")
            ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=3,
                      frameon=False, labelcolor="#ccddee", fontsize=8)
            ax.set_title("Disaster Type Distribution", color="#f8fafc", fontsize=11, fontweight="bold", pad=12)
            fig.tight_layout()
            charts["disaster_types"] = fig_to_b64(fig)
            plt.close(fig)

        # Chart 3: Resource Utilization Gauges
        if analytics.get("resource_util"):
            fig, axes = plt.subplots(1, 4, figsize=(10, 3), facecolor="none")
            r_data = analytics["resource_util"]
            r_labels = {"food": "Food", "water": "Water", "medical_kits": "Medical", "rescue_teams": "Rescue"}
            r_colors = ["#06b6d4", "#10b981", "#ef4444", "#eab308"]
            
            for ax, (key, info), color in zip(axes, r_data.items(), r_colors):
                ax.set_facecolor("none")
                pct = (info["used"] / info["total"]) * 100 if info["total"] > 0 else 0
                theta = np.linspace(0, np.pi, 100)
                ax.plot(np.cos(theta), np.sin(theta), color="#1e293b", lw=6)
                fill_theta = np.linspace(0, np.pi * pct/100, 100)
                ax.plot(np.cos(fill_theta), np.sin(fill_theta), color=color, lw=6)
                ax.plot(0, 0, "o", color=CARD_BG, ms=8)
                ax.text(0, -0.2, f"{pct:.0f}%", ha="center", va="center", color=color, fontsize=13, fontweight="bold")
                ax.text(0, -0.52, r_labels[key], ha="center", va="center", color="#94a3b8", fontsize=8)
                ax.set_xlim(-1.3, 1.3)
                ax.set_ylim(-0.7, 1.1)
                ax.set_aspect("equal")
                ax.axis("off")
                for spine in ax.spines.values():
                    spine.set_visible(False)
            fig.suptitle("Resource Utilization", color="#f8fafc", fontsize=12, fontweight="bold", y=1.02)
            fig.tight_layout()
            charts["resource_util"] = fig_to_b64(fig)
            plt.close(fig)

        # Chart 4: Severity Breakdown
        if analytics.get("severity_dist"):
            fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="none")
            ax.set_facecolor("none")
            order = ["Critical", "High", "Medium", "Low"]
            sev_col = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#10b981"}
            cats = [s for s in order if s in analytics["severity_dist"]]
            vals = [analytics["severity_dist"][s] for s in cats]
            cols = [sev_col[s] for s in cats]
            
            bars = ax.bar(cats, vals, color=cols, edgecolor="none", width=0.55)
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        str(val), ha="center", color="#ccddee", fontsize=10, fontweight="bold")
            ax.set_ylabel("Incidents", color="#94a3b8", fontsize=9)
            ax.set_title("Severity Distribution", color="#f8fafc", fontsize=11, fontweight="bold", pad=10)
            ax.tick_params(colors="#94a3b8")
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_ylim(0, max(vals, default=1) + 1.5)
            ax.grid(axis="y", color="#1e293b", linewidth=0.5)
            fig.tight_layout()
            charts["severity_dist"] = fig_to_b64(fig)
            plt.close(fig)

        # Chart 5: Incident Timeline (Cumulative surge over time - Section 10.1 of PDF)
        if incidents:
            try:
                fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="none")
                ax.set_facecolor("none")
                sorted_incidents = sorted(incidents, key=lambda x: x.timestamp)
                times = [pd.to_datetime(x.timestamp) for x in sorted_incidents]
                counts = np.arange(1, len(sorted_incidents) + 1)
                ax.plot(times, counts, color="#06b6d4", marker="o", markersize=4, linewidth=2)
                ax.fill_between(times, counts, color="#06b6d4", alpha=0.15)
                ax.set_ylabel("Total Incidents", color="#94a3b8", fontsize=9)
                ax.set_title("Incident Timeline Surge", color="#f8fafc", fontsize=11, fontweight="bold", pad=10)
                ax.tick_params(colors="#94a3b8", labelsize=8)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                fig.autofmt_xdate()
                ax.grid(axis="y", color="#1e293b", linewidth=0.5)
                fig.tight_layout()
                charts["incident_timeline"] = fig_to_b64(fig)
                plt.close(fig)
            except Exception:
                pass

        return charts

    def export_folium_map(self, graph, incidents, shelters, highlight_path=None, highlight_shelters=None) -> str:
        """Generates an interactive Folium map as an HTML string."""
        center_lat = np.mean([n.lat for n in graph.nodes.values()])
        center_lng = np.mean([n.lng for n in graph.nodes.values()])
        m = folium.Map(location=[center_lat, center_lng], zoom_start=12, tiles="CartoDB dark_matter")

        # Add Severity-Weighted Heatmap Layer (Section 14.2 of PDF)
        from folium.plugins import HeatMap
        heat_data = []
        for inc in incidents:
            if inc.status.lower() != "resolved":
                node = graph.nodes.get(inc.location)
                if node:
                    weight = float(inc.severity * inc.population_affected)
                    heat_data.append([node.lat, node.lng, weight])
        if heat_data:
            HeatMap(
                heat_data,
                name="⚠️ Severity Heatmap",
                min_opacity=0.35,
                radius=30,
                blur=18,
                max_zoom=13
            ).add_to(m)

        color_map = {
            "HQ": ("#00d4ff", "home", "blue"),
            "Depot": ("#ffd700", "archive", "orange"),
            "Shelter": ("#00e676", "plus-sign", "green"),
            "Affected Zone": ("#ff4444", "exclamation-sign", "red"),
        }
        severity_colors = {"Low": "#88ff88", "Medium": "#ffcc00", "High": "#ff8800", "Critical": "#ff2222"}

        # Draw graph edges
        edge_drawn = set()
        for u, neighbors in graph.G.adjacency():
            for v, data in neighbors.items():
                key = tuple(sorted([u, v]))
                if key in edge_drawn:
                    continue
                edge_drawn.add(key)
                if u in graph.nodes and v in graph.nodes:
                    un, vn = graph.nodes[u], graph.nodes[v]
                    folium.PolyLine(
                        [[un.lat, un.lng], [vn.lat, vn.lng]],
                        color="#334455", weight=1.5, opacity=0.5,
                        tooltip=f"{un.name} ↔ {vn.name}: {data.get('distance', data.get('weight', 1.0)):.1f} km"
                    ).add_to(m)

        # Highlight rescue route
        if highlight_path and len(highlight_path) > 1:
            coords = [(graph.nodes[p].lat, graph.nodes[p].lng) for p in highlight_path if p in graph.nodes]
            folium.PolyLine(coords, color="#00ffff", weight=5, opacity=0.9, tooltip="🚑 Rescue Route").add_to(m)

        # Draw nodes
        incident_locations = {i.location: i for i in incidents if i.status.lower() != "resolved"}
        for nid, node in graph.nodes.items():
            color, icon, marker_color = color_map.get(node.loc_type, ("#cccccc", "info-sign", "gray"))
            
            popup_html = f"""
            <div style='font-family:Inter,sans-serif;min-width:180px'>
              <b style='color:{color}'>{node.name}</b><br>
              <span style='opacity:0.7'>{node.loc_type}</span><br>
              <small>{node.description}</small>
            </div>"""

            if nid in incident_locations:
                inc = incident_locations[nid]
                sev_col = severity_colors.get(inc.severity_level_str, "#ff4444")
                popup_html = f"""
                <div style='font-family:Inter,sans-serif;min-width:220px'>
                  <b style='color:{sev_col}'>⚠️ {inc.disaster_type} Incident</b><br>
                  <b>Severity:</b> <span style='color:{sev_col}'>{inc.severity_level_str}</span> (Score: {inc.severity})<br>
                  <b>Population:</b> {inc.population_affected:,}<br>
                  <b>ID:</b> {inc.incident_id}<br>
                  <small style='opacity:0.7'>{inc.description}</small>
                </div>"""
                
                folium.CircleMarker(
                    [node.lat, node.lng], radius=14 + inc.severity * 3,
                    color=sev_col, fill=True, fill_color=sev_col, fill_opacity=0.35,
                    popup=folium.Popup(popup_html, max_width=280)
                ).add_to(m)

            if nid in (highlight_shelters or []):
                folium.CircleMarker(
                    [node.lat, node.lng], radius=22,
                    color="#00ff88", fill=True, fill_color="#00ff88", fill_opacity=0.25
                ).add_to(m)

            folium.Marker(
                [node.lat, node.lng],
                icon=folium.Icon(color=marker_color, icon=icon, prefix="glyphicon"),
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=node.name,
            ).add_to(m)

        # Legend overlay
        legend_html = """
        <div style='position:fixed;bottom:30px;left:30px;z-index:1000;background:rgba(0,0,0,0.75);
                    border-radius:12px;padding:14px 18px;font-family:Inter,sans-serif;font-size:12px;color:#eee;
                    backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.1)'>
          <b style='color:#00d4ff'>LEGEND</b><br><br>
          🏠 <b>HQ</b> – Command Center<br>
          📦 <b>Depot</b> – Resource Supply<br>
          🏥 <b>Shelter</b> – Evacuation Site<br>
          ⚠️ <b>Zone</b> – Affected Area<br>
          <span style='color:#00ffff'>━━</span> Rescue Route
        </div>"""
        # Add Layer Control toggle for Heatmap/Markers
        folium.LayerControl(position="topright").add_to(m)
        m.get_root().html.add_child(folium.Element(legend_html))

        return m._repr_html_()
