from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes.customer_router import router as customer_router
from app.routes.auth_router import router as auth_router

# Import DB init
from app.core.database import init_db

app = FastAPI(
    title="Paynaka Backend",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Connecting to MongoDB...")
    await init_db()
    print("MongoDB connected successfully!")

# Routers
app.include_router(customer_router)
app.include_router(auth_router)

# Root
@app.get("/")
async def root():
    return {"message": "Paynaka FastAPI backend is running!"}
