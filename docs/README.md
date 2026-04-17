# 문서 인덱스

이 폴더는 `nba-game-player-analysis`를 공개 저장소 기준으로 빠르게 검토할 수 있도록 정리한 인덱스입니다.

## 먼저 보는 순서

1. [../README.md](../README.md)
2. [reproducibility_and_validation.md](./reproducibility_and_validation.md)
3. [NBA_머신러닝_인사이트.md](./NBA_머신러닝_인사이트.md)
4. [NBA_프로젝트_설명서.md](./NBA_프로젝트_설명서.md)

## Public Review 경로

원본 Kaggle CSV를 아직 내려받지 않아도 아래 자산만으로 핵심 문제, 결과, 예측 성능을 먼저 읽을 수 있습니다.

| 자산 | 역할 |
|------|------|
| [../outputs/NBA_시각화_결과/07_대시보드/NBA_05_종합_대시보드.png](../outputs/NBA_시각화_결과/07_대시보드/NBA_05_종합_대시보드.png) | 주요 KPI와 분석 결과를 한 화면에서 확인 |
| [../outputs/NBA_시각화_결과/02_히트맵_상관_비교/NBA_01_상관관계_히트맵.png](../outputs/NBA_시각화_결과/02_히트맵_상관_비교/NBA_01_상관관계_히트맵.png) | 승리 요인 해석의 핵심 상관 구조 |
| [../outputs/NBA_시각화_결과/00_기타/NBA_06_승패예측_모델_성능.png](../outputs/NBA_시각화_결과/00_기타/NBA_06_승패예측_모델_성능.png) | 분류 모델 성능 요약 |
| [../outputs/NBA_시각화_결과/00_기타/NBA_07_선수PLUS_MINUS예측_모델_성능.png](../outputs/NBA_시각화_결과/00_기타/NBA_07_선수PLUS_MINUS예측_모델_성능.png) | 선수 성과 회귀 모델 검토 |
| [NBA_머신러닝_인사이트.md](./NBA_머신러닝_인사이트.md) | 성능 수치와 해석 맥락 |
| [reproducibility_and_validation.md](./reproducibility_and_validation.md) | 데이터 준비와 검증 범위 확인 |

## 문서 역할

| 문서 | 용도 |
|------|------|
| [reproducibility_and_validation.md](./reproducibility_and_validation.md) | 데이터 다운로드 전제, 재현 범위, 검증 포인트 |
| [NBA_머신러닝_인사이트.md](./NBA_머신러닝_인사이트.md) | 예측/군집 결과 해석 |
| [NBA_분석플로우.md](./NBA_분석플로우.md) | 분석 단계 흐름 정리 |
| [NBA_프로젝트_설명서.md](./NBA_프로젝트_설명서.md) | 프로젝트 전체 구조와 산출물 설명 |
| [NBA_비즈니스_전략.md](./NBA_비즈니스_전략.md) | 전술/스카우팅 관점 활용 해석 |

## 참고

- 공개 저장소에는 원본 Kaggle CSV가 포함되지 않습니다.
- 대신 문서, 대표 시각화, smoke test를 통해 공개 상태에서도 핵심 결과와 코드 구조를 먼저 검토할 수 있게 구성했습니다.
