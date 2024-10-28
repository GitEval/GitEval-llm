
from fastapi import FastAPI
from server import handlers
from config import config
import uvicorn


config.get_config('./config/config.yaml')
# 初始化app
app = FastAPI()
app.include_router(handlers.router)



if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=5000)
