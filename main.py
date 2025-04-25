import os
from os.path import join, dirname
import json
from datetime import date

from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends, Response, Request
from typing import Optional

import httpx

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = FastAPI()

headers = {'X-API-KEY': os.environ.get("X_API_KEY")}


@app.get(
    "/customer_list/",
    tags=["Клиенты"],
    summary="Список клиентов.",
    description="Получение списка клиентов с возможностью фильтрации по имени, email и диапазону дат.",
    responses={
        200: {
            "description": "Список клиентов успешно получен.",
            "content": {
                "application/json": {
                    "example": {
                        "customers": [],
                        "pagination": {
                            "currentPage": 1,
                            "limit": 10,
                            "totalCount": 2,
                            "totalPageCount": 1
                        },
                        "success": True
                    }
                }
            }
        },
        400: {
            "description": "Список клиентов не получен.",
            "content": {
                "application/json": {
                    "example": {
                        "errorMsg": "Invalid data",
                        "errors": {"error": ["Error text"]},
                        "success": False
                    }
                }
            }
        }
    }
)
async def get_customers(
        name: Optional[str] = Query(
            None,
            description="Фильтр по имени клиента. Поиск выполняется по частичному совпадению.",
            example="Иван"
        ),
        email: Optional[str] = Query(
            None,
            description="Фильтр по email клиента. Поиск выполняется по точному совпадению.",
            example="ivan@example.com"
        ),
        date_from: Optional[date] = Query(
            None,
            description="Фильтр по начальной дате создания клиента (включительно). Формат: YYYY-MM-DD.",
            example="2023-01-01"
        ),
        date_to: Optional[date] = Query(
            None,
            description="Фильтр по конечной дате создания клиента (включительно). Формат: YYYY-MM-DD.",
            example="2023-12-31"
        )
):
    params = {}

    if name:
        params['filter[name]'] = name
    if email:
        params['filter[email]'] = email
    if date_from:
        params['filter[dateFrom]'] = date_from.isoformat()
    if date_to:
        params['filter[dateTo]'] = date_to.isoformat()

    r = httpx.get('https://usernzt.retailcrm.ru/api/v5/customers', headers=headers, params=params)

    if r.status_code == 200:
        return r.json()
    else:
        raise HTTPException(status_code=r.status_code, detail=r.json())


@app.post(
    "/customer_create/",
    tags=["Клиенты"],
    summary="Создание клиента.",
    responses={
        201: {
            "description": "Клиент создан.",
            "content": {
                "application/json": {
                    "example": {
                        'success': True, 'id': 0
                    }
                }
            }
        },
        400: {
            "description": "Клиент не создан.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False, 'errorMsg': "Error message"
                    }
                }
            }
        }
    },
    status_code=201,
)
async def customer_create(
        first_name: str = Query(..., description="Имя", example="Иван"),
        last_name: Optional[str] = Query(None, description="Фамилия", example="Иванов"),
        patronymic: Optional[str] = Query(None, description="Отчество", example="Иванович"),
        email: str = Query(..., description="Адрес электронной почты", example="ivan@example.com"),
        birthday: Optional[date] = Query(None, description="Дата рождения в формате ГГГГ-ММ-ДД", example="2023-01-01"),
        sex: Optional[str] = Query(None, description="Пол (выбор между male/female).", example="male"),
        region: Optional[str] = Query(None, description="Страна", example="Беларусь"),
        city: Optional[str] = Query(None, description="Населенный пункт", example="Минск"),
        number: str = Query(..., description="Номер телефона", example="+375291234567"),
):
    data = {
        'firstName': first_name,
        'lastName': last_name,
        'patronymic': patronymic,
        'email': email,
        'birthday': birthday.isoformat(),
        'sex': sex,
        'address': {
            'region': region,
            'city': city
        },
        'phones': [{
            'number': number,
        }],
    }

    params = {
        'customer': json.dumps(data, ensure_ascii=False),
    }
    r = httpx.post('https://usernzt.retailcrm.ru/api/v5/customers/create', headers=headers, data=params)
    if r.status_code == 201:
        return r.json()
    else:
        raise HTTPException(status_code=r.status_code, detail=r.json())


@app.get(
    "/orders/{customer_id}",
    tags=["Заказы"],
    summary="Список заказов клиента по ID.",
    description="Получение списка заказов одного конкретного клиента по его ID.",
    responses={
        200: {
            "description": "Список заказов клиента получен.",
            "content": {
                "application/json": {
                    "example": {
                        "orders": [],
                        "pagination": {"currentPage": 0,
                                       "limit": 0,
                                       "totalCount": 0,
                                       "totalPageCount": 0},
                        "success": True}
                }
            }
        },
        400: {
            "description": "Список заказов клиента не получен.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False, "errorMsg": "Error message"
                    }
                }
            }
        }
    }
)
async def get_orders(customer_id: int = Path(..., description="ID клиента", example=0)):
    params = {
        'filter[customerId]': customer_id,
    }
    r = httpx.get('https://usernzt.retailcrm.ru/api/v5/orders', headers=headers, params=params)

    if r.status_code == 200:
        return r.json()
    else:
        raise HTTPException(status_code=r.status_code, detail=r.json())


@app.post(
    "/orders/",
    tags=["Заказы"],
    summary="Создание нового заказа.",
    responses={
        201: {
            'description': "Новый заказ создан.",
            'content': {
                "application/json": {
                    "example": {
                        'id': 0,
                        'order': {'order: info'},
                        'success': True}
                }
            }
        },
        400: {
            'description': "Заказ не создан.",
            'content': {
                "application/json": {
                    "example": {
                        'success': False, 'errorMsg': "Error message"
                    }
                }
            }
        }
    },
    status_code=201,
)
async def order_create(
        customer_id: int = Query(..., description="ID клиента", example=0),
        order_number: int = Query(..., description="Номер заказа", example=999),
        product_name: str = Query(..., description="Название товара", example="Шины"),
        quantity: int = Query(..., description="Количество товара", example=4),
        price: float = Query(..., description="Цена на товар", example=0.99),
):
    data = {
        'customer': {
            'id': customer_id,
        },
        'number': order_number,
        'items': [{
            'productName': product_name,
            'quantity': quantity,
            'initialPrice': price,
        }],

    }
    params = {
        'order': json.dumps(data, ensure_ascii=False),
    }
    r = httpx.post('https://usernzt.retailcrm.ru/api/v5/orders/create', headers=headers, data=params)
    if r.status_code == 201:
        return r.json()
    else:
        raise HTTPException(status_code=r.status_code, detail=r.json())


@app.post(
    "/orders/payment/",
    tags=["Заказы"],
    summary="Создание и привязка платежа к заказу.",
    responses={
        201: {
            'description': "Платеж создан и привязан к заказу.",
            'content': {
                "application/json": {
                    "example": {'id': 0, 'success': True}
                }
            }
        },
        400: {
            'description': "Платеж не создан и не привязан.",
            'content': {
                "application/json": {
                    "example": {
                        'success': False, 'errorMsg': "Error message"
                    }
                }
            }
        }
    },
    status_code=201,
)
async def order_payment(
        order_id: int = Query(..., description="ID заказа", example=0),
):
    data = {
        'order': {'id': order_id},
        'type': 'cash',
        'status': 'paid',
    }
    params = {'payment': json.dumps(data, ensure_ascii=False)}
    r = httpx.post('https://usernzt.retailcrm.ru/api/v5/orders/payments/create', headers=headers, data=params)
    if r.status_code == 201:
        return r.json()
    else:
        raise HTTPException(status_code=r.status_code, detail=r.json())
