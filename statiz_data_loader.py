# [최종 수정 완료된 함수]

def get_statiz_data(year=2025, data_type='hitter'):
    """
    스탯티즈에서 특정 연도의 전체 선수 기록을 가져옵니다.
    qu=0 필터로 규정 타석/이닝을 채우지 않은 선수도 모두 포함합니다.
    """
    if data_type == 'hitter':
        url = f'http://www.statiz.co.kr/stat.php?opt=0&sopt=0&re=0&ys={year}&ye={year}&se=0&te=&tm=&ty=0&qu=0&po=0&as=&ae=&hi=&un=&pl=&da=1&o1=WAR_ALL_ADJ&o2=TPA&de=1&lr=0&tr=&cv=&ml=1&sn=2000'
    elif data_type == 'pitcher':
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
        
        if '이름' in df.columns:
            df.rename(columns={'이름': '선수명'}, inplace=True)
        if '팀' in df.columns:
            df.rename(columns={'팀': '팀명'}, inplace=True)
        if 'Age' in df.columns:
            df.rename(columns={'Age': '나이'}, inplace=True)
            
        print("✅ 데이터 수집 및 정제 완료!")
        
        # 파일 저장 코드가 삭제된 후, 성공 시 데이터를 반환합니다.
        return df

    except Exception as e:
        print(f"❌ 데이터를 가져오는 데 실패했습니다: {e}")
        return None
