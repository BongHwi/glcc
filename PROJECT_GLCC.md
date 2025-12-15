# Project GLCC: Global Logistics Command Center (Master Plan)

## 1. 프로젝트 개요 (Overview)
* **목적:** 기존에 보유한 `delivery-tracker` 리포지토리(KR)와 새로 구축할 해외 배송 크롤러(Global)를 통합하여, 전 세계 택배 배송 상태를 관리하는 **Self-Hosted 플랫폼** 구축.
* **핵심 전략:**
    1.  **Submodule Integration:** 기존 `delivery-tracker`를 Git Submodule로 포함하여 관리 효율성 증대.
    2.  **Hybrid Engine:** Python 라이브러리(KR) + Playwright 크롤링(Global) + 통합 API.
    3.  **Microservices:** Docker Compose를 이용한 API(FastAPI), Dashboard(Streamlit), Scheduler 통합 운영.

## 2. 기술 스택 (Tech Stack)

### Backend
* **Language:** Python 3.11
* **Framework:** FastAPI
* **Database:** SQLite + SQLAlchemy (ORM)
* **Core Logic:**
    * **KR:** `delivery-tracker` (Submodule)
    * **Global:** `playwright` (Headless Browser)
* **Scheduling:** `APScheduler`

### Frontend
* **UI:** Streamlit (API Client 역할)

### Infrastructure
* **Container:** Docker (Multi-stage build), Docker Compose
* **VCS:** Git (with Submodules)

---

## 3. 디렉토리 구조 (Directory Structure)

```text
glcc/
├── .gitignore
├── .env                    # 환경변수 (API Key, DB Path)
├── docker-compose.yml      # 통합 실행 설정
├── PROJECT_GLCC.md         # 본 계획서
├── backend/
│   ├── Dockerfile          # Playwright 포함된 이미지 빌드
│   ├── requirements.txt
│   ├── main.py             # FastAPI Entrypoint
│   ├── database.py         # DB Session
│   ├── models.py           # DB Schema
│   ├── crud.py             # DB Queries
│   ├── schemas.py          # Pydantic Models
│   ├── libs/               # [Submodule Location]
│   │   └── delivery-tracker/  <-- Git Submodule (Existing Repo)
│   ├── trackers/           # Business Logic
│   │   ├── __init__.py
│   │   ├── kr_adapter.py   # Submodule Wrapper
│   │   └── global_scraper.py # Playwright Logic
│   └── routers/            # API Endpoints
└── frontend/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py              # Streamlit Dashboard

## 4. 단계별 구현 계획 (Phased Implementation Roadmap)

### Phase 1: 프로젝트 초기화 및 서브모듈 설정 (Init & Submodule)
* **목표:** Git 저장소 초기화, `delivery-tracker` 서브모듈 연결, 기본 FastAPI 골격 생성.
* **Action Items:**
    1.  프로젝트 루트 생성 및 `git init`.
    2.  `backend/libs/delivery-tracker` 경로에 기존 리포지토리 서브모듈 추가.
        * `git submodule add https://github.com/BongHwi/delivery-tracker backend/libs/delivery-tracker`
    3.  `backend/main.py` 생성 (Hello World 레벨).
    4.  `backend/requirements.txt` 작성 (FastAPI, SQLAlchemy, uvicorn 등).
* **[Test]:**
    * `python backend/main.py` 실행 시 서브모듈 폴더(`libs/delivery-tracker`)가 존재하는지 확인.

### Phase 2: DB 모델링 및 추적 엔진 통합 (Core Logic)
* **목표:** DB 스키마 정의 및 서브모듈을 import하여 실제 조회 로직 연결.
* **Action Items:**
    1.  **DB Modeling:** `models.py`에 `Package` 테이블 정의.
        * (id, tracking_number, carrier, alias, status, last_updated, is_active, notify_enabled)
    2.  **KR Adapter (`kr_adapter.py`):**
        * `sys.path.append` 등을 사용하여 `libs/delivery-tracker`를 import 경로에 추가.
        * 서브모듈의 기능을 호출하는 래퍼 함수 `track_kr(carrier, number)` 구현.
    3.  **Global Scraper (`global_scraper.py`):**
        * Playwright 설치 및 기본 스크래핑 함수 `track_global(carrier, number)` 스켈레톤 작성.
* **[Test]:**
    * 로컬 파이썬 환경에서 `kr_adapter.py`를 실행했을 때 기존 라이브러리가 정상 동작하여 배송 정보를 가져오는가?

### Phase 3: API 엔드포인트 구현 (API Development)
* **목표:** 프론트엔드와 통신할 REST API 완성.
* **Action Items:**
    1.  `routers/packages.py` 구현.
    2.  `POST /packages`: 택배 등록 (등록 시 즉시 1회 조회 실행).
    3.  `GET /packages`: 전체 목록 조회.
    4.  `POST /packages/refresh`: 전체 현황 업데이트 (가장 중요한 기능).
* **[Test]:**
    * Swagger UI (`/docs`)에서 데이터 입력 및 조회 성공 확인.

### Phase 4: 스케줄러 및 알림 (Automation)
* **목표:** 자동화된 추적 및 푸시 알림.
* **Action Items:**
    1.  `APScheduler` 설정 (1시간 간격).
    2.  `refresh_all_packages` 로직 구현:
        * DB 조회 -> 상태 변경 감지 -> `notify_user` 호출.
    3.  **Notification:** 텔레그램 봇 API 연동.
* **[Test]:**
    * DB 데이터를 임의로 수정한 뒤, Refresh API를 호출했을 때 알림이 오는가?

### Phase 5: Docker Integration (Deployment Setup)
* **목표:** 서브모듈을 포함한 Docker 이미지 빌드 및 실행.
* **Critical Configuration (`backend/Dockerfile`):**
    * Base Image: `mcr.microsoft.com/playwright/python:v1.40.0-jammy` (필수).
    * **Submodule Handling:**
        ```dockerfile
        COPY . .
        # 서브모듈 경로를 PYTHONPATH에 추가하거나, setup.py가 있다면 설치
        ENV PYTHONPATH="${PYTHONPATH}:/app/libs/delivery-tracker"
        RUN pip install -r requirements.txt
        ```
* **[Test]:**
    * `docker-compose up --build` 실행 시 에러 없이 서버가 뜨는가?

### Phase 6: Frontend Dashboard (UI)
* **목표:** Streamlit 기반 관리 화면.
* **Action Items:**
    1.  `frontend/app.py` 작성.
    2.  API 서버와 통신 (`requests.get/post`).
    3.  기능: 리스트 보기, 추가하기, 새로고침 버튼.

---

## 5. 실행 가이드 (For AI Agent)

**Step 1: 초기화**
터미널에서 아래 명령어를 실행하여 템플릿을 잡고 시작하세요.
> "이 프로젝트 명세서(Phase 1)를 기반으로 폴더 구조를 생성하고, git 초기화 및 서브모듈 추가 명령어를 알려줘. (서브모듈 URL은 사용자에게 물어볼 것)"

**Step 2: 구현**
> "Phase 2를 진행하자. `models.py`를 작성하고, `backend/libs`에 있는 서브모듈을 import 할 수 있도록 `kr_adapter.py`를 작성해줘."

**Step 3: 도커**
> "Phase 5를 진행하자. 서브모듈이 포함된 소스코드를 컨테이너에 복사하고, Playwright 환경까지 포함하는 `backend/Dockerfile`을 작성해줘."