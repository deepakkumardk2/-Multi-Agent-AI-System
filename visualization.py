import os
import uuid
import sqlite3
import matplotlib
# Use non-interactive backend to avoid GUI/Tkinter issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyvis.network import Network
import plotly.graph_objects as go
import altair as alt
import pandas as pd
import shap
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Disable Altair max rows transformer for large data
alt.data_transformers.disable_max_rows()

def generate_agent_network():
    """
    Generate a network diagram with a radial layout and customized node/edge styles.
    """
    net = Network(height="600px", width="100%", directed=True)
    
    # Customize physics for a radial layout
    net.barnes_hut(gravity=-20000, central_gravity=0.3, spring_length=250, spring_strength=0.001)
    
    # Simulated numerical data for each agent
    store_info = "Store\nOrders: 150\nStockouts: 20"
    warehouse_info = "Warehouse\nCapacity: 80%\nBacklog: 5"
    supplier_info = "Supplier\nLead Time: 3d\nOn-Time: 95%"
    customer_info = "Customer\nAvg. Satisfaction: 4.5"
    
    # Add nodes with larger size and updated styling
    net.add_node("Store", label=store_info, title=store_info, color="#2ecc71", size=25)
    net.add_node("Warehouse", label=warehouse_info, title=warehouse_info, color="#3498db", size=30)
    net.add_node("Supplier", label=supplier_info, title=supplier_info, color="#e67e22", size=25)
    net.add_node("Customer", label=customer_info, title=customer_info, color="#9b59b6", size=20)
    
    # Add edges with thickness and smooth curves
    net.add_edge("Supplier", "Warehouse", label="Supply", width=2, arrows="to")
    net.add_edge("Warehouse", "Store", label="Deliver", width=3, arrows="to")
    net.add_edge("Store", "Customer", label="Sell", width=2, arrows="to")
    
    filename = f"network_{uuid.uuid4().hex}.html"
    filepath = os.path.join("static", filename)
    net.show(filepath, notebook=False)
    return filename

def generate_inventory_dashboard():
    """
    Create a Plotly gauge chart for warehouse capacity utilization.
    """
    inventory_level = 70  # simulated value (70%)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=inventory_level,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Warehouse Capacity Utilization (%)"}
    ))
    return fig.to_html(full_html=False)

def generate_pricing_chart():
    """
    Generates an enlarged, interactive dynamic pricing chart.
    The chart displays pricing fluctuations for a selected store via a dropdown menu.
    Hover labels are customized for clarity.
    """
    db_path = os.path.join(os.path.dirname(__file__), 'inventory.db')
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM pricing_status", conn)
        conn.close()
    except Exception:
        csv_path = os.path.join("test_data", "pricing_optimization.csv")
        df = pd.read_csv(csv_path)
    
    if 'Date' not in df.columns:
        df['Date'] = pd.date_range("2025-01-01", periods=len(df))
    
    # Determine the store column: use "Store ID" if available, else try "Store"
    if "Store ID" in df.columns:
        store_column = "Store ID"
    elif "Store" in df.columns:
        store_column = "Store"
    else:
        return "<h3>No store information available in pricing data.</h3>"
    
    store_ids = sorted(df[store_column].unique())
    
    # If there are no store_ids, return a message
    if not store_ids:
        return "<h3>No store records found in pricing data.</h3>"
    
    # Create a trace for each store; by default, all traces are hidden except for the first store.
    traces = []
    for store in store_ids:
        store_df = df[df[store_column] == store]
        trace = go.Scatter(
            x=store_df['Date'],
            y=store_df['Optimized_Price'],
            mode='lines+markers',
            name=f"Store {store}",
            visible=False,
            hovertemplate='Date: %{x}<br>Optimized Price: $%{y:.2f}<extra></extra>'
        )
        traces.append(trace)
    traces[0]['visible'] = True  # Show the first store by default
    
    # Build update buttons so that each button shows only one store's trace.
    buttons = []
    for store in store_ids:
        visible = [True if s == store else False for s in store_ids]
        buttons.append({
            "method": "update",
            "label": f"Store {store}",
            "args": [{"visible": visible},
                     {"title": f"Dynamic Pricing Fluctuations for Store {store}"}]
        })
    updatemenus = [{
        "buttons": buttons,
        "direction": "down",
        "showactive": True,
        "x": 0.1,
        "y": 1.15,
        "xanchor": "left",
        "yanchor": "top"
    }]
    
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=f"Dynamic Pricing Fluctuations for Store {store_ids[0]}",
        xaxis_title="Date",
        yaxis_title="Optimized Price ($)",
        updatemenus=updatemenus,
        width=1200,
        height=700,
        legend=dict(x=0, y=1),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig.to_html(full_html=False)

def generate_forecasting_comparison():
    """
    Generates a full-screen Plotly bar chart that mimics a SHAP summary for demand forecasting feature importance.
    This chart is designed to be large and human-friendly.
    """
    # Generate dummy data for demonstration
    X_dummy = pd.DataFrame(np.random.randn(100, 5), columns=[f"Feature_{i}" for i in range(5)])
    y_dummy = np.random.randn(100)
    model = RandomForestRegressor()
    model.fit(X_dummy, y_dummy)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_dummy)
    
    avg_shap = np.abs(shap_values).mean(axis=0)
    fig = go.Figure([go.Bar(x=list(X_dummy.columns), y=avg_shap, marker_color='indianred')])
    fig.update_layout(
        title="Demand Forecasting Feature Importance",
        width=1200,
        height=700,
        xaxis_title="Features",
        yaxis_title="Average SHAP Value",
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig.to_html(full_html=False)

def generate_agent_conversation_viewer():
    """
    Generates an HTML table displaying agent conversation data.
    """
    conversations = [
        {"From": "Store", "Message": "Requesting stock update", "Time": "10:00"},
        {"From": "Warehouse", "Message": "Stock level confirmed", "Time": "10:01"},
        {"From": "Supplier", "Message": "Shipment dispatched", "Time": "10:02"},
        {"From": "Store", "Message": "Price update inquiry", "Time": "10:03"},
        {"From": "Pricing", "Message": "Dynamic pricing adjusted", "Time": "10:04"}
    ]
    html = '<table border="1" style="width:100%; border-collapse: collapse;">'
    html += "<tr style='background-color:#f2f2f2;'><th>From</th><th>Message</th><th>Time</th></tr>"
    for conv in conversations:
        html += f"<tr><td>{conv['From']}</td><td>{conv['Message']}</td><td>{conv['Time']}</td></tr>"
    html += "</table>"
    return html

def generate_agent_results_tables(results):
    """
    Generates separate HTML tables for each agent's results.
    """
    html = ""
    for agent, data in results.items():
        html += f"<h3>{agent} Results</h3>"
        html += '<table border="1" style="width:100%; border-collapse: collapse;">'
        if data:
            headers = data[0].keys()
            html += "<tr style='background-color:#d9edf7;'>" + "".join(f"<th>{header}</th>" for header in headers) + "</tr>"
            for row in data:
                html += "<tr>" + "".join(f"<td>{row.get(header, '')}</td>" for header in headers) + "</tr>"
        else:
            html += "<tr><td>No data available</td></tr>"
        html += "</table>"
    return html

def generate_demand_analysis_chart():
    """
    Creates a grouped bar chart for high vs low demanding products.
    """
    db_path = os.path.join(os.path.dirname(__file__), 'inventory.db')
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM demand_forecast", conn)
        conn.close()
    except Exception:
        df = pd.DataFrame({
            "Product ID": [101, 102, 103, 104],
            "Forecasted Sales": [50, 30, 80, 20]
        })
    avg_demand = df["Forecasted Sales"].mean()
    df["Demand Category"] = df["Forecasted Sales"].apply(lambda x: "High" if x >= avg_demand else "Low")
    
    colors = {"High": "crimson", "Low": "royalblue"}
    fig = go.Figure()
    for category in df["Demand Category"].unique():
        sub_df = df[df["Demand Category"] == category]
        fig.add_trace(go.Bar(
            x=sub_df["Product ID"],
            y=sub_df["Forecasted Sales"],
            name=category,
            marker_color=colors[category]
        ))
    fig.update_layout(
        title="High vs Low Demanding Products",
        xaxis_title="Product ID",
        yaxis_title="Forecasted Sales",
        barmode="group",
        width=1000,
        height=600,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig.to_html(full_html=False)

def generate_scenario_chart(factor):
    """
    Generates a scenario chart comparing base demand with demand adjusted by a factor.
    """
    products = ["A", "B", "C", "D", "E"]
    base_demand = np.array([50, 30, 80, 20, 60])
    new_demand = base_demand * factor
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=products, y=base_demand, mode='lines+markers', name='Base Demand'))
    fig.add_trace(go.Scatter(x=products, y=new_demand, mode='lines+markers', name='Scenario Demand'))
    fig.update_layout(
        title=f"Scenario Playground Chart (Factor: {factor})",
        width=800,
        height=500,
        xaxis_title="Products",
        yaxis_title="Demand",
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig.to_html(full_html=False)
