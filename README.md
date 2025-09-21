# 정부 공문서 AI 검색 서비스

## 📋 프로젝트 개요

**일반시민을 위한 정부 공문서 AI 검색 서비스**는 복잡한 정부 정책과 공문서를 시민이 쉽게 이해할 수 있도록 돕는 Multi-Agent AI 시스템입니다.

## 🏛️ 주요 기능

- **자연어 검색**: 일상 언어로 정부 정책 검색
- **시민 친화적 설명**: 복잡한 공문서를 쉬운 언어로 변환
- **대화형 상담**: AI와의 실시간 정책 상담
- **카테고리별 브라우징**: 주제별 정책 탐색
- **관련 정보 추천**: 연관된 정책 및 서비스 제안

## 🔧 기술 스택

### Frontend (Streamlit)
- **Streamlit**: 웹 인터페이스
- **httpx**: HTTP 클라이언트
- **Python 3.9+**

### Backend (FastAPI)
- **FastAPI**: REST API 서버
- **LangChain**: AI 프레임워크
- **LangGraph**: Multi-Agent 워크플로우
- **Azure OpenAI**: GPT-4o, text-embedding-3-large
- **FAISS**: 벡터 데이터베이스
- **SQLite**: 세션 관리

### Infrastructure
- **Docker**: 컨테이너화
- **pytest**: 테스트 프레임워크
- **Uvicorn**: ASGI 서버

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/gov-info-assistant.git
cd gov-info-assistant

# 환경변수 설정
cp .env.example .env
# .env 파일에서 Azure OpenAI 설정 입력
```

### 2. Docker로 실행

```bash
# Docker Compose로 전체 시스템 실행
docker-compose up --build

# 브라우저에서 접속
# - Streamlit 클라이언트: http://localhost:8501
# - FastAPI 문서: http://localhost:8000/docs
```

### 3. 로컬 개발 환경

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-client.txt

# 서버 실행
cd fastapi_server
python main.py

# 클라이언트 실행 (별도 터미널)
cd streamlit_app
streamlit run main.py
```

## 📁 프로젝트 구조

```
gov-info-assistant/
├── streamlit_app/           # Streamlit 클라이언트
│   ├── main.py             # 메인 앱
│   ├── pages/              # 페이지 컴포넌트
│   ├── components/         # UI 컴포넌트
│   ├── services/           # API 클라이언트
│   └── utils/              # 유틸리티
├── fastapi_server/         # FastAPI 서버
│   ├── main.py             # 서버 진입점
│   ├── api/                # API 라우터
│   ├── core/               # 핵심 비즈니스 로직
│   │   ├── agents/         # Multi-Agent 시스템
│   │   ├── services/       # 비즈니스 서비스
│   │   └── workflow/       # LangGraph 워크플로우
│   ├── models/             # 데이터 모델
│   └── utils/              # 서버 유틸리티
├── data/                   # 데이터 파일
│   ├── documents/          # 원본 문서
│   ├── vector_db/          # 벡터 DB
│   └── sessions.db         # 세션 DB
├── tests/                  # 테스트 코드
├── docs/                   # 문서
└── docker-compose.yml      # Docker 설정
```

## 🤖 Multi-Agent 시스템

### Agent 구성
1. **CitizenQueryAnalyzer**: 시민 질의 분석
2. **PolicyDocumentRetriever**: 정책 문서 검색
3. **CitizenFriendlyProcessor**: 시민 친화적 변환
4. **InteractiveResponseGenerator**: 대화형 응답 생성

### 워크플로우
```
사용자 질의 → 질의 분석 → 문서 검색 → 내용 처리 → 응답 생성
```

## 📊 성능 지표

- **검색 응답 시간**: < 3초
- **정확도**: 80% 이상
- **동시 사용자**: 20명 이상
- **가용성**: 99% 이상

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=fastapi_server --cov=streamlit_app

# 특정 테스트 실행
pytest tests/unit/
pytest tests/integration/
```

## 📚 API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 주요 API 엔드포인트

### 검색 API
- `POST /api/v1/search/query` - 문서 검색
- `GET /api/v1/search/categories` - 카테고리 목록
- `GET /api/v1/search/popular` - 인기 검색어

### 채팅 API
- `POST /api/v1/chat/message` - 메시지 전송
- `POST /api/v1/chat/session` - 세션 생성
- `GET /api/v1/chat/history/{session_id}` - 대화 기록

### 헬스체크
- `GET /api/v1/health` - 서비스 상태 확인

## 🌍 환경 변수

### 필수 환경 변수
```bash
# Azure OpenAI
AOAI_ENDPOINT=https://your-instance.openai.azure.com/
AOAI_API_KEY=your-api-key
AOAI_DEPLOY_GPT4O_MINI=gpt-4o-mini
AOAI_DEPLOY_GPT4O=gpt-4o
AOAI_DEPLOY_EMBED_3_LARGE=text-embedding-3-large

# 애플리케이션
CLIENT_URL=http://localhost:8501
SERVER_URL=http://localhost:8000
VECTOR_DB_PATH=./data/vector_db
SESSION_DB_PATH=./data/sessions.db
LOG_LEVEL=INFO
```

## 🐳 Docker 배포

### 개발 환경
```bash
docker-compose up --build
```

### 프로덕션 환경
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 모니터링

### 헬스체크
```bash
curl http://localhost:8000/api/v1/health
```

### 메트릭 확인
```bash
curl http://localhost:8000/api/v1/metrics
```

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/gov-info-assistant/issues)
- **문서**: [프로젝트 위키](https://github.com/your-username/gov-info-assistant/wiki)
- **이메일**: support@gov-info-assistant.com

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- 행정안전부의 정부 공문서 AI 학습데이터 제공
- OpenAI의 Azure OpenAI 서비스
- LangChain 및 LangGraph 커뮤니티
- Streamlit 팀의 훌륭한 프레임워크

---

**정부 공문서 AI 검색 서비스**로 더 나은 디지털 정부 서비스를 경험하세요! 🏛️✨
