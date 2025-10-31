"""
Prompt Loading Test
프롬프트 로딩 기능을 테스트합니다
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.framework.llm.prompt_manager import PromptManager


def test_prompt_loading():
    """프롬프트 로딩 테스트"""
    print("="*60)
    print("Prompt Loading Test")
    print("="*60)

    manager = PromptManager()

    # Test 1: List available prompts
    print("\n1. Available Prompts:")
    print("-"*60)
    available = manager.list_available_prompts()
    for category, prompts in available.items():
        print(f"\n{category}/")
        for prompt in prompts:
            print(f"  - {prompt}")

    # Test 2: Load search_type_selection (new YAML)
    print("\n2. Loading search_type_selection.yaml:")
    print("-"*60)
    try:
        prompt = manager.get(
            "search_type_selection",
            variables={
                "query": "지난 달 매출 통계",
                "available_search_types": "vector_search, text2sql, unstructured_search"
            }
        )
        print(f"✅ Success! Prompt length: {len(prompt)} chars")
        print(f"First 200 chars: {prompt[:200]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 3: Load orchestration/execution_strategy
    print("\n3. Loading orchestration/execution_strategy.yaml:")
    print("-"*60)
    try:
        prompt = manager.get(
            "orchestration/execution_strategy",
            variables={
                "query": "매출 분석해줘",
                "decomposed_queries": '["매출 데이터 검색", "매출 분석"]'
            }
        )
        print(f"✅ Success! Prompt length: {len(prompt)} chars")
        print(f"First 200 chars: {prompt[:200]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 4: Load intent_analysis (existing TXT)
    print("\n4. Loading intent_analysis.txt:")
    print("-"*60)
    try:
        prompt = manager.get(
            "intent_analysis",
            variables={
                "query": "전세 계약서 작성해줘"
            }
        )
        print(f"✅ Success! Prompt length: {len(prompt)} chars")
        print(f"First 200 chars: {prompt[:200]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 5: Get with metadata
    print("\n5. Loading with metadata (search_type_selection):")
    print("-"*60)
    try:
        result = manager.get_with_metadata(
            "search_type_selection",
            variables={
                "query": "테스트",
                "available_search_types": "all"
            }
        )
        print(f"✅ Success!")
        print(f"Metadata: {result['metadata']}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)


if __name__ == "__main__":
    test_prompt_loading()
