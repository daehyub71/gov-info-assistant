"""
헬스체크 API 테스트
"""
import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import status

from fastapi_server.core.config import settings


@pytest.mark.unit
class TestBasicHealthCheck:
    """기본 헬스체크 테스트"""
    
    def test_basic_health_check_success(self, client: TestClient):
        """기본 헬스체크 성공 테스트"""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
        assert "environment" in data
        assert data["version"] == settings.APP_VERSION
    
    def test_basic_health_check_response_format(self, client: TestClient):
        """헬스체크 응답 형식 테스트"""
        response = client.get("/api/v1/health/")
        
        data = response.json()
        
        # 필수 필드 확인
        required_fields = ["status", "timestamp", "version", "uptime", "environment"]
        for field in required_fields:
            assert field in data
        
        # 데이터 타입 확인
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["uptime"], (int, float))
        assert isinstance(data["environment"], str)


@pytest.mark.unit
class TestDetailedHealthCheck:
    """상세 헬스체크 테스트"""
    
    def test_detailed_health_check_success(self, client: TestClient):
        """상세 헬스체크 성공 테스트"""
        with patch("fastapi_server.api.health.psutil.cpu_percent", return_value=25.5):
            with patch("fastapi_server.api.health.psutil.virtual_memory") as mock_memory:
                mock_memory.return_value = Mock(
                    total=8589934592,  # 8GB
                    available=4294967296,  # 4GB
                    percent=50.0,
                    used=4294967296  # 4GB
                )
                with patch("fastapi_server.api.health.psutil.disk_usage") as mock_disk:
                    mock_disk.return_value = Mock(
                        total=107374182400,  # 100GB
                        used=53687091200,    # 50GB
                        free=53687091200     # 50GB
                    )
                    
                    response = client.get("/api/v1/health/detailed")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # 기본 필드 확인
        assert data["status"] in ["healthy", "warning", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
        assert "environment" in data
        
        # 추가 필드 확인
        assert "system" in data
        assert "services" in data
        assert "database" in data
        assert "disk_usage" in data
    
    def test_detailed_health_check_system_metrics(self, client: TestClient):
        """시스템 메트릭 테스트"""
        with patch("fastapi_server.api.health.psutil.cpu_percent", return_value=25.5):
            with patch("fastapi_server.api.health.psutil.virtual_memory") as mock_memory:
                mock_memory.return_value = Mock(
                    total=8589934592,
                    available=4294967296,
                    percent=50.0,
                    used=4294967296
                )
                with patch("fastapi_server.api.health.psutil.disk_usage") as mock_disk:
                    mock_disk.return_value = Mock(
                        total=107374182400,
                        used=53687091200,
                        free=53687091200
                    )
                    
                    response = client.get("/api/v1/health/detailed")
        
        data = response.json()
        system = data["system"]
        
        # CPU 메트릭
        assert "cpu" in system
        assert "percent" in system["cpu"]
        assert "count" in system["cpu"]
        
        # 메모리 메트릭
        assert "memory" in system
        memory = system["memory"]
        assert "total" in memory
        assert "available" in memory
        assert "percent" in memory
        assert "used" in memory
        assert "total_gb" in memory
        assert "used_gb" in memory
        
        # 디스크 메트릭
        assert "disk" in system
        disk = system["disk"]
        assert "total" in disk
        assert "used" in disk
        assert "free" in disk
        assert "percent" in disk
    
    def test_detailed_health_check_services(self, client: TestClient):
        """서비스 상태 테스트"""
        response = client.get("/api/v1/health/detailed")
        
        data = response.json()
        services = data["services"]
        
        # 서비스 상태 확인
        assert "azure_openai" in services
        assert "vector_database" in services
        assert "session_database" in services
        
        # 각 서비스 상태 구조 확인
        for service_name, service_data in services.items():
            assert "status" in service_data
            assert service_data["status"] in ["healthy", "warning", "unhealthy"]
            assert "message" in service_data


@pytest.mark.unit
class TestReadinessCheck:
    """준비 상태 확인 테스트"""
    
    def test_readiness_check_ready(self, client: TestClient):
        """준비 상태 확인 - 준비됨"""
        response = client.get("/api/v1/health/readiness")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data
    
    @patch("fastapi_server.api.health.check_azure_openai")
    def test_readiness_check_not_ready(self, mock_check, client: TestClient):
        """준비 상태 확인 - 준비되지 않음"""
        mock_check.return_value = {
            "status": "unhealthy",
            "message": "Azure OpenAI not available"
        }
        
        response = client.get("/api/v1/health/readiness")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.unit
class TestLivenessCheck:
    """생존 상태 확인 테스트"""
    
    def test_liveness_check_alive(self, client: TestClient):
        """생존 상태 확인 - 살아있음"""
        response = client.get("/api/v1/health/liveness")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data


@pytest.mark.unit
class TestHealthCheckHelpers:
    """헬스체크 헬퍼 함수 테스트"""
    
    def test_check_azure_openai_valid_config(self):
        """Azure OpenAI 설정 유효성 테스트"""
        from fastapi_server.api.health import check_azure_openai
        
        result = check_azure_openai()
        
        assert "status" in result
        assert "message" in result
        assert result["status"] in ["healthy", "unhealthy"]
    
    def test_check_vector_database_not_exists(self):
        """벡터 데이터베이스 없음 테스트"""
        from fastapi_server.api.health import check_vector_database
        
        with patch("pathlib.Path.exists", return_value=False):
            result = check_vector_database()
        
        assert result["status"] == "warning"
        assert "not initialized" in result["message"]
    
    def test_check_session_database_not_exists(self):
        """세션 데이터베이스 없음 테스트"""
        from fastapi_server.api.health import check_session_database
        
        with patch("pathlib.Path.exists", return_value=False):
            result = check_session_database()
        
        assert result["status"] == "warning"
        assert "not initialized" in result["message"]
    
    @patch("fastapi_server.api.health.psutil.cpu_percent")
    @patch("fastapi_server.api.health.psutil.virtual_memory")
    @patch("fastapi_server.api.health.psutil.disk_usage")
    def test_get_system_metrics(self, mock_disk, mock_memory, mock_cpu):
        """시스템 메트릭 수집 테스트"""
        from fastapi_server.api.health import get_system_metrics
        
        mock_cpu.return_value = 25.5
        mock_memory.return_value = Mock(
            total=8589934592,
            available=4294967296,
            percent=50.0,
            used=4294967296
        )
        mock_disk.return_value = Mock(
            total=107374182400,
            used=53687091200,
            free=53687091200
        )
        
        metrics = get_system_metrics()
        
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
        
        assert metrics["cpu"]["percent"] == 25.5
        assert metrics["memory"]["percent"] == 50.0


@pytest.mark.integration
class TestHealthCheckIntegration:
    """헬스체크 통합 테스트"""
    
    def test_health_endpoints_accessibility(self, client: TestClient):
        """모든 헬스체크 엔드포인트 접근성 테스트"""
        endpoints = [
            "/api/v1/health/",
            "/api/v1/health/detailed",
            "/api/v1/health/readiness",
            "/api/v1/health/liveness"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 503]  # 503은 서비스 준비 안됨
    
    def test_health_check_response_time(self, client: TestClient):
        """헬스체크 응답 시간 테스트"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/health/")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0  # 1초 이내 응답
    
    def test_health_check_json_format(self, client: TestClient):
        """헬스체크 JSON 응답 형식 테스트"""
        response = client.get("/api/v1/health/")
        
        assert response.headers["content-type"] == "application/json"
        
        # JSON 파싱 가능 여부 확인
        try:
            json.loads(response.text)
        except json.JSONDecodeError:
            pytest.fail("Response is not valid JSON")


@pytest.mark.slow
class TestHealthCheckPerformance:
    """헬스체크 성능 테스트"""
    
    def test_multiple_health_checks(self, client: TestClient):
        """다중 헬스체크 요청 테스트"""
        import time
        
        start_time = time.time()
        
        # 10번 연속 요청
        for _ in range(10):
            response = client.get("/api/v1/health/")
            assert response.status_code == status.HTTP_200_OK
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 평균 응답 시간이 0.1초 이내
        average_time = total_time / 10
        assert average_time < 0.1
    
    def test_detailed_health_check_performance(self, client: TestClient):
        """상세 헬스체크 성능 테스트"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/health/detailed")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 2.0  # 2초 이내 응답