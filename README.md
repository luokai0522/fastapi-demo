# demo-fastapi

一个最小可运行的 FastAPI 接口 Demo，用来补简历上「FastAPI / Pydantic / 分页 / 依赖注入」这一行。
20 分钟能跑通，面试时能讲清楚每个设计取舍。

## 跑起来

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

打开 http://127.0.0.1:8000/docs ，直接在 Swagger 页面点「Try it out」就能调。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查，返回 `{"status": "ok"}` |
| GET | `/items?page=1&size=10&q=关键词` | 分页 + 标题模糊搜索 |
| POST | `/items` | 新建，body 校验失败返回 422 |
| GET | `/items/{item_id}` | 不存在返回 404 |
| DELETE | `/items/{item_id}` | 删除，返回 204 |

## 面试怎么讲（背这 3 句）

1. 「这个 Demo 我用 Pydantic 做入参校验，字段类型不对 FastAPI 会自动返回 422，不用手写 if。」
2. 「分页用 `page/size` 两个 query 参数，返回里带 `total`，前端能算总页数；数据层现在是内存 dict，换成 PostgreSQL 只需要改 store 这一层。」
3. 「依赖注入我用 `Depends` 把分页参数抽成公共依赖，后面加鉴权时可以在同一个位置挂 `Depends(get_current_user)`。」

## 接下来可以做的（面试被问「怎么上生产」时用）

- [ ] 把 `store.py` 换成 SQLAlchemy + PostgreSQL，加 Alembic 迁移
- [ ] 列表接口加 Redis 缓存（对应简历里「离线预计算 + 缓存」的思路）
- [ ] 加 JWT 鉴权：`Depends(get_current_user)` 挂在写接口上
- [ ] 加 pytest：正常分页、越界页、404、422 四个用例
- [ ] 用 `wrk` 或 `locust` 压一次，记录 QPS / P95，和简历里 Flask 的 864 req/s 做对比

## 目录

```
demo-fastapi/
├── main.py            # 路由 + Pydantic 模型 + 分页依赖
├── requirements.txt
└── README.md
```
