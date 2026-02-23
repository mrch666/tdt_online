from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
import logging
from pathlib import Path

logger = logging.getLogger("api")


def check_and_create_external_images_table(db: Session):
    """
    Проверяет существование таблицы modelgoods_external_images и создает ее при необходимости
    Включает создание генератора и триггера для автоматической генерации ID
    """
    try:
        # Проверяем существование таблицы
        inspector = inspect(db.get_bind())
        table_exists = inspector.has_table('modelgoods_external_images')
        
        if not table_exists:
            logger.info("Таблица modelgoods_external_images не существует, создаем...")
            
            # Читаем полный SQL файл с созданием таблицы, генератора и триггера
            sql_file_path = Path(__file__).parent.parent / "create_external_images_complete.sql"
            
            if not sql_file_path.exists():
                logger.error(f"SQL файл не найден: {sql_file_path}")
                return False
            
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Разделяем SQL на отдельные команды (используем точку с запятой как разделитель)
            # Но сохраняем блоки SET TERM ^ ... SET TERM ; ^ как единые команды
            sql_commands = []
            current_command = ""
            in_term_block = False
            
            for line in sql_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('SET TERM ^'):
                    in_term_block = True
                    current_command = line + '\n'
                elif line.startswith('SET TERM ; ^'):
                    current_command += line + '\n'
                    sql_commands.append(current_command.strip())
                    current_command = ""
                    in_term_block = False
                elif in_term_block:
                    current_command += line + '\n'
                elif ';' in line:
                    # Разделяем по точке с запятой вне блоков SET TERM
                    parts = line.split(';')
                    for i, part in enumerate(parts):
                        if i < len(parts) - 1:
                            # Добавляем часть с точкой с запятой
                            if current_command:
                                current_command += ' ' + part + ';'
                            else:
                                current_command = part + ';'
                            sql_commands.append(current_command.strip())
                            current_command = ""
                        else:
                            # Последняя часть строки
                            if part.strip():
                                current_command = part.strip()
                else:
                    if current_command:
                        current_command += ' ' + line
                    else:
                        current_command = line
            
            # Добавляем последнюю команду, если она есть
            if current_command.strip():
                sql_commands.append(current_command.strip())
            
            # Выполняем команды
            for command in sql_commands:
                command = command.strip()
                if command:
                    try:
                        logger.debug(f"Выполняем SQL команду: {command[:200]}...")
                        db.execute(text(command))
                        logger.debug(f"SQL команда выполнена успешно")
                    except Exception as e:
                        logger.warning(f"Ошибка при выполнении SQL команды: {str(e)}")
                        # Продолжаем выполнение других команд
            
            db.commit()
            logger.info("Таблица modelgoods_external_images успешно создана с генератором и триггером")
            return True
        else:
            logger.debug("Таблица modelgoods_external_images уже существует")
            
            # Проверяем существование генератора и триггера
            try:
                # Проверяем существование генератора
                result = db.execute(text("""
                    SELECT 1 FROM RDB$GENERATORS 
                    WHERE RDB$GENERATOR_NAME = 'GEN_m_ex_images_ID'
                """)).fetchone()
                
                if not result:
                    logger.info("Генератор GEN_m_ex_images_ID не существует, создаем...")
                    db.execute(text('CREATE GENERATOR "GEN_m_ex_images_ID"'))
                    db.commit()
                    logger.info("Генератор GEN_m_ex_images_ID успешно создан")
                else:
                    logger.debug("Генератор GEN_m_ex_images_ID уже существует")
                
                # Проверяем существование триггера
                result = db.execute(text("""
                    SELECT 1 FROM RDB$TRIGGERS 
                    WHERE RDB$TRIGGER_NAME = 'modelgoods_external_images_BI0'
                """)).fetchone()
                
                if not result:
                    logger.info("Триггер modelgoods_external_images_BI0 не существует, создаем...")
                    # Создаем триггер
                    trigger_sql = """
                    SET TERM ^ ;
                    CREATE OR ALTER TRIGGER "modelgoods_external_images_BI0" FOR "modelgoods_external_images"
                    ACTIVE BEFORE INSERT POSITION 0
                    AS
                    BEGIN
                      -- Если id равен '0' или NULL, генерируем новый ID
                      IF (NEW."id" = '0' OR NEW."id" IS NULL) THEN BEGIN
                        -- Генерируем ID: преобразуем число в строку с ведущими нулями до 12 символов
                        NEW."id" = LPAD(GEN_ID("GEN_m_ex_images_ID", 1), 12, '0');
                      END
                      
                      -- Устанавливаем значения по умолчанию для других полей
                      IF (NEW."url" IS NULL) THEN NEW."url" = '';
                      IF (NEW."is_approved" IS NULL) THEN NEW."is_approved" = 0;
                      IF (NEW."is_loaded_to_db" IS NULL) THEN NEW."is_loaded_to_db" = 0;
                      IF (NEW."userid" IS NULL) THEN NEW."userid" = '0';
                    END
                    ^
                    SET TERM ; ^
                    """
                    
                    # Выполняем команды триггера
                    for cmd in trigger_sql.split('^'):
                        cmd = cmd.strip()
                        if cmd:
                            db.execute(text(cmd))
                    
                    db.commit()
                    logger.info("Триггер modelgoods_external_images_BI0 успешно создан")
                else:
                    logger.debug("Триггер modelgoods_external_images_BI0 уже существует")
                
            except Exception as e:
                logger.warning(f"Ошибка при проверке/создании генератора или триггера: {str(e)}")
                db.rollback()
            
            return True
            
    except Exception as e:
        logger.error(f"Ошибка при проверке/создании таблицы modelgoods_external_images: {str(e)}")
        db.rollback()
        return False


def check_table_exists(db: Session, table_name: str) -> bool:
    """
    Проверяет существование таблицы в базе данных
    """
    try:
        inspector = inspect(db.get_bind())
        return inspector.has_table(table_name)
    except Exception as e:
        logger.error(f"Ошибка при проверке существования таблицы {table_name}: {str(e)}")
        return False


def get_table_info(db: Session, table_name: str) -> dict:
    """
    Получает информацию о таблице
    """
    try:
        inspector = inspect(db.get_bind())
        
        if not inspector.has_table(table_name):
            return {"exists": False}
        
        columns = inspector.get_columns(table_name)
        indexes = inspector.get_indexes(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        return {
            "exists": True,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": col.get("default"),
                    "primary_key": col.get("primary_key", False)
                }
                for col in columns
            ],
            "indexes": [
                {
                    "name": idx["name"],
                    "columns": idx["column_names"],
                    "unique": idx.get("unique", False)
                }
                for idx in indexes
            ],
            "foreign_keys": [
                {
                    "name": fk.get("name"),
                    "constrained_columns": fk.get("constrained_columns", []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", [])
                }
                for fk in foreign_keys
            ]
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении информации о таблице {table_name}: {str(e)}")
        return {"exists": False, "error": str(e)}