"""
Quick test: validate greedy proportional allocation distributes to all incidents.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.platform_orchestrator import DisasterPlatform

platform = DisasterPlatform(bootstrap=True)

print("=== PRE-ALLOCATION INVENTORY ===")
inv = platform.global_inventory
print(f"  Food: {inv.food:,}  Water: {inv.water:,}  Meds: {inv.medical_kits}  Teams: {inv.rescue_teams}")
print(f"  Active incidents: {len(platform.incidents)}")
print()

log = platform.greedy_allocate_resources(strategy="greedy")

print("=== ALLOCATION LOG (Proportional Greedy) ===")
for entry in log:
    a = entry['allocated']
    d = entry['deficit']
    print(f"  {entry['incident_id']}  alloc→ F:{a['food']:>7,}  W:{a['water']:>8,}  M:{a['medical_kits']:>5}  T:{a['rescue_teams']}")
    has_deficit = any(v > 0 for v in d.values())
    if has_deficit:
        print(f"           deficit→ F:{d['food']:>7,}  W:{d['water']:>8,}  M:{d['medical_kits']:>5}  T:{d['rescue_teams']}")

print()
print("=== POST-ALLOCATION INVENTORY ===")
inv = platform.global_inventory
print(f"  Food: {inv.food:,}  Water: {inv.water:,}  Meds: {inv.medical_kits}  Teams: {inv.rescue_teams}")

# Verify no single incident took everything
allocs = [e['allocated']['food'] for e in log]
if max(allocs) == sum(allocs) and len(log) > 1:
    print("\n[FAIL] Single incident consumed ALL food resources!")
else:
    print("\n[OK] Resources distributed across multiple incidents.")
