"""
NBA 데이터 전처리 모듈

이 모듈은 NBA 경기 데이터를 로드하고, 병합하며, 정제하고, 파생 지표를 계산합니다.
"""

import os
import pandas as pd
import numpy as np
from typing import Optional, Tuple
import NBA_설정 as config


class NBADataPreprocessor:
    """
    NBA 데이터 전처리 클래스
    
    주요 기능:
    - 원본 CSV 데이터 로드 및 병합
    - 데이터 타입 변환 및 결측치 처리
    - 이상치 제거
    - 파생 지표 계산
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        초기화
        
        Args:
            base_dir: 작업 디렉토리 경로 (None이면 config에서 가져옴)
        """
        self.base_dir = base_dir or config.BASE_DIR
        self.merged_df: Optional[pd.DataFrame] = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        원본 CSV 데이터 로드
        
        Returns:
            (df_games, df_details, df_players, df_teams) 튜플
        """
        print("=" * 60)
        print("1단계: 원본 데이터 로드")
        print("=" * 60)
        
        try:
            df_games = pd.read_csv(config.GAMES_CSV)
            df_details = pd.read_csv(config.GAMES_DETAILS_CSV)
            df_players = pd.read_csv(config.PLAYERS_CSV)
            df_teams = pd.read_csv(config.TEAMS_CSV)
            
            print(f"[OK] games.csv: {len(df_games):,}행")
            print(f"[OK] games_details.csv: {len(df_details):,}행")
            print(f"[OK] players.csv: {len(df_players):,}행")
            print(f"[OK] teams.csv: {len(df_teams):,}행")
            
            return df_games, df_details, df_players, df_teams
            
        except FileNotFoundError as e:
            print(f"[ERR] 파일을 찾을 수 없습니다: {e}")
            raise
    
    def merge_data(self, df_games: pd.DataFrame, df_details: pd.DataFrame,
                   df_players: pd.DataFrame, df_teams: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 병합
        
        Args:
            df_games: 경기 기본 정보
            df_details: 경기 상세 기록
            df_players: 선수 정보
            df_teams: 팀 정보
            
        Returns:
            병합된 DataFrame
        """
        print("\n" + "=" * 60)
        print("2단계: 데이터 병합")
        print("=" * 60)
        
        # 1. 경기 상세 + 경기 기본 정보 병합
        merged_df = pd.merge(
            df_details,
            df_games[['GAME_ID', 'SEASON', 'GAME_DATE_EST', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID']],
            on='GAME_ID',
            how='left'
        )
        print(f"[OK] 경기 정보 병합 완료: {len(merged_df):,}행")
        
        # 2. 선수 이름 병합
        merged_df = pd.merge(
            merged_df,
            df_players[['PLAYER_ID', 'PLAYER_NAME']],
            on='PLAYER_ID',
            how='left',
            suffixes=('_OLD', '_NEW')
        )
        
        # 중복 컬럼 처리
        if 'PLAYER_NAME_NEW' in merged_df.columns:
            merged_df['PLAYER_NAME'] = merged_df['PLAYER_NAME_NEW']
            merged_df.drop(columns=['PLAYER_NAME_NEW', 'PLAYER_NAME_OLD'], 
                         errors='ignore', inplace=True)
        print("[OK] 선수 정보 병합 완료")
        
        # 3. 팀 정보 병합
        merged_df = pd.merge(
            merged_df,
            df_teams[['TEAM_ID', 'ABBREVIATION', 'CITY']],
            on='TEAM_ID',
            how='left',
            suffixes=('', '_TEAM_INFO')
        )
        
        # 컬럼명 명확하게 변경
        merged_df = merged_df.rename(columns={
            'ABBREVIATION': 'TEAM_ABBREVIATION',
            'CITY': 'TEAM_CITY'
        })
        
        # 중복 컬럼 처리
        clean_cols = merged_df.columns[~merged_df.columns.duplicated(keep=False)].tolist()
        cols = merged_df.columns
        
        abbr_locs = [i for i, col in enumerate(cols) if col == 'TEAM_ABBREVIATION']
        city_locs = [i for i, col in enumerate(cols) if col == 'TEAM_CITY']
        
        merged_df_final = merged_df[clean_cols].copy()
        if abbr_locs:
            merged_df_final['TEAM_ABBREVIATION'] = merged_df.iloc[:, abbr_locs[-1]]
        if city_locs:
            merged_df_final['TEAM_CITY'] = merged_df.iloc[:, city_locs[-1]]
        
        merged_df = merged_df_final
        print("[OK] 팀 정보 병합 완료")
        
        return merged_df
    
    @staticmethod
    def convert_min_to_float(min_str) -> float:
        """
        MIN 컬럼 변환 (MM:SS -> float 분)
        
        Args:
            min_str: 시간 문자열 (예: "35:30")
            
        Returns:
            분 단위 float 값
        """
        if pd.isna(min_str) or min_str is None or str(min_str).strip() == '':
            return np.nan
        min_str = str(min_str).strip()
        if ':' in min_str:
            try:
                minutes, seconds = map(int, min_str.split(':'))
                return minutes + seconds / 60
            except ValueError:
                return np.nan
        try:
            return float(min_str)
        except ValueError:
            return np.nan
    
    def transform_data(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 타입 변환
        
        Args:
            merged_df: 병합된 DataFrame
            
        Returns:
            변환된 DataFrame
        """
        print("\n" + "=" * 60)
        print("3단계: 데이터 변환")
        print("=" * 60)
        
        # MIN 컬럼 변환
        merged_df['MIN'] = merged_df['MIN'].apply(self.convert_min_to_float)
        print("[OK] MIN 컬럼 변환 완료 (MM:SS -> float 분)")
        
        # 날짜 타입 변환
        merged_df['GAME_DATE_EST'] = pd.to_datetime(merged_df['GAME_DATE_EST'])
        print("[OK] 날짜 타입 변환 완료")
        
        return merged_df
    
    def handle_missing_values(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        결측치 처리
        
        Args:
            merged_df: DataFrame
            
        Returns:
            결측치가 처리된 DataFrame
        """
        print("\n" + "=" * 60)
        print("4단계: 결측치 처리")
        print("=" * 60)
        
        # 숫자형 컬럼 결측치 처리
        existing_num_cols = [c for c in config.NUMERICAL_COLS if c in merged_df.columns]
        merged_df[existing_num_cols] = merged_df[existing_num_cols].fillna(0)
        print(f"[OK] 숫자형 컬럼 결측치 처리: {len(existing_num_cols)}개 컬럼")
        
        # 범주형 컬럼 결측치 처리
        existing_cat_cols = [c for c in config.CATEGORICAL_COLS if c in merged_df.columns]
        for col in existing_cat_cols:
            merged_df[col] = merged_df[col].fillna('UNKNOWN')
        print(f"[OK] 범주형 컬럼 결측치 처리: {len(existing_cat_cols)}개 컬럼")
        
        # PLUS_MINUS 없는 행 제거
        before_count = len(merged_df)
        merged_df.dropna(subset=['PLUS_MINUS'], inplace=True)
        after_count = len(merged_df)
        print(f"[OK] PLUS_MINUS 결측치 행 제거: {before_count - after_count:,}행")
        
        # 성공률 재채우기
        merged_df.loc[:, ['FG_PCT', 'FG3_PCT', 'FT_PCT']] = \
            merged_df[['FG_PCT', 'FG3_PCT', 'FT_PCT']].fillna(0)
        
        # START_POSITION 채우기
        if 'START_POSITION' in merged_df.columns:
            merged_df['START_POSITION'] = merged_df['START_POSITION'].fillna('BENCH')
        
        # COMMENT 컬럼 제거
        merged_df.drop(columns=['COMMENT'], errors='ignore', inplace=True)
        
        return merged_df
    
    def remove_outliers(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        이상치 제거
        
        Args:
            merged_df: DataFrame
            
        Returns:
            이상치가 제거된 DataFrame
        """
        print("\n" + "=" * 60)
        print("5단계: 이상치 제거")
        print("=" * 60)
        
        before_count = len(merged_df)
        
        # MIN < 0 제거
        merged_df = merged_df[merged_df['MIN'] >= 0].copy()
        
        # MIN > 60 제거
        merged_df = merged_df[merged_df['MIN'] <= config.MAX_MINUTES].copy()
        print(f"[OK] MIN 이상치 제거: {before_count - len(merged_df):,}행")
        
        # 무기록 행 제거
        before_count = len(merged_df)
        merged_df = merged_df[
            (merged_df['MIN'] > 0) &
            ((merged_df['FGA'] > 0) | (merged_df['FTA'] > 0) | (merged_df['REB'] > 0))
        ].copy()
        print(f"[OK] 무기록 행 제거: {before_count - len(merged_df):,}행")
        
        return merged_df
    
    def calculate_derived_metrics(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        파생 지표 계산
        
        Args:
            merged_df: DataFrame
            
        Returns:
            파생 지표가 추가된 DataFrame
        """
        print("\n" + "=" * 60)
        print("6단계: 파생 지표 계산")
        print("=" * 60)
        
        # 기본 파생 지표
        merged_df['PPM'] = merged_df['PTS'] / merged_df['MIN'].replace(0, np.nan)
        merged_df['PPM'] = merged_df['PPM'].fillna(0)
        
        merged_df['SEI'] = (
            merged_df['PTS'] + merged_df['REB'] + merged_df['AST'] + 
            merged_df['STL'] + merged_df['BLK']
        ) - (
            merged_df['TO'] + (merged_df['FGA'] - merged_df['FGM'])
        )
        
        merged_df['SEI_PER_MIN'] = merged_df['SEI'] / merged_df['MIN'].replace(0, np.nan)
        merged_df['SEI_PER_MIN'] = merged_df['SEI_PER_MIN'].fillna(0)
        print("[OK] 기본 파생 지표 계산 완료 (PPM, SEI, SEI_PER_MIN)")
        
        # 고급 파생 지표
        merged_df['EFG_PCT'] = np.where(
            merged_df['FGA'] > 0,
            (merged_df['FGM'] + 0.5 * merged_df['FG3M']) / merged_df['FGA'],
            0
        )
        
        merged_df['TS_PCT'] = np.where(
            (merged_df['FGA'] + 0.44 * merged_df['FTA']) > 0,
            merged_df['PTS'] / (2 * (merged_df['FGA'] + 0.44 * merged_df['FTA'])),
            0
        )
        print("[OK] 고급 파생 지표 계산 완료 (EFG_PCT, TS_PCT)")
        
        # 성공률 재계산
        merged_df['FG_PCT'] = np.where(
            merged_df['FGA'] > 0,
            merged_df['FGM'] / merged_df['FGA'],
            0
        )
        merged_df['FG3_PCT'] = np.where(
            merged_df['FG3A'] > 0,
            merged_df['FG3M'] / merged_df['FG3A'],
            0
        )
        merged_df['FT_PCT'] = np.where(
            merged_df['FTA'] > 0,
            merged_df['FTM'] / merged_df['FTA'],
            0
        )
        print("[OK] 성공률 재계산 완료")
        
        # 날짜 파생 컬럼
        merged_df['YEAR'] = merged_df['GAME_DATE_EST'].dt.year
        merged_df['MONTH'] = merged_df['GAME_DATE_EST'].dt.month
        merged_df['DAY'] = merged_df['GAME_DATE_EST'].dt.day
        merged_df['WEEKDAY'] = merged_df['GAME_DATE_EST'].dt.weekday
        
        # 시즌 문자열 생성
        merged_df['SEASON_STR'] = merged_df['GAME_DATE_EST'].apply(
            lambda x: None if pd.isna(x) else (
                f"{x.year}-{x.year + 1}" if x.month >= 10 
                else f"{x.year - 1}-{x.year}"
            )
        )
        print("[OK] 날짜 파생 컬럼 생성 완료")
        
        return merged_df
    
    def print_statistics(self, merged_df: pd.DataFrame):
        """
        전처리 통계 출력
        
        Args:
            merged_df: 전처리된 DataFrame
        """
        print("\n" + "=" * 60)
        print("7단계: 전처리 통계")
        print("=" * 60)
        
        # 홈팀 승/패 비교
        home_mask = merged_df['HOME_TEAM_ID'] == merged_df['TEAM_ID']
        home_df = merged_df[home_mask].copy()
        
        win_stats = home_df[home_df['PLUS_MINUS'] > 0][['PTS', 'AST', 'REB', 'FG_PCT']].mean()
        loss_stats = home_df[home_df['PLUS_MINUS'] <= 0][['PTS', 'AST', 'REB', 'FG_PCT']].mean()
        
        comparison_df = pd.DataFrame({
            '승리_평균': win_stats,
            '패배_평균': loss_stats
        })
        comparison_df['차이'] = comparison_df['승리_평균'] - comparison_df['패배_평균']
        
        print("\n[홈팀 승/패 핵심 지표 비교]")
        print(comparison_df.round(2))
        
        # PLUS_MINUS 상관관계
        corr_cols = [c for c in config.CORRELATION_COLS if c in merged_df.columns]
        if len(corr_cols) > 1:
            corr_matrix = merged_df[corr_cols].corr()
            plus_corr = corr_matrix['PLUS_MINUS'].sort_values(ascending=False).drop('PLUS_MINUS')
            
            print("\n[PLUS_MINUS 상관관계 Top 10]")
            print(plus_corr.head(10).round(3))
        
        # 선수별 SEI 통계
        player_sei_stats = merged_df.groupby('PLAYER_NAME').agg(
            total_minutes=('MIN', 'sum'),
            avg_sei_per_min=('SEI_PER_MIN', 'mean')
        )
        
        qualified_players = player_sei_stats[
            player_sei_stats['total_minutes'] >= config.MIN_MINUTES_THRESHOLD
        ]
        
        top_sei = qualified_players.nlargest(10, 'avg_sei_per_min')
        print("\n[SEI/M Top 10 (최소 1000분 출전)]")
        print(top_sei.round(3))
    
    def save_data(self, merged_df: pd.DataFrame):
        """
        전처리된 데이터 저장
        
        Args:
            merged_df: 전처리된 DataFrame
        """
        print("\n" + "=" * 60)
        print("8단계: 데이터 저장")
        print("=" * 60)
        
        # 출력 폴더 생성 (data/processed/)
        os.makedirs(os.path.dirname(config.MERGED_PKL), exist_ok=True)
        os.makedirs(os.path.dirname(config.FINAL_CSV), exist_ok=True)
        
        # PKL 형식 저장
        merged_df.to_pickle(config.MERGED_PKL)
        print(f"[OK] PKL 파일 저장 완료: {config.MERGED_PKL}")
        
        # CSV 형식 저장
        merged_df.to_csv(config.FINAL_CSV, index=False, encoding='utf-8')
        print(f"[OK] CSV 파일 저장 완료: {config.FINAL_CSV}")
        
        print(f"\n최종 데이터 shape: {merged_df.shape}")
    
    def process(self) -> pd.DataFrame:
        """
        전체 전처리 프로세스 실행
        
        Returns:
            전처리된 DataFrame
        """
        # 1. 데이터 로드
        df_games, df_details, df_players, df_teams = self.load_data()
        
        # 2. 데이터 병합
        merged_df = self.merge_data(df_games, df_details, df_players, df_teams)
        
        # 3. 데이터 변환
        merged_df = self.transform_data(merged_df)
        
        # 4. 결측치 처리
        merged_df = self.handle_missing_values(merged_df)
        
        # 5. 이상치 제거
        merged_df = self.remove_outliers(merged_df)
        
        # 6. 파생 지표 계산
        merged_df = self.calculate_derived_metrics(merged_df)
        
        # 7. 통계 출력
        self.print_statistics(merged_df)
        
        # 8. 데이터 저장
        self.save_data(merged_df)
        
        self.merged_df = merged_df
        return merged_df


if __name__ == "__main__":
    # 직접 실행 시 전처리 프로세스 실행
    preprocessor = NBADataPreprocessor()
    df = preprocessor.process()
    print("\n" + "=" * 60)
    print("전처리 완료!")
    print("=" * 60)

