# Python 3.9-slim 버전을 기반으로 이미지를 빌드합니다.
FROM python:3.9-slim

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# requirements.txt 파일을 먼저 복사하여, 종속성이 변경되지 않았을 경우 Docker 캐시를 활용합니다.
COPY requirements.txt .

# pip를 최신 버전으로 업그레이드하고, requirements.txt에 명시된 라이브러리를 설치합니다.
# --no-cache-dir 옵션은 불필요한 캐시 파일을 남기지 않아 이미지 크기를 줄여줍니다.
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 프로젝트의 나머지 파일들을 작업 디렉토리로 복사합니다.
COPY . .

# 컨테이너 외부에서 5000번 포트에 접근할 수 있도록 설정합니다.
EXPOSE 5000

# 환경 변수 설정
# PYTHONUNBUFFERED: Python의 출력 버퍼링을 비활성화하여, 로그가 즉시 출력되도록 합니다.
# FLASK_APP: 실행할 Flask 애플리케이션 파일을 지정합니다.
# FLASK_RUN_HOST: 모든 네트워크 인터페이스에서 요청을 수신하도록 설정합니다.
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 컨테이너가 시작될 때 Flask 개발 서버를 실행합니다.
# gunicorn과 같은 프로덕션용 WSGI 서버를 사용하는 것이 권장되지만, 
# 이 프로젝트의 목적에는 Flask 개발 서버로도 충분합니다.
CMD ["flask", "run"]
