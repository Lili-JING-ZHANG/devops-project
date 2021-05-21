#!/usr/bin/env python3

import uvicorn

from fastapi import Depends, FastAPI, HTTPException
from starlette.responses import Response
from fastapi.logger import logger
from mongoengine import connect
from starlette.requests import Request
from pydantic import BaseModel
from typing import List

from photographer_mongo_wrapper import *
import pymongo
import requests
from photographer_const import Dname, Photographer, PHOTOGRAPHER_BODY, Photographers
from photographer import MongoPhotographer
import re

mongo_service_host = 'mongo-service'

mongo_service = mongo_service_host

app = FastAPI(title = "Photographer Service")

# FastAPI logging
gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers


@app.on_event("startup")
def startup_event():
    connect("photographers", host=mongo_service)
    # connect("devops-s21-00-photographer-db",
    #         username="devops-s21-00-user",
    #         password="***",
    #         host="mongo.cloud.rennes.enst-bretagne.fr")

@app.get("/photographers", response_model = Photographers, status_code = 200)    
def get_photographers(request: Request, offset: int = 0, limit: int = 10):
    logger.info("get_photographers")
    list_of_photographers = list()
    try:
        (has_more, photographers) = mongo_get_photographers(offset, limit)
        for ph in photographers:
            ph._data['link'] = "http://" + request.headers['host'] + "/photographer/" + str(ph.display_name)
            list_of_photographers.append(ph._data)
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")
    return {'items': list_of_photographers, 'has_more': has_more}

@app.post("/photographers", status_code = 201)
def create_photographer(response: Response, photographer: Photographer = PHOTOGRAPHER_BODY):
    logger.info("Creating photographer ...")
    try:
        if mongo_check(photographer.display_name) > 0:                       
            raise HTTPException(status_code = 409, detail = "Conflict")
        else:                                                                   
            ph = mongo_add (photographer.display_name,                       
                            photographer.first_name,                         
                            photographer.last_name,
                            photographer.interests
            )
            response.headers["Location"] = "/photographer/" + str(ph.display_name)
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise HTTPException(status_code = 503, detail = "Mongo unavailable")

@app.get("/photographer/{display_name}", response_model = Photographer, status_code = 200)    
def get_photographer(display_name: str = Dname.PATH_PARAM):

    logging.info('Getting photographer with name: ' + display_name)
    try:
        ph = mongo_get_photographer_by_name(display_name)
    except (MongoPhotographer.DoesNotExist, InvalidId):
        raise HTTPException(status_code = 404, detail = "Photographer does not exist")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code = 503, detail = "Mongo unavailable")
    return ph._data

    
@app.put("/photographer/{display_name}", status_code = 200)
def update_photographer(display_name: str = Dname.PATH_PARAM,
                        photographer: Photographer = PHOTOGRAPHER_BODY):
    try:
        ph = mongo_update_photographer_by_name(display_name, photographer)
        if ph:
            return
        else:
            raise HTTPException(status_code = 503, detail = "Not Found")
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise HTTPException(status_code = 503, detail = "Mongo unavailable")

@app.put("/photographer/{display_name}", status_code = 200)
def update_photographer(display_name: str = Dname.PATH_PARAM,
                        photographer: Photographer = PHOTOGRAPHER_BODY):
    try:
        ph = mongo_update_photographer_by_name(display_name, photographer)
        if ph:
            return
        else:
            raise HTTPException(status_code = 503, detail = "Not Found")
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise HTTPException(status_code = 503, detail = "Mongo unavailable")
@app.delete("/photographer/{display_name}", status_code = 200)
def delete_photographer(display_name: str = Dname.PATH_PARAM):
    try:
        ph = mongo_delete_photographer_by_name(display_name)
        if ph:
            return
        else:
            raise HTTPException(status_code = 503, detail = "Not Found")
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise HTTPException(status_code = 503, detail = "Mongo unavailable")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="info")
    #logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(gunicorn_logger.level)
