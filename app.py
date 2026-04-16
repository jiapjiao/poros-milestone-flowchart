import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**老师想要的流程图风格**：横向时间线 + 每个节点有日期和描述")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
    
    if '父记录' in df.columns:
        df['父记录'] = df['父记录'].astype(str).str.strip().replace(['nan', 'None', ''], None)
    
    # 转换日期（安全处理）
    for col in ["Milestone 1 目标日期", "Milestone 2 目标日期", "Milestone 3 目标日期"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = pd.to_datetime(df[col], unit='D', origin='1899-12-30', errors='coerce')
    
    return df

df = load_data()

# 侧边栏选择
st.sidebar.header("选择产品")
products = sorted(df['产品名称'].unique())
selected = st.sidebar.selectbox("选择产品", products)

# 主产品 + 子产品
main_df = df[df['产品名称'] == selected].copy()
child_df = df[df['父记录'] == selected].copy() if '父记录' in df.columns else pd.DataFrame()
combined_df = pd.concat([main_df, child_df])

# 构建流程图数据（每个 Milestone 做成一个小横条）
gantt_data = []
for _, row in combined_df.iterrows():
    prod = str(row['产品名称']).strip()
    display_name = f"→ {prod}" if row.get('父记录') == selected else prod
    owner = str(row.get('负责人', '')) if pd.notna(row.get('负责人')) else ''
    
    for i in [1, 2, 3]:
        date_col = f"Milestone {i} 目标日期"
        desc_col = f"Milestone {i} 描述"
        
        date_val = row.get(date_col)
        desc = str(row.get(desc_col, "")).strip()
        
        if pd.notna(date_val):
            short_desc = desc[:40] + "..." if len(desc) > 40 else desc
            if not short_desc:
                short_desc = "无描述"
            
            start = date_val - timedelta(days=2)
            end = date_val + timedelta(days=2)
            
            gantt_data.append({
                "产品/子产品": display_name,
                "阶段": f"MS{i}",
                "开始": start,
                "结束": end,
                "描述": short_desc,
                "完整描述": desc or "无描述",
                "目标日期": date_val.strftime("%Y-%m-%d")
            })

gantt_df = pd.DataFrame(gantt_data)

if gantt_df.empty:
    st.error(f"{selected} 暂无有效的 Milestone 日期数据")
    st.stop()

st.success(f"当前显示：**{selected}**")

# 绘制流程图
fig = px.timeline(
    gantt_df,
    x_start="开始",
    x_end="结束",
    y="产品/子产品",
    color="阶段",
    hover_data=["完整描述", "目标日期"],
    title=f"{selected} Milestone 流程图",
    labels={"产品/子产品": "产品 / 子产品"}
)

fig.update_layout(
    height=720,
    xaxis_title="时间轴（2026 年）",
    yaxis_title="产品 / 子产品",
    legend_title="里程碑阶段",
    xaxis=dict(tickformat="%m.%d"),
    margin=dict(l=200, r=50, t=100, b=100)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 横条代表每个 Milestone • 鼠标悬停可看完整描述 • 子产品会用 → 标记")

with st.expander("查看原始数据"):
    st.dataframe(combined_df, use_container_width=True)