"""
data/simulation.py - Bootstrap simulation data for DisasterOS.
"""
from models.location import GraphNode, ShelterNode
from models.incident import DisasterIncident
from models.resource import ResourceInventory

def bootstrap_platform(platform):
    """
    Loads nodes, shelters, routes, and sample incidents into the platform.
    Matches the preloaded simulation scenario from Section 12/17 of the PDF.
    """
    # 1. Clear existing data
    platform.graph.nodes = {}
    platform.graph.G.clear()
    platform.incident_manager.incidents = []
    platform.incident_manager.priority_queue._heap = []
    platform.incident_manager.dispatch_queue.clear()
    platform.resource_allocator.allocation_log = []
    
    # Reset default stockpile to matching sample report levels
    platform.resource_allocator.inventory = ResourceInventory(
        food=120000, 
        water=200000, 
        medical_kits=2000, 
        rescue_teams=50
    )

    # 2. Add Location Nodes (HQ, Depots, Shelters, Zones)
    nodes_data = [
        # HQ / Depots
        ("N01", "Central Command HQ",         20.2961, 85.8245, False, 0, "Main operations center"),
        ("N02", "North Supply Depot",          20.3500, 85.8100, False, 0, "Primary food & water stockpile"),
        ("N03", "South Logistics Hub",         20.2400, 85.8400, False, 0, "Medical & rescue equipment"),
        # Shelters
        ("N04", "City Stadium Shelter",        20.3120, 85.8350, True, 5000, "5000-person facility"),
        ("N05", "Community Center Alpha",      20.2780, 85.8550, True, 2000, "2000-person facility"),
        ("N06", "High-Ground School Complex",  20.3400, 85.7900, True, 1500, "1500-person facility"),
        ("N07", "Hill Crest Evacuation Base",  20.2500, 85.7800, True, 3000, "3000-person facility"),
        # Affected Zones
        ("N08", "Riverside District",          20.3200, 85.8600, False, 0, "Severe flooding"),
        ("N09", "Port Industrial Area",        20.2600, 85.8700, False, 0, "Cyclone damage"),
        ("N10", "Downtown Commercial Block",   20.2900, 85.8300, False, 0, "Earthquake damage"),
        ("N11", "Eastern Suburban Sector",     20.3100, 85.8700, False, 0, "Flash flood"),
        ("N12", "Southern Coastal Strip",      20.2200, 85.8500, False, 0, "Tsunami risk"),
        ("N13", "Northern Hill Village",       20.3700, 85.8000, False, 0, "Landslide"),
        ("N14", "Wetlands Refugee Camp",       20.2800, 85.7700, False, 0, "Displacement camp"),
    ]
    for nid, name, lat, lon, is_shelter, capacity, desc in nodes_data:
        platform.graph.add_location(nid, name, lat, lon, is_shelter, capacity, desc)

    # 3. Initialize Shelter Registry (node_id -> ShelterNode)
    # The graph automatically instantiated the ShelterNode, let's copy references
    for nid, node in platform.graph.nodes.items():
        if isinstance(node, ShelterNode):
            # Customize supplies per shelter as in app.py
            if nid == "N04":
                node.supplies = ResourceInventory(food=400, water=600, medical_kits=120, rescue_teams=10)
            elif nid == "N05":
                node.supplies = ResourceInventory(food=200, water=300, medical_kits=60, rescue_teams=5)
            elif nid == "N06":
                node.supplies = ResourceInventory(food=150, water=250, medical_kits=40, rescue_teams=4)
            elif nid == "N07":
                node.supplies = ResourceInventory(food=300, water=450, medical_kits=90, rescue_teams=8)
            platform.shelters[nid] = node

    # 4. Add Routes (Edges with distance, road condition, flood risk, time of day - Section 9.1 of PDF)
    # format: (u, v, distance_km, road_condition, flood_risk, time_of_day)
    edges_data = [
        ("N01", "N02", 6.5, 1.0, 1.0, 1.0), 
        ("N01", "N03", 7.2, 1.0, 1.0, 1.0), 
        ("N01", "N04", 3.8, 1.0, 1.0, 1.0),
        ("N01", "N05", 4.1, 1.0, 1.0, 1.0), 
        ("N01", "N10", 2.9, 1.2, 1.1, 1.0),
        ("N02", "N06", 4.3, 1.1, 1.0, 1.0), 
        ("N02", "N08", 5.1, 1.3, 2.2, 1.1), # Riverside District (severe flood)
        ("N02", "N13", 4.8, 2.4, 1.0, 1.1), # Hill landslide path
        ("N03", "N05", 5.0, 1.0, 1.0, 1.0), 
        ("N03", "N09", 4.7, 1.5, 1.4, 1.1), # Port area (cyclone)
        ("N03", "N12", 6.3, 1.4, 1.5, 1.1), # Coastal tsunami risk path
        ("N04", "N08", 3.5, 1.2, 2.0, 1.1), 
        ("N04", "N11", 4.9, 1.1, 1.6, 1.0), # Eastern flash flood
        ("N05", "N10", 2.6, 1.2, 1.0, 1.0), 
        ("N05", "N09", 3.8, 1.4, 1.3, 1.1),
        ("N06", "N13", 3.3, 2.0, 1.0, 1.1),
        ("N06", "N07", 5.7, 1.1, 1.0, 1.0),
        ("N07", "N14", 4.2, 1.2, 1.1, 1.1),
        ("N07", "N13", 6.1, 2.2, 1.0, 1.1),
        ("N08", "N11", 2.2, 1.2, 1.8, 1.0),
        ("N08", "N09", 7.5, 1.5, 1.6, 1.1),
        ("N09", "N12", 3.6, 1.4, 1.5, 1.1), 
        ("N10", "N14", 5.4, 1.3, 1.0, 1.0),
        ("N11", "N13", 8.2, 1.8, 1.3, 1.1), 
        ("N12", "N14", 4.5, 1.2, 1.2, 1.1),
    ]
    for u, v, dist, road, flood, time in edges_data:
        platform.graph.add_route(u, v, dist, road, flood, time)

    # 5. Preload Sample Incidents (Section 17 of PDF)
    incidents_data = [
        ("N08", "Cyclone",    "Critical", 45000, "Chennai Coastal Zone - Severe surge & flooding", "Field Unit Alpha"),
        ("N09", "Flood",      "High",     12000, "Adyar River Banks - Severe overflowing", "Coast Guard"),
        ("N10", "Earthquake", "Medium",    8500, "Tambaram Old Town - Structural damage", "Seismic Team"),
        ("N11", "Flood",      "Low",       3200, "Velachery Suburb - Water logging", "District Collector"),
        ("N12", "Fire",       "High",      1800, "Anna Nagar West - Industrial warehouse fire", "Fire Chief"),
    ]
    
    # We load them as "Reported" to run the triage and allocation demo cleanly
    for idx, (loc_id, dtype, sev, pop, desc, rep) in enumerate(incidents_data, start=1):
        inc_id = f"INC-{idx:03d}"
        node = platform.graph.nodes.get(loc_id)
        coords = (node.lat, node.lng) if node else (0.0, 0.0)
        
        inc = DisasterIncident(
            location=loc_id,
            disaster_type=dtype,
            severity=sev,
            population_affected=pop,
            description=desc,
            reporter=rep,
            incident_id=inc_id,
            coordinates=coords,
            status="Reported"
        )
        platform.incident_manager.register(inc)
