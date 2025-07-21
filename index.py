from fastapi import FastAPI
from pydantic import BaseModel
from typing import List,Optional
from pymongo import MongoClient
from bson import ObjectId

app=FastAPI()

client=MongoClient("mongodb://localhost:27017")
db=client["ecommerce"]
products_col=db["products"]
orders_col=db["orders"]

@app.get("/products")
# Helpers
def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

class orderItem(BaseModel):
    productID:str
    qty:int

class createOrder(BaseModel):
    userId:str
    items:List[orderItem]

# List Products API
@app.get("/products")
def list_products(name: Optional[str] = None, size: Optional[str] = None, limit: int = 10, offset: int = 0):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if size:
        query["sizes.size"] = size

    products = list(products_col.find(query).skip(offset).limit(limit))
    return {
        "data": [serialize(p) for p in products],
        "page": {
            "next": offset + limit,
            "limit": limit,
            "previous": max(offset - limit, 0)
        }
    }

# Create Order API 
@app.post("/orders", status_code=201)
def create_order(order: createOrder):
    new_order = {
        "userId": order.userId,
        "items": [item.dict() for item in order.items]
    }
    result = orders_col.insert_one(new_order)
    return {"id": str(result.inserted_id)}

# Get User Orders API
@app.get("/orders/{user_id}")
def get_orders(user_id: str, limit: int = 10, offset: int = 0):
    orders = list(orders_col.find({"userId": user_id}).skip(offset).limit(limit))
    return {
        "data": [serialize(o) for o in orders],
        "page": {
            "next": offset + limit,
            "limit": limit,
            "previous": max(offset - limit, 0)
        }
    }
