"""
FastAPI application factory.

Startup order matters:
1. Exception handlers (registered first so they wrap everything)
2. Middleware (LIFO — last added is outermost)
3. Routers
"""
import warnings
warnings.filterwarnings('ignore', message='.*bcrypt.*')
import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.schemas.common import HealthResponse

settings = get_settings()

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level="DEBUG" if settings.debug else "INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
## Industrial Plant Management API

A production-ready API for managing industrial plant records,
built with **FastAPI** and designed for deployment on **Google Cloud Run**.

### Authentication
All protected endpoints require a JWT access token.

1. Call `POST /api/v1/auth/login` with your credentials.
2. Copy the `access_token` from the response.
3. Click **Authorize** (🔒) above and enter: `Bearer <your_token>`.

### Roles
| Role | Permissions |
|------|------------|
| `viewer` | Read-only access to plants |
| `operator` | Create and update own plants |
| `admin` | Full access including delete |

### Test Credentials
| Username | Password | Role |
|----------|----------|------|
| admin | Admin@123 | admin |
| operator | Operator@123 | operator |
| viewer | Viewer@123 | viewer |
        """,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        # Custom 422 handler is registered below — disable FastAPI default
        openapi_tags=[
            {"name": "Authentication", "description": "Login, token refresh, and user profile"},
            {"name": "Plants", "description": "Plant CRUD operations"},
            {"name": "Health", "description": "System health check"},
        ],
        license_info={"name": "MIT"},
        contact={"name": "Abhishek Kumar Jha", "email": "abhimasum@gmail.com"},
    )

    # 1. Exception handlers (must come before middleware)
    register_exception_handlers(app)

    # 2. Middleware (added in reverse wrap order)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(LoggingMiddleware)
    # Note: Rate limiting is applied selectively at the endpoint level
    # Raw ASGI middleware can be complex; use endpoint-level checks instead

    # 3. Routers
    app.include_router(v1_router)

    # Health check — no auth, no rate limit (excluded in middleware)
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Health check",
        description="Returns 200 OK if the service is running. Used by Cloud Run health probes.",
    )
    def health_check() -> HealthResponse:
        logger = logging.getLogger(__name__)
        
        # Debug: Log health check call
        logger.debug("🏥 Health check endpoint called")
        logger.debug(f"📊 Settings: version={settings.app_version}, environment={settings.environment}")
        
        response = HealthResponse(
            status="ok",
            version=settings.app_version,
            environment=settings.environment,
        )
        
        # Debug: Log response
        logger.debug(f"✅ Health check response: {response}")
        return response

    return app


app = create_app()
