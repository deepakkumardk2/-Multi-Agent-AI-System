import os
import threading
from flask import Flask, render_template, jsonify, request
from agents import demand_run, inventory_run, pricing_run
from visualization import (
    generate_agent_network,
    generate_inventory_dashboard,
    generate_pricing_chart,
    generate_forecasting_comparison,
    generate_agent_conversation_viewer,
    generate_agent_results_tables,
    generate_demand_analysis_chart,
    generate_scenario_chart
)
import sqlite3
import ollama  # Import ollama for the Ask feature

app = Flask(__name__)

# Global variable to simulate agent status (running/closed)
agents_running = False

@app.route('/')
def index():
    # Generate visualization components
    network_file = generate_agent_network()  # returns filename in static folder
    inventory_dashboard_html = generate_inventory_dashboard()
    pricing_chart_html = generate_pricing_chart()
    # Demand forecasting chart rendered full screen (via style in template)
    forecasting_chart_html = generate_forecasting_comparison()
    conversation_viewer_html = generate_agent_conversation_viewer()
    demand_analysis_chart = generate_demand_analysis_chart()
    scenario_chart = generate_scenario_chart(1.0)  # default scenario factor
    
    return render_template('index.html',
                           network_file=network_file,
                           inventory_dashboard=inventory_dashboard_html,
                           pricing_chart=pricing_chart_html,
                           forecasting_chart=forecasting_chart_html,
                           conversation_viewer=conversation_viewer_html,
                           demand_analysis_chart=demand_analysis_chart,
                           scenario_chart=scenario_chart)

@app.route('/run_agents', methods=['POST'])
def run_agents():
    global agents_running
    agents_running = True  # Mark agents as running
    threads = []
    results = {}

    def run_agent(agent_func, agent_name):
        result = agent_func()
        results[agent_name] = result

    agents = [
        (demand_run, "Demand Forecasting"),
        (inventory_run, "Inventory Monitoring"),
        (pricing_run, "Pricing Optimization")
    ]
    
    for func, name in agents:
        t = threading.Thread(target=run_agent, args=(func, name))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    tables_html = generate_agent_results_tables(results)
    return jsonify({"tables_html": tables_html})

@app.route('/close_agents', methods=['POST'])
def close_agents():
    global agents_running
    agents_running = False
    return jsonify({"message": "Agents have been closed."})

@app.route('/search', methods=['GET'])
def search():
    store_id = request.args.get('store_id')
    product_id = request.args.get('product_id')
    # Simple search in the inventory_status and pricing_status tables
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'inventory.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM inventory_status WHERE `Store ID`=? AND `Product ID`=?"
    cursor.execute(query, (store_id, product_id))
    inventory_result = [dict(row) for row in cursor.fetchall()]
    query2 = "SELECT * FROM pricing_status WHERE `Store ID`=? AND `Product ID`=?"
    cursor.execute(query2, (store_id, product_id))
    pricing_result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"inventory": inventory_result, "pricing": pricing_result})

@app.route('/simulate_scenario', methods=['POST'])
def simulate_scenario():
    # Read scenario factor from POST data (e.g., a multiplier for demand)
    factor = float(request.form.get('factor', 1.0))
    # Generate a new scenario chart based on the factor
    scenario_chart = generate_scenario_chart(factor)
    return jsonify({"scenario_chart": scenario_chart})

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    
    # Check if the question is related to the database details
    keywords = ["database", "inventory", "pricing", "stock", "product"]
    if any(kw in question.lower() for kw in keywords):
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'inventory.db')
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch counts as a simple summary from key tables
            cursor.execute("SELECT COUNT(*) as count FROM inventory_status")
            inventory_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM pricing_status")
            pricing_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM demand_forecast")
            demand_count = cursor.fetchone()["count"]
            conn.close()
            
            db_summary = (f"Database Summary:\n"
                          f"- Inventory records: {inventory_count}\n"
                          f"- Pricing records: {pricing_count}\n"
                          f"- Demand forecast records: {demand_count}\n")
        except Exception as e:
            db_summary = f"Error fetching database summary: {str(e)}"
        
        prompt_text = question + "\n" + db_summary
    else:
        prompt_text = question

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt_text}])
    
    answer = response.message.content if hasattr(response, 'message') else str(response)
    formatted_answer = answer  # You may format the answer further if needed
    return jsonify({"answer": formatted_answer})

if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)
