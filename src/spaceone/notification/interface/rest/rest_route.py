from fastapi import FastAPI
from spaceone.notification.interface.rest.v1 import webhook

app = FastAPI()
app.include_router(webhook.router)

