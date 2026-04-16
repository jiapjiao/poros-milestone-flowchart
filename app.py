import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**横向时间节点流程图**（已适配你的最新 Excel 文件）")

# 加载数据（不再强制转数字，直接用已有的日期格式）
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    # 清理产品名称
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
    
    # 处理父记录
    if '父记录' in df.columns:
        df['父记录'] = df['父记录'].astype(str).str.strip().replace(['nan', 'None', ''], None)
    
    return df

df = load_data()

# 侧边栏选择
st.sidebar.header("选择产品查看流程图")
products = sorted(df['产品名称'].unique())
selected = st.sidebar.selectbox("选择产品", products)

# 获取主产品 + 子产品
main_df = df[df['产品名称'] == selected].copy()
child_df = df[df['父记录'] == selected].copy() if '父记录' in df.columns else pd.DataFrame()
combined_df = pd.concat([main_df, child_df])

st.success(f"当前显示：**{selected}**")

# 构建节点 —— 只要是有效日期就显示
nodes = []
for _, row in combined_df.iterrows():
    prod = str(row['产品名称']).strip()
    display_name = f"{prod} (子)" if row.get('父记录') == selected else prod
    
    for i in [1, 2, 3]:
        date_val = row.get(f"Milestone {i} 目标日期")
        desc = str(row.get(f"Milestone {i} 描述", "")).strip()
        
        # 关键：只要 date_val 是有效日期就加入
        if pd.notna(date_val) and isinstance(date_val, pd.Timestamp):
            short_desc = desc[:48] + ("..." if len(desc) > 48 else "") if desc else "(无描述)"
            nodes.append({
                "显示名称": display_name,
                "阶段": f"MS{i}",
                "日期": date_val,
                "日期标签": date_val.strftime("%m.%d"),
                "描述": short_desc,
                "完整描述": desc or "(无描述)"
            })

timeline_df = pd.DataFrame(nodes)

if timeline_df.empty:
    st.error(f"{selected} 没有检测到有效的 Milestone 目标日期")
    st.info("提示：请尝试选择 PorosData Designer、PorosHoster 或 PorosData toolset")
    st.stop()

# 绘制图表
fig = px.timeline(
    timeline_df,
    x_start="日期",
    x_end="日期",
    y="显示名称",
    color="阶段",
    hover_data=["完整描述"],
    title=f"{selected} Milestone 时间节点流程图"
)

fig.update_traces(
    marker=dict(size=24, line=dict(width=3)),
    text=timeline_df["日期标签"] + "<br>" + timeline_df["描述"],
    textposition="top center",
    textfont=dict(size=12)
)

fig.update_layout(
    height=720,
    xaxis_title="时间节点（2026 年）",
    yaxis_title="产品 / 子产品",
    xaxis=dict(tickformat="%m.%d", tickangle=45),
    margin=dict(l=140, r=50, t=100, b=140)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 每个节点显示日期 + 描述 • 日期已直接读取飞书导出格式")

with st.expander("调试 - 查看当前产品原始数据"):
    st.dataframe(combined_df, use_container_width=True)