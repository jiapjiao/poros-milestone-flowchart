import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Poros 产品 Milestone 流程图", layout="wide")

st.title("🚀 Poros 产品 Milestone 流程图")

# 加载数据并安全转换日期
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone", engine="openpyxl")
    
    # 安全转换 Excel 日期序列号
    date_cols = ["Milestone 1 目标日期", "Milestone 2 目标日期", "Milestone 3 目标日期"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = pd.to_datetime(df[col], unit='D', origin='1899-12-30', errors='coerce')
    
    # 清理数据
    df = df.dropna(subset=['产品名称']).copy()
    df['产品名称'] = df['产品名称'].astype(str).str.strip()
    df = df[df['产品名称'] != '']
    
    return df

df = load_data()

st.success(f"✅ 数据加载成功！共 {len(df)} 条记录")

# ==================== 侧边栏筛选 ====================
st.sidebar.header("🔍 筛选条件")

products = sorted(df['产品名称'].unique())
selected_products = st.sidebar.multiselect("选择产品", products, default=products[:8])

status_list = sorted(df['当前状态'].dropna().unique())
selected_status = st.sidebar.multiselect("当前状态", status_list, default=["开发中"])

# 过滤数据
filtered_df = df.copy()
if selected_products:
    filtered_df = filtered_df[filtered_df['产品名称'].isin(selected_products)]
if selected_status:
    filtered_df = filtered_df[filtered_df['当前状态'].isin(selected_status)]

# ==================== 显示数据表格 ====================
st.subheader("📋 Milestone 数据表")
st.dataframe(filtered_df, use_container_width=True, height=400)

# ==================== 生成 Gantt 时间轴图 ====================
st.subheader("📊 Milestone 时间轴流程图（推荐给老师看）")

gantt_data = []

for _, row in filtered_df.iterrows():
    product = str(row['产品名称']).strip()
    owner = str(row.get('负责人', '')) if pd.notna(row.get('负责人')) else ''
    
    for i in [1, 2, 3]:
        desc_col = f"Milestone {i} 描述"
        date_col = f"Milestone {i} 目标日期"
        
        if pd.notna(row.get(desc_col)) and pd.notna(row.get(date_col)):
            desc = str(row[desc_col]).strip()
            target_date = row[date_col]
            
            if pd.notna(target_date):
                gantt_data.append({
                    "产品": product,
                    "负责人": owner,
                    "阶段": f"Milestone {i}",
                    "描述": desc[:70] + ("..." if len(desc) > 70 else ""),
                    "开始日期": target_date - pd.Timedelta(days=5),
                    "结束日期": target_date + pd.Timedelta(days=5),
                    "目标日期": target_date.strftime("%Y-%m-%d")
                })

gantt_df = pd.DataFrame(gantt_data)

if not gantt_df.empty:
    fig = px.timeline(
        gantt_df,
        x_start="开始日期",
        x_end="结束日期",
        y="产品",
        color="阶段",
        hover_data=["负责人", "描述", "目标日期"],
        title="Poros 各产品 Milestone 时间轴流程图",
        labels={"产品": "产品名称", "阶段": "里程碑阶段"}
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=max(700, len(gantt_df) * 25),
        xaxis_title="时间 (2026 年)",
        yaxis_title="产品 / 项目",
        legend_title="里程碑阶段",
        hoverlabel=dict(font_size=13, bgcolor="white")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("💡 使用方法：鼠标悬停查看详情 • 可拖动缩放时间轴 • 左侧可筛选产品和状态")
else:
    st.info("当前筛选条件下没有带日期的 Milestone 数据")

st.caption("数据来源：飞书导出 Excel • 日期已自动转换")