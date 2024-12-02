from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from application.services.auth_service import AuthenticationService


class GarminSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.auth_service = AuthenticationService()
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/", "/docs", "/openapi.json"]:
            return await call_next(request)

        await self.auth_service.ensure_authentication()
        return await call_next(request)
