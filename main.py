"""
1. Phân quyền:
- GET /api/v1/system/settings (Header X-User-Role: STAFF) -> 403 Forbidden (PASS)
- GET /api/v1/system/settings (Header X-User-Role: ADMIN) -> 200 OK (PASS)

2. CORS:
- OPTIONS /api/v1/profile (Origin: https://internal.megamart.com) -> 200 OK, trả về Access-Control-Allow-Origin (PASS)
- OPTIONS /api/v1/profile (Origin: https://evil-attacker.xyz) -> Bị từ chối, không trả về header Origin (PASS)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="MegaMart ERP Backend")

origins = [
    "https://internal.megamart.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["GET", "POST"], 
    allow_headers=["Content-Type", "X-User-Role"], 
)

@app.middleware("http")
async def rbac_middleware(request: Request, call_next):
    route_permissions = {
        "/api/v1/salary/modify": ["ADMIN", "HR"],
        "/api/v1/system/settings": ["ADMIN"],
        "/api/v1/profile": ["ADMIN", "HR", "STAFF"]
    }

    path = request.url.path
    
    if path in route_permissions:
        user_role = request.headers.get("X-User-Role")
        
        allowed_roles = route_permissions[path]
        
        if user_role not in allowed_roles:
            return JSONResponse(
                status_code=403,
                content={"error": "Permission Denied"}
            )
            
    response = await call_next(request)
    return response

@app.get("/api/v1/salary/modify")
async def modify_salary():
    return {"message": "Success! You have permission to modify salary."}

@app.get("/api/v1/system/settings")
async def system_settings():
    return {"message": "Success! You have permission to view system settings."}

@app.get("/api/v1/profile")
async def profile():
    return {"message": "Success! You have permission to view profile."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
