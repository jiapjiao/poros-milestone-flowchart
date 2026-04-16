import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**老师想要的流程图**：横向时间线 + 每个节点有日期和描述（已美化）")

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

# 构建 Gantt 数据
data = []
for _, row in combined.iterrows():
    name = row['产品名称']
    display = f"→ {name}" if row.get('父记录') == selected else name
   
    for i in [1, 2, 3]:
        date = row.get(f"Milestone {i} 目标日期")
        desc = str(row.get(f"Milestone {i} 描述", "")).strip()
       
        if pd.notna(date):
            short = (desc[:40] + "...") if len(desc) > 40 else desc
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

# 美化后的图表
fig = px.timeline(
    gantt_df,
    x_start="开始",
    x_end="结束",
    y="产品",
    color="阶段",
    hover_data=["完整描述"],
    title=f"{selected} Milestone 流程图",
    color_discrete_map={"MS1": "#1f77b4", "MS2": "#ff7f0e", "MS3": "#2ca02c"}
)

# 美化关键部分
fig.update_traces(
    text=gantt_df["日期"] + "<br>" + gantt_df["描述"],   # 在节点上直接显示日期 + 描述
    textposition="inside",
    textfont=dict(size=11, color="white"),
    marker_line_width=2,
    opacity=0.9
)

fig.update_layout(
    height=720,
    xaxis_title="时间轴 (2026 年)",
    yaxis_title="产品 / 子产品",
    legend_title="里程碑阶段",
    xaxis=dict(tickformat="%m.%d", tickangle=45),
    margin=dict(l=200, r=50, t=100, b=120),
    font=dict(size=13)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 每个彩色横条 = 一个 Milestone 节点 • 节点内显示日期 + 描述 • 子产品用 → 表示")

with st.expander("查看当前产品原始数据"):
    st.dataframe(combined, use_container_width=True)