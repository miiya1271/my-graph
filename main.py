import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

# 앱 제목 및 설명
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown(
    "박스오피스 일별 데이터를 바탕으로 **시간에 따른 영화 시장의 변화와 관객 추이**를 시각화합니다."
)
st.markdown("---")


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
  # 날짜 열을 문자열로 읽어옴
  df = pd.read_csv(url, dtype={"날짜": str})

  # 날짜 열을 datetime 형식으로 변환 (YYYYMMDD -> YYYY-MM-DD)
  df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

  # 숫자형 컬럼 변환
  num_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
  for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

  return df


try:
  df = load_data()
except Exception as e:
  st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
  st.stop()

# ----------------------------------------------------
# Section 1: 영화별 일관객 변화
# ----------------------------------------------------
st.header("📌 Section 1. 영화별 일관객 변화 추이")
st.caption(
    "선택한 영화의 상영 기간 동안 일일 관객수가 어떻게 변화했는지 추적합니다."
)

# 영화 선택 드롭다운 (누적 관객 많은 순으로 정렬)
movie_list = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
)
selected_movie = st.selectbox("📊 분석할 영화를 선택하세요:", movie_list)

if selected_movie:
  movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

  # Plotly 선 그래프
  fig1 = px.line(
      movie_df,
      x="날짜",
      y="일관객",
      title=f"<b>[{selected_movie}]</b> 날짜별 일관객수 변화",
      labels={"날짜": "날짜", "일관객": "일일 관객수(명)"},
      markers=True,
  )

  # 마우스 호버(Hover) 설정 및 스타일링
  fig1.update_traces(
      hovertemplate=(
          "<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
      ),
      line=dict(width=2.5),
  )
  fig1.update_layout(
      hovermode="x unified",
      xaxis_title="날짜",
      yaxis_title="일일 관객수(명)",
      template="plotly_white",
      margin=dict(l=40, r=40, t=60, b=40),
  )

  # 그래프 출력
  st.plotly_chart(fig1, use_container_width=True)

  # 이 그래프로 알 수 있는 것 문구
  st.info(
      f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 초기"
      " 관객 집중도, 주말과 평일 간의 관객 수 변동 폭, 그리고 흥행 유효"
      " 기간(상승·하강 곡선)을 한눈에 볼 수 있습니다."
  )

st.markdown("---")

# ----------------------------------------------------
# Section 2 & 3: 추후 확장용 섹션
# ----------------------------------------------------
st.header("📌 Section 2. [추가 예정] 날짜별 전체 박스오피스 총관객 추이")
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 특정 연휴나 성수기 시즌의 전체 극장가"
    " 관객 규모 변화를 파악할 수 있습니다."
)

st.markdown("---")

st.header("📌 Section 3. [추가 예정] 요일별 / 월별 관객 패턴 분석")
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 평일 대비 주말 관객 수의 비율과 관객이"
    " 몰리는 주요 요일 패턴을 비교해 볼 수 있습니다."
)
