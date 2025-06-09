from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
import io
import zipfile
import logging

logger = logging.getLogger("api")

# Helper functions to decode model IDs
def dec64i0(modelid: str) -> str:
    """Decode first part of model ID"""
    return modelid[:8]

def dec64i1(modelid: str) -> str:
    """Decode second part of model ID"""
    return modelid[8:16]
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import os
import tempfile
import zipfile
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.database import get_db
from fastapi.templating import Jinja2Templates
from math import ceil
from sqlalchemy import or_

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/modelgoods/parameters", tags=["modelgoods"])

class ParametersInput(BaseModel):
    parameters: str

def save_parameters_to_file(product_id: str, xml_content: str, db: Session):
    """Сохраняет XML-параметры товара в файл"""
    logger.info(f"Сохранение параметров для товара ID: {product_id}")
    product_id = product_id.strip()
    if not product_id:
        logger.error("Пустой ID товара")
        raise HTTPException(400, "Неверный ID товара")
    
    try:
        # Обработка XML-контента
        xml_content = xml_content.strip()
        if 'encoding="UTF-8"' not in xml_content:
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_content}'
        logger.debug(f"XML контент (начало): {xml_content[:1000]}")
        
        params_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('PARAMS_SUBDIR')) + os.sep
        logger.debug(f"Каталог параметров: {params_dir}")
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
            # Записываем XML в файл с кодировкой windows-1251
            tmp_file.write(xml_content.encode('windows-1251'))
            tmp_path = tmp_file.name
        
        # Передаем временный файл в хранимую процедуру
        sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.xml', :xml_content)""")
        logger.debug(f"Выполняемый SQL: {sql}")
        
        with open(tmp_path, 'rb') as file:
            xml_blob = file.read()
        
            db.execute(sql, {
                'dir': params_dir,
                'modelid': product_id,
                "xml_content": xml_blob
            }).fetchall()
        db.commit()
        
        # Update model changedate
        update_sql = text("""UPDATE "modelgoods" SET "changedate"=current_timestamp WHERE "id"=:id""")
        logger.debug(f"Обновление даты изменения: {update_sql}")
        db.execute(update_sql, {"id": product_id})
        db.commit()
        
        logger.info(f"Параметры успешно сохранены для товара ID: {product_id}")
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        logger.exception(f"Ошибка сохранения параметров: {str(e)}")
        raise HTTPException(500, "Ошибка сервера при сохранении параметров")
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass

@router.post(
    "/{modelid}/{param}",
    summary="Сохранение xml файла с параметрами товара",
    response_description="Результат сохранения параметров",
    responses={
        200: {"description": "параметры успешно сохранены"},
        400: {"description": "Неверный формат данных"},
        404: {"description": "Неверное имя параметра"},
        500: {"description": "Ошибка сервера при сохранении"},
    },
)
async def upload_model_parameters(
    request: Request,
    modelid: str,
    param: str,  # Добавляем параметр пути для сохранения структуры URL
    db: Session = Depends(get_db)
):
    """Эндпоинт для загрузки полного XML параметров"""
    try:
        body = await request.body()
        try:
            # Пытаемся разобрать JSON
            json_data = json.loads(body)
            parameters = json_data.get("parameters")
            logger.debug(f"Переданные данные: {parameters}")
            if not parameters:
                raise HTTPException(400, "Поле 'parameters' обязательно")
        except json.JSONDecodeError:
            # Если не JSON, пробуем как plain text
            parameters = body.decode("utf-8")
        
        return save_parameters_to_file(modelid, parameters, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка загрузки параметров: {str(e)}")
        raise HTTPException(500, "Внутренняя ошибка сервера")

class ParameterValue(BaseModel):
    value: str = Field(..., example="42", description="Значение параметра в строковом формате")

def update_xml_parameter(xml_content: str, param_name: str, param_value: str) -> str:
    try:
        root = fromstring(xml_content)
        elem = root.find(param_name)
        if elem is not None:
            elem.text = param_value
        else:
            new_elem = ET.Element(param_name)
            new_elem.text = param_value
            root.append(new_elem)
        xml_str = ET.tostring(root, encoding="windows-1251", xml_declaration=True).decode("windows-1251")
        return xml_str.replace('encoding="windows-1251"', 'encoding="WINDOWS-1251"')
    except Exception as e:
        logger.error(f"XML parsing error: {str(e)}")
        return f'<?xml version="1.0" encoding="WINDOWS-1251"?>\n<data>\n<{param_name}>{param_value}</{param_name}>\n</data>'

@router.get(
    "/{modelid}",
    response_class=Response,
    summary="Получение xml файла с параметрами товара",
    response_description="XML файл с параметрами",
    responses={
        200: {"content": {"application/xml": {}}, "description": "XML параметров"},
        404: {"description": "Параметры не найдены"},
        500: {"description": "Ошибка сервера"},
    })
async def get_parameters(
    modelid: str,
    db: Session = Depends(get_db)):
    try:
        logger.info(f"Запрос параметров для modelid: {modelid}")
        params_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('PARAMS_SUBDIR')) + os.sep
        logger.debug(f"Каталог параметров: {params_dir}")
        
        sql = text("""
            SELECT loadblobfromfile(
                :param_dir || dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.xml'
            )
            FROM RDB$DATABASE
        """)
        logger.debug(f"Выполняемый SQL: {sql}")
        logger.debug(f"modelid: {modelid},params_dir: {params_dir}")
        result = db.execute(sql, {
            "modelid": modelid,
            "param_dir": params_dir
        }).fetchone()
        


        if not result or not result[0]:
            logger.warning(f"Параметры не найдены для modelid: {modelid}")
            raise HTTPException(404, "Параметры не найдены")
        
        logger.info(f"Параметры успешно получены для modelid: {modelid}")
        content = result[0].decode("windows-1251")
        return Response(content=content, media_type="application/xml")
    except HTTPException as he:
        logger.error(f"HTTP ошибка: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"Ошибка получения параметров: {str(e)}")
        raise HTTPException(500, "Internal server error")

@router.get("/{model_id}/{param_name}",
    summary="Получение значения конкретного параметра",
    responses={
        200: {"description": "Значение параметра"},
        404: {"description": "Параметр не найден"},
        500: {"description": "Ошибка сервера"}})
async def get_parameter(
    model_id: str,
    param_name: str = Query(..., min_length=1),
    db: Session = Depends(get_db)):
    try:
        result = await get_parameters(model_id, db)
        content = result.body.decode("utf-8")
        root = fromstring(content)
        elem = root.find(param_name)
        if elem is not None and elem.text:
            return {"value": elem.text}
        raise HTTPException(404, "Параметр не найден")
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка получения параметра: {str(e)}")
        raise HTTPException(500, "Internal server error")

@router.post("/{model_id}/{param_name}",
    summary="Сохранение значения конкретного параметра",
    responses={
        200: {"description": "Параметр успешно сохранен"},
        400: {"description": "Неверный формат данных"},
        500: {"description": "Ошибка сервера"}})
async def set_parameter(
    request: Request,  # Добавляем request для логирования
    model_id: str,
    param_name: str,
    data: ParameterValue,
    db: Session = Depends(get_db)):
    try:
        # Логируем тело запроса для отладки
        body = await request.body()
        logger.info(f"Тело запроса (первые 1000 байт): {body[:1000]}")
        
        try:
            result = await get_parameters(model_id, db)
            xml_content = result.body.decode("utf-8")
        except HTTPException:
            xml_content = '<?xml version="1.0" encoding="WINDOWS-1251"?>\n<data/>'
        
        updated_xml = update_xml_parameter(xml_content, param_name, data.value)
        
        # Упрощаем вызов: сохраняем параметры напрямую
        return save_parameters_to_file(model_id, updated_xml, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка сохранения параметра: {str(e)}")
        raise HTTPException(500, "Internal server error")
