"""
Import 경로 자동 수정 스크립트
framework → agent_system
team_supervisor → main
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 변경 패턴 정의
REPLACEMENTS: List[Tuple[str, str]] = [
    # 1. 디렉토리 변경: framework → agent_system
    (r'from app\.framework\.', 'from app.agent_system.'),
    (r'import app\.framework\.', 'import app.agent_system.'),
    (r'from\s+app\.framework\s+import', 'from app.agent_system import'),

    # 2. 파일명 변경: team_supervisor → main (supervisor 폴더는 유지)
    (r'from app\.agent_system\.supervisor\.team_supervisor\s+import',
     'from app.agent_system.supervisor.main import'),
    (r'import app\.agent_system\.supervisor\.team_supervisor',
     'import app.agent_system.supervisor.main'),
]

def refactor_file(file_path: Path) -> bool:
    """
    단일 파일의 import 경로를 수정

    Args:
        file_path: 수정할 파일 경로

    Returns:
        변경 여부 (True: 변경됨, False: 변경 안 됨)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return False

    original_content = content

    # 모든 패턴 적용
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    # 변경사항이 있으면 파일 저장
    if content != original_content:
        try:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Refactored: {file_path.relative_to(Path.cwd())}")
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False

    return False

def find_python_files(root_dir: Path) -> List[Path]:
    """
    Python 파일 목록 찾기

    Args:
        root_dir: 검색 시작 디렉토리

    Returns:
        Python 파일 경로 리스트
    """
    return list(root_dir.rglob("*.py"))

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Import 경로 자동 수정 시작")
    print("=" * 60)

    # 루트 디렉토리 설정
    backend_dir = Path(__file__).parent.parent
    app_dir = backend_dir / "app"
    tests_dir = backend_dir / "tests"

    # Python 파일 수집
    python_files = []
    python_files.extend(find_python_files(app_dir))
    if tests_dir.exists():
        python_files.extend(find_python_files(tests_dir))

    print(f"\n📁 검색된 Python 파일: {len(python_files)}개")
    print("-" * 60)

    # 파일별 수정
    changed_count = 0
    for py_file in python_files:
        if refactor_file(py_file):
            changed_count += 1

    print("-" * 60)
    print(f"\n✨ 완료: {changed_count}개 파일 수정됨")
    print("=" * 60)

    if changed_count > 0:
        print("\n다음 단계:")
        print("1. 수정된 파일 확인: git diff")
        print("2. 테스트 실행: pytest backend/tests/ -v")
        print("3. 커밋: git add . && git commit -m 'Refactor: Update imports for agent_system'")

if __name__ == "__main__":
    main()
