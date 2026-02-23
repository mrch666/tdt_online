-- Упрощенный SQL скрипт для создания таблицы внешних изображений
-- Без триггеров и сложных конструкций

CREATE TABLE "modelgoods_external_images" (
    "id" CHAR(12) NOT NULL,
    "modelid" CHAR(12) NOT NULL,
    "url" VARCHAR(2000) NOT NULL,
    "is_approved" INTEGER DEFAULT 0,
    "is_loaded_to_db" INTEGER DEFAULT 0,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "userid" CHAR(12) DEFAULT '0'
);

ALTER TABLE "modelgoods_external_images" ADD CONSTRAINT "PK_modelgoods_external_images" PRIMARY KEY ("id");

CREATE INDEX "idx_modelgoods_external_images_modelid" ON "modelgoods_external_images" ("modelid");

ALTER TABLE "modelgoods_external_images" ADD CONSTRAINT "FK_modelgoods_external_images_modelid"
    FOREIGN KEY ("modelid") REFERENCES "modelgoods"("id");