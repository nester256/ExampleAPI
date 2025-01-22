from webapp.api.base.router import base_router


@base_router.get('/health')
async def health():
    return {'status': 'ok'}