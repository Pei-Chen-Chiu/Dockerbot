# Docker --linebot deploy on ngrok(本地端執行)
> 使用者輸入文字、圖片，linebot 會幫你把文字、圖片存入 SQL

```
├──image # 資料夾 存入圖片用
├── app.py # 主程式
├── docker-compose.yml # Docker部署
├── dockerfile-flask # 部署Python容器(docker-compose.yml)
├── get_ngrok_url.sh # bash檔，取得Ngrok容器內的公開網址
├── mysql-init.sql # 部署MySQL容器初始化資料庫，儲存訊息和照片
├── requirements.txt # 部署套件(dockerfile-flask)
└── secretFile.txt # token
```
## 一、docker-compose.yml
> Docker 部署的 yaml 檔

* MySQL
* Flask
* Ngrok

### 1. MySQL
* `docker-compose.yml`:
```yaml!
version: "3.1"
services:

  db:
    image: mysql
    container_name: chatbot_db
    restart: always
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=123456 # MySQL password
    volumes:
      - ./mysql-init.sql:/docker-entrypoint-initdb.d/mysql-init.sql
      - ./mysql_data:/var/lib/mysql
```
* `mysql-init.sql`:
```sql!
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
```
### 2. Flask
* `docker-compose.yml`:
```yaml!
version: "3.1"
services:

  web:
    build:
      context: .
      dockerfile: dockerfile-flask
    container_name: chatbot_web
    restart: always
    ports:
      - "5000:5000"
    depends_on:
      - db
    volumes:
      - .:/code
    environment:
      FLASK_ENV: development
```
* `dockerfile-flask`:
```dockerfile!
# 使用的 Docker image
FROM python:3.7-alpine

# 容器內執行 Python 的路徑
WORKDIR /code

# 執行 flask 檔名為 app.py 
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 將requirement.txt檔案放到容器內
COPY requirements.txt requirements.txt

# 安裝 requirement.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
```
### 3. Ngrok
* `docker-compose.yml`:
```yaml!
version: "3.1"
services:

  ngrok:
    image: wernight/ngrok
    container_name: chatbot_ngrok
    tty: true
    stdin_open: true
    restart: always
    ports:
      - "4040:4040"
    depends_on:
      - web
    command: ngrok http chatbot_web:5000 -region ap
```
* `get_ngrok_url.sh`:
```bash!
#!bin/bash
# 讀取ngrok的資訊(JSON檔案格式)
curl $(docker port chatbot_ngrok 4040)/api/tunnels > tunnels.json

# 利用jq(處理Json檔案格式工具)找出ngrok產生的public_url
docker run -v $(pwd)/tunnels.json:/tmp/tunnels.json --rm  realguess/jq jq .tunnels[1].public_url /tmp/tunnels.json 

# 刪除檔案
rm tunnels.json
```
## 二、app.py
利用`json.load`函數將`secretFile.txt`讀進`app.py`
```python!
# 讀取linebot和mysql連線資訊
secretFile = json.load(open('secretFile.txt', 'r'))
```
* `secretFile.txt`:
```json!
{
  "channelAccessToken":"[您的channelAccessToken]",
  "channelSecret":"[您的channelSecret]",
  "host":"chatbot_db",
  "port":3306, 
  "user":"root",
  "passwd":"123456"
}
```
line token
```python!
# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])
```
## 三、部署
在當前資料夾
*確認有安裝 `docker-compose`
1. 開始部署
    ```powershell
    docker-compose up -d
    ```
2. 檢查容器運作狀態
    ```powershell
    docker-compose ps -a
    ```
3. 取得 Ngrok 公開網址，貼入 LINE Webhook URL(不用加 callback)
    ```powershell
    bash get_ngrok_url.sh
    ```
4. 查看本地端圖片
    ```powershell
    ls image
    ```
5. 查詢資料庫內容
    1. 查詢容器
        ```powershell
        docker ps
        ```
    2. 進入 MySQL 容器
        ```powershell!
        docker exec -it <CONTAINER ID> bash
        ```
    3. 登入 MySQL
        ```powershell!
        mysql -u root -p 
        show databases;
        use linebot;
        show tables;
        select * from msg;
        ```
