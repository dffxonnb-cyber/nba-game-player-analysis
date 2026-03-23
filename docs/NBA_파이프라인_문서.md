# NBA 데이터 전처리 및 시각화 파이프라인

## 📋 목차

1. [개요](#개요)
2. [데이터 소스](#데이터-소스)
3. [전처리 프로세스](#전처리-프로세스)
4. [시각화 프로세스](#시각화-프로세스)
5. [출력 파일](#출력-파일)
6. [실행 방법](#실행-방법)

---

## 개요

이 파이프라인은 NBA 경기 데이터를 전처리하고 시각화하는 전체 프로세스를 포함합니다.

**주요 단계:**
- 원본 CSV 데이터 로드 및 병합
- 데이터 정제 및 파생 지표 계산
- 8가지 핵심 시각화 생성

---

## 데이터 소스

### 입력 파일
- `data/games.csv` - 경기 기본 정보
- `data/games_details.csv` - 경기 상세 기록
- `data/players.csv` - 선수 정보
- `data/teams.csv` - 팀 정보

### 출력 파일
- `data/processed/NBA_전처리_데이터.pkl` - 전처리된 데이터 (Pickle 형식)
- `data/processed/NBA_전처리_최종_데이터.csv` - 전처리된 데이터 (CSV 형식)
- `outputs/NBA_시각화_결과/` - 시각화 이미지 폴더

---

## 전처리 프로세스

### 1. 데이터 병합

#### 1.1 경기 상세 + 경기 기본 정보
- `games_details`와 `games` 테이블을 `GAME_ID`로 병합
- 추가 컬럼: `SEASON`, `GAME_DATE_EST`, `HOME_TEAM_ID`, `VISITOR_TEAM_ID`

#### 1.2 선수 정보 병합
- `players` 테이블과 병합하여 `PLAYER_NAME` 추가
- 중복 컬럼 처리 (`PLAYER_NAME_OLD`, `PLAYER_NAME_NEW` 정리)

#### 1.3 팀 정보 병합
- `teams` 테이블과 병합하여 `TEAM_ABBREVIATION`, `TEAM_CITY` 추가
- 중복 컬럼 처리

### 2. 데이터 변환

#### 2.1 MIN 컬럼 변환
- 형식: `MM:SS` → `float` (분 단위)
- 예: `"35:30"` → `35.5`

#### 2.2 날짜 타입 변환
- `GAME_DATE_EST` → `datetime` 형식으로 변환

### 3. 결측치 처리

#### 3.1 숫자형 컬럼
- 결측치 → `0`으로 채움
- 대상 컬럼: `MIN`, `FGM`, `FGA`, `FG_PCT`, `FG3M`, `FG3A`, `FG3_PCT`, `FTM`, `FTA`, `FT_PCT`, `OREB`, `DREB`, `REB`, `AST`, `STL`, `BLK`, `TO`, `PF`, `PTS`, `PLUS_MINUS`

#### 3.2 범주형 컬럼
- 결측치 → `'UNKNOWN'`으로 채움
- 대상 컬럼: `PLAYER_NAME`, `TEAM_ABBREVIATION`, `TEAM_CITY`, `NICKNAME`

#### 3.3 특수 처리
- `PLUS_MINUS`가 없는 행 제거
- `START_POSITION` 결측치 → `'BENCH'`로 채움
- `COMMENT` 컬럼 제거

### 4. 이상치 제거

#### 4.1 MIN 관련
- `MIN < 0` 제거
- `MIN > 60` 제거 (60분 초과 이상치)

#### 4.2 무기록 행 제거
- 조건: `MIN > 0` AND (`FGA > 0` OR `FTA > 0` OR `REB > 0`)
- 출전했지만 기록이 전혀 없는 행 제거

### 5. 파생 지표 계산

#### 5.1 기본 파생 지표
- **PPM** (Points Per Minute): `PTS / MIN`
- **SEI** (Simple Efficiency Index): 
  ```
  (PTS + REB + AST + STL + BLK) - (TO + (FGA - FGM))
  ```
- **SEI_PER_MIN**: `SEI / MIN`

#### 5.2 고급 파생 지표
- **EFG_PCT** (Effective Field Goal %): 
  ```
  (FGM + 0.5 * FG3M) / FGA
  ```
- **TS_PCT** (True Shooting %): 
  ```
  PTS / (2 * (FGA + 0.44 * FTA))
  ```
- **USG_PROX** (Usage Rate Proxy): 
  ```
  (FGA + 0.44 * FTA + TO) / MIN
  ```
- **ORB_PCT_PROX**: `OREB / MIN`
- **DRB_PCT_PROX**: `DREB / MIN`
- **PIE_PROX** (Player Impact Estimate Proxy)
- **PER_PROX** (Player Efficiency Rating Proxy)

#### 5.3 성공률 재계산
- **FG_PCT**: `FGM / FGA` (FGA > 0일 때만)
- **FG3_PCT**: `FG3M / FG3A` (FG3A > 0일 때만)
- **FT_PCT**: `FTM / FTA` (FTA > 0일 때만)

### 6. 날짜 파생 컬럼

- `YEAR`: 연도
- `MONTH`: 월
- `DAY`: 일
- `WEEKDAY`: 요일 (0=월요일, 6=일요일)
- `SEASON_STR`: 시즌 문자열 (예: "2020-2021")

### 7. 전처리 통계 출력

#### 7.1 홈팀 승/패 비교
- 승리 경기와 패배 경기의 평균 지표 비교
- 비교 지표: `PTS`, `AST`, `REB`, `FG_PCT`

#### 7.2 PLUS_MINUS 상관관계
- PLUS_MINUS와 상관관계가 높은 지표 Top 10 출력

#### 7.3 선수별 SEI 통계
- 최소 1000분 출전 선수 기준
- SEI/M Top 10 및 Bottom 10 출력

---

## 시각화 프로세스

### 설정

#### 한글 폰트 설정
- Windows: `Malgun Gothic`, `NanumGothic` 등 자동 감지
- Mac: `AppleGothic`
- Linux: `NanumGothic`
- 마이너스 기호 깨짐 방지 설정

#### 색상 팔레트
- 파스텔 톤 색상 사용
- 시각화별 색상 매핑 정의

### 시각화 목록

#### 1. 상관관계 히트맵
- **파일명**: `1_상관관계_히트맵.png`
- **내용**: 주요 지표 간 상관관계 매트릭스
- **지표**: `PLUS_MINUS`, `PTS`, `FGM`, `FG_PCT`, `AST`, `REB`, `STL`, `FG3M`, `MIN`, `FTA`, `FGA`, `BLK`, `TO`, `EFG_PCT`, `TS_PCT`
- **색상맵**: `RdBu_r` (빨강-파랑 역순)

#### 2. PLUS_MINUS 상관관계 Top 10
- **파일명**: `1_PLUS_MINUS_상관관계.png`
- **내용**: PLUS_MINUS와 상관관계가 높은 지표 Top 10
- **형식**: 수평 막대 그래프
- **색상**: 파란색 그라데이션

#### 3. 선수별 평균 득점 Top 10
- **파일명**: `2_선수별_득점_Top10.png`
- **내용**: 최소 1000분 출전 선수 중 평균 득점 Top 10
- **형식**: 수평 막대 그래프
- **색상**: 파란색 팔레트

#### 4. 시즌별 평균 기록 추이
- **파일명**: `3_시즌별_기록_추이.png`
- **내용**: 시즌별 평균 득점, 어시스트, 리바운드 추이
- **형식**: 선 그래프 (3개 지표)
- **색상**: 빨강(득점), 파랑(어시스트), 초록(리바운드)

#### 5. 홈팀 승/패 핵심 지표 비교
- **파일명**: `4_승패_비교.png`
- **내용**: 홈팀 승리 경기 vs 패배 경기의 지표 비교
- **지표**: `PTS`, `AST`, `REB`, `FG_PCT`, `STL`, `BLK`, `TO`
- **형식**: 그룹 막대 그래프

#### 6. 종합 대시보드
- **파일명**: `5_종합_대시보드.png`
- **내용**: 6개 패널로 구성된 종합 대시보드
  - 리그 전체 핵심 지표 요약 (KPI)
  - 팀별 PLUS_MINUS 상위 8팀
  - 시즌별 평균 득점 추이
  - 홈 승리 vs 패배 지표 차이
  - Top 20 선수 득점 vs PLUS_MINUS 스캐터
  - 승리 vs 패배 PLUS_MINUS 분포 (KDE)

#### 7. 득점 vs PLUS_MINUS 스캐터 플롯
- **파일명**: `6_지표_관계_스캐터.png`
- **내용**: 선수별 평균 득점과 평균 PLUS_MINUS의 관계
- **조건**: 최소 1000분 출전 선수
- **형식**: 스캐터 플롯 (색상: 득점 값)

#### 8. 승/패 PLUS_MINUS 분포
- **파일명**: `7_승패_PLUS_MINUS_분포.png`
- **내용**: 승리 경기와 패배 경기의 PLUS_MINUS 분포 비교
- **형식**: 히스토그램 + KDE (밀도 추정)
- **샘플링**: 데이터가 30만 행 초과 시 샘플링

---

## 출력 파일

### 전처리 결과
- `data/processed/NBA_전처리_데이터.pkl`: 전처리된 데이터 (Pickle 형식, 빠른 로드)
- `data/processed/NBA_전처리_최종_데이터.csv`: 전처리된 데이터 (CSV 형식, 호환성)

### 시각화 결과
모든 시각화는 `outputs/NBA_시각화_결과/` 폴더에 저장됩니다.

1. `1_상관관계_히트맵.png`
2. `1_PLUS_MINUS_상관관계.png`
3. `2_선수별_득점_Top10.png`
4. `3_시즌별_기록_추이.png`
5. `4_승패_비교.png`
6. `5_종합_대시보드.png`
7. `6_지표_관계_스캐터.png`
8. `7_승패_PLUS_MINUS_분포.png`

---

## 실행 방법

### 방법 1: 통합 파이프라인 실행

```bash
python "NBA 갠플젝/NBA_통합_파이프라인.py"
```

이 스크립트는 전처리부터 시각화까지 전체 프로세스를 자동으로 실행합니다.

### 방법 2: 개별 파일 실행

#### 전처리만 실행
```bash
python "NBA 갠플젝/NBA_전처리_모듈.py"
```

#### 시각화만 실행
- 전처리된 데이터(`NBA_전처리_데이터.pkl` 또는 `NBA_전처리_최종_데이터.csv`)가 있는 경우 아래 중 하나로 실행
  - 파이썬 스크립트: `python "NBA 갠플젝/NBA_시각화_모듈.py"`
  - (선택) 노트북: Jupyter Notebook에서 `NBA_시각화_최종.ipynb` 실행

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
- `PPM`: 분당 득점
- `SEI`: 단순 효율 지수
- `SEI_PER_MIN`: 분당 SEI
- `EFG_PCT`: 유효 야투 성공률
- `TS_PCT`: 실제 슛 성공률
- `USG_PROX`: 사용률 근사치
- `ORB_PCT_PROX`, `DRB_PCT_PROX`: 공격/수비 리바운드 비율 근사치
- `PIE_PROX`, `PER_PROX`: PIE/PER 근사치

#### 날짜 파생
- `YEAR`, `MONTH`, `DAY`, `WEEKDAY`: 날짜 정보
- `SEASON_STR`: 시즌 문자열

---

## 주요 통계 및 인사이트

### 전처리 통계

#### 홈팀 승/패 비교
- 승리 경기와 패배 경기의 핵심 지표 차이 분석
- 승리 시 평균적으로 더 높은 득점, 어시스트, 리바운드, 야투 성공률 기록

#### PLUS_MINUS 상관관계
- PLUS_MINUS와 가장 높은 상관관계를 보이는 지표 확인
- 일반적으로 득점, 야투 성공률, 어시스트 등과 높은 상관관계

#### 선수별 SEI 통계
- 최소 1000분 출전 선수 기준으로 효율성 분석
- SEI/M 기준 Top 10 및 Bottom 10 선수 확인

### 시각화 인사이트

1. **상관관계 분석**: 지표 간 관계 파악
2. **선수 성과**: 최고 성과 선수 식별
3. **시계열 트렌드**: 시즌별 변화 추이 분석
4. **승/패 요인**: 승리와 패배의 핵심 차이점
5. **종합 분석**: 전체적인 데이터 요약 및 인사이트

---

## 주의사항

1. **데이터 크기**: 원본 데이터가 매우 클 수 있으므로 메모리 사용량 주의
2. **실행 시간**: 전체 파이프라인 실행 시 시간이 소요될 수 있음
3. **폰트 설정**: 한글 폰트가 설치되어 있지 않으면 한글이 깨질 수 있음
4. **시각화 샘플링**: 일부 시각화는 성능을 위해 데이터 샘플링을 수행함

---

## 기술 스택

- **Python 3.x**
- **pandas**: 데이터 처리
- **numpy**: 수치 연산
- **matplotlib**: 시각화
- **seaborn**: 고급 시각화

---

## 업데이트 이력

- 초기 버전: 전처리 및 시각화 통합 파이프라인 생성

