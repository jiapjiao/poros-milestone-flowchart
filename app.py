import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**横向时间节点流程图**（日期 + 描述，直接对应飞书目标日期）")

# 加载数据 + 正确转换日期
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    # 关键：正确转换 Excel 序列号日期
    for col in ["Milestone 1 目标日期", "Milestone 2 目标日期", "Milestone 3 目标日期"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = pd.to_datetime(df[col], unit='D', origin='1899-12-30', errors='coerce')
    
    # 清理
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
    
    # 父子关系
    if '父记录' in df.columns:
        df['父记录'] = df['父记录'].astype(str).str.strip().replace(['nan', 'None', ''], None)
    
    return df

df = load_data()

# 侧边栏选择
st.sidebar.header("选择产品查看流程图")
main_list = sorted(df['产品名称'].unique())
selected = st.sidebar.selectbox("选择主产品", main_list)

# 获取主产品和子产品
main_df = df[df['产品名称'] == selected].copy()
child_df = df[df.get('父记录') == selected].copy() if '父记录' in df.columns else pd.DataFrame()

# 准备节点（只要有日期就显示）
nodes = []
for _, row in pd.concat([main_df, child_df]).iterrows():
    prod = str(row['产品名称']).strip()
    is_child = row.get('父记录') == selected
    display_name = f"{prod} (子)" if is_child else prod
    
    for i in [1, 2, 3]:
        desc = str(row.get(f"Milestone {i} 描述", "")).strip()
        date_val = row.get(f"Milestone {i} 目标日期")
        
        if pd.notna(date_val):   # 只要有日期就创建节点（描述可空）
            short_desc = desc[:45] + ("..." if len(desc) > 45 else "") if desc else "无描述"
            nodes.append({
                "显示名称": display_name,
                "阶段": f"MS{i}",
                "日期": date_val,
                "日期标签": date_val.strftime("%m.%d"),
                "描述": short_desc,
                "完整描述": desc or "暂无描述"
            })

timeline_df = pd.DataFrame(nodes)

if timeline_df.empty:
    st.error(f"{selected} 暂无任何 Milestone 日期")
    st.stop()

st.success(f"当前显示：**{selected}** （共 {len(timeline_df)} 个时间节点）")

# 绘制流程图
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
    marker=dict(size=22, line=dict(width=3)),
    text=timeline_df["日期标签"] + "<br>" + timeline_df["描述"],
    textposition="top center",
    textfont=dict(size=12)
)

fig.update_layout(
    height=700,
    xaxis_title="时间节点（2026 年）",
    yaxis_title="产品 / 子产品",
    xaxis=dict(tickformat="%m.%d", tickangle=45),
    margin=dict(l=120, r=50, t=100, b=120)
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 每个节点显示 **日期 + 描述** • 鼠标悬停看完整描述 • 日期来自飞书「Milestone 目标日期」列")

with st.expander("调试 - 查看当前产品原始数据"):
    st.dataframe(pd.concat([main_df, child_df]), use_container_width=True)