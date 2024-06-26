from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import auth_router
from app.routers.workflows import nodes_router, workflows_router
from app.utils.auth import get_auth_header

app = FastAPI(title="Workflows API", openapi_url="/openapi/", docs_url="/docs/")

app.include_router(auth_router)
app.include_router(workflows_router, dependencies=[Depends(get_auth_header)])
app.include_router(nodes_router, dependencies=[Depends(get_auth_header)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
