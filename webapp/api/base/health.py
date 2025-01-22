from webapp.api.base.router import base_router
from fastapi.responses import ORJSONResponse

@base_router.get('/health')
async def health() -> dict:
    return {"content":"i`m healthy"}