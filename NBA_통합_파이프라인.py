"""
NBA 데이터 분석 통합 파이프라인

이 스크립트는 NBA 데이터의 전처리부터 시각화, 머신러닝까지 전체 프로세스를 실행합니다.

사용법:
    python NBA_통합_파이프라인.py [--skip-preprocessing] [--skip-visualization] [--skip-ml]

옵션:
    --skip-preprocessing: 전처리 단계 건너뛰기 (이미 전처리된 데이터가 있는 경우)
    --skip-visualization: 시각화 단계 건너뛰기 (전처리만 실행하는 경우)
    --skip-ml: 머신러닝 단계 건너뛰기
"""

import argparse
from NBA_전처리_모듈 import NBADataPreprocessor
from NBA_EDA_모듈 import NBAEDA
from NBA_통계검정_모듈 import NBAStatisticalTest
from NBA_시각화_모듈 import NBADataVisualizer
from NBA_머신러닝_모듈 import NBAMachineLearning


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='NBA 데이터 분석 통합 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 전체 프로세스 실행 (전처리 + EDA + 통계검정 + 시각화 + 머신러닝)
  python NBA_통합_파이프라인.py
  
  # 전처리만 실행
  python NBA_통합_파이프라인.py --skip-eda --skip-statistics --skip-visualization --skip-ml
  
  # 통계 검정만 실행 (전처리된 데이터 필요)
  python NBA_통합_파이프라인.py --skip-preprocessing --skip-eda --skip-visualization --skip-ml
  
  # 머신러닝만 실행
  python NBA_통합_파이프라인.py --skip-preprocessing --skip-eda --skip-statistics --skip-visualization
        """
    )
    
    parser.add_argument(
        '--skip-preprocessing',
        action='store_true',
        help='전처리 단계 건너뛰기'
    )
    
    parser.add_argument(
        '--skip-visualization',
        action='store_true',
        help='시각화 단계 건너뛰기'
    )
    
    parser.add_argument(
        '--skip-ml',
        action='store_true',
        help='머신러닝 단계 건너뛰기'
    )
    
    parser.add_argument(
        '--skip-eda',
        action='store_true',
        help='EDA 단계 건너뛰기'
    )
    
    parser.add_argument(
        '--skip-statistics',
        action='store_true',
        help='통계 검정 단계 건너뛰기'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("NBA 데이터 분석 통합 파이프라인")
    print("=" * 60)
    
    # 전처리 단계
    if not args.skip_preprocessing:
        print("\n[전처리 단계 시작]")
        preprocessor = NBADataPreprocessor()
        df = preprocessor.process()
        print("\n✓ 전처리 완료!")
    else:
        print("\n[전처리 단계 건너뛰기]")
    
    # EDA 단계
    if not args.skip_eda:
        print("\n[EDA 단계 시작]")
        eda = NBAEDA()
        eda.perform_all_eda()
        print("\n✓ EDA 완료!")
    else:
        print("\n[EDA 단계 건너뛰기]")
    
    # 통계 검정 단계
    if not args.skip_statistics:
        print("\n[통계 검정 단계 시작]")
        stat_test = NBAStatisticalTest()
        stat_test.perform_all_tests()
        print("\n✓ 통계 검정 완료!")
    else:
        print("\n[통계 검정 단계 건너뛰기]")
    
    # 시각화 단계
    if not args.skip_visualization:
        print("\n[시각화 단계 시작]")
        visualizer = NBADataVisualizer()
        visualizer.visualize_all()
        print("\n✓ 시각화 완료!")
    else:
        print("\n[시각화 단계 건너뛰기]")
    
    # 머신러닝 단계
    if not args.skip_ml:
        print("\n[머신러닝 단계 시작]")
        ml = NBAMachineLearning()
        ml.train_all_models()
        print("\n✓ 머신러닝 완료!")
        
        # 머신러닝 결과 시각화
        print("\n[머신러닝 결과 시각화]")
        visualizer = NBADataVisualizer()
        visualizer.visualize_ml_results()
        print("\n✓ 머신러닝 시각화 완료!")
    else:
        print("\n[머신러닝 단계 건너뛰기]")
    
    print("\n" + "=" * 60)
    print("전체 프로세스 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

