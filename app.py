from flask import Flask, render_template, request
import joblib
from datetime import datetime, timedelta

app = Flask(__name__)

# Load trained models
cost_model = joblib.load("models/cost_model.pkl")
delay_model = joblib.load("models/delay_model.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create")
def create():
    return render_template("create_project.html")

@app.route("/generate", methods=["POST"])
def generate():

    area = int(request.form["area"])
    total_workers = int(request.form["workers"])
    budget = int(request.form["budget"])
    project_type = request.form["project_type"]
    start_date = request.form["start_date"]

    # ---------------------------------
    # 🧠 AI WORKFORCE DISTRIBUTION
    # ---------------------------------

    # Smart dynamic distribution
    engineers = max(1, int(total_workers * 0.15))
    planners = max(1, int(total_workers * 0.10))
    inspectors = max(1, int(total_workers * 0.05))

    skilled_workers = int(total_workers * 0.30)
    labor_workers = total_workers - (engineers + planners + inspectors + skilled_workers)

    # ---------------------------------
    # 💰 COST BASED ON PROJECT TYPE
    # ---------------------------------

    cost_map = {
        "residential": 1500,
        "commercial": 2200,
        "road": 900,
        "bridge": 3000
    }

    base_cost = area * cost_map.get(project_type, 1500)

    # Workforce efficiency calculation
    efficiency_score = (
        engineers * 2 +
        planners * 1.5 +
        skilled_workers * 1.2 +
        labor_workers * 1
    ) / (area / 100 + 1)

    predicted_cost = base_cost * (1 + (1 - min(efficiency_score, 1)) * 0.25)

    # ---------------------------------
    # ⏳ DELAY CALCULATION
    # ---------------------------------

    base_delay = 60
    delay = base_delay / max(efficiency_score, 0.6)

    if budget < predicted_cost:
        shortage = (predicted_cost - budget) / predicted_cost
        delay += shortage * 60

    delay = max(15, min(delay, 200))

    # ---------------------------------
    # ⚠ RISK SCORE
    # ---------------------------------

    risk_score = int(
        min(100,
            (delay / 150) * 60 +
            max(0, (predicted_cost - budget) / predicted_cost * 40)
        )
    )

    # ---------------------------------
    # 📅 COMPLETION DATE
    # ---------------------------------

    completion_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=int(delay))

    # ---------------------------------
    # 💰 COST BREAKDOWN
    # ---------------------------------

    material_cost = predicted_cost * 0.5
    labor_cost = predicted_cost * 0.3
    equipment_cost = predicted_cost * 0.15
    misc_cost = predicted_cost * 0.05

    # ---------------------------------
    # 🕒 TIME BREAKDOWN BY ROLE
    # ---------------------------------

    planning_time = delay * 0.20
    engineering_time = delay * 0.25
    execution_time = delay * 0.40
    inspection_time = delay * 0.15
    # -----------------------------
# 🧠 AI WORKFORCE RECOMMENDATION
# -----------------------------

    if total_workers < area / 150:
        recommendation = "Increase workforce to avoid major delays."
    elif total_workers > area / 80:
        recommendation = "Workforce is high. You may optimize labor cost."
    else:
        recommendation = "Workforce allocation looks balanced."

    required_workers_estimate = int(area / 100)

    return render_template(
        "dashboard.html",
        cost=round(predicted_cost, 2),
        delay=round(delay, 2),
        completion=completion_date.date(),
        risk=risk_score,
        material=round(material_cost, 2),
        labor=round(labor_cost, 2),
        equipment=round(equipment_cost, 2),
        misc=round(misc_cost, 2),
        recommendation=recommendation,
        required_workers=required_workers_estimate,

        # Workforce distribution
        engineers=engineers,
        planners=planners,
        skilled_workers=skilled_workers,
        labor_workers=labor_workers,
        inspectors=inspectors,

        # Time breakdown
        planning_time=round(planning_time,2),
        engineering_time=round(engineering_time,2),
        execution_time=round(execution_time,2),
        inspection_time=round(inspection_time,2)
    )


if __name__ == "__main__":
    app.run(debug=True)