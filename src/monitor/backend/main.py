from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time
import os
from threading import Lock

from .models import *

app = FastAPI(
    title='SMS Simulator Statistics Collector',
    description='Simple API providing an endpoint for reporting results and one for retrieving statistics',
    version='0.0.0'
)

stat_lock = Lock()

message_statistics = MessageStatistics(
    total_messages=0,
    success_messages=0,
    average_delay=0.0
)

@app.get("/")
def server_check():
    return JSONResponse(
        content={
            "timestamp": time.time(),
            "message": "OK"
        }
    )

@app.get("/interval")
def get_interval():
    return {
        "interval": float(os.getenv("SMS_UPDATE_INTERVAL", 1))
    }

@app.post("/message", response_model=None, responses={"400": {"model": ErrorResponse}})
def report_message_result(message_result: MessageResultRequest):
    
    # The API isn't running multiple workers - it's not
    # necessary quite yet, so this lock is mainly
    # to demonstrate that we want to ensure we don't miss 
    # an update to race conditions when we do go to 
    # multiple workers.

    with stat_lock:
        message_statistics.success_messages += 1 if message_result.success else 0
        message_statistics.average_delay = (message_statistics.average_delay * message_statistics.total_messages + message_result.delay) / (message_statistics.total_messages + 1)
        message_statistics.total_messages += 1

    return "OK"

@app.get("/statistics", response_model=MessageStatistics)
def retrieve_statistics():
    return message_statistics

@app.post("/reset", response_model=None)
def reset_statistics():
    with stat_lock:
        message_statistics.total_messages = 0
        message_statistics.success_messages = 0
        message_statistics.average_delay = 0.0

    return "OK"