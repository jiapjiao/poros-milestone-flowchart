import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**老师想要的流程图**：横向时间线 + 每个 Milestone 有日期和描述")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
    
    if '父记录' in df.columns:
        df['父记录'] = df['父记录'].astype(str).str.strip().replace(['nan', 'None', ''], None)
    return df

df = load_data()

st.sidebar.header("选择产品")
selected = st.sidebar.selectbox("选择产品", sorted(df['产品名称'].unique()))

# 主产品 + 子产品
main_df = df[df['产品名称'] == selected].copy()
child_df = df[df['父记录'] == selected].copy() if '父记录' in df.columns else pd.DataFrame()
combined = pd.concat([main_df, child_df])

# 构建 Gantt 数据（每个 Milestone 一个横条）
data = []
for _, row in combined.iterrows():
    name = row['产品名称']
    display = f"→ {name}" if row.get('父记录') == selected else name
    
    for i in [1, 2, 3]:
        date = row.get(f"Milestone {i} 目标日期")
        desc = str(row.get(f"Milestone {i} 描述", "")).strip()
        
        if pd.notna(date):
            short = (desc[:38] + "...") if len(desc) > 38 else desc
            short = short if short else "无描述"
            
            data.append({
                "产品": display,
                "阶段": f"MS{i}",
                "开始": date - timedelta(days=3),
                "结束": date + timedelta(days=3),
                "描述": short,
                "完整描述": desc or "无描述",
                "日期": date.strftime("%m.%d")
            })

gantt_df = pd.DataFrame(data)

if gantt_df.empty:
    st.error(f"{selected} 暂无有效的 Milestone 日期")
    st.stop()

st.success(f"当前显示：**{selected}**")

fig = px.timeline(
    gantt_df,
    x_start="开始",
    x_end="结束",
    y="产品",
    color="阶段",
    hover_data=["完整描述"],
    title=f"{selected} Milestone 流程图",
)

fig.update_layout(
    height=680,
    xaxis_title="时间轴 (2026 年)",
    yaxis_title="产品 / 子产品",
    xaxis=dict(tickformat="%m.%d"),
    margin=dict(l=180, r=50, t=80, b=100)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 每个彩色横条代表一个 Milestone • 鼠标悬停看完整描述 • 子产品用 → 表示")

with st.expander("查看当前产品原始数据"):
    st.dataframe(combined, use_container_width=True)