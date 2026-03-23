"""
NBA 데이터 분석 프로젝트 설정 파일
"""

import os

# ============================================================================
# 경로 설정
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 입력 데이터 경로
#
# NOTE:
# - 공개 저장소에는 원본 데이터를 포함하지 않습니다.
# - Kaggle 원본 CSV를 내려받아 `data/games.csv` 등 영문 파일명으로 두는 구성을 기본값으로 사용합니다.
RAW_DATA_DIR = os.path.join(BASE_DIR, "data")
GAMES_CSV = os.path.join(RAW_DATA_DIR, "games.csv")
GAMES_DETAILS_CSV = os.path.join(RAW_DATA_DIR, "games_details.csv")
PLAYERS_CSV = os.path.join(RAW_DATA_DIR, "players.csv")
TEAMS_CSV = os.path.join(RAW_DATA_DIR, "teams.csv")

# 전처리 산출물 경로
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
MERGED_PKL = os.path.join(PROCESSED_DATA_DIR, 'NBA_전처리_데이터.pkl')
FINAL_CSV = os.path.join(PROCESSED_DATA_DIR, 'NBA_전처리_최종_데이터.csv')

# 시각화 출력 경로
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
VISUALIZATIONS_DIR = os.path.join(OUTPUT_DIR, 'NBA_시각화_결과')

# ============================================================================
# 전처리 설정
# ============================================================================

# 최소 출전 시간 (분) - 선수 필터링 기준
MIN_MINUTES_THRESHOLD = 1000

# MIN 컬럼 상한선 (분)
MAX_MINUTES = 60

# 숫자형 컬럼 목록
NUMERICAL_COLS = [
    'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
    'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
    'STL', 'BLK', 'TO', 'PF', 'PTS', 'PLUS_MINUS'
]

# 범주형 컬럼 목록
CATEGORICAL_COLS = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_CITY', 'NICKNAME']

# ============================================================================
# 시각화 설정
# ============================================================================

# 한글 폰트 설정
KOREAN_FONTS_WINDOWS = ['Malgun Gothic', 'NanumGothic', 'NanumBarunGothic', 'Gulim', 'Batang']
KOREAN_FONT_MAC = 'AppleGothic'
KOREAN_FONT_LINUX = 'NanumGothic'

# 시각화 해상도
DPI = 300

# 색상 팔레트
COLOR_PALETTE = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#6C757D'
}

# 시각화 샘플링 설정 (대용량 데이터용)
MAX_ROWS_FOR_VISUALIZATION = 300000
MAX_ROWS_FOR_DASHBOARD = 150000

# ============================================================================
# 분석 설정
# ============================================================================

# 상관관계 분석 대상 지표
CORRELATION_COLS = [
    'PLUS_MINUS', 'PTS', 'FGM', 'FG_PCT', 'AST', 'REB', 'STL',
    'FG3M', 'MIN', 'FTA', 'FGA', 'BLK', 'TO', 'EFG_PCT', 'TS_PCT'
]

# 승/패 비교 지표
COMPARISON_METRICS = ['PTS', 'AST', 'REB', 'FG_PCT', 'STL', 'BLK', 'TO']

# KPI 지표
KPI_METRICS = ['PTS', 'AST', 'REB', 'FG_PCT', 'EFG_PCT', 'TS_PCT', 'PLUS_MINUS']

# Top N 설정
TOP_PLAYERS_COUNT = 10
TOP_TEAMS_COUNT = 8
TOP_PLAYERS_DASHBOARD = 20

# ============================================================================
# 머신러닝 설정
# ============================================================================

# 머신러닝 모델 저장 경로
ML_MODELS_DIR = os.path.join(OUTPUT_DIR, 'NBA_머신러닝_모델')

# 머신러닝 결과 저장 경로
ML_RESULTS_DIR = os.path.join(OUTPUT_DIR, 'NBA_머신러닝_결과')

# 머신러닝 모델 하이퍼파라미터
ML_RANDOM_STATE = 42
ML_TEST_SIZE = 0.2
ML_N_ESTIMATORS = 100
ML_MAX_DEPTH = 10
ML_MIN_SAMPLES_SPLIT = 5
ML_MIN_SAMPLES_LEAF = 2

# 클러스터링 설정
CLUSTERING_N_CLUSTERS = 5

# ============================================================================
# 통계 검정 설정
# ============================================================================

# 통계 검정 결과 저장 경로
STATISTICAL_TEST_DIR = os.path.join(OUTPUT_DIR, 'NBA_통계검정_결과')

# 통계 검정 유의수준
STATISTICAL_ALPHA = 0.05

# EDA 결과 저장 경로
EDA_RESULTS_DIR = os.path.join(OUTPUT_DIR, 'NBA_EDA_결과')
