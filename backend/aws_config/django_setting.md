- AWS RDS 시간이 좀 걸린다. (5-10분정도)

# 파일명
- gunicorn systemd 등록 파일
  - "/etc/systemd/system/mypoll_chat-wsgi.service"
- nginx systemd 설정파일
  - "/etc/nginx/sites-available/mypoll_chat"
- **socket file 디렉토리**
  - "/run/mypoll_chat"
  - 소유: ubuntu:www-data
- **static, media Root경로**
  - '/var/www/mypoll_chat/static'
  - '/var/www/mypoll_chat/media'
  - 소유: ubuntu:ubuntu

# 설치
1. 설치

uv venv .venv --python=3.12
source .venv/bin/activate
uv pip install django django-bootstrap5 pillow langchain langchain-openai python-dotenv gunicorn

- .env 파일 업로드

1. settings.py
    - ALLOWED_HOST 변경 - EC2 public ip, "localhost", "127.0.0.1" 등록
    - SECRET_KEY  - .env로 이동
    - DEBUG=False

    - STATIC_ROOT = '/var/www/mypoll_chat/static'
    - MEDIA_ROOT = '/var/www/mypoll_chat/media'
 
1. STATIC_ROOT 디렉토리 생성 및 collectstatic
     ```bash
      mkdir -p /var/www/mypoll_chat/static
      chown $USER:$USER /var/www/mypoll_chat/static/
     ```
    - `python manage.py collectstatic`
    - makemigration, migrate, createsuperuser 까지 실행
    - **개발서버 실행**
        - python manage.py runserver 0.0.0.0:8000
  
2. MEDIA_ROOT 디렉토리 생성 및 설정
   ```bash
    mkdir -p /var/www/mypoll_chat/
    chown $USER:$USER /var/www/mypoll_chat/media/
    ```
3. gunicorn 설정
- sudo nano /etc/systemd/system/mypoll_chat-wsgi.service
    - aws_config/wsgi_config.txt 내용을 복붙 (**주석이 있으면 안된다.**)
- - socket 파일을 저장 디렉토리 생성 및 설정 (/run/mypoll_chat)
    ```bash
     sudo mkdir -p /run/mypoll_chat
     sudo chown $USER:www-data /run/mypoll_chat
     sudo chmod 775 /run/mypoll_chat
    ```

- 서비스 시작 (mypoll_chat-wsgi.service 를 서비스로 시작 및 등록)
    ```bash
    sudo systemctl start mypoll_chat-wsgi      # 서비스로 시작
    sudo systemctl enable mypoll_chat-wsgi     # 자동등록
    sudo systemctl status mypoll_chat-wsgi     # 상태확인
    ```
- 문제가 있어서 수정하게 되면
    ```bash
    sudo systemctl daemon-reload      # 서비스로 시작
    sudo systemctl restart mypoll_chat-wsgi     # 자동등록
    sudo systemctl status mypoll_chat-wsgi     # 상태확인
    ```
> socket으로 접속했기 때문에 직접 로컬에서는 지금 요청이 안된다. (nginx 연동 후 가능)


4. nginx 설정
- ngix 설치
    ```bash
    sudo apt update
    sudo apt upgrade
    sudo apt install nginx
    ```
http://ip 로 확인

- django-ngix 연동 설정
    - AWS_config/ngix.txt 확인