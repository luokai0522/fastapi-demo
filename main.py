# -*- coding: utf-8 -*-
"""最小可运行的 FastAPI 接口 Demo：分页 / 校验 / 依赖注入 / 错误处理。

运行：uvicorn main:app --reload
文档：http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Demo API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------- 数据层
# 真实项目换成 SQLAlchemy + PostgreSQL；这里用内存 dict 降低门槛。
_DB: dict[int, "Item"] = {}
_SEQ = 0


class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="商品名")
    price: float = Field(gt=0, description="单价，必须大于 0")
    tags: list[str] = Field(default_factory=list, max_length=5)


class ItemOut(ItemIn):
    id: int


class Page(BaseModel):
    total: int
    page: int
    size: int
    items: list[ItemOut]


class Pagination(BaseModel):
    page: int
    size: int
    offset: int


def pagination(
    page: Annotated[int, Query(ge=1, description="页码，从 1 开始")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="每页条数")] = 10,
) -> Pagination:
    """公共分页依赖：换成真实数据库时，offset/limit 直接传给 SQL。"""
    return Pagination(page=page, size=size, offset=(page - 1) * size)


PageDep = Annotated[Pagination, Depends(pagination)]


# ---------------------------------------------------------------- 接口
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items", response_model=Page)
def list_items(p: PageDep, q: Annotated[str | None, Query(max_length=50)] = None) -> Page:
    rows = sorted(_DB.values(), key=lambda x: x.id)
    if q:
        rows = [x for x in rows if q.lower() in x.name.lower()]
    window = rows[p.offset : p.offset + p.size]
    return Page(total=len(rows), page=p.page, size=p.size, items=window)


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemIn) -> ItemOut:
    global _SEQ
    _SEQ += 1
    item = ItemOut(id=_SEQ, **payload.model_dump())
    _DB[item.id] = item
    return item


@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int) -> ItemOut:
    item = _DB.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"item {item_id} not found")
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    if item_id not in _DB:
        raise HTTPException(status_code=404, detail=f"item {item_id} not found")
    del _DB[item_id]
