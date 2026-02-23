/******************************************************************************/
/***               Complete script for modelgoods_external_images          ***/
/******************************************************************************/

SET SQL DIALECT 3;

-- Проверка существования таблицы
SET TERM ^ ;

EXECUTE BLOCK
AS
BEGIN
  -- Проверяем существование таблицы
  IF (NOT EXISTS(
    SELECT 1 FROM RDB$RELATIONS 
    WHERE RDB$RELATION_NAME = 'modelgoods_external_images'
  )) THEN
  BEGIN
    -- Создаем таблицу
    EXECUTE STATEMENT '
      CREATE TABLE "modelgoods_external_images" (
          "id"          CHAR(12) DEFAULT ''0'' NOT NULL,
          "modelid"     CHAR(12) DEFAULT ''0'' NOT NULL,
          "url"         VARCHAR(2000) COLLATE PXW_CYRL,
          "is_approved" INTEGER DEFAULT 0 NOT NULL,
          "is_loaded_to_db" INTEGER DEFAULT 0 NOT NULL,
          "created_at"  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          "updated_at"  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          "userid"      CHAR(12) DEFAULT ''0'' NOT NULL
      )
    ';
    
    -- Добавляем первичный ключ
    EXECUTE STATEMENT '
      ALTER TABLE "modelgoods_external_images" 
      ADD CONSTRAINT "PK_modelgoods_external_images" PRIMARY KEY ("id")
    ';
    
    -- Создаем индекс
    EXECUTE STATEMENT '
      CREATE INDEX "idx_modelgoods_external_images_modelid" 
      ON "modelgoods_external_images" ("modelid")
    ';
    
    -- Добавляем внешний ключ
    EXECUTE STATEMENT '
      ALTER TABLE "modelgoods_external_images" 
      ADD CONSTRAINT "FK_modelgoods_external_images_modelid" 
      FOREIGN KEY ("modelid") REFERENCES "modelgoods"("id")
    ';
  END
END
^

-- Проверка существования генератора
EXECUTE BLOCK
AS
BEGIN
  -- Проверяем существование генератора
  IF (NOT EXISTS(
    SELECT 1 FROM RDB$GENERATORS 
    WHERE RDB$GENERATOR_NAME = ''GEN_m_ex_images_ID''
  )) THEN
  BEGIN
    -- Создаем генератор
    EXECUTE STATEMENT ''CREATE GENERATOR "GEN_m_ex_images_ID"'';
  END
END
^

-- Создаем или изменяем триггер для автоматической генерации ID
CREATE OR ALTER TRIGGER "modelgoods_external_images_BI0" FOR "modelgoods_external_images"
ACTIVE BEFORE INSERT POSITION 0
AS
BEGIN
  -- Если id равен ''0'' или NULL, генерируем новый ID
  IF (NEW."id" = ''0'' OR NEW."id" IS NULL) THEN BEGIN
    -- Генерируем ID: преобразуем число в строку с ведущими нулями до 12 символов
    NEW."id" = LPAD(GEN_ID("GEN_m_ex_images_ID", 1), 12, ''0'');
  END
  
  -- Устанавливаем значения по умолчанию для других полей
  IF (NEW."url" IS NULL) THEN NEW."url" = '''';
  IF (NEW."is_approved" IS NULL) THEN NEW."is_approved" = 0;
  IF (NEW."is_loaded_to_db" IS NULL) THEN NEW."is_loaded_to_db" = 0;
  IF (NEW."userid" IS NULL) THEN NEW."userid" = ''0'';
END
^

-- Создаем или изменяем триггер для обновления
CREATE OR ALTER TRIGGER "modelgoods_external_images_BU0" FOR "modelgoods_external_images"
ACTIVE BEFORE UPDATE POSITION 0
AS
BEGIN
  -- Устанавливаем значения по умолчанию для других полей
  IF (NEW."url" IS NULL) THEN NEW."url" = '''';
  IF (NEW."is_approved" IS NULL) THEN NEW."is_approved" = 0;
  IF (NEW."is_loaded_to_db" IS NULL) THEN NEW."is_loaded_to_db" = 0;
  IF (NEW."userid" IS NULL) THEN NEW."userid" = ''0'';
  
  -- Обновляем время изменения
  NEW."updated_at" = CURRENT_TIMESTAMP;
END
^

SET TERM ; ^

-- Проверка создания
SELECT 
  'Table created: modelgoods_external_images' as result
FROM RDB$DATABASE
WHERE EXISTS(
  SELECT 1 FROM RDB$RELATIONS 
  WHERE RDB$RELATION_NAME = 'modelgoods_external_images'
)
UNION ALL
SELECT 
  'Generator created: GEN_m_ex_images_ID' as result
FROM RDB$DATABASE
WHERE EXISTS(
  SELECT 1 FROM RDB$GENERATORS 
  WHERE RDB$GENERATOR_NAME = 'GEN_m_ex_images_ID'
)
UNION ALL
SELECT 
  'Trigger created: modelgoods_external_images_BI0' as result
FROM RDB$DATABASE
WHERE EXISTS(
  SELECT 1 FROM RDB$TRIGGERS 
  WHERE RDB$TRIGGER_NAME = 'modelgoods_external_images_BI0'
);