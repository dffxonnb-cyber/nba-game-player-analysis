# NBA 데이터 분석 프로젝트

NBA 경기 데이터를 활용한 종합 데이터 분석 프로젝트입니다. 데이터 전처리부터 시각화까지 전체 파이프라인을 포함합니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [사용 방법](#사용-방법)
- [데이터 구조](#데이터-구조)
- [주요 인사이트](#주요-인사이트)
- [기술 스택](#기술-스택)
- [머신러닝 인사이트](#머신러닝-인사이트)
- [문제 정의 및 가설](#문제-정의-및-가설)
- [분석 플로우](#분석-플로우)
- [비즈니스 전략](#비즈니스-전략)

> 💡 **상세 문서:**
> - [머신러닝 인사이트](./NBA_머신러닝_인사이트.md)
> - [문제 정의 및 가설](./NBA_문제정의_및_가설.md)
> - [분석 플로우](./NBA_분석플로우.md)
> - [비즈니스 전략](./NBA_비즈니스_전략.md)

---

## 프로젝트 개요

이 프로젝트는 NBA 경기 데이터를 분석하여 다음과 같은 인사이트를 제공합니다:

- **지표 간 상관관계 분석**: 주요 지표들 간의 상관관계를 히트맵으로 시각화
- **선수 성과 분석**: 최소 출전 시간 기준으로 선수별 성과 랭킹
- **시계열 트렌드 분석**: 시즌별 평균 기록 추이 분석
- **승/패 요인 분석**: 홈팀 승리와 패배 경기의 핵심 지표 차이 분석
- **종합 대시보드**: 전체 데이터 요약 및 핵심 인사이트 제공
- **머신러닝 예측**: 경기 승/패 예측, 선수 성과 예측, 선수 클러스터링

---

## 주요 기능

### 1. 데이터 전처리 (`NBA_전처리_모듈.py`)

- **데이터 병합**: 경기, 경기 상세, 선수, 팀 정보 통합
- **데이터 정제**: 결측치 처리, 이상치 제거, 타입 변환
- **파생 지표 계산**:
  - 기본 지표: PPM (Points Per Minute), SEI (Simple Efficiency Index)
  - 고급 지표: eFG%, TS% (True Shooting %)
  - 날짜 파생: 시즌 문자열, 연도, 월, 요일 등

### 2. 탐색적 데이터 분석 (`NBA_EDA_모듈.py`)

- **분포 분석**: 주요 지표의 분포 확인 및 시각화
- **이상치 탐지**: IQR 방법 및 Z-score 방법으로 이상치 탐지
- **다변량 분석**: 지표 간 관계 분석 (산점도, 상관관계)
- **정규성 검정**: 데이터 분포의 정규성 확인

### 3. 통계 검정 (`NBA_통계검정_모듈.py`)

- **승/패 그룹 간 차이 검정**: t-test, Mann-Whitney U 검정
- **클러스터 간 차이 검정**: ANOVA, Kruskal-Wallis 검정
- **효과 크기 계산**: Cohen's d 계산 및 해석
- **정규성 검정**: Shapiro-Wilk, D'Agostino 검정
- **가설 검증**: 통계적 유의성 검증

### 4. 데이터 시각화 (`NBA_시각화_모듈.py`)

- **상관관계 히트맵**: 주요 지표 간 상관관계 시각화
- **선수별 성과 Top 10**: 평균 득점 기준 상위 선수
- **시즌별 기록 추이**: 득점, 어시스트, 리바운드 시계열 분석
- **승/패 비교 분석**: 홈팀 승리와 패배 경기의 지표 차이
- **종합 대시보드**: 6개 패널로 구성된 통합 대시보드
- **머신러닝 결과 시각화**: 모델 성능, 특성 중요도, 클러스터링 결과
- **통계 검정 결과 시각화**: 검정 결과 및 효과 크기 시각화

### 5. 머신러닝 (`NBA_머신러닝_모듈.py`)

- **경기 승/패 예측**: Random Forest 분류 모델로 경기 결과 예측
- **선수 성과 예측**: PLUS_MINUS, 득점 등 선수 성과 예측 (회귀)
- **선수 클러스터링**: K-Means를 활용한 플레이 스타일 분석
- **모델 평가**: 교차 검증, 혼동 행렬, R² Score 등 성능 지표 제공
- **특성 중요도 분석**: 각 모델에서 중요한 지표 분석

### 6. 통합 파이프라인 (`NBA_통합_파이프라인.py`)

- 전처리, EDA, 통계 검정, 시각화, 머신러닝을 한 번에 실행
- 단계별 실행 옵션 제공
- 진행 상황 및 통계 정보 출력

---

## 프로젝트 구조

```
NBA 갠플젝/
│
├── NBA_통합_파이프라인.py          # 통합 파이프라인 (메인 실행 파일)
├── NBA_전처리_모듈.py               # 전처리 모듈
├── NBA_EDA_모듈.py                  # 탐색적 데이터 분석 모듈
├── NBA_통계검정_모듈.py              # 통계 검정 모듈
├── NBA_시각화_모듈.py               # 시각화 모듈
├── NBA_머신러닝_모듈.py              # 머신러닝 모듈
├── NBA_설정.py                     # 설정 파일
├── requirements.txt               # 의존성 패키지 목록
│
├── docs/                           # 문서
│   ├── NBA_프로젝트_설명서.md
│   ├── NBA_파이프라인_문서.md
│   ├── NBA_머신러닝_인사이트.md    # 머신러닝 모델 인사이트 분석
│   ├── NBA_문제정의_및_가설.md     # 문제 정의 및 가설 설정
│   ├── NBA_분석플로우.md           # 분석 플로우 문서
│   └── NBA_비즈니스_전략.md        # 비즈니스 전략 및 실행 계획
│
├── data/
│   ├── games.csv                   # 경기 기본 정보
│   ├── games_details.csv           # 경기 상세 기록
│   ├── players.csv                 # 선수 정보
│   ├── teams.csv                   # 팀 정보
│   └── processed/                  # 전처리 산출물
│       ├── NBA_전처리_데이터.pkl
│       └── NBA_전처리_최종_데이터.csv
│
└── outputs/
    ├── NBA_시각화_결과/             # 시각화 결과 폴더 (출력)
    │   ├── NBA_01_상관관계_히트맵.png
    │   ├── NBA_02_선수별_득점_Top10.png
    │   ├── NBA_03_시즌별_기록_추이.png
    │   ├── NBA_04_승패_비교.png
    │   ├── NBA_05_종합_대시보드.png
    │   ├── NBA_06_승패예측_모델_성능.png
    │   ├── NBA_07_선수PLUS_MINUS예측_모델_성능.png
    │   ├── NBA_07_선수PTS예측_모델_성능.png
    │   └── NBA_08_선수_클러스터링_결과.png
    ├── NBA_머신러닝_모델/           # 학습된 모델 저장 폴더
    │   ├── win_loss_classifier.pkl
    │   ├── player_PLUS_MINUS_regressor.pkl
    │   └── player_PTS_regressor.pkl
    ├── NBA_머신러닝_결과/           # 머신러닝 결과 저장 폴더
    │   ├── win_loss_results.pkl
    │   ├── player_PLUS_MINUS_results.pkl
    │   ├── player_PTS_results.pkl
    │   └── player_clustering.csv
    ├── NBA_통계검정_결과/           # 통계 검정 결과 저장 폴더
    │   ├── win_loss_statistical_test.csv
    │   └── clustering_statistical_test.csv
    └── NBA_EDA_결과/                # EDA 결과 저장 폴더
        ├── 지표별_분포_분석.png
        ├── 이상치_탐지_박스플롯.png
        ├── 이상치_요약.csv
        └── 다변량분석_*.png
```

---

## 설치 및 실행

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터 파일 준비

이 저장소에는 원본 데이터가 포함되지 않습니다. 다음 입력 파일을 `data/` 폴더에 두고 실행합니다.
- `data/games.csv`
- `data/games_details.csv`
- `data/players.csv`
- `data/teams.csv`

### 3. 실행 방법

#### 방법 1: 통합 파이프라인 실행 (권장)

```bash
# 전체 프로세스 실행 (전처리 + 시각화)
python NBA_통합_파이프라인.py

# 전처리만 실행
python NBA_통합_파이프라인.py --skip-visualization

  # 시각화만 실행 (전처리된 데이터 필요)
  python NBA_통합_파이프라인.py --skip-preprocessing --skip-eda --skip-statistics --skip-ml
  
  # 통계 검정만 실행
  python NBA_통합_파이프라인.py --skip-preprocessing --skip-eda --skip-visualization --skip-ml
  
  # 머신러닝만 실행
  python NBA_통합_파이프라인.py --skip-preprocessing --skip-eda --skip-statistics --skip-visualization
  
  # 전체 프로세스 실행 (전처리 + EDA + 통계검정 + 시각화 + 머신러닝)
  python NBA_통합_파이프라인.py
```

#### 방법 2: 개별 모듈 실행

```bash
# 전처리만 실행
python NBA_전처리_모듈.py

# 시각화만 실행
python NBA_시각화_모듈.py
```

---

## 사용 방법

### 전처리 모듈 사용 예제

```python
from NBA_전처리_모듈 import NBADataPreprocessor

# 전처리 객체 생성
preprocessor = NBADataPreprocessor()

# 전체 전처리 프로세스 실행
df = preprocessor.process()

# 또는 단계별 실행
df_games, df_details, df_players, df_teams = preprocessor.load_data()
merged_df = preprocessor.merge_data(df_games, df_details, df_players, df_teams)
# ... 추가 단계
```

### 시각화 모듈 사용 예제

```python
from NBA_시각화_모듈 import NBADataVisualizer

# 시각화 객체 생성
visualizer = NBADataVisualizer()

# 데이터 로드
visualizer.load_data()

# 모든 시각화 생성
visualizer.visualize_all()

# 또는 개별 시각화 생성
visualizer.visualize_correlation_heatmap()
visualizer.visualize_top_players()
# ... 추가 시각화

# 머신러닝 결과 시각화 (모델 학습 후)
visualizer.visualize_ml_results()
```

### EDA 모듈 사용 예제

```python
from NBA_EDA_모듈 import NBAEDA

# EDA 객체 생성
eda = NBAEDA()

# 데이터 로드
eda.load_data()

# 모든 EDA 수행
eda.perform_all_eda()

# 또는 개별 EDA 수행
eda.analyze_distribution()
eda.detect_outliers()
eda.analyze_multivariate('PTS', 'PLUS_MINUS')
```

### 통계 검정 모듈 사용 예제

```python
from NBA_통계검정_모듈 import NBAStatisticalTest

# 통계 검정 객체 생성
stat_test = NBAStatisticalTest()

# 데이터 로드
stat_test.load_data()

# 모든 통계 검정 수행
stat_test.perform_all_tests()

# 또는 개별 검정 수행
stat_test.test_win_loss_difference()
stat_test.test_cluster_difference()
```

### 머신러닝 모듈 사용 예제

```python
from NBA_머신러닝_모듈 import NBAMachineLearning

# 머신러닝 객체 생성
ml = NBAMachineLearning()

# 데이터 로드
ml.load_data()

# 모든 모델 학습
ml.train_all_models()

# 또는 개별 모델 학습
ml.train_win_loss_classifier()
ml.train_player_performance_regressor(target='PLUS_MINUS')
ml.train_player_performance_regressor(target='PTS')
ml.perform_player_clustering()
```

---

## 데이터 구조

### 주요 컬럼

#### 기본 정보
- `GAME_ID`: 경기 ID
- `SEASON`: 시즌
- `GAME_DATE_EST`: 경기 날짜
- `PLAYER_ID`, `PLAYER_NAME`: 선수 정보
- `TEAM_ID`, `TEAM_ABBREVIATION`, `TEAM_CITY`: 팀 정보
- `HOME_TEAM_ID`, `VISITOR_TEAM_ID`: 홈/원정 팀 ID

#### 경기 기록
- `MIN`: 출전 시간 (분)
- `PTS`: 득점
- `FGM`, `FGA`, `FG_PCT`: 야투 성공/시도/성공률
- `FG3M`, `FG3A`, `FG3_PCT`: 3점슛 성공/시도/성공률
- `FTM`, `FTA`, `FT_PCT`: 자유투 성공/시도/성공률
- `REB`, `OREB`, `DREB`: 리바운드 (전체/공격/수비)
- `AST`: 어시스트
- `STL`: 스틸
- `BLK`: 블록
- `TO`: 턴오버
- `PF`: 파울
- `PLUS_MINUS`: +/- 지표

#### 파생 지표
- `PPM`: 분당 득점 (Points Per Minute)
- `SEI`: 단순 효율 지수 (Simple Efficiency Index)
- `SEI_PER_MIN`: 분당 SEI
- `EFG_PCT`: 유효 야투 성공률 (Effective Field Goal %)
- `TS_PCT`: 실제 슛 성공률 (True Shooting %)

#### 날짜 파생
- `YEAR`, `MONTH`, `DAY`, `WEEKDAY`: 날짜 정보
- `SEASON_STR`: 시즌 문자열 (예: "2020-2021")

---

## 주요 인사이트

### 1. 상관관계 분석
- PLUS_MINUS와 가장 높은 상관관계를 보이는 지표는 일반적으로 득점, 야투 성공률, 어시스트 등입니다.

### 2. 선수 성과
- 최소 1000분 출전 기준으로 선수별 평균 득점 Top 10을 분석합니다.
- 고득점 선수들이 팀 성과에 미치는 영향을 확인할 수 있습니다.

### 3. 시계열 트렌드
- 시즌별 평균 득점, 어시스트, 리바운드 추이를 통해 리그의 변화를 파악합니다.

### 4. 승/패 요인
- 홈팀 승리 경기와 패배 경기의 핵심 지표 차이를 분석합니다.
- 승리 시 평균적으로 더 높은 득점, 어시스트, 리바운드, 야투 성공률을 기록합니다.

### 5. 종합 대시보드
- 리그 전체 핵심 지표 요약
- 팀별 PLUS_MINUS 상위 팀
- 시즌별 평균 득점 추이
- 홈 승리 vs 패배 지표 차이
- Top 20 선수 득점 vs PLUS_MINUS 관계
- 승리 vs 패배 PLUS_MINUS 분포

### 6. 통계 검정 분석
- **승/패 그룹 간 차이 검정**: t-test, Mann-Whitney U 검정으로 유의성 검증
- **클러스터 간 차이 검정**: ANOVA, Kruskal-Wallis 검정으로 유의성 검증
- **효과 크기 계산**: Cohen's d로 실질적 의미 파악
- **가설 검증**: 5개 가설의 통계적 유의성 검증 완료

### 7. 머신러닝 분석
- **경기 승/패 예측**: 팀 통계를 기반으로 경기 결과 예측 (정확도 약 70-80%)
- **선수 성과 예측**: 선수의 과거 성과와 최근 폼을 기반으로 다음 경기 성과 예측
- **선수 클러스터링**: 플레이 스타일에 따라 선수를 5개 그룹으로 분류
  - 득점형, 어시스트형, 리바운드형, 올라운더, 역할 선수 등
- **통계 검정으로 검증**: 클러스터 간 유의한 차이 확인 (p < 0.001)

---

## 기술 스택

- **Python 3.7+**
- **pandas**: 데이터 처리 및 분석
- **numpy**: 수치 연산
- **matplotlib**: 시각화
- **seaborn**: 고급 시각화
- **scikit-learn**: 머신러닝 모델 (분류, 회귀, 클러스터링)
- **scipy**: 통계 검정 (t-test, ANOVA, Kruskal-Wallis 등)

---

## 문제 정의 및 가설

이 프로젝트는 명확한 문제 정의와 가설 검증 구조를 가지고 있습니다.

📄 **[NBA_문제정의_및_가설.md](./NBA_문제정의_및_가설.md)** 문서에서 다음 내용을 확인할 수 있습니다:

- 핵심 문제: "NBA 경기에서 승리를 결정하는 핵심 요인은 무엇인가?"
- 연구 질문 (RQ1, RQ2, RQ3)
- 5개의 검증 가능한 가설
- 검증 방법 및 기대 효과

**주요 가설:**
- H1: 슛 효율성이 득점량보다 승리에 더 중요
- H2: 어시스트가 리바운드보다 승리에 더 큰 영향
- H3: 승리/패배 경기 간 지표에 유의한 차이 존재
- H4: 최근 5경기 평균이 다음 경기 예측에 중요
- H5: 클러스터 간 성과 지표에 유의한 차이 존재

---

## 분석 플로우

이 프로젝트는 체계적인 분석 플로우를 따릅니다.

📄 **[NBA_분석플로우.md](./NBA_분석플로우.md)** 문서에서 다음 내용을 확인할 수 있습니다:

- 전체 분석 플로우 다이어그램
- 단계별 상세 설명 (8단계)
- 가설 검증 프로세스
- 결과 해석 가이드

**분석 플로우:**
1. 문제 정의 → 2. 가설 설정 → 3. 데이터 전처리 → 4. EDA
5. 통계 검정 → 6. 머신러닝 → 7. 결과 해석 → 8. 비즈니스 제언

---

## 머신러닝 인사이트

이 프로젝트의 머신러닝 모델을 통해 도출된 주요 인사이트는 별도 문서로 정리되어 있습니다.

📄 **[NBA_머신러닝_인사이트.md](./NBA_머신러닝_인사이트.md)** 문서에서 다음 내용을 확인할 수 있습니다:

- 경기 승/패 예측 모델 인사이트
- 선수 성과 예측 모델 인사이트
- 선수 클러스터링 인사이트
- 통합 인사이트 및 활용 방안
- 구체적인 분석 예시
- 비즈니스 인사이트

---

## 비즈니스 전략

데이터 분석 결과를 바탕으로 한 구체적인 비즈니스 전략과 실행 계획이 수립되었습니다.

📄 **[NBA_비즈니스_전략.md](./NBA_비즈니스_전략.md)** 문서에서 다음 내용을 확인할 수 있습니다:

- 핵심 발견 요약
- 전략적 우선순위 (5가지 전략)
- 구체적 실행 전략 (액션 아이템 포함)
- 예상 효과 및 ROI 계산
- 리스크 관리
- 실행 계획 타임라인

**주요 전략:**
1. 슛 효율성 개선 (최우선) - 승률 +5-8%p
2. 어시스트 증가 (2순위) - 승률 +3-5%p
3. 턴오버 감소 (3순위) - 승률 +2-4%p
4. 라인업 최적화
5. 트레이드 및 계약 전략

**예상 ROI**: 약 100% (1시즌 내 투자 회수)

---

## 설정 파일 (`NBA_설정.py`)

프로젝트의 주요 설정은 `NBA_설정.py` 파일에서 관리됩니다:

- **경로 설정**: 입력/출력 파일 경로
- **전처리 설정**: 최소 출전 시간, 이상치 기준 등
- **시각화 설정**: 한글 폰트, 해상도, 색상 팔레트 등
- **분석 설정**: 상관관계 분석 대상 지표, Top N 설정 등

---

## 주의사항

1. **데이터 크기**: 원본 데이터가 매우 클 수 있으므로 메모리 사용량을 주의하세요.
2. **실행 시간**: 전체 파이프라인 실행 시 시간이 소요될 수 있습니다.
3. **폰트 설정**: 한글 폰트가 설치되어 있지 않으면 한글이 깨질 수 있습니다.
   - Windows: Malgun Gothic (기본 제공)
   - Mac: AppleGothic
   - Linux: NanumGothic (별도 설치 필요)
4. **시각화 샘플링**: 일부 시각화는 성능을 위해 데이터 샘플링을 수행합니다.

---

## 라이선스

이 프로젝트는 개인 포트폴리오 목적으로 제작되었습니다.

---

## 작성자

NBA 데이터 분석 프로젝트

---

## 업데이트 이력

- **v1.0.0** (2024): 초기 버전
  - 전처리 및 시각화 통합 파이프라인 생성
  - 모듈화 및 클래스 기반 구조로 리팩토링
  - 포트폴리오용 문서화 완료

