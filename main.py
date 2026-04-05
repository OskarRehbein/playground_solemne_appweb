from datetime import datetime

from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("✓ Docker is working!")


@app.get("/")
def get_time():
    return {"time": str(datetime.now())}


def suma(a, b):
    return a + b
