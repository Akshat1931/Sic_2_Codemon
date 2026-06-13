"""
web_app.py - FastAPI application runner using the refactored modular backend.
"""
import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

from modules.platform_orchestrator import DisasterPlatform

app = FastAPI(title="Disaster Response Platform", version="1.0.0")
platform = DisasterPlatform(bootstrap=True)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Template Dir config
_TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"

def _read_template(name: str) -> str:
    """Reads HTML file from the templates directory."""
    return (_TEMPLATE_DIR / name).read_text(encoding="utf-8")

# ── Pydantic Request Schemas ──────────────────────────────────────
class IncidentRequest(BaseModel):
    location_id: str
    disaster_type: str
    severity: str
    population_affected: int
    description: str = ""
    reporter: str = "Anonymous"

class RouteRequest(BaseModel):
    source_id: str
    target_id: str

class ShelterRequest(BaseModel):
    incident_id: str
    max_results: int = 4

class AllocateRequest(BaseModel):
    strategy: str = "greedy"

# ── API Routes ───────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Renders the dashboard page."""
    return HTMLResponse(content=_read_template("index.html"))

@app.get("/api/nodes")
async def get_nodes():
    return JSONResponse(platform.graph.all_nodes_list())

@app.get("/api/edges")
async def get_edges():
    return JSONResponse(platform.graph.all_edges_list())

@app.get("/api/incidents")
async def get_incidents():
    return JSONResponse([i.to_dict() for i in platform.incidents])

@app.post("/api/incidents")
async def add_incident(req: IncidentRequest):
    try:
        inc = platform.report_incident(
            location_id=req.location_id,
            disaster_type=req.disaster_type,
            severity=req.severity,
            population_affected=req.population_affected,
            description=req.description,
            reporter=req.reporter
        )
        return JSONResponse(inc.to_dict(), status_code=201)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/api/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    if platform.resolve_incident(incident_id):
        return {"status": "resolved", "incident_id": incident_id}
    raise HTTPException(status_code=404, detail="Incident not found")

@app.get("/api/shelters")
async def get_shelters():
    return JSONResponse([s.to_dict() for s in platform.shelters.values()])

@app.post("/api/shelters/recommend")
async def shelter_recommend(req: ShelterRequest):
    try:
        recs = platform.recommend_shelters(req.incident_id, req.max_results)
        return JSONResponse(recs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/route")
async def plan_route(req: RouteRequest):
    try:
        result = platform.plan_rescue_route(req.source_id, req.target_id)
        if "error" in result:
            raise ValueError(result["error"])
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/route/alternatives")
async def plan_alternative_routes(req: RouteRequest):
    try:
        result = platform.plan_alternative_routes(req.source_id, req.target_id)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/allocate")
async def allocate_resources(req: AllocateRequest = AllocateRequest()):
    log = platform.greedy_allocate_resources(strategy=req.strategy)
    return JSONResponse({
        "allocation_log": log,
        "remaining": platform.global_inventory.to_dict()
    })

@app.get("/api/inventory")
async def get_inventory():
    return JSONResponse(platform.global_inventory.to_dict())

@app.get("/api/queue")
async def get_queue():
    return JSONResponse(platform.queue_status())

@app.post("/api/queue/dequeue")
async def dequeue():
    item = platform.dequeue_incident()
    if item:
        return JSONResponse(item)
    return JSONResponse({"message": "Queue is empty"}, status_code=200)

@app.get("/api/analytics")
async def analytics():
    return JSONResponse(platform.get_analytics())

@app.get("/api/map")
async def get_map(highlight: str = "", shelters: str = ""):
    path_ids = [x for x in highlight.split(",") if x] if highlight else None
    shelter_ids = [x for x in shelters.split(",") if x] if shelters else None
    html_map = platform.generate_map(path_ids, shelter_ids)
    return HTMLResponse(content=html_map)

@app.get("/api/charts")
async def get_charts():
    return JSONResponse(platform.generate_charts())

@app.get("/api/report/pdf")
async def download_pdf_report():
    import os
    os.makedirs("outputs/reports", exist_ok=True)
    filepath = "outputs/reports/incident_report.pdf"
    platform.export_pdf_report(filepath)
    return FileResponse(filepath, media_type="application/pdf", filename="incident_report.pdf")
