from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
import xml.etree.ElementTree as ET
from defusedxml.ElementTree import fromstring
import io
import zipfile
import logging

logger = logging.getLogger("api")
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import os
import tempfile
import zipfile
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.database import get_db
from app.models import dec64i0, dec64i1

router = APIRouter(prefix="/modelgoods/parameters", tags=["modelgoods"])


class ParametersInput(BaseModel):
    parameters: str

def save_parameters_to_file(product_id: str, params: str, db: Session):
    product_id = product_id.strip()
    if not product_id or not params:
        raise HTTPException(400, "Invalid product ID or parameters")
    
    try:
        if product_id and params:
            # Store raw XML without HTML formatting
            # Явно указываем кодировку Windows-1251 в XML декларации
            # Форсируем указание кодировки в XML декларации
            params_xml = params.strip()
            if 'encoding="UTF-8"' not in params_xml:
                params_xml = params_xml.replace('<?xml', '<?xml encoding="UTF-8"')
                params_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n{params_xml}'
            params_dir = os.path.join(os.getenv('BASE_DIR'), os.getenv('PARAMS_SUBDIR')) + os.sep
            sql = f"""SELECT * FROM \"wp_SaveBlobToFile\"('{params_dir}', dec64i0(:modelid) || '_' || dec64i1(:modelid) || '.xml',:xml_content)"""
            
            try:
                db.execute(
                    text(sql), 
                    {
                        'modelid': product_id,
                    "xml_content": params_xml.encode('windows-1251')  # Явное указание WINDOWS-1251 кодировки
                    }
                ).fetchall()
                logger.info(f"Saved bytes sample (WINDOWS-1251): {params_xml.encode('windows-1251')[:100].hex()}")  # Логируем WINDOWS-1251 байты
                db.commit()
                db.execute(text("""UPDATE "modelgoods" SET "changedate"=current_timestamp where "id"=:id"""), {"id": product_id})
                db.commit()
            except Exception as e:
                raise HTTPException(500, f"Failed to save parameters: {str(e)}")
            
            return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving parameters: {str(e)}")
        raise HTTPException(500, "Parameters save failed")

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
    data: ParametersInput,
    db: Session = Depends(get_db)
):
    try:
        return save_parameters_to_file(modelid, data.parameters, db)
    except Exception as e:
        logger.error(f"Parameters upload error: {str(e)}")
        raise HTTPException(500, "Internal server error")

# Новые модели для работы с отдельными параметрами
class ParameterValue(BaseModel):
    value: str = Field(..., example="42", description="Значение параметра в строковом формате")

def update_xml_parameter(xml_content: str, param_name: str, param_value: str) -> str:
    """Обновляет или добавляет параметр в XML структуру"""
    try:
        root = fromstring(xml_content)
        elem = root.find(param_name)
        if elem is not None:
            elem.text = param_value
        else:
            new_elem = ET.Element(param_name)
            new_elem.text = param_value
            root.append(new_elem)
        # Нормализуем XML декларацию для WINDOWS-1251
        xml_str = ET.tostring(root, encoding="windows-1251", xml_declaration=True).decode("windows-1251")
        return xml_str.replace('encoding="windows-1251"', 'encoding="WINDOWS-1251"')  # Приводим к верхнему регистру
    except Exception as e:
        logger.error(f"XML parsing error: {str(e)}")
        return f'<?xml version="1.0" encoding="WINDOWS-1251"?>\n<data>\n<{param_name}>{param_value}</{param_name}>\n</data>'

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
    model_id: str,
    param_name: str,
    data: ParameterValue,
    db: Session = Depends(get_db)):
    try:
        try:
            # Пытаемся получить существующие параметры
            result = await get_parameters(model_id, db)
            xml_content = result.body.decode("utf-8")
        except HTTPException:
            # Если файла нет - создаем пустой XML
            xml_content = '<?xml version="1.0" encoding="WINDOWS-1251"?>\n<data/>'
        
        updated_xml = update_xml_parameter(xml_content, param_name, data.value)
        # Создаем заглушку для Request
        from fastapi.requests import Request
        from starlette.requests import Scope
        fake_scope = {
            'type': 'http',
            'asgi': {'version': '3.0', 'spec_version': '2.3'},
            'http_version': '1.1',
            'path': '/',
            'method': 'POST',
            'headers': [],
            'server': ('localhost', 7990),
            'scheme': 'http',
            'client': ('127.0.0.1', 12345),
            'root_path': '',
            'query_string': b'',
            'extensions': {}
        }
        return await upload_model_parameters(Request(scope=fake_scope), model_id, ParametersInput(parameters=updated_xml), db)
        
    except Exception as e:
        logger.error(f"Ошибка сохранения параметра: {str(e)}")
        raise HTTPException(500, "Internal server error")

@router.get("/{model_id}")
async def get_parameters(model_id: str, db: Session = Depends(get_db)):
    try:
        try:
            file_path = os.path.join(
                os.getenv('BASE_DIR'),
                os.getenv('PARAMS_SUBDIR'),
                f"{dec64i0(model_id)}_{dec64i1(model_id)}.xml"
            )
            logger.info(f"Trying to load parameters from: {file_path}")
            
            result = db.execute(
                text("""
                    SELECT loadblobfromfile(:file_path)
                    FROM "modelgoods" 
                    WHERE "id" = :model_id
                """),
                {"model_id": model_id, "file_path": file_path}
            ).fetchone()
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise HTTPException(500, "Failed to execute database query")

        if not result or not result[0]:
            raise HTTPException(404, "Параметры не найдены")

        raw_bytes = result[0]
        logger.info(f"Raw bytes from DB (hex): {raw_bytes.hex()[:200]}")  # Log first 200 hex chars
        
        try:
            # Пытаемся определить кодировку по BOM
            if raw_bytes.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
                content = raw_bytes.decode('utf-8-sig')
            elif raw_bytes.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
                content = raw_bytes.decode('utf-16-le')
            else:  # Пробуем Windows-1251 и UTF-8 как fallback
                try:
                    content = raw_bytes.decode('windows-1251')
                except UnicodeDecodeError:
                    content = raw_bytes.decode('utf-8', errors='replace').encode('utf-8').decode('utf-8')
                if 'encoding="' in content:
                    encoding_info = content.split('encoding="')[1].split('"')[0]
                else:
                    encoding_info = 'unknown'
                logger.info(f"XML encoding detected: {encoding_info}")
                logger.info("Decoded content start: %s", content[:200].encode('utf-8', errors='replace').decode('utf-8'))  # Явное кодирование для логов
            # Явно указываем кодировку в XML ответе
            # Кодируем в UTF-8 и возвращаем как bytes с явным указанием кодировки
            try:
                # Формируем XML ответ с явной кодировкой
                xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{content}'
                logger.info(f"Final XML content: {xml_content[:200]}")  # Логируем итоговый XML
                # Формируем ответ с явным указанием кодировки
                encoded_content = xml_content.encode('utf-8')
                logger.info(f"Response bytes (hex): {encoded_content[:100].hex()}")  # Логируем первые 100 байт ответа
                return Response(
                    content=encoded_content,
                    media_type="application/xml",
                    headers={
                        "Content-Type": "application/xml; charset=utf-8",
                        "Content-Length": str(len(encoded_content))
                    }
                )
            except Exception as e:
                logger.error(f"Response creation error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create response",
                    headers={"Content-Type": "application/xml; charset=utf-8"}
                )
        except Exception as e:
            logger.error(f"Decoding failed: {str(e)}")
            raise HTTPException(500, "Failed to decode parameters")

    except Exception as e:
        logger.error(f"Ошибка получения параметров: {str(e)}")
        raise HTTPException(500, "Internal server error")
