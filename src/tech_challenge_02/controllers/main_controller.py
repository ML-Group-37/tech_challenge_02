from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["Main"]
)

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify the API is working.
    Returns a simple message.
    """
    return {"message": "API is working!", "status": "success"} 