# test_azure_openai.py
"""
Azure OpenAI 설정 검증 스크립트
"""

import os
from dotenv import load_dotenv

def test_azure_openai_connection():
    """Azure OpenAI 연결 및 설정 테스트"""
    
    # 1. 환경변수 로드
    load_dotenv()
    
    # 2. 필수 환경변수 확인
    required_vars = {
        'AOAI_ENDPOINT': os.getenv('AOAI_ENDPOINT'),
        'AOAI_API_KEY': os.getenv('AOAI_API_KEY'),
        'AOAI_DEPLOY_GPT4O_MINI': os.getenv('AOAI_DEPLOY_GPT4O_MINI'),
        'AOAI_DEPLOY_EMBED_3_LARGE': os.getenv('AOAI_DEPLOY_EMBED_3_LARGE')
    }
    
    print("=== 환경변수 확인 ===")
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            if 'API_KEY' in var_name:
                print(f"✅ {var_name}: {var_value[:10]}...{var_value[-5:]}")
            else:
                print(f"✅ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: 설정되지 않음")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n⚠️  누락된 환경변수: {missing_vars}")
        return False
    
    # 3. Azure OpenAI 클라이언트 연결 테스트
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            azure_endpoint=required_vars['AOAI_ENDPOINT'],
            api_key=required_vars['AOAI_API_KEY'],
            api_version="2024-02-15-preview"
        )
        
        print("\n=== 연결 테스트 ===")
        print("✅ Azure OpenAI 클라이언트 생성 성공")
        
        # 4. Chat Completion 테스트
        try:
            response = client.chat.completions.create(
                model=required_vars['AOAI_DEPLOY_GPT4O_MINI'],
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                max_tokens=10
            )
            print("✅ Chat Completion API 테스트 성공")
            print(f"   응답: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"❌ Chat Completion API 테스트 실패: {e}")
            return False
        
        # 5. Embedding 테스트
        try:
            embedding_response = client.embeddings.create(
                model=required_vars['AOAI_DEPLOY_EMBED_3_LARGE'],
                input="테스트 임베딩"
            )
            print("✅ Embedding API 테스트 성공")
            print(f"   임베딩 차원: {len(embedding_response.data[0].embedding)}")
            
        except Exception as e:
            print(f"❌ Embedding API 테스트 실패: {e}")
            return False
        
        print("\n🎉 모든 테스트 통과! Azure OpenAI 설정이 올바릅니다.")
        return True
        
    except ImportError:
        print("❌ openai 패키지가 설치되지 않았습니다.")
        print("   pip install openai 를 실행하세요.")
        return False
    except Exception as e:
        print(f"❌ Azure OpenAI 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_azure_openai_connection()