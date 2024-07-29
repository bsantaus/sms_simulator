from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from threading import Lock

from .models import *

app = FastAPI(
    title='SMS Simulator Statistics Collector',
    description='Simple API providing an endpoint for reporting results and one for retrieving statistics',
    version='0.0.0'
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

stat_lock = Lock()

message_statistics = MessageStatistics(
    total_messages=0,
    success_messages=0,
    average_delay=0.0
)

@app.get("/")
def server_check():
    '''
        Return a healthcheck to confirm API is available
    '''
    return JSONResponse(
        content={
            "timestamp": time.time(),
            "message": "OK"
        }
    )

@app.get("/interval")
def get_interval():
    '''
        For Monitor frontend, return interval at which the 
        Monitor should poll for updates.
    '''
    return {
        "interval": float(os.getenv("SMS_UPDATE_INTERVAL", 1))
    }

@app.post("/message", response_model=None, responses={"400": {"model": ErrorResponse}})
def report_message_result(message_result: MessageResultRequest):
    '''
        Receive report of a Message processing from a Sender

        Update collected statistics in-memory.
    '''
    
    # The API isn't running multiple workers - it's not
    # necessary quite yet, so this lock is mainly
    # to demonstrate that we want to ensure we don't miss 
    # an update to race conditions when we do go to 
    # multiple workers.

    with stat_lock:
        message_statistics.success_messages += 1 if message_result.success else 0
        message_statistics.average_delay = round((message_statistics.average_delay * message_statistics.total_messages + message_result.delay) / (message_statistics.total_messages + 1), 4)
        message_statistics.total_messages += 1

    return "OK"

@app.get("/statistics", response_model=MessageStatistics)
def retrieve_statistics():
    '''
        Return collected statistics to Monitor frontend
    '''
    return message_statistics

@app.post("/reset", response_model=None)
def reset_statistics():
    '''
        Used for testing - reset statistics to 0s
    '''
    with stat_lock:
        message_statistics.total_messages = 0
        message_statistics.success_messages = 0
        message_statistics.average_delay = 0.0

    return "OK"