import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_statiz_data(year=2025, data_type='hitter'):
    """
    스탯티즈에서 특정 연도의 전체 선수 기록을 가져옵니다.
    qu=0 필터로 규정 타석/이닝을 채우지 않은 선수도 모두 포함합니다.
    """
    if data_type == 'hitter':
        # qu=0 (모든 선수), sn=2000 (최대 2000명)으로 수정
        url = f'http://www.statiz.co.kr/stat.php?opt=0&sopt=0&re=0&ys={year}&ye={year}&se=0&te=&tm=&ty=0&qu=0&po=0&as=&ae=&hi=&un=&pl=&da=1&o1=WAR_ALL_ADJ&o2=TPA&de=1&lr=0&tr=&cv=&ml=1&sn=2000'
    elif data_type == 'pitcher':
        # qu=0 (모든 선수), sn=2000 (최대 2000명)으로 수정
        url = f'http://www.statiz.co.kr/stat.php?opt=0&sopt=0&re=1&ys={year}&ye={year}&se=0&te=&tm=&ty=0&qu=0&po=0&as=&ae=&hi=&un=&pl=&da=1&o1=WAR&o2=Out&de=1&lr=0&tr=&cv=&ml=1&sn=2000'
    else:
        return None
    
    try:
        print(f"⚾ {year}년 스탯티즈 전체 {data_type} 기록 수집을 시작합니다...")
        tables = pd.read_html(url, encoding='utf-8')
        df = tables[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)
        
        df = df.drop('순', axis=1, errors='ignore')
        
        # 컬럼 이름 최종 통일
        if '이름' in df.columns:
            df.rename(columns={'이름': '선수명'}, inplace=True)
        if '팀' in df.columns:
            df.rename(columns={'팀': '팀명'}, inplace=True)
        if 'Age' in df.columns:
            df.rename(columns={'Age': '나이'}, inplace=True)
            
        print("✅ 데이터 수집 및 정제 완료!")

        # 선수 명단 파일로 저장
        try:
            player_names = df['선수명'].tolist()
            file_name = f'{data_type}_list_{year}.txt'
            with open(file_name, 'w', encoding='utf-8') as f:
                for name in player_names:
                    f.write(name + '\n')
            print(f"✅ '{file_name}' 파일에 전체 선수 명단을 저장했습니다.")
        except Exception as e:
            print(f"⚠️ 선수 명단 저장 중 오류 발생: {e}")
            
        return df

    except Exception as e:
        print(f"❌ 데이터를 가져오는 데 실패했습니다: {e}")
        return None