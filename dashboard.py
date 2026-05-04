import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from datetime import datetime
import time
from collections import Counter
import re

st.set_page_config(page_title="ChatBot Analytics", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'DM Mono', monospace; background-color: #0a0a0f; color: #e8e8f0; }
    .stApp { background-color: #0a0a0f; }
    section[data-testid="stSidebar"] { background-color: #111118 !important; border-right: 1px solid #1e1e2e; }
    section[data-testid="stSidebar"] * { color: #e8e8f0 !important; }
    [data-testid="metric-container"] { background: #111118; border: 1px solid #1e1e2e; border-radius: 12px; padding: 16px !important; }
    [data-testid="metric-container"]:hover { border-color: #7c6af7; }
    [data-testid="stMetricLabel"] { font-size: 11px !important; letter-spacing: 2px; text-transform: uppercase; color: #5a5a78 !important; }
    [data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-size: 32px !important; font-weight: 800 !important; color: #e8e8f0 !important; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: #e8e8f0 !important; }
    .stButton button { background: linear-gradient(135deg, #7c6af7, #3ddcf7); color: white; border: none; border-radius: 8px; }
    .stTabs [data-baseweb="tab-list"] { background: #111118; border-radius: 10px; padding: 4px; border: 1px solid #1e1e2e; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #5a5a78; border-radius: 8px; font-size: 13px; }
    .stTabs [aria-selected="true"] { background: #1e1e2e !important; color: #7c6af7 !important; }
    .section-header { font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #5a5a78; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #1e1e2e; }
</style>
""", unsafe_allow_html=True)

DB_URL = "postgresql://postgres:Aaisaheb04@localhost:5432/chatbot_db"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

def load_data():
    try:
        df = pd.read_sql("SELECT * FROM chat_logs ORDER BY created_at DESC", get_engine())
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color="#e8e8f0", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1e1e2e", linecolor="#1e1e2e"),
    yaxis=dict(gridcolor="#1e1e2e", linecolor="#1e1e2e"),
)
COLORS = {"positive": "#2ed47a", "negative": "#f75e6a", "neutral": "#7c6af7", "accent": "#3ddcf7"}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:24px'>
        <div style='width:36px;height:36px;background:linear-gradient(135deg,#7c6af7,#3ddcf7);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px'>⚡</div>
        <div>
            <div style='font-family:Syne,sans-serif;font-weight:800;font-size:18px;background:linear-gradient(135deg,#7c6af7,#3ddcf7);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>OpenAIChat</div>
            <div style='font-size:10px;color:#5a5a78;letter-spacing:2px'>ANALYTICS DASHBOARD</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔧 Filters")
    auto_refresh     = st.toggle("Auto Refresh (30s)", value=False)
    sentiment_filter = st.multiselect("Sentiment", ["positive","negative","neutral"], default=["positive","negative","neutral"])
    user_filter      = st.text_input("Filter by User ID", placeholder="e.g. user1")
    limit            = st.slider("Max Records", 10, 500, 100)

    st.divider()
    st.markdown("### 📡 Pipeline Status")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("🟢 **FastAPI**")
        st.markdown("🟢 **Kafka**")
    with c2:
        st.markdown("🟢 **Spark**")
        st.markdown("🟢 **PostgreSQL**")

    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ── Load & Filter ─────────────────────────────────────────────────────────────
df, error = load_data()
if error:
    st.error(f"❌ Database error: {error}")
    st.stop()
if df.empty:
    st.warning("No data found. Send some messages first!")
    st.stop()

if sentiment_filter:
    df = df[df["sentiment"].isin(sentiment_filter)]
if user_filter:
    df = df[df["user_id"].str.contains(user_filter, case=False, na=False)]
df = df.head(limit)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-family:Syne,sans-serif;font-size:32px;font-weight:800;background:linear-gradient(135deg,#7c6af7,#3ddcf7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px'>
    ChatBot Analytics Dashboard
</h1>
<p style='color:#5a5a78;font-size:13px;margin-bottom:24px'>Real-time insights · Kafka · Spark · PostgreSQL</p>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total        = len(df)
positive     = len(df[df["sentiment"] == "positive"])
negative     = len(df[df["sentiment"] == "negative"])
neutral      = len(df[df["sentiment"] == "neutral"])
pos_pct      = round(positive / total * 100, 1) if total else 0
neg_pct      = round(negative / total * 100, 1) if total else 0
unique_users = df["user_id"].nunique()

k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Total Messages", f"{total:,}", "Live")
with k2: st.metric("Positive 😊", positive, f"{pos_pct}%")
with k3: st.metric("Negative 😔", negative, f"-{neg_pct}%", delta_color="inverse")
with k4: st.metric("Neutral 😐", neutral)
with k5: st.metric("Unique Users", unique_users)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "💬 Chat Logs", "🔍 Deep Analysis"])

# ════════════════════════════ TAB 1 — Overview ════════════════════════════════
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Sentiment Distribution</div>', unsafe_allow_html=True)
        sc = df["sentiment"].value_counts().reset_index()
        sc.columns = ["sentiment", "count"]
        fig_donut = go.Figure(go.Pie(
            labels=sc["sentiment"], values=sc["count"], hole=0.65,
            marker=dict(colors=[COLORS.get(s,"#7c6af7") for s in sc["sentiment"]], line=dict(color="#0a0a0f", width=3)),
            textinfo="label+percent", textfont=dict(family="DM Mono", size=12),
        ))
        fig_donut.add_annotation(text=f"<b>{total}</b><br>Total", x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#e8e8f0", family="Syne"))
        fig_donut.update_layout(**PLOT_LAYOUT, height=320, showlegend=True,
            legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_donut, key="donut")

    with col2:
        st.markdown('<div class="section-header">Messages per User</div>', unsafe_allow_html=True)
        uc = df.groupby("user_id").agg(
            total=("id","count"),
            positive=("sentiment", lambda x:(x=="positive").sum()),
            negative=("sentiment", lambda x:(x=="negative").sum()),
            neutral=("sentiment",  lambda x:(x=="neutral").sum()),
        ).reset_index().sort_values("total", ascending=False).head(10)

        fig_bar = go.Figure()
        for s, c in [("positive",COLORS["positive"]),("negative",COLORS["negative"]),("neutral",COLORS["neutral"])]:
            fig_bar.add_trace(go.Bar(name=s.capitalize(), x=uc["user_id"], y=uc[s], marker_color=c, marker_line_width=0))
        fig_bar.update_layout(**PLOT_LAYOUT, height=320, barmode="stack", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_bar, key="userbar")

    st.markdown('<div class="section-header">Sentiment Health Score</div>', unsafe_allow_html=True)
    health = round((positive*100 + neutral*50) / (total*100) * 100, 1) if total else 0
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=health, delta={"reference": 70},
        title={"text": "Overall Sentiment Health", "font": {"family":"Syne","size":16,"color":"#e8e8f0"}},
        number={"suffix":"%","font":{"family":"Syne","size":48,"color":"#e8e8f0"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#5a5a78"},
            "bar":{"color":"#7c6af7","thickness":0.3},
            "bgcolor":"#111118","bordercolor":"#1e1e2e",
            "steps":[{"range":[0,40],"color":"rgba(247,94,106,0.2)"},
                     {"range":[40,70],"color":"rgba(124,106,247,0.2)"},
                     {"range":[70,100],"color":"rgba(46,212,122,0.2)"}],
            "threshold":{"line":{"color":"#3ddcf7","width":3},"value":70},
        }
    ))
    fig_gauge.update_layout(**PLOT_LAYOUT, height=280)
    st.plotly_chart(fig_gauge, key="gauge")

# ════════════════════════════ TAB 2 — Trends ══════════════════════════════════
with tab2:
    df_time = df.copy()
    has_dates = "created_at" in df_time.columns and df_time["created_at"].notna().any()

    if has_dates:
        df_time["created_at"] = pd.to_datetime(df_time["created_at"])
        df_time["hour"]        = df_time["created_at"].dt.floor("h")   # lowercase h (pandas 2.x)
        df_time["hour_of_day"] = df_time["created_at"].dt.hour
        df_time["day_of_week"] = df_time["created_at"].dt.strftime("%a")

        st.markdown('<div class="section-header">Messages Over Time</div>', unsafe_allow_html=True)
        ts = df_time.groupby(["hour","sentiment"]).size().reset_index(name="count")
        fig_line = px.line(ts, x="hour", y="count", color="sentiment",
                           color_discrete_map=COLORS, markers=True)
        fig_line.update_traces(line_width=2.5, marker_size=6)
        fig_line.update_layout(**PLOT_LAYOUT, height=320, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_line, key="timeline")

        st.markdown('<div class="section-header">Activity Heatmap</div>', unsafe_allow_html=True)
        hm = df_time.groupby(["day_of_week","hour_of_day"]).size().reset_index(name="count")
        hm_pivot = hm.pivot(index="day_of_week", columns="hour_of_day", values="count").fillna(0)
        # FIX: cast to int before formatting
        x_labels = [f"{int(h):02d}:00" for h in hm_pivot.columns]
        fig_heat = go.Figure(go.Heatmap(
            z=hm_pivot.values, x=x_labels, y=hm_pivot.index.tolist(),
            colorscale=[[0,"#111118"],[0.5,"#7c6af7"],[1,"#3ddcf7"]], showscale=True,
        ))
        fig_heat.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig_heat, key="heatmap")
    else:
        st.info("📅 Timestamp data not available. Send new messages to see trends!")
        sc2 = df["sentiment"].value_counts().reset_index()
        sc2.columns = ["Sentiment","Count"]
        fig_h = px.bar(sc2, x="Count", y="Sentiment", orientation="h",
                       color="Sentiment", color_discrete_map=COLORS)
        fig_h.update_layout(**PLOT_LAYOUT, height=250, showlegend=False)
        st.plotly_chart(fig_h, key="sent_bar")

# ════════════════════════════ TAB 3 — Chat Logs ═══════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Recent Conversations</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3,1])
    with c2:
        sort_by = st.selectbox("Sort by", ["id","created_at","sentiment","user_id"])
        asc     = st.checkbox("Ascending", False)

    df_disp = df.sort_values(sort_by, ascending=asc) if sort_by in df.columns else df

    def color_sentiment(val):
        return {
            "positive": "background-color:rgba(46,212,122,0.15);color:#2ed47a",
            "negative": "background-color:rgba(247,94,106,0.15);color:#f75e6a",
            "neutral":  "background-color:rgba(124,106,247,0.15);color:#7c6af7",
        }.get(val, "")

    cols = [c for c in ["id","user_id","user_message","bot_response","sentiment","created_at"] if c in df_disp.columns]
    styled = df_disp[cols].style.map(color_sentiment, subset=["sentiment"]).set_properties(**{"font-size":"12px"})
    st.dataframe(styled, height=450)
    st.download_button("⬇ Download CSV", df_disp[cols].to_csv(index=False), "chat_logs.csv", "text/csv")

# ════════════════════════════ TAB 4 — Deep Analysis ══════════════════════════
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Sentiment Ratio by User</div>', unsafe_allow_html=True)
        us = df.groupby(["user_id","sentiment"]).size().unstack(fill_value=0)
        for c in ["positive","negative","neutral"]:
            if c not in us.columns: us[c] = 0
        us = us.sort_values("positive", ascending=True).head(10)
        fig_ratio = go.Figure()
        for s, c in [("positive",COLORS["positive"]),("negative",COLORS["negative"]),("neutral",COLORS["neutral"])]:
            fig_ratio.add_trace(go.Bar(y=us.index, x=us[s], name=s.capitalize(), orientation="h", marker_color=c))
        fig_ratio.update_layout(**PLOT_LAYOUT, height=350, barmode="stack", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_ratio, key="ratio")

    with col2:
        st.markdown('<div class="section-header">Message Length Analysis</div>', unsafe_allow_html=True)
        df["msg_len"] = df["user_message"].str.len()
        df["res_len"] = df["bot_response"].str.len()
        fig_scat = px.scatter(df, x="msg_len", y="res_len", color="sentiment",
            color_discrete_map=COLORS, opacity=0.75, hover_data=["user_id"],
            labels={"msg_len":"User Msg Length","res_len":"Bot Response Length"})
        fig_scat.update_traces(marker_size=9)
        fig_scat.update_layout(**PLOT_LAYOUT, height=350, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_scat, key="scatter")

    st.markdown('<div class="section-header">Top Keywords</div>', unsafe_allow_html=True)
    stop = {"i","the","a","is","it","to","and","you","me","my","in","of","for","on",
            "are","be","this","that","can","do","how","what","please","help","hi","hello","im","just"}
    words = []
    for msg in df["user_message"].dropna():
        words.extend([w for w in re.findall(r'\b[a-z]{3,}\b', msg.lower()) if w not in stop])
    if words:
        wdf = pd.DataFrame(Counter(words).most_common(20), columns=["word","count"])
        fig_w = px.bar(wdf, x="word", y="count", color="count",
                       color_continuous_scale=[[0,"#7c6af7"],[1,"#3ddcf7"]])
        fig_w.update_layout(**PLOT_LAYOUT, height=280, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_w, key="keywords")
    else:
        st.info("Not enough message data for keyword analysis.")

    st.markdown('<div class="section-header">Summary Statistics</div>', unsafe_allow_html=True)
    df["msg_len"] = df["user_message"].str.len()
    summary = pd.DataFrame({
        "Metric": ["Total Messages","Unique Users","Avg Message Length","Positive Rate","Negative Rate","Most Active User"],
        "Value":  [str(total), str(unique_users), f"{df['msg_len'].mean():.1f} chars",
                   f"{pos_pct}%", f"{neg_pct}%", df["user_id"].value_counts().idxmax() if total else "N/A"]
    })
    st.dataframe(summary, hide_index=True)

if auto_refresh:
    time.sleep(30)
    st.rerun()