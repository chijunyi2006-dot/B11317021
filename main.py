from typing import Annotated

from fastapi import FastAPI,Body,Path, Cookie,Form
from pydantic import BaseModel,Field

class Item(BaseModel):
    name: str
    descripion: str | None = Field(
        default=None,title="Ted description of the item",max_length=300
    )
    price: float = Field(gt=0 , description="The price must be greater than zero")
    tax: float | None = None
    tags: list = []




app = FastAPI()

@app.post("/login")
async def login(
    username: Annotated[str,Form()],
    password: Annotated[str,Form()]
):
    return {"username": username}

@app.get("/")
async def root():
    return{"message":"Hello world"}


@app.get("/items/{item_id}")   
async def read_items(item_id):
    return{"item_id" : item_id}

'''
@app.get("/items/")
async def read_item(skip : int = 0 , limit: int=10):
    return fake_items_db[skip : skip + limit]
fake_items_db = [
    {"item_name" : "Foo"},
    {"item_name" : "Bar"},
    {"item_name" : "Baz"}
]
'''

@app.get("/items/")
async def read_items(ads_id: Annotated[str |None ,Cookie()]):
    return {"ads_id":ads_id}

'''
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump() # item.dict()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
'''
@app.get("/items/")
async def creat_items(Item: Item) -> Item:
    return Item

'''

@app.put("/items/{item_id}")   
async def update_item(
    item_id:Annotated[int,Path(title="The ID of the item rto get",ge=0,le=1000)], 
    q:str | None = None,
    item: Item | None = None,
):
    result = {"item_id" : item_id}
    if q:
        result.update({"q":q})
    if item:
        results.update({"item": item})
    return result
'''
@app.put("/items/{item_id}")
async def update_item(item_id: int, item:Annotated[Item, Body(embed=True)]):
    results = {"itec_id": item_id, "item": item}
    return results