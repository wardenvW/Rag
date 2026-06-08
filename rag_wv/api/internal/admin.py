from fastapi import APIRouter

admin_router = APIRouter()

@admin_router.get("/")
async def admin_panel():
    return {"response": "admin panel comming soon"}
