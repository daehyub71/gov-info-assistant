"""
Agent 모듈 패키지
"""
from .interfaces import (
    # 기본 클래스
    BaseAgent,
    AgentResult,
    AgentError,
    
    # Agent 인터페이스
    ICitizenQueryAnalyzer,
    IPolicyDocumentRetriever,
    ICitizenFriendlyProcessor,
    IInteractiveResponseGenerator,
    
    # 입출력 모델
    QueryAnalysisInput,
    QueryAnalysisOutput,
    DocumentRetrievalInput,
    DocumentRetrievalOutput,
    ContentProcessingInput,
    ContentProcessingOutput,
    ResponseGenerationInput,
    ResponseGenerationOutput,
)

__all__ = [
    # 기본 클래스
    "BaseAgent",
    "AgentResult", 
    "AgentError",
    
    # Agent 인터페이스
    "ICitizenQueryAnalyzer",
    "IPolicyDocumentRetriever",
    "ICitizenFriendlyProcessor",
    "IInteractiveResponseGenerator",
    
    # 입출력 모델
    "QueryAnalysisInput",
    "QueryAnalysisOutput",
    "DocumentRetrievalInput", 
    "DocumentRetrievalOutput",
    "ContentProcessingInput",
    "ContentProcessingOutput",
    "ResponseGenerationInput",
    "ResponseGenerationOutput",
]