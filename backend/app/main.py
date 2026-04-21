from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建应用
app = FastAPI(
    title="PropertyPulse",
    description="Real Estate Investment Analysis API",
    version="0.1.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/")
async def root():
    return {
        "message": "PropertyPulse API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# 导入路由
from app.api import auth, properties, reports, payments

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(properties.router, prefix="/api/properties", tags=["Properties"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
