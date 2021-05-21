#!/usr/bin/env python3

import logging
import json

from photographer import MongoPhotographer
from mongoengine import *
import socket
import pymongo

from bson.objectid import ObjectId
from bson import json_util
from bson.errors import InvalidId


import json
import robustify

logging.basicConfig(level=logging.DEBUG)

@robustify.retry_mongo
def mongo_check(display_name):
    count = MongoPhotographer.objects(display_name=display_name).count()
    return count

@robustify.retry_mongo
def mongo_add(display_name, first_name, last_name, interests):
    ph = MongoPhotographer(display_name = display_name,
                           first_name = first_name,
                           last_name = last_name,
                           interests = interests).save()
    return ph

@robustify.retry_mongo
def mongo_get_photographers(offset, limit):
    qs = MongoPhotographer.objects.order_by('id').skip(offset).limit(limit)
    if qs.count(with_limit_and_skip = False) > (offset + limit):
        has_more = True
    else:
        has_more = False

    return (has_more, qs)

@robustify.retry_mongo
def mongo_get_photographer_by_id(photographer_id):
    ph = MongoPhotographer.objects(id=ObjectId(photographer_id)).get()
    return ph

@robustify.retry_mongo
def mongo_get_photographer_by_name(name):
    ph = MongoPhotographer.objects(display_name=name).get()
    return ph
@robustify.retry_mongo
def mongo_delete_photographer_by_name(name):
    ph = MongoPhotographer.objects(display_name=name).get()
    try:

        ph.delete()
    except (MongoPhotographer.DoesNotExist,
            MongoPhotographer.MultipleObjectsReturned):
        return False
    return True


@robustify.retry_mongo
def mongo_update_photographer_by_name(name, attributes):
    try:
        ph = MongoPhotographer.objects(display_name=name).get()
        for key, value in attributes:
            set_attr = "set__" + key
            ph.update(**{set_attr: value})
    except (MongoPhotographer.DoesNotExist,
            MongoPhotographer.MultipleObjectsReturned):
        return False
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.ServerSelectionTimeoutError,
            pymongo.errors.NetworkTimeout) as e:
        raise 
    return True

