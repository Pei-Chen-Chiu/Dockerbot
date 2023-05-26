# 建立資料庫
CREATE SCHEMA  if not exists `linebot`;

# 建立儲存圖片的資料表
CREATE TABLE if not exists `linebot`.`upload_fig` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `time` DATETIME NULL,
  `file_path` TEXT NULL COMMENT '圖片存放路徑',
  PRIMARY KEY (`id`))
COMMENT = '上傳圖片資料表';

# 建立儲存訊息的資料表
CREATE TABLE if not exists `linebot`.`msg` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `time` DATETIME NULL,
  `msg` TEXT NULL COMMENT '使用者輸入訊息',
  PRIMARY KEY (`id`))
COMMENT = '使用者輸入訊息資料表';