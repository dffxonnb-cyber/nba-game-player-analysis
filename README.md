# alone_NBA – NBA 경기·선수 분석

NBA 공개 데이터셋을 활용해 경기 승리 요인, 선수 성과 예측, 플레이 스타일 군집을 분석한 프로젝트입니다.

## 개요

- **목적**: 경기 승리 요인 분석, 선수 성과 예측·분류, 플레이 스타일 클러스터링
- **기능**: 전처리, EDA, 통계 검정, 머신러닝(Random Forest·K-Means), 시각화
- **저장소 정책**: 원본 데이터와 대용량 전처리 산출물은 GitHub에 포함하지 않음

## 대표 이미지

### 종합 대시보드

![NBA 종합 대시보드](./outputs/NBA_시각화_결과/07_대시보드/NBA_05_종합_대시보드.png)

### 상관관계 히트맵

![NBA 상관관계 히트맵](./outputs/NBA_시각화_결과/02_히트맵_상관_비교/NBA_01_상관관계_히트맵.png)

## 데이터

이 저장소에는 원본 CSV와 대용량 전처리 결과를 포함하지 않습니다.

코드는 아래 파일이 `data/` 폴더에 있다고 가정합니다.

- `data/games.csv`
- `data/games_details.csv`
- `data/players.csv`
- `data/teams.csv`

전처리 실행 후 아래 산출물이 로컬에 생성됩니다.

- `data/processed/NBA_전처리_데이터.pkl`
- `data/processed/NBA_전처리_최종_데이터.csv`

### 데이터셋 출처

- **NBA Games (Kaggle)**  
  [NBA Games - Nathan Lauga (Kaggle)](https://www.kaggle.com/datasets/nathanlauga/nba-games/data)  
  필요한 CSV를 다운로드한 뒤 `data/` 폴더에 배치하고 파이프라인을 실행하면 됩니다.

## 실행

```bash
pip install -r requirements.txt
python NBA_통합_파이프라인.py
```

단계별 생략: `--skip-preprocessing`, `--skip-eda`, `--skip-statistics`, `--skip-visualization`, `--skip-ml`

## 폴더 구조

- `docs/`: 프로젝트 설명, 분석 플로우, 머신러닝 인사이트
- `data/`: 로컬 원본 데이터와 전처리 산출물 위치
- `outputs/`: 시각화 결과, 통계 검정 결과, 머신러닝 결과
- `NBA_통합_파이프라인.py`: 전체 파이프라인 실행 스크립트

## 주요 모듈

| 모듈 | 설명 |
|------|------|
| `NBA_전처리_모듈.py` | 경기·경기상세·선수·팀 병합, MIN→분 변환, 결측·이상치 처리, 파생 지표 계산 |
| `NBA_EDA_모듈.py` | 분포·이상치(IQR·Z-score)·상관관계 히트맵·정규성 검토 |
| `NBA_통계검정_모듈.py` | 승/패 t-test·Mann-Whitney U·Cohen's d, 클러스터 간 ANOVA·Kruskal-Wallis |
| `NBA_머신러닝_모듈.py` | 경기 승/패 분류, 선수 PLUS_MINUS·PTS 회귀(LAG5 포함), K-Means 5그룹 클러스터링 |
| `NBA_시각화_모듈.py` | 상관 히트맵·선수 Top10·시즌별 추이·승패 비교·종합 대시보드 시각화 |

## 주요 인사이트

- **승리 요인**: eFG%·TS%가 PTS보다 중요하고, AST가 REB보다 설명력이 큼
- **선수 예측**: 최근 5경기(LAG5) 평균이 다음 경기 예측에 가장 중요
- **클러스터**: 득점형·플레이메이커·리바운더·올라운더·역할선수 5그룹 도출

## GitHub 업로드 기준

- 포함 권장: Python 코드, `README.md`, `docs/`, 시각화 PNG 결과
- 제외 권장: `data/*.csv`, `data/processed/*`, `outputs/**/*.pkl`, `__pycache__/`

## 상세 문서

- [docs/NBA_프로젝트_설명서.md](./docs/NBA_프로젝트_설명서.md) – 전체 개요·구조·설치
- [docs/NBA_머신러닝_인사이트.md](./docs/NBA_머신러닝_인사이트.md) – ML 인사이트
- [docs/NBA_비즈니스_전략.md](./docs/NBA_비즈니스_전략.md) – 비즈니스 전략·실행 계획
