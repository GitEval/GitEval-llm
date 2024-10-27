from fastapi import FastAPI
from server import handlers
import uvicorn
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# 初始化app
app = FastAPI()
app.include_router(handlers.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
