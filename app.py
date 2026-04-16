import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="Poros Milestone 流程图", layout="wide")
st.title("🚀 Poros 产品 Milestone 流程图")
st.markdown("**支持多选产品，选中后主任务和子任务会同时高亮显示**")

# ====================== 加载数据 ======================
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df['父记录'] = df.get('父记录', pd.Series()).astype(str).str.strip().replace(['nan', 'None', ''], None)
    return df

df = load_data()

# ====================== 左侧多选 ======================
st.sidebar.header("选择产品（可多选）")

product_list = sorted(df['产品名称'].unique())
selected_products = st.sidebar.multiselect("选择产品", options=product_list, default=product_list[:3])

# ====================== 准备数据 ======================
# 获取所有选中的主任务和它们的子任务
display_df = df[df['产品名称'].isin(selected_products)].copy()

# 加入子任务
child_df = df[df['父记录'].isin(selected_products)].copy()
combined = pd.concat([display_df, child_df]).drop_duplicates()

if combined.empty:
    st.warning("请选择至少一个产品")
    st.stop()

# ====================== 绘制大图 ======================
fig = go.Figure()

for _, row in combined.iterrows():
    name = row['产品名称']
    is_child = row.get('父记录') in selected_products
    display_name = f"→ {name}" if is_child else name
    
    color = "#1f77b4" if not is_child else "#ff7f0e"   # 主任务蓝色，子任务橙色

    for i in [1, 2, 3]:
        date_col = f"Milestone {i} 目标日期"
        desc_col = f"Milestone {i} 描述"
        
        if pd.notna(row.get(date_col)):
            date = row[date_col]
            desc = str(row.get(desc_col, "")).strip()[:60]
            if len(str(row.get(desc_col, ""))) > 60:
                desc += "..."
            
            fig.add_trace(go.Scatter(
                x=[date],
                y=[display_name],
                mode='markers+text',
                marker=dict(size=14, color=color, symbol='circle'),
                text=[f"M{i} {date.strftime('%m-%d')}"],
                textposition="top center",
                hovertemplate=f"<b>{display_name}</b><br>{desc}<extra></extra>",
                name=display_name
            ))

fig.update_layout(
    title="Poros 产品 Milestone 总览（支持多选 + 子任务显示）",
    xaxis_title="时间轴 (2026 年)",
    yaxis_title="产品 / 子产品",
    height=900,
    showlegend=False,
    hovermode="closest",
    plot_bgcolor="#f8fafc",
    xaxis=dict(type='date', tickformat='%m-%d'),
    margin=dict(l=250, r=50, t=100, b=100),
    font=dict(size=14)
)

fig.update_yaxes(autorange="reversed")  # 时间早的在下面

st.plotly_chart(fig, use_container_width=True)

st.caption("💡 蓝色 = 主任务　橙色 = 子任务　每个节点显示日期 + 描述　支持同时选中多个产品")

# ====================== 详细数据表 ======================
with st.expander("查看选中产品的原始数据"):
    st.dataframe(combined[['产品名称', '负责人', '当前状态', 'M1描述', 'M1日期', 'M2描述', 'M2日期', 'M3描述', 'M3日期']], use_container_width=True)
