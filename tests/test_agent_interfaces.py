"""
Agent 인터페이스 Mock 테스트
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from typing import List, Dict, Any

from fastapi_server.core.agents.interfaces import (
    BaseAgent, AgentResult, AgentError,
    ICitizenQueryAnalyzer, IPolicyDocumentRetriever,
    ICitizenFriendlyProcessor, IInteractiveResponseGenerator,
    QueryAnalysisInput, QueryAnalysisOutput,
    DocumentRetrievalInput, DocumentRetrievalOutput,
    ContentProcessingInput, ContentProcessingOutput,
    ResponseGenerationInput, ResponseGenerationOutput
)
from fastapi_server.models.schemas import (
    DocumentResult, ChatMessage, DifficultyLevel, MessageRole
)


# === Mock Agent 구현체들 ===

class MockCitizenQueryAnalyzer(ICitizenQueryAnalyzer):
    """MockCitizenQueryAnalyzer 구현체"""
    
    def __init__(self):
        super().__init__("MockCitizenQueryAnalyzer")
        self.initialized = True
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        return True
    
    async def analyze_query(self, query: str, context: Dict[str, Any] = None) -> QueryAnalysisOutput:
        """Mock 질의 분석"""
        if "주민등록" in query:
            return QueryAnalysisOutput(
                processed_query=query.strip(),
                intent="정보조회",
                category="행정서비스",
                keywords=["주민등록", "발급"],
                entities={"서류": ["주민등록등본"]},
                confidence=0.9,
                suggestions=["주민등록초본 발급", "가족관계증명서"],
                difficulty_hint=DifficultyLevel.BEGINNER
            )
        return QueryAnalysisOutput(
            processed_query=query.strip(),
            intent="일반문의",
            confidence=0.5
        )
    
    async def extract_keywords(self, query: str) -> List[str]:
        # 간단한 키워드 추출 로직
        return query.split()[:3]
    
    async def classify_category(self, query: str) -> str:
        if "주민등록" in query or "발급" in query:
            return "행정서비스"
        elif "세금" in query:
            return "세무"
        return "일반"
    
    async def detect_intent(self, query: str) -> str:
        if "어떻게" in query or "방법" in query:
            return "정보조회"
        elif "문의" in query:
            return "상담요청"
        return "일반문의"
    
    async def extract_entities(self, query: str) -> Dict[str, List[str]]:
        entities = {}
        if "주민등록" in query:
            entities["서류"] = ["주민등록등본"]
        if "발급" in query:
            entities["행위"] = ["발급"]
        return entities


class MockPolicyDocumentRetriever(IPolicyDocumentRetriever):
    """MockPolicyDocumentRetriever 구현체"""
    
    def __init__(self):
        super().__init__("MockPolicyDocumentRetriever")
        self.initialized = True
        self.mock_documents = [
            DocumentResult(
                id="doc_001",
                title="주민등록등본 발급 안내",
                content="주민등록등본은 온라인 또는 주민센터에서 발급받을 수 있습니다.",
                category="행정서비스",
                published_date="2024-01-15",
                difficulty=DifficultyLevel.BEGINNER,
                score=0.95,
                highlights=["주민등록등본", "발급"],
                metadata={"author": "행정안전부"}
            ),
            DocumentResult(
                id="doc_002",
                title="세금 신고 방법",
                content="개인소득세 신고는 국세청 홈택스에서 가능합니다.",
                category="세무",
                published_date="2024-01-20",
                difficulty=DifficultyLevel.INTERMEDIATE,
                score=0.85,
                highlights=["세금", "신고"],
                metadata={"author": "국세청"}
            )
        ]
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        return True
    
    async def search_documents(self, query: str, keywords: List[str] = None, max_results: int = 5) -> DocumentRetrievalOutput:
        """Mock 문서 검색"""
        filtered_docs = []
        for doc in self.mock_documents:
            if any(keyword in doc.content for keyword in query.split()):
                filtered_docs.append(doc)
        
        return DocumentRetrievalOutput(
            documents=filtered_docs[:max_results],
            total_count=len(filtered_docs),
            search_strategy="semantic_search",
            retrieval_metadata={"query_terms": query.split()}
        )
    
    async def hybrid_search(self, query: str, keywords: List[str], category: str = None) -> DocumentRetrievalOutput:
        """Mock 하이브리드 검색"""
        filtered_docs = []
        for doc in self.mock_documents:
            if category and doc.category != category:
                continue
            if any(keyword.lower() in doc.content.lower() for keyword in keywords):
                filtered_docs.append(doc)
        
        return DocumentRetrievalOutput(
            documents=filtered_docs,
            total_count=len(filtered_docs),
            search_strategy="hybrid_search"
        )
    
    async def filter_by_category(self, documents: List[DocumentResult], category: str) -> List[DocumentResult]:
        return [doc for doc in documents if doc.category == category]
    
    async def rank_documents(self, documents: List[DocumentResult], query: str) -> List[DocumentResult]:
        return sorted(documents, key=lambda x: x.score, reverse=True)
    
    async def get_similar_documents(self, document_id: str, limit: int = 3) -> List[DocumentResult]:
        return self.mock_documents[:limit]


class MockCitizenFriendlyProcessor(ICitizenFriendlyProcessor):
    """MockCitizenFriendlyProcessor 구현체"""
    
    def __init__(self):
        super().__init__("MockCitizenFriendlyProcessor")
        self.initialized = True
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        return True
    
    async def simplify_language(self, content: str, target_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER) -> str:
        """Mock 언어 단순화"""
        # 간단한 치환 로직
        simplified = content.replace("발급받을 수 있습니다", "받을 수 있어요")
        simplified = simplified.replace("신고는", "신고를 하려면")
        return simplified
    
    async def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """Mock 핵심 포인트 추출"""
        sentences = content.split('.')
        return [s.strip() for s in sentences if s.strip()][:max_points]
    
    async def create_step_guide(self, content: str) -> List[str]:
        """Mock 단계별 가이드 생성"""
        if "주민등록" in content:
            return [
                "1단계: 준비물 확인 (신분증)",
                "2단계: 온라인 사이트 접속 또는 주민센터 방문",
                "3단계: 신청서 작성",
                "4단계: 수수료 결제",
                "5단계: 발급 완료"
            ]
        return ["1단계: 해당 기관 웹사이트 방문", "2단계: 필요 서류 준비", "3단계: 신청 진행"]
    
    async def explain_terminology(self, content: str) -> Dict[str, str]:
        """Mock 용어 설명"""
        terms = {}
        if "주민등록등본" in content:
            terms["주민등록등본"] = "주민의 신상정보가 기록된 공식 문서"
        if "홈택스" in content:
            terms["홈택스"] = "국세청에서 운영하는 인터넷 세무서비스"
        return terms
    
    async def adjust_difficulty(self, content: str, current_difficulty: DifficultyLevel, target_difficulty: DifficultyLevel) -> str:
        """Mock 난이도 조정"""
        if target_difficulty == DifficultyLevel.BEGINNER:
            return content.replace("신고", "세금 신고").replace("발급", "문서 발급")
        return content
    
    async def calculate_readability(self, content: str) -> float:
        """Mock 가독성 계산"""
        # 단순한 가독성 점수 (문장 길이 기반)
        sentences = content.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        return max(0, min(1, (20 - avg_length) / 20))  # 0-1 사이 점수


class MockInteractiveResponseGenerator(IInteractiveResponseGenerator):
    """MockInteractiveResponseGenerator 구현체"""
    
    def __init__(self):
        super().__init__("MockInteractiveResponseGenerator")
        self.initialized = True
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        self.config = config
        return True
    
    async def generate_response(self, query: str, content: str, chat_history: List[ChatMessage] = None) -> str:
        """Mock 응답 생성"""
        if "주민등록" in query:
            return f"안녕하세요! 주민등록등본 발급에 대해 문의하셨네요. {content} 추가로 궁금한 점이 있으시면 언제든 말씀해 주세요."
        return f"질문해 주신 내용에 대한 답변입니다: {content}"
    
    async def suggest_follow_ups(self, query: str, response: str) -> List[str]:
        """Mock 후속 질문 제안"""
        if "주민등록" in query:
            return [
                "온라인 발급 시 필요한 준비물은 무엇인가요?",
                "발급 수수료는 얼마인가요?",
                "주민등록초본과의 차이점은 무엇인가요?"
            ]
        return ["더 자세한 정보가 필요하신가요?", "다른 궁금한 점이 있으신가요?"]
    
    async def find_related_info(self, query: str, current_content: str) -> List[Dict[str, str]]:
        """Mock 관련 정보 링크"""
        if "주민등록" in query:
            return [
                {"title": "주민등록초본 발급", "url": "/info/resident-abstract"},
                {"title": "가족관계증명서", "url": "/info/family-certificate"},
                {"title": "온라인 민원 서비스", "url": "/info/online-service"}
            ]
        return [{"title": "관련 정보", "url": "/info/general"}]
    
    async def calculate_confidence(self, query: str, response: str, source_documents: List[DocumentResult]) -> float:
        """Mock 신뢰도 계산"""
        base_confidence = 0.7
        if source_documents:
            avg_score = sum(doc.score for doc in source_documents) / len(source_documents)
            return min(1.0, base_confidence + avg_score * 0.3)
        return base_confidence
    
    async def personalize_response(self, response: str, user_profile: Dict[str, Any]) -> str:
        """Mock 개인화 응답"""
        if user_profile.get("preferred_style") == "formal":
            return response.replace("해주세요", "해주시기 바랍니다")
        return response
    
    async def format_response(self, content: str, style: str = "conversational") -> str:
        """Mock 응답 포맷팅"""
        if style == "formal":
            return content.replace("해요", "합니다")
        return content


# === 테스트 클래스들 ===

@pytest.mark.unit
class TestAgentResult:
    """AgentResult 테스트"""
    
    def test_agent_result_success(self):
        """성공 결과 테스트"""
        result = AgentResult(True, data="test_data", processing_time=1.5)
        
        assert result.is_success()
        assert result.get_data() == "test_data"
        assert result.processing_time == 1.5
        assert result.error is None
    
    def test_agent_result_failure(self):
        """실패 결과 테스트"""
        result = AgentResult(False, error="Test error")
        
        assert not result.is_success()
        assert result.get_error() == "Test error"
        
        with pytest.raises(AgentError):
            result.get_data()
    
    def test_agent_result_metadata(self):
        """메타데이터 테스트"""
        metadata = {"key": "value", "count": 5}
        result = AgentResult(True, data="test", metadata=metadata)
        
        assert result.metadata == metadata
        assert result.metadata["key"] == "value"


@pytest.mark.unit
class TestCitizenQueryAnalyzer:
    """CitizenQueryAnalyzer 인터페이스 테스트"""
    
    @pytest.fixture
    def analyzer(self):
        return MockCitizenQueryAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_query_resident_registration(self, analyzer):
        """주민등록 질의 분석 테스트"""
        result = await analyzer.analyze_query("주민등록등본 발급 방법")
        
        assert result.intent == "정보조회"
        assert result.category == "행정서비스"
        assert "주민등록" in result.keywords
        assert result.confidence == 0.9
        assert result.difficulty_hint == DifficultyLevel.BEGINNER
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, analyzer):
        """키워드 추출 테스트"""
        keywords = await analyzer.extract_keywords("주민등록등본 발급 방법 문의")
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 3
        assert "주민등록등본" in keywords
    
    @pytest.mark.asyncio
    async def test_classify_category(self, analyzer):
        """카테고리 분류 테스트"""
        category1 = await analyzer.classify_category("주민등록등본 발급")
        category2 = await analyzer.classify_category("세금 신고 방법")
        category3 = await analyzer.classify_category("일반 문의사항")
        
        assert category1 == "행정서비스"
        assert category2 == "세무"
        assert category3 == "일반"
    
    @pytest.mark.asyncio
    async def test_process_integration(self, analyzer):
        """통합 처리 테스트"""
        input_data = QueryAnalysisInput(
            query="주민등록등본 발급 방법을 알고 싶습니다",
            session_id="test-session"
        )
        
        result = await analyzer.process(input_data)
        
        assert result.is_success()
        assert isinstance(result.get_data(), QueryAnalysisOutput)
        assert result.processing_time > 0
        assert "query_length" in result.metadata
    
    @pytest.mark.asyncio
    async def test_validation_failure(self, analyzer):
        """입력 검증 실패 테스트"""
        invalid_input = QueryAnalysisInput(query="")
        
        result = await analyzer.process(invalid_input)
        
        assert not result.is_success()
        assert "Invalid input data" in result.error


@pytest.mark.unit
class TestPolicyDocumentRetriever:
    """PolicyDocumentRetriever 인터페이스 테스트"""
    
    @pytest.fixture
    def retriever(self):
        return MockPolicyDocumentRetriever()
    
    @pytest.mark.asyncio
    async def test_search_documents(self, retriever):
        """문서 검색 테스트"""
        result = await retriever.search_documents("주민등록", max_results=3)
        
        assert isinstance(result, DocumentRetrievalOutput)
        assert len(result.documents) <= 3
        assert result.total_count >= 0
        assert result.search_strategy == "semantic_search"
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, retriever):
        """하이브리드 검색 테스트"""
        result = await retriever.hybrid_search(
            "주민등록 발급", 
            ["주민등록", "발급"], 
            category="행정서비스"
        )
        
        assert result.search_strategy == "hybrid_search"
        assert all(doc.category == "행정서비스" for doc in result.documents)
    
    @pytest.mark.asyncio
    async def test_filter_by_category(self, retriever):
        """카테고리 필터링 테스트"""
        all_docs = retriever.mock_documents
        admin_docs = await retriever.filter_by_category(all_docs, "행정서비스")
        
        assert all(doc.category == "행정서비스" for doc in admin_docs)
        assert len(admin_docs) <= len(all_docs)
    
    @pytest.mark.asyncio
    async def test_rank_documents(self, retriever):
        """문서 순위화 테스트"""
        docs = retriever.mock_documents.copy()
        ranked_docs = await retriever.rank_documents(docs, "테스트 질의")
        
        # 점수 순으로 정렬되었는지 확인
        scores = [doc.score for doc in ranked_docs]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_process_integration(self, retriever):
        """통합 처리 테스트"""
        input_data = DocumentRetrievalInput(
            processed_query="주민등록등본 발급",
            keywords=["주민등록", "발급"],
            max_results=5
        )
        
        result = await retriever.process(input_data)
        
        assert result.is_success()
        assert isinstance(result.get_data(), DocumentRetrievalOutput)
        assert "search_type" in result.metadata


@pytest.mark.unit 
class TestCitizenFriendlyProcessor:
    """CitizenFriendlyProcessor 인터페이스 테스트"""
    
    @pytest.fixture
    def processor(self):
        return MockCitizenFriendlyProcessor()
    
    @pytest.mark.asyncio
    async def test_simplify_language(self, processor):
        """언어 단순화 테스트"""
        content = "주민등록등본을 발급받을 수 있습니다"
        simplified = await processor.simplify_language(content, DifficultyLevel.BEGINNER)
        
        assert "받을 수 있어요" in simplified
        assert simplified != content  # 변화가 있어야 함
    
    @pytest.mark.asyncio
    async def test_extract_key_points(self, processor):
        """핵심 포인트 추출 테스트"""
        content = "첫번째 문장입니다. 두번째 문장입니다. 세번째 문장입니다."
        key_points = await processor.extract_key_points(content, max_points=2)
        
        assert isinstance(key_points, list)
        assert len(key_points) <= 2
        assert all(isinstance(point, str) for point in key_points)
    
    @pytest.mark.asyncio
    async def test_create_step_guide(self, processor):
        """단계별 가이드 생성 테스트"""
        content = "주민등록등본 발급 과정입니다"
        guide = await processor.create_step_guide(content)
        
        assert isinstance(guide, list)
        assert len(guide) > 0
        assert all("단계" in step for step in guide)
    
    @pytest.mark.asyncio
    async def test_explain_terminology(self, processor):
        """용어 설명 테스트"""
        content = "주민등록등본을 홈택스에서 확인하세요"
        explanations = await processor.explain_terminology(content)
        
        assert isinstance(explanations, dict)
        assert "주민등록등본" in explanations
        assert "홈택스" in explanations
    
    @pytest.mark.asyncio
    async def test_calculate_readability(self, processor):
        """가독성 계산 테스트"""
        content = "짧은 문장입니다. 이것도 짧아요."
        score = await processor.calculate_readability(content)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    @pytest.mark.asyncio
    async def test_process_integration(self, processor):
        """통합 처리 테스트"""
        documents = [
            DocumentResult(
                id="test_doc",
                title="테스트 문서",
                content="테스트 내용입니다.",
                category="테스트",
                published_date="2024-01-01",
                difficulty=DifficultyLevel.BEGINNER,
                score=0.9
            )
        ]
        
        input_data = ContentProcessingInput(
            documents=documents,
            user_query="테스트 질의",
            target_difficulty=DifficultyLevel.BEGINNER
        )
        
        result = await processor.process(input_data)
        
        assert result.is_success()
        assert isinstance(result.get_data(), ContentProcessingOutput)
        assert result.get_data().difficulty_adjusted
        assert "documents_processed" in result.metadata


@pytest.mark.unit
class TestInteractiveResponseGenerator:
    """InteractiveResponseGenerator 인터페이스 테스트"""
    
    @pytest.fixture
    def generator(self):
        return MockInteractiveResponseGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_response(self, generator):
        """응답 생성 테스트"""
        response = await generator.generate_response(
            "주민등록등본 발급 방법",
            "온라인 또는 주민센터에서 발급 가능합니다"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "주민등록등본" in response
    
    @pytest.mark.asyncio
    async def test_suggest_follow_ups(self, generator):
        """후속 질문 제안 테스트"""
        suggestions = await generator.suggest_follow_ups(
            "주민등록등본 발급",
            "발급 방법 안내"
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)
        assert any("준비물" in s for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_find_related_info(self, generator):
        """관련 정보 링크 테스트"""
        links = await generator.find_related_info(
            "주민등록등본",
            "발급 관련 내용"
        )
        
        assert isinstance(links, list)
        assert all(isinstance(link, dict) for link in links)
        assert all("title" in link and "url" in link for link in links)
    
    @pytest.mark.asyncio
    async def test_calculate_confidence(self, generator):
        """신뢰도 계산 테스트"""
        documents = [
            DocumentResult(
                id="doc1", title="테스트", content="내용", 
                category="테스트", published_date="2024-01-01",
                difficulty=DifficultyLevel.BEGINNER, score=0.9
            )
        ]
        
        confidence = await generator.calculate_confidence(
            "테스트 질의", "테스트 응답", documents
        )
        
        assert 0 <= confidence <= 1
        assert isinstance(confidence, float)
    
    @pytest.mark.asyncio
    async def test_process_integration(self, generator):
        """통합 처리 테스트"""
        processed_content = ContentProcessingOutput(
            simplified_content="간단한 설명입니다",
            key_points=["핵심1", "핵심2"],
            readability_score=0.8
        )
        
        input_data = ResponseGenerationInput(
            user_query="테스트 질의",
            processed_content=processed_content,
            include_suggestions=True
        )
        
        result = await generator.process(input_data)
        
        assert result.is_success()
        assert isinstance(result.get_data(), ResponseGenerationOutput)
        assert len(result.get_data().main_response) > 0
        assert "response_length" in result.metadata


@pytest.mark.integration
class TestAgentInterfaces:
    """Agent 인터페이스 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_complete_agent_workflow(self):
        """전체 Agent 워크플로우 테스트"""
        # Agent 인스턴스 생성
        analyzer = MockCitizenQueryAnalyzer()
        retriever = MockPolicyDocumentRetriever()
        processor = MockCitizenFriendlyProcessor()
        generator = MockInteractiveResponseGenerator()
        
        # 1. 질의 분석
        query_input = QueryAnalysisInput("주민등록등본 발급 방법을 알려주세요")
        analysis_result = await analyzer.process(query_input)
        
        assert analysis_result.is_success()
        analysis_output = analysis_result.get_data()
        
        # 2. 문서 검색
        retrieval_input = DocumentRetrievalInput(
            processed_query=analysis_output.processed_query,
            keywords=analysis_output.keywords,
            category=analysis_output.category
        )
        retrieval_result = await retriever.process(retrieval_input)
        
        assert retrieval_result.is_success()
        retrieval_output = retrieval_result.get_data()
        
        # 3. 내용 처리
        processing_input = ContentProcessingInput(
            documents=retrieval_output.documents,
            user_query=query_input.query,
            target_difficulty=analysis_output.difficulty_hint
        )
        processing_result = await processor.process(processing_input)
        
        assert processing_result.is_success()
        processing_output = processing_result.get_data()
        
        # 4. 응답 생성
        generation_input = ResponseGenerationInput(
            user_query=query_input.query,
            processed_content=processing_output
        )
        generation_result = await generator.process(generation_input)
        
        assert generation_result.is_success()
        generation_output = generation_result.get_data()
        
        # 최종 검증
        assert len(generation_output.main_response) > 0
        assert generation_output.confidence_score > 0
        assert len(generation_output.follow_up_questions) > 0
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Agent 에러 처리 테스트"""
        analyzer = MockCitizenQueryAnalyzer()
        
        # 잘못된 입력 데이터
        invalid_input = "잘못된 타입의 입력"
        
        # Exception 대신 실패 결과 확인
        result = await analyzer.process(invalid_input)
        
        assert not result.is_success()
        assert "Invalid input data" in result.error
    
    @pytest.mark.asyncio
    async def test_agent_health_checks(self):
        """Agent 상태 확인 테스트"""
        agents = [
            MockCitizenQueryAnalyzer(),
            MockPolicyDocumentRetriever(),
            MockCitizenFriendlyProcessor(),
            MockInteractiveResponseGenerator()
        ]
        
        for agent in agents:
            health = await agent.health_check()
            
            assert "name" in health
            assert "initialized" in health
            assert "status" in health
            assert health["status"] == "healthy"
    
    def test_agent_metrics(self):
        """Agent 메트릭 테스트"""
        agents = [
            MockCitizenQueryAnalyzer(),
            MockPolicyDocumentRetriever(),
            MockCitizenFriendlyProcessor(),
            MockInteractiveResponseGenerator()
        ]
        
        for agent in agents:
            metrics = agent.get_metrics()
            
            assert "name" in metrics
            assert "initialized" in metrics
            assert isinstance(metrics["config_keys"], list)