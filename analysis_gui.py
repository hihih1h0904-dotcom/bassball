import tkinter as tk
from tkinter import font as tkfont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ssl
import time

# --- 1. 데이터 로더 (KBO 공식 홈페이지) ---
def get_kbo_data(year=2025, data_type='hitter'):
    """
    KBO 공식 홈페이지에서 데이터를 가져옵니다.
    '팀명' 컬럼이 정상적으로 포함되어 있습니다.
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    all_pages_data = []
    
    print(f"⚾ {year}년 KBO 공식 홈페이지 {data_type} 기록 수집을 시작합니다...")

    for page_num in range(1, 21):
        if data_type == 'hitter':
            url = f'https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?recordTeamDiv=0&year={year}&playerOrder=AVG&order=DESC&page={page_num}'
            encoding = 'utf-8'
        else: # pitcher
            url = f'https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?recordTeamDiv=0&year={year}&playerOrder=ERA&order=ASC&page={page_num}'
            encoding = 'utf-8' # 투수 인코딩도 utf-8로 통일
        
        try:
            tables = pd.read_html(url, encoding=encoding)
            df_page = tables[0]
            if df_page.empty: break
            all_pages_data.append(df_page)
            print(f"✅ {page_num}페이지 데이터 수집 완료.")
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ {page_num}페이지 오류: {e}. 수집을 중단합니다.")
            break
            
    if not all_pages_data: return None
    
    df_total = pd.concat(all_pages_data, ignore_index=True)
    print("✅ 전체 데이터 통합 완료!")
    return df_total

# --- 2. 데이터 로딩 및 전처리 ---
print("KBO 공식 홈페이지에서 데이터를 로딩합니다...")
try:
    hitter_df = get_kbo_data(year=2025, data_type='hitter')
    pitcher_df = get_kbo_data(year=2025, data_type='pitcher')
    for df in [hitter_df, pitcher_df]:
        if df is not None:
            for col in df.columns:
                if col not in ['선수명', '팀명']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    print("✅ 데이터 로딩 완료!")
except Exception as e:
    print(f"❌ 데이터 로딩 실패: {e}")
    hitter_df = pd.DataFrame()
    pitcher_df = pd.DataFrame()

# --- 3. GUI 프로그램 ---
try:
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("⚠️ Malgun Gothic 폰트가 없어 그래프에 한글이 깨질 수 있습니다.")

class KBOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KBO 선수 기록 비교 프로그램")
        self.root.geometry("1000x700")
        
        self.default_font = tkfont.Font(family="Malgun Gothic", size=10)
        
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=5)
        self.player_mode = tk.StringVar(value="hitter")
        
        tk.Label(mode_frame, text="비교 유형 선택:", font=self.default_font).pack(side="left", padx=10)
        tk.Radiobutton(mode_frame, text="타자", variable=self.player_mode, value="hitter", font=self.default_font).pack(side="left")
        tk.Radiobutton(mode_frame, text="투수", variable=self.player_mode, value="pitcher", font=self.default_font).pack(side="left")

        input_frame = tk.Frame(root, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="선수 1:", font=self.default_font).pack(side="left", padx=5)
        self.entry1 = tk.Entry(input_frame, width=15, font=self.default_font)
        self.entry1.pack(side="left", padx=5)

        tk.Label(input_frame, text="선수 2:", font=self.default_font).pack(side="left", padx=5)
        self.entry2 = tk.Entry(input_frame, width=15, font=self.default_font)
        self.entry2.pack(side="left", padx=5)

        self.compare_button = tk.Button(input_frame, text="기록 비교", command=self.compare_players, font=self.default_font)
        self.compare_button.pack(side="left", padx=10)
        
        self.status_label = tk.Label(input_frame, text="비교 유형을 선택하고 선수 이름을 입력하세요.", fg="blue", font=self.default_font)
        self.status_label.pack(side="left", padx=5)

        result_frame = tk.Frame(root)
        result_frame.pack(fill="both", expand=True)

        self.text_area = tk.Text(result_frame, width=40, wrap="word", font=self.default_font)
        self.text_area.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas_frame = tk.Frame(result_frame)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def compare_players(self):
        player1_name = self.entry1.get().strip()
        player2_name = self.entry2.get().strip()
        mode = self.player_mode.get()

        df = hitter_df if mode == "hitter" else pitcher_df
        
        player1_data = df[df['선수명'] == player1_name]
        player2_data = df[df['선수명'] == player2_name]

        if player1_data.empty or player2_data.empty:
            self.status_label.config(text=f"선수를 ({mode}) 기록에서 찾을 수 없습니다.", fg="red")
            return
        
        p1 = player1_data.iloc[0]
        p2 = player2_data.iloc[0]

        self.status_label.config(text="✅ 기록을 성공적으로 불러왔습니다.", fg="green")
        self.update_text_area(p1, p2, mode)
        self.update_graph(p1, p2, mode)

    def update_text_area(self, p1, p2, mode):
        self.text_area.delete('1.0', tk.END)
        if mode == 'hitter':
            display_stats = ['팀명', 'AVG', 'G', 'PA', 'AB', 'R', 'H', 'HR', 'RBI', 'SB', 'BB', 'SO', 'OPS']
        else:
            display_stats = ['팀명', 'ERA', 'G', 'W', 'L', 'SV', 'IP', 'H', 'HR', 'BB', 'SO', 'WHIP']
        
        header1 = f"--- {p1['선수명']} ({p1['팀명']}) ---"
        header2 = f"--- {p2['선수명']} ({p2['팀명']}) ---"
        
        self.text_area.insert('1.0', f"{header1:<20} | {header2}\n")
        self.text_area.insert('1.0', "="*50 + "\n")
        
        for stat in display_stats:
            if stat in p1 and stat in p2:
                line = f"{stat:<5} | {str(p1[stat]):<18} | {str(p2[stat])}\n"
                self.text_area.insert('1.0', line)

    def update_graph(self, p1, p2, mode):
        self.ax.clear()
        if mode == 'hitter':
            compare_stats = ['AVG', 'HR', 'RBI', 'OPS', 'SLG', 'OBP']
        else:
            compare_stats = ['ERA', 'W', 'L', 'SO', 'IP', 'WHIP']

        valid_compare_stats = [s for s in compare_stats if s in p1 and s in p2]
        p1_stats = p1[valid_compare_stats]
        p2_stats = p2[valid_compare_stats]
        
        index = range(len(valid_compare_stats))
        bar_width = 0.35

        bar1 = self.ax.bar([i - bar_width/2 for i in index], p1_stats, bar_width, label=p1['선수명'])
        bar2 = self.ax.bar([i + bar_width/2 for i in index], p2_stats, bar_width, label=p2['선수명'])

        self.ax.set_ylabel('기록')
        self.ax.set_title(f"'{p1['선수명']}' vs '{p2['선수명']}' 핵심 지표 비교", fontdict={'size': 12, 'weight': 'bold'})
        self.ax.set_xticks(index)
        self.ax.set_xticklabels(valid_compare_stats)
        self.ax.legend()
        
        for rect in bar1 + bar2:
            height = rect.get_height()
            self.ax.text(rect.get_x() + rect.get_width()/2.0, height, f'{height:.3f}' if isinstance(height, float) and height < 1 else f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        self.canvas.draw()

if __name__ == "__main__":
    if hitter_df is None or pitcher_df is None or hitter_df.empty or pitcher_df.empty:
        print("데이터프레임이 비어있어 GUI를 실행할 수 없습니다.")
    else:
        root = tk.Tk()
        app = KBOApp(root)
        root.mainloop()