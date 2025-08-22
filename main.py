"""
FastAPI main application for the MBT Affordability Benchmarking Tool.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import os
from datetime import datetime
from typing import Optional
import traceback

from models import get_db, create_tables
from scenario_runner import ScenarioRunner

# Create FastAPI app
app = FastAPI(
    title="MBT Affordability Benchmarking Tool",
    description="Automated mortgage affordability benchmarking using MBT data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory and static files
templates = Jinja2Templates(directory="templates")

# Mount static files (if directory exists)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database
create_tables()

# Global scenario runner instance
scenario_runner = ScenarioRunner()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/run-sample-scenarios")
async def run_sample_scenarios():
    """Run sample scenarios and return results."""
    try:
        print("Starting sample scenarios...")
        
        # Test login first for faster feedback
        from mbt_automation_final import MBTAutomationFinal
        mbt = MBTAutomationFinal()
        await mbt.start_browser(headless=True)
        
        login_result = await mbt.login()
        if not login_result:
            await mbt.close()
            return JSONResponse(
                status_code=400,
                content={"error": "MBT login failed. Please check credentials or try again."}
            )
        
        await mbt.close()
        print("✅ Login test successful, proceeding with scenarios...")
        
        # For now, return enhanced mock data while automation completes
        # This provides immediate feedback while the full automation is being refined
        mock_results = {
            'session_id': f'demo-session-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'status': 'demo_mode',
            'message': 'Login successful! Returning demo data while full automation is being optimized.',
            'results': {
                'joint_vanilla_40k': {
                    'scenario_id': 'joint_vanilla_40k',
                    'lender_results': {
                        'Gen H': 320000,
                        'Accord': 315000,
                        'Skipton': 325000,
                        'Kensington': 310000,
                        'Precise': 305000,
                        'Atom': 330000,
                        'Clydesdale': 318000,
                        'Newcastle': 316000,
                        'Metro': 322000,
                        'Nottingham': 314000,
                        'Hinckley & Rugby': 312000,
                        'Leeds': 319000,
                        'Principality': 321000,
                        'Coventry': 317000,
                        'Santander': 320000
                    },
                    'statistics': {
                        'average': 317600,
                        'gen_h_amount': 320000,
                        'gen_h_difference': 2400,
                        'gen_h_rank': 7
                    }
                },
                'single_self_employed_40k': {
                    'scenario_id': 'single_self_employed_40k', 
                    'lender_results': {
                        'Gen H': 160000,
                        'Accord': 155000,
                        'Skipton': 165000,
                        'Kensington': 150000,
                        'Precise': 145000,
                        'Atom': 170000,
                        'Clydesdale': 158000,
                        'Newcastle': 156000,
                        'Metro': 162000,
                        'Nottingham': 154000,
                        'Hinckley & Rugby': 152000,
                        'Leeds': 159000,
                        'Principality': 161000,
                        'Coventry': 157000,
                        'Santander': 160000
                    },
                    'statistics': {
                        'average': 157600,
                        'gen_h_amount': 160000,
                        'gen_h_difference': 2400,
                        'gen_h_rank': 6
                    }
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print("Returning demo data with successful login verification")
        return JSONResponse(content=mock_results)
        
        # TODO: Uncomment this when full automation timing is optimized
        # results = await scenario_runner.run_sample_scenarios()
        # print(f"Sample scenarios completed: {len(results.get('results', {}))}")
        # return JSONResponse(content=results)
        
    except Exception as e:
        print(f"Error in run_sample_scenarios: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e), "traceback": traceback.format_exc()}
        )

@app.get("/api/latest-results")
async def get_latest_results(db: Session = Depends(get_db)):
    """Get the most recent results."""
    try:
        results = scenario_runner.get_latest_results(db)
        return JSONResponse(content=results)
    except Exception as e:
        print(f"Error in get_latest_results: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )

@app.get("/api/run-full-automation")
async def run_full_automation():
    """Run the complete MBT automation (may take several minutes)."""
    try:
        print("Starting full MBT automation...")
        
        # Run the actual automation
        results = await scenario_runner.run_sample_scenarios()
        print(f"Full automation completed: {len(results.get('results', {}))}")
        return JSONResponse(content=results)
        
    except Exception as e:
        print(f"Error in full automation: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e), "details": "Full automation failed"}
        )

@app.get("/api/historical-results")
async def get_historical_results(
    scenario_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get historical results."""
    try:
        results = scenario_runner.get_historical_results(db, scenario_id)
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios")
async def get_scenarios():
    """Get all available scenarios."""
    try:
        sample_scenarios = scenario_runner.create_sample_scenarios()
        all_scenarios = scenario_runner.create_all_scenarios()
        
        return JSONResponse(content={
            "sample_scenarios": sample_scenarios,
            "all_scenarios": all_scenarios
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get application status."""
    return JSONResponse(content={
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("HOST", "127.0.0.1"), 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )