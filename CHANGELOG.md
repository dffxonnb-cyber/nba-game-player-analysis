# Changelog

## 2026-04-17

- [docs/README.md](./docs/README.md) 추가로 공개 저장소 기준 검토 순서와 대표 자산 경로를 인덱싱
- [scripts/check_public_artifacts.py](./scripts/check_public_artifacts.py) 추가로 README, 핵심 문서, 대표 PNG 산출물 존재 여부를 자동 검증
- [tests/test_nba_smoke.py](./tests/test_nba_smoke.py) 추가로 전처리 시간 변환과 머신러닝 준비 단계의 synthetic dataframe 기반 smoke test를 도입
- [.github/workflows/verify.yml](./.github/workflows/verify.yml) 추가로 public artifact check와 smoke test를 GitHub Actions에 연결

## 2026-03-23

- README를 `재현 범위`, `분석 가치`, `검증 수치`, `엔지니어링 신호` 중심으로 재정리
- [docs/reproducibility_and_validation.md](./docs/reproducibility_and_validation.md) 추가
- 공개 데이터 다운로드 전제와 문서 기준 검증 수치를 첫 화면에서 바로 보이도록 정리
