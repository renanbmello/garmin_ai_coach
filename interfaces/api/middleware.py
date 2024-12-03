from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from application.services.auth_service import AuthenticationService
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GarminSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.auth_service = AuthenticationService()

    async def dispatch(self, request: Request, call_next):
        try:
            # Só tenta autenticar se for uma rota que precisa de autenticação
            if self._needs_auth(request.url.path):
                try:
                    await self.auth_service.ensure_authentication()
                except Exception as e:
                    logger.error(f"Authentication error: {str(e)}")
                    if "Too Many Requests" in str(e):
                        raise HTTPException(
                            status_code=429,
                            detail="Too many requests to Garmin. Please try again in a few minutes."
                        )
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication failed"
                    )

            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Middleware error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _needs_auth(self, path: str) -> bool:
        """Determina se a rota precisa de autenticação"""
        # Lista de rotas que não precisam de autenticação
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/status"
        ]
        
        return not any(path.startswith(public_path) for public_path in public_paths)
