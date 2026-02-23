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

def save_parameters_to_file(product_id: str, param_name: str, param_value: str, xml_content: str, db: Session):
    """Сохраняет XML-параметры товара в файл с указанием имени параметра"""
    logger.info(f"Сохранение параметра '{param_name}' для товара ID: {product_id}")
    product_id = product_id.strip()
    if not product_id:
        logger.error("Пустой ID товара")
        raise HTTPException(400, "Неверный ID товара")
    
    try:
        # Всегда создаем XML с корневым элементом <data>
        try:
            # Пытаемся разобрать существующий XML
            root = fromstring(xml_content)
            # Если корневой элемент не <data>, создаем новый
            if root.tag != "data":
                new_root = ET.Element("data")
                # Добавляем все дочерние элементы из старого корня
                for child in root:
                    new_root.append(child)
                root = new_root
        except:
            # Если парсинг не удался, создаем новый корневой элемент
            root = ET.Element("data")
        
        # Находим или создаем элемент параметра
        elem = root.find(param_name)
        if elem is not None:
            elem.text = param_value
        else:
            new_elem = ET.Element(param_name)
            new_elem.text = param_value
            root.append(new_elem)
        
        # Формируем финальный XML
        xml_declaration = '<?xml version="1.0" encoding="Windows-1251"?>'
        xml_content = f"{xml_declaration}\n{ET.tostring(root, encoding='unicode')}"
        
        logger.debug(f"Сформированный XML: {xml_content[:1000]}")
        
        params_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('PARAMS_SUBDIR')) + os.sep
        logger.debug(f"Каталог параметров: {params_dir}")
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
            # Записываем XML в файл с кодировкой windows-1251
            tmp_file.write(xml_content.encode('windows-1251'))
            tmp_path = tmp_file.name
        
        with open(tmp_path, 'rb') as file:
            xml_blob = file.read()
        
        # Для Firebird используем хранимую процедуру
        sql = text("""SELECT * FROM "wp_SaveBlobToFile"(:dir, dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.xml', :xml_content)""")
        logger.debug(f"Выполняемый SQL: {sql}")
        
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

        logger.info(f"Тело запроса (первые 1000 байт): {body[:1000]}")
        logger.info(f"Параметры: model_id={modelid}, param_name={param}")
        
        try:
            # Получаем текущие параметры
            xml_content = get_xml_content(modelid, db)
            logger.info(f"Текущий XML перед обновлением:\n{xml_content}")
        except HTTPException:
            xml_content = '<?xml version="1.0" encoding="Windows-1251"?>\n<data/>'
            logger.info("Файл параметров не найден, создаем новый XML")
     
        try:
            # Пытаемся разобрать JSON
            json_data = json.loads(body)
            # Принимаем как "value" (для тестов) или "parameters" (для обратной совместимости)
            parameters = json_data.get("value") or json_data.get("parameters")
            logger.debug(f"Имя параметра {param} Переданные данные: {parameters}")
            if not parameters:
                raise HTTPException(400, "Поле 'value' или 'parameters' обязательно")
        except json.JSONDecodeError:
            # Если не JSON, пробуем как plain text
            parameters = body.decode("utf-8")
            #  Обновляем XML
      
        # logger.info(f"Обновленный XML после изменений:\n{updated_xml}")  
        return save_parameters_to_file(modelid, param, parameters, xml_content, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка загрузки параметров: {str(e)}")
        raise HTTPException(500, "Внутренняя ошибка сервера")


def get_xml_content(modelid: str, db: Session) -> str:
    """Получение XML-контента параметров товара"""
    try:
        logger.info(f"Запрос XML-контента для modelid: {modelid}")
        params_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('PARAMS_SUBDIR')) + os.sep
        logger.debug(f"Каталог параметров: {params_dir}")
        
        # Для Firebird используем оригинальный запрос
        sql = text("""
            SELECT loadblobfromfile(
                :param_dir || dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.xml'
            )
            FROM RDB$DATABASE
        """)
        result = db.execute(sql, {
            "modelid": modelid,
            "param_dir": params_dir
        }).fetchone()
        
        if not result or not result[0]:
            logger.warning(f"Параметры не найдены для modelid: {modelid}")
            raise HTTPException(404, "Параметры не найдены")
        
        logger.info(f"XML-контент успешно получен для modelid: {modelid}")
        return result[0].decode("windows-1251")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Ошибка получения XML-контента: {str(e)}")
        raise HTTPException(500, "Internal server error")

@router.get(
    "/{modelid}",
    summary="Получение параметров товара в XML или JSON формате",
    response_description="Параметры товара",
    responses={
        200: {
            "content": {
                "application/xml": {},
                "application/json": {}
            },
            "description": "Параметры товара"
        },
        404: {"description": "Параметры не найдены"},
        500: {"description": "Ошибка сервера"},
    })
async def get_parameters(
    modelid: str,
    format: str = Query('xml', description="Формат возвращаемых данных: xml или json"),
    db: Session = Depends(get_db)
):
    try:
        content = get_xml_content(modelid, db)
        
        # Обработка формата вывода
        if format == 'json':
            try:
                # Преобразование XML в словарь
                root = fromstring(content)
                data = {}
                for child in root:
                    data[child.tag] = child.text
                return data
            except Exception as e:
                logger.error(f"Ошибка преобразования XML в JSON: {str(e)}")
                raise HTTPException(500, "Ошибка преобразования данных")
        else:
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
    param_name: str,
    db: Session = Depends(get_db)):
    try:
        # Получаем XML контент напрямую, не вызывая get_parameters
        content = get_xml_content(model_id, db)
        
        # Парсим XML и находим параметр
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
