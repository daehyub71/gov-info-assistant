"""
Agent 인터페이스 정의 (Abstract Base Classes)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio

from fastapi_server.models.schemas import (
    SearchRequest, SearchResponse, DocumentResult, 
    ChatMessage, AgentState, DifficultyLevel
)
from fastapi_server.core.logging_config import LoggerMixin


class AgentError(Exception):
    """Agent 처리 중 발생하는 에러"""
    
    def __init__(self, message: str, agent_name: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.agent_name = agent_name
        self.details = details or {}
        super().__init__(f"[{agent_name}] {message}")


class AgentResult:
    """Agent 처리 결과 기본 클래스"""
    
    def __init__(
        self, 
        success: bool, 
        data: Any = None, 
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        processing_time: float = 0.0
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.processing_time = processing_time
        self.timestamp = datetime.utcnow()
    
    def is_success(self) -> bool:
        """성공 여부 반환"""
        return self.success
    
    def get_data(self) -> Any:
        """결과 데이터 반환"""
        if not self.success:
            raise AgentError(f"Cannot get data from failed result: {self.error}", "AgentResult")
        return self.data
    
    def get_error(self) -> Optional[str]:
        """에러 메시지 반환"""
        return self.error


class BaseAgent(ABC, LoggerMixin):
    """모든 Agent의 기본 추상 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.config = {}
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Agent 초기화"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """메인 처리 로직"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """입력 데이터 검증"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Agent 상태 확인"""
        return {
            "name": self.name,
            "initialized": self.initialized,
            "status": "healthy" if self.initialized else "not_initialized",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Agent 메트릭 반환"""
        return {
            "name": self.name,
            "initialized": self.initialized,
            "config_keys": list(self.config.keys())
        }


# === 질의 분석 Agent ===

class QueryAnalysisInput:
    """질의 분석 입력 데이터"""
    
    def __init__(
        self, 
        query: str, 
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.query = query
        self.session_id = session_id
        self.context = context or {}


class QueryAnalysisOutput:
    """질의 분석 출력 데이터"""
    
    def __init__(
        self,
        processed_query: str,
        intent: str,
        category: Optional[str] = None,
        keywords: List[str] = None,
        entities: Dict[str, List[str]] = None,
        confidence: float = 0.0,
        suggestions: List[str] = None,
        difficulty_hint: Optional[DifficultyLevel] = None
    ):
        self.processed_query = processed_query
        self.intent = intent
        self.category = category
        self.keywords = keywords or []
        self.entities = entities or {}
        self.confidence = confidence
        self.suggestions = suggestions or []
        self.difficulty_hint = difficulty_hint


class ICitizenQueryAnalyzer(BaseAgent):
    """시민 질의 분석 Agent 인터페이스"""
    
    @abstractmethod
    async def analyze_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> QueryAnalysisOutput:
        """질의 분석 및 의도 파악"""
        pass
    
    @abstractmethod
    async def extract_keywords(self, query: str) -> List[str]:
        """키워드 추출"""
        pass
    
    @abstractmethod
    async def classify_category(self, query: str) -> Optional[str]:
        """카테고리 분류"""
        pass
    
    @abstractmethod
    async def detect_intent(self, query: str) -> str:
        """의도 탐지 (정보조회, 절차문의, 정책문의 등)"""
        pass
    
    @abstractmethod
    async def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """개체명 인식 (기관명, 서류명, 날짜 등)"""
        pass
    
    async def process(self, input_data: QueryAnalysisInput, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """통합 처리 메서드"""
        try:
            if not self.validate_input(input_data):
                return AgentResult(False, error="Invalid input data")
            
            start_time = asyncio.get_event_loop().time()
            
            result = await self.analyze_query(input_data.query, context)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"query_length": len(input_data.query)}
            )
            
        except Exception as e:
            self.logger.error(f"Query analysis failed: {e}")
            return AgentResult(False, error=str(e))
    
    def validate_input(self, input_data: QueryAnalysisInput) -> bool:
        """입력 검증"""
        return (
            isinstance(input_data, QueryAnalysisInput) and
            input_data.query and
            len(input_data.query.strip()) >= 2
        )


# === 문서 검색 Agent ===

class DocumentRetrievalInput:
    """문서 검색 입력 데이터"""
    
    def __init__(
        self,
        processed_query: str,
        keywords: List[str] = None,
        category: Optional[str] = None,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ):
        self.processed_query = processed_query
        self.keywords = keywords or []
        self.category = category
        self.max_results = max_results
        self.filters = filters or {}


class DocumentRetrievalOutput:
    """문서 검색 출력 데이터"""
    
    def __init__(
        self,
        documents: List[DocumentResult],
        total_count: int,
        search_strategy: str,
        retrieval_metadata: Dict[str, Any] = None
    ):
        self.documents = documents
        self.total_count = total_count
        self.search_strategy = search_strategy
        self.retrieval_metadata = retrieval_metadata or {}


class IPolicyDocumentRetriever(BaseAgent):
    """정책 문서 검색 Agent 인터페이스"""
    
    @abstractmethod
    async def search_documents(
        self, 
        query: str, 
        keywords: List[str] = None,
        max_results: int = 5
    ) -> DocumentRetrievalOutput:
        """의미적 유사도 기반 문서 검색"""
        pass
    
    @abstractmethod
    async def hybrid_search(
        self, 
        query: str, 
        keywords: List[str],
        category: Optional[str] = None
    ) -> DocumentRetrievalOutput:
        """하이브리드 검색 (벡터 + 키워드)"""
        pass
    
    @abstractmethod
    async def filter_by_category(
        self, 
        documents: List[DocumentResult], 
        category: str
    ) -> List[DocumentResult]:
        """카테고리별 필터링"""
        pass
    
    @abstractmethod
    async def rank_documents(
        self, 
        documents: List[DocumentResult], 
        query: str
    ) -> List[DocumentResult]:
        """문서 관련성 재순위화"""
        pass
    
    @abstractmethod
    async def get_similar_documents(
        self, 
        document_id: str, 
        limit: int = 3
    ) -> List[DocumentResult]:
        """유사 문서 찾기"""
        pass
    
    async def process(self, input_data: DocumentRetrievalInput, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """통합 처리 메서드"""
        try:
            if not self.validate_input(input_data):
                return AgentResult(False, error="Invalid input data")
            
            start_time = asyncio.get_event_loop().time()
            
            if input_data.keywords:
                result = await self.hybrid_search(
                    input_data.processed_query,
                    input_data.keywords,
                    input_data.category
                )
            else:
                result = await self.search_documents(
                    input_data.processed_query,
                    max_results=input_data.max_results
                )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"search_type": "hybrid" if input_data.keywords else "semantic"}
            )
            
        except Exception as e:
            self.logger.error(f"Document retrieval failed: {e}")
            return AgentResult(False, error=str(e))
    
    def validate_input(self, input_data: DocumentRetrievalInput) -> bool:
        """입력 검증"""
        return (
            isinstance(input_data, DocumentRetrievalInput) and
            input_data.processed_query and
            1 <= input_data.max_results <= 20
        )


# === 시민 친화적 처리 Agent ===

class ContentProcessingInput:
    """내용 처리 입력 데이터"""
    
    def __init__(
        self,
        documents: List[DocumentResult],
        user_query: str,
        target_difficulty: Optional[DifficultyLevel] = None,
        processing_options: Optional[Dict[str, Any]] = None
    ):
        self.documents = documents
        self.user_query = user_query
        self.target_difficulty = target_difficulty
        self.processing_options = processing_options or {}


class ContentProcessingOutput:
    """내용 처리 출력 데이터"""
    
    def __init__(
        self,
        simplified_content: str,
        key_points: List[str],
        step_by_step_guide: List[str] = None,
        terminology_explanations: Dict[str, str] = None,
        difficulty_adjusted: bool = False,
        readability_score: float = 0.0
    ):
        self.simplified_content = simplified_content
        self.key_points = key_points
        self.step_by_step_guide = step_by_step_guide or []
        self.terminology_explanations = terminology_explanations or {}
        self.difficulty_adjusted = difficulty_adjusted
        self.readability_score = readability_score


class ICitizenFriendlyProcessor(BaseAgent):
    """시민 친화적 처리 Agent 인터페이스"""
    
    @abstractmethod
    async def simplify_language(
        self, 
        content: str, 
        target_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    ) -> str:
        """공문서 언어를 시민 친화적으로 변환"""
        pass
    
    @abstractmethod
    async def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """핵심 내용 추출"""
        pass
    
    @abstractmethod
    async def create_step_guide(self, content: str) -> List[str]:
        """단계별 절차 안내 생성"""
        pass
    
    @abstractmethod
    async def explain_terminology(self, content: str) -> Dict[str, str]:
        """전문 용어 설명"""
        pass
    
    @abstractmethod
    async def adjust_difficulty(
        self, 
        content: str, 
        current_difficulty: DifficultyLevel,
        target_difficulty: DifficultyLevel
    ) -> str:
        """난이도 조정"""
        pass
    
    @abstractmethod
    async def calculate_readability(self, content: str) -> float:
        """가독성 점수 계산"""
        pass
    
    async def process(self, input_data: ContentProcessingInput, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """통합 처리 메서드"""
        try:
            if not self.validate_input(input_data):
                return AgentResult(False, error="Invalid input data")
            
            start_time = asyncio.get_event_loop().time()
            
            # 문서 내용 결합
            combined_content = "\n\n".join([doc.content for doc in input_data.documents])
            
            # 시민 친화적 처리
            simplified = await self.simplify_language(
                combined_content, 
                input_data.target_difficulty or DifficultyLevel.BEGINNER
            )
            
            key_points = await self.extract_key_points(simplified)
            step_guide = await self.create_step_guide(simplified)
            terminology = await self.explain_terminology(combined_content)
            readability = await self.calculate_readability(simplified)
            
            result = ContentProcessingOutput(
                simplified_content=simplified,
                key_points=key_points,
                step_by_step_guide=step_guide,
                terminology_explanations=terminology,
                difficulty_adjusted=True,
                readability_score=readability
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"documents_processed": len(input_data.documents)}
            )
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {e}")
            return AgentResult(False, error=str(e))
    
    def validate_input(self, input_data: ContentProcessingInput) -> bool:
        """입력 검증"""
        return (
            isinstance(input_data, ContentProcessingInput) and
            input_data.documents and
            input_data.user_query
        )


# === 대화형 응답 생성 Agent ===

class ResponseGenerationInput:
    """응답 생성 입력 데이터"""
    
    def __init__(
        self,
        user_query: str,
        processed_content: ContentProcessingOutput,
        chat_history: List[ChatMessage] = None,
        response_style: str = "conversational",
        include_suggestions: bool = True
    ):
        self.user_query = user_query
        self.processed_content = processed_content
        self.chat_history = chat_history or []
        self.response_style = response_style
        self.include_suggestions = include_suggestions


class ResponseGenerationOutput:
    """응답 생성 출력 데이터"""
    
    def __init__(
        self,
        main_response: str,
        follow_up_questions: List[str] = None,
        related_links: List[Dict[str, str]] = None,
        confidence_score: float = 0.0,
        response_metadata: Dict[str, Any] = None
    ):
        self.main_response = main_response
        self.follow_up_questions = follow_up_questions or []
        self.related_links = related_links or []
        self.confidence_score = confidence_score
        self.response_metadata = response_metadata or {}


class IInteractiveResponseGenerator(BaseAgent):
    """대화형 응답 생성 Agent 인터페이스"""
    
    @abstractmethod
    async def generate_response(
        self, 
        query: str, 
        content: str,
        chat_history: List[ChatMessage] = None
    ) -> str:
        """메인 응답 생성"""
        pass
    
    @abstractmethod
    async def suggest_follow_ups(
        self, 
        query: str, 
        response: str
    ) -> List[str]:
        """후속 질문 제안"""
        pass
    
    @abstractmethod
    async def find_related_info(
        self, 
        query: str, 
        current_content: str
    ) -> List[Dict[str, str]]:
        """관련 정보 링크 제공"""
        pass
    
    @abstractmethod
    async def calculate_confidence(
        self, 
        query: str, 
        response: str, 
        source_documents: List[DocumentResult]
    ) -> float:
        """응답 신뢰도 계산"""
        pass
    
    @abstractmethod
    async def personalize_response(
        self, 
        response: str, 
        user_profile: Dict[str, Any]
    ) -> str:
        """사용자 맞춤형 응답"""
        pass
    
    @abstractmethod
    async def format_response(
        self, 
        content: str, 
        style: str = "conversational"
    ) -> str:
        """응답 형식 조정"""
        pass
    
    async def process(self, input_data: ResponseGenerationInput, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """통합 처리 메서드"""
        try:
            if not self.validate_input(input_data):
                return AgentResult(False, error="Invalid input data")
            
            start_time = asyncio.get_event_loop().time()
            
            # 메인 응답 생성
            main_response = await self.generate_response(
                input_data.user_query,
                input_data.processed_content.simplified_content,
                input_data.chat_history
            )
            
            # 후속 질문 및 관련 정보
            follow_ups = []
            related_links = []
            
            if input_data.include_suggestions:
                follow_ups = await self.suggest_follow_ups(input_data.user_query, main_response)
                related_links = await self.find_related_info(input_data.user_query, main_response)
            
            # 신뢰도 계산 (문서 정보가 있는 경우)
            confidence = 0.8  # 기본값, 실제로는 문서 기반 계산
            
            result = ResponseGenerationOutput(
                main_response=main_response,
                follow_up_questions=follow_ups,
                related_links=related_links,
                confidence_score=confidence,
                response_metadata={
                    "style": input_data.response_style,
                    "has_history": len(input_data.chat_history) > 0
                }
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                success=True,
                data=result,
                processing_time=processing_time,
                metadata={"response_length": len(main_response)}
            )
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return AgentResult(False, error=str(e))
    
    def validate_input(self, input_data: ResponseGenerationInput) -> bool:
        """입력 검증"""
        return (
            isinstance(input_data, ResponseGenerationInput) and
            input_data.user_query and
            input_data.processed_content and
            input_data.processed_content.simplified_content
        )