from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import json
import os
import secrets
import string
from bitmap_generator import generate_monochrome_bmp, generate_setup_cube_bmp

# Database setup
DATABASE_URL = "sqlite:///./db.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    access_token = Column(String)
    creation_timestamp = Column(Integer)
    log_id = Column(Integer)
    log_message = Column(Text)
    log_codeline = Column(Integer)
    log_sourcefile = Column(String)
    device_status = Column(Text)  # JSON string of device status
    additional_info = Column(Text)  # JSON string of additional info
    received_at = Column(DateTime, default=datetime.utcnow)

class Setup(Base):
    __tablename__ = "setup"
    
    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, nullable=False, unique=True)
    friendly_id = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class DeviceStatusStamp(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    wifi_rssi_level: int
    wifi_status: str
    refresh_rate: int
    time_since_last_sleep_start: int
    current_fw_version: str
    special_function: str
    battery_voltage: float
    wakeup_reason: str
    free_heap_size: int
    max_alloc_size: int

class LogArrayItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    creation_timestamp: int
    device_status_stamp: DeviceStatusStamp
    log_id: int
    log_message: str
    log_codeline: int
    log_sourcefile: str
    additional_info: Dict[str, Any]

class LogData(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    logs_array: List[LogArrayItem]

class LogRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    log: LogData

# Create tables
Base.metadata.create_all(bind=engine)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# FastAPI app
app = FastAPI(title="TRMNL Server", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/log",
          tags=["logs"],
          summary="Receive TRMNL device logs",
          description="Accepts log entries from TRMNL devices and stores them in the database. Requires device ID and access token in headers.")
async def receive_log(request: Request, log_request: LogRequest):
    # Extract headers
    device_id = request.headers.get("ID")
    access_token = request.headers.get("Access-Token")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Process each log entry
        for log_item in log_request.log.logs_array:
            log_entry = LogEntry(
                device_id=device_id,
                access_token=access_token,
                creation_timestamp=log_item.creation_timestamp,
                log_id=log_item.log_id,
                log_message=log_item.log_message,
                log_codeline=log_item.log_codeline,
                log_sourcefile=log_item.log_sourcefile,
                device_status=json.dumps(log_item.device_status_stamp.dict()),
                additional_info=json.dumps(log_item.additional_info)
            )
            db.add(log_entry)
        
        db.commit()
        return {"status": "success", "message": "Log entries saved"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving log: {str(e)}")
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index():
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Index file not found</h1><p>Please create static/index.html</p>")

@app.get("/logs", response_class=HTMLResponse, include_in_schema=False)
async def serve_logs():
    try:
        with open("static/logs.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Log viewer not found</h1><p>Please create static/logs.html</p>")

@app.get("/api/logs",
         tags=["logs"],
         summary="Get stored log entries", 
         description="Retrieves log entries from the database. Returns the most recent entries first, with an optional limit parameter.")
async def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(LogEntry).order_by(desc(LogEntry.received_at)).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "device_id": log.device_id,
            "access_token": log.access_token,
            "creation_timestamp": log.creation_timestamp,
            "log_id": log.log_id,
            "log_message": log.log_message,
            "log_codeline": log.log_codeline,
            "log_sourcefile": log.log_sourcefile,
            "device_status": json.loads(log.device_status) if log.device_status else {},
            "additional_info": json.loads(log.additional_info) if log.additional_info else {},
            "received_at": log.received_at.isoformat() if log.received_at else None
        })
    
    return {"logs": result}

@app.get("/api/setup/",
         tags=["setup"],
         summary="Device setup registration",
         description="Registers a new TRMNL device or returns existing setup information. Requires device MAC address in ID header.")
async def device_setup(request: Request, db: Session = Depends(get_db)):

    mac_address = request.headers.get("ID")
    if not mac_address:
        raise HTTPException(status_code=400, detail="Missing ID header (MAC address)")
    
    device_setup = db.query(Setup).filter(Setup.mac_address == mac_address).first()
    
    if not device_setup:
        alphabet = string.ascii_letters + string.digits
        api_key = "".join(secrets.choice(alphabet) for _ in range(18))
        
        while True:
            friendly_id = secrets.token_hex(3).upper()
            if not db.query(Setup).filter(Setup.friendly_id == friendly_id).first():
                break
        
        device_setup = Setup(
            mac_address=mac_address,
            api_key=api_key,
            friendly_id=friendly_id
        )
        db.add(device_setup)
        db.commit()
        db.refresh(device_setup)
    else:
        raise HTTPException(status_code=400, detail="Device already set up")
    
    # Generate image URL for setup cube
    image_url = f"http://{request.url.hostname}:{request.url.port}/api/bitmap?type=setup_cube"
    
    return {
        "status": 200,
        "api_key": device_setup.api_key,
        "friendly_id": device_setup.friendly_id,
        "image_url": image_url,
        "filename": "setup_cube"
    }

@app.get("/api/devices",
         tags=["setup"],
         summary="List all devices",
         description="Returns a list of all registered devices with their setup information.")
async def list_devices(db: Session = Depends(get_db)):
    devices = db.query(Setup).order_by(desc(Setup.created_at)).all()
    
    result = []
    for device in devices:
        result.append({
            "id": device.id,
            "mac_address": device.mac_address,
            "api_key": device.api_key,
            "friendly_id": device.friendly_id,
            "created_at": device.created_at.isoformat() if device.created_at else None,
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None
        })
    
    return {"devices": result}


@app.delete("/api/setup",
           tags=["setup"],
           summary="Delete device setup",
           description="Removes a device setup from the database. Requires api_key as query parameter.")
async def delete_device_setup(api_key: str, db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=400, detail="Missing api_key parameter")
    
    device_setup = db.query(Setup).filter(Setup.api_key == api_key).first()
    
    if not device_setup:
        raise HTTPException(status_code=404, detail="Device setup not found")
    
    # Delete the setup
    db.delete(device_setup)
    db.commit()
    
    return {"status": 200, "message": "Device setup deleted successfully"}

@app.get("/api/display",
         tags=["display"],
         summary="Get display configuration",
         description="Returns display configuration for TRMNL device including image URL, refresh rate, and firmware update information.")
async def get_display(request: Request, db: Session = Depends(get_db)):
    # Extract headers
    device_id = request.headers.get("id")
    access_token = request.headers.get("access-token")
    refresh_rate = request.headers.get("refresh-rate", "1800")
    battery_voltage = request.headers.get("battery-voltage")
    fw_version = request.headers.get("fw-version")
    rssi = request.headers.get("rssi")
    width = int(request.headers.get("width", "800"))
    height = int(request.headers.get("height", "480"))
       
    # Store display request in database
    if device_id and access_token:
        try:
            log_entry = LogEntry(
                device_id=device_id,
                access_token=access_token,
                creation_timestamp=int(datetime.now().timestamp()),
                log_id=0,  # Display requests don't have log_id
                log_message=f"Display request - {width}x{height}, battery: {battery_voltage}V, RSSI: {rssi}dBm",
                log_codeline=0,
                log_sourcefile="api/display",
                device_status=json.dumps({
                    "refresh_rate": refresh_rate,
                    "battery_voltage": float(battery_voltage) if battery_voltage else None,
                    "fw_version": fw_version,
                    "rssi": int(rssi) if rssi else None,
                    "width": width,
                    "height": height
                }),
                additional_info=json.dumps({})
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            print(f"Failed to log display request: {e}")
            db.rollback()
    
    # Return the required JSON format
    return {
        "status": 0,  # 202 if no user_id is attached to device
        "image_url": f"http://{request.url.hostname}:{request.url.port}/api/bitmap?width={width}&height={height}",
        "filename": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + ".bmp",
        "update_firmware": False,
        "firmware_url": None,
        "refresh_rate": "60",
        "reset_firmware": False
    }

@app.get("/api/bitmap",
         tags=["display"],
         summary="Generate monochrome bitmap",
         description="Generates a dynamic monochrome BMP file for TRMNL display. Supports different bitmap types via 'type' parameter.")
async def get_bitmap(width: int = 800, height: int = 480, type: str = "default"):
    if type == "setup_cube":
        bmp_data = generate_setup_cube_bmp(width, height)
        filename = "setup_cube.bmp"
    else:
        bmp_data = generate_monochrome_bmp(width, height)
        filename = "display.bmp"
    
    return Response(
        content=bmp_data,
        media_type="image/bmp",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4711)

if __name__ == "__main__":
    main()
