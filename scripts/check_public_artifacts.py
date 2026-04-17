from pathlib import Path
import sys


REQUIRED_PATHS = [
    "README.md",
    "docs/README.md",
    "docs/reproducibility_and_validation.md",
    "docs/NBA_머신러닝_인사이트.md",
    "docs/NBA_프로젝트_설명서.md",
    "NBA_통합_파이프라인.py",
    "NBA_전처리_모듈.py",
    "NBA_머신러닝_모듈.py",
    "outputs/NBA_시각화_결과/07_대시보드/NBA_05_종합_대시보드.png",
    "outputs/NBA_시각화_결과/02_히트맵_상관_비교/NBA_01_상관관계_히트맵.png",
    "outputs/NBA_시각화_결과/00_기타/NBA_06_승패예측_모델_성능.png",
    "outputs/NBA_시각화_결과/00_기타/NBA_07_선수PLUS_MINUS예측_모델_성능.png",
]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED_PATHS if not (repo_root / path).exists()]

    if missing:
        print("Missing public review artifacts:")
        for path in missing:
            print(f"- {path}")
        return 1

    print("Public review artifacts verified:")
    for path in REQUIRED_PATHS:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
