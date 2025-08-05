import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import random

# Set page configuration
st.set_page_config(page_title="🔋 Battery Monitoring Dashboard", layout="wide")

# Session state to store data
if "battery_data" not in st.session_state:
    st.session_state.battery_data = pd.DataFrame()
if "manual_inputs" not in st.session_state:
    st.session_state.manual_inputs = {}

st.markdown("""
    <div style='
        background: linear-gradient(90deg, #90caf9, #0d47a1);
        padding: 25px;
        border-radius: 14px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    '>
        <h1 style='text-align: center; color: #ffffff; margin: 0;'>🔋 <b>Battery Monitoring Dashboard</b></h1>
        <p style='text-align: center; color: #e3f2fd;'>Track real-time metrics of your battery cells with interactive visuals and alerts</p>
    </div>
    <hr style='border: 1px solid #1565c0;'>
""", unsafe_allow_html=True)



# Sidebar Configuration
st.sidebar.title("⚙️ Cell Configuration")

num_cells = st.sidebar.number_input("🔢 Number of Cells", min_value=1, max_value=20, value=8)

voltage_threshold = st.sidebar.slider("⚡ Voltage Alert Threshold (V)", 2.0, 5.0, 3.5)
temp_threshold = st.sidebar.slider("🌡️ Temperature Alert Threshold (°C)", 20, 100, 60)
auto_refresh = st.sidebar.checkbox("🔄 Enable Auto Refresh")

# Input values for each cell
with st.sidebar.form("manual_input_form"):
    for i in range(num_cells):
        with st.expander(f"🟩 Cell {i+1} Input"):
            mode = st.selectbox(f"Mode - Cell {i+1}", ["Idle", "Charging", "Discharging"], key=f"m_{i}")
            voltage = st.number_input(f"Voltage (V) - Cell {i+1}", key=f"v_{i}",value=5.0)
            current = st.number_input(f"Current (A) - Cell {i+1}", key=f"c_{i}",value=10.0)
            temp = st.number_input(f"Temperature (°C) - Cell {i+1}", key=f"t_{i}",value=30.0)
            cap = st.number_input(f"Capacity (%) - Cell {i+1}", key=f"cap_{i}",value=100.0)
            st.session_state.manual_inputs[f"Cell {i+1}"] = {
                "Voltage": voltage,
                "Current": current,
                "Temperature": temp,
                "Capacity": cap,
                "Status": mode
            }
    submit_btn = st.form_submit_button("🚀 Update Dashboard")
    if submit_btn:
        for i in range(num_cells):
            cell_id = f"Cell {i+1}"
            st.session_state.manual_inputs[cell_id] = {
                "Voltage": st.session_state[f"v_{i}"],
                "Current": st.session_state[f"c_{i}"],
                "Temperature": st.session_state[f"t_{i}"],
                "Capacity": st.session_state[f"cap_{i}"],
                "Status": st.session_state[f"m_{i}"]
            }


# Simulate real-time values
now = datetime.now()
data = []
for i in range(num_cells):
    cell_id = f"Cell {i+1}"
    cell_data = st.session_state.manual_inputs.get(cell_id)
    if cell_data:
        data.append({
            "Time": now,
            "Cell": cell_id,
            **cell_data
        })
new_data = pd.DataFrame(data)
st.session_state.battery_data = pd.concat([st.session_state.battery_data, new_data])

# Limit to last 100 entries per cell
st.session_state.battery_data = st.session_state.battery_data.groupby("Cell").tail(100)

# Display latest values per cell
st.markdown("""
<h2 style='color: #111;'>📊 Cell Status Overview</h2>
""", unsafe_allow_html=True)

latest_data = new_data.set_index("Cell")

for i in range(0, num_cells, 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < num_cells:
            cell_id = f"Cell {i + j + 1}"
            if cell_id in latest_data.index:
                row = latest_data.loc[cell_id]
                status_icon = "🔺" if row["Status"] == "Charging" else ("🔻" if row["Status"] == "Discharging" else "⏸️")
                # Determine font color
                status_color = "#28a745" if row["Status"] == "Charging" else ("#dc3545" if row["Status"] == "Discharging" else "#000000")
                status_text = f"<span style='color: {status_color}; font-weight: bold;'>{status_icon} {row['Status']}</span>"

                with cols[j]:
                    st.markdown(f"""
                    <div style='border-radius: 16px; background-color: #e6f7ff; padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>
                        <h4 style='color: #007acc; margin-bottom: 10px;'>🔋 <b>{cell_id}</b></h4>
                        <p>⚙️ Mode: <b>{row['Status']}</b></p>
                        <p>🔌 Voltage: <b>{round(row['Voltage'],4)} V</b></p>
                        <p>⚡ Current: <b>{round(row['Current'],4)} A</b></p>
                        <p>🌡️ Temperature: <b>{round(row['Temperature'],2)} °C</b></p>
                        <p>📊 Capacity: <b>{round(row['Capacity'],4)} %</b></p>
                       <p>{status_text}</p>

                    </div>
                    """, unsafe_allow_html=True)

# Select cell to view detailed graph
selected_cell = st.selectbox("📊 Select Cell for Analysis", [f"Cell {i+1}" for i in range(num_cells)])
cell_data = st.session_state.battery_data[st.session_state.battery_data["Cell"] == selected_cell]
# print(cell_data)
# Time-series Graphs
st.subheader(f"📈 Time Series Analysis for {selected_cell} :")
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📈 Voltage Tracking Over Time ")

fig_voltage = go.Figure()
fig_voltage.add_trace(go.Scatter(x=cell_data["Time"], y=cell_data["Voltage"], mode='lines+markers',line=dict(color='blue'),name='Voltage'))
fig_voltage.update_layout(xaxis_title="Time", yaxis_title="Voltage (V)")
st.plotly_chart(fig_voltage, use_container_width=True)

st.subheader("⚡ Current Tracking Over Time")
fig_current = go.Figure()
fig_current.add_trace(go.Scatter(x=cell_data["Time"], y=cell_data["Current"], mode='lines+markers',line=dict(color='green'),name='Voltage'))
fig_current.update_layout(xaxis_title="Time", yaxis_title="Current (A)")
st.plotly_chart(fig_current, use_container_width=True)

st.subheader("🌡️ Temperature Tracking Over Time")
fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(x=cell_data["Time"], y=cell_data["Temperature"], mode='lines+markers',line=dict(color='red'),name='Voltage'))
fig_temp.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
st.plotly_chart(fig_temp, use_container_width=True)

# Health overview
st.subheader("🧭 System Health Overview")
avg_capacity = latest_data["Capacity"].mean()
st.metric("📊 Avg Capacity", f"{avg_capacity:.1f}%")

# Export
st.download_button("⬇️ Export CSV", data=st.session_state.battery_data.to_csv(index=False), file_name="battery_data.csv")

# Optional: auto-refresh logic
if auto_refresh:
    st.experimental_rerun()