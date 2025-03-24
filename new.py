import streamlit as st
import numpy_financial as npf  # Correct import for numpy-financial
import pandas as pd  # For data table display
import numpy as np
import math
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Function to calculate water volume
def calculate_water_volume(culture_type, species, yearly_production):
    if culture_type == "Intensive":
        culture_density = 80  # kg per m³
    elif culture_type == "Semi-Intensive":
        culture_density = 60  # kg per m³
    else:
        raise ValueError("Invalid culture type")

    if species == "Pabda":
        batch_per_year = 2.4  # batches per year
    elif species == "Gulsha":
        batch_per_year = 2.6  # batches per year
    else:
        raise ValueError("Invalid species")

    total_volume = yearly_production / (culture_density * batch_per_year)
    return round(total_volume, 2)

# Function to calculate payback period
def calculate_payback_period(cumulative_cash_flow):
    for year, cash in enumerate(cumulative_cash_flow):
        if cash >= 0:
            return year
    return None

# Function to print all results as text output
def print_results(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data, total_volume, tank_diameter, volume_per_tank):
    # Format IRR separately to avoid f-string formatting issues
    irr_display = f"{irr:.2%}" if irr is not None and not pd.isna(irr) else "N/A"

    report_text = (
        f"Initial Investment: {initial_investment:,.2f} BDT\n"
        f"Estimated Annual Revenue: {estimated_revenue:,.2f} BDT\n"
        f"Operational Cost per Year: {operational_cost:,.2f} BDT\n"
        f"Project Payback Period (Years): {payback_period if payback_period is not None else 'N/A'}\n"
        f"Internal Rate of Return (IRR): {irr_display}\n"
        f"Total Water Volume Required: {total_volume} m³\n"
        f"Tank Diameter: {tank_diameter} m\n"
        f"Total Volume per Tank: {volume_per_tank} m³\n"
    )

    st.markdown(
        """
        <style>
            .responsive-header h1 {
                color: green;
                text-decoration: underline;
                font-weight: bold;
                text-align: center;
                font-size: clamp(25px, 4vw, 35px);
                margin-bottom: 0px;
            }
        </style>
        <div class="responsive-header">
            <h1>Report Details</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.text_area("", report_text, height=300)

    st.subheader("Cash Flow Table")
    st.write(cash_flow_data)

    if st.button("Prepare Report"):
        pdf_buffer = generate_pdf_report(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data, total_volume, tank_diameter, volume_per_tank)
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer.getvalue(),
            file_name="financial_report.pdf",
            mime="application/pdf"
        )

# Function to generate PDF report using reportlab
def generate_pdf_report(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data, total_volume, tank_diameter, volume_per_tank):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Cost-Benefit Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Project Overview Section
    elements.append(Paragraph("Project Overview", styles["Heading2"]))
    report_text = (
        f"Initial Investment: {initial_investment:,.2f} BDT<br/>"
        f"Estimated Annual Revenue: {estimated_revenue:,.2f} BDT<br/>"
        f"Operational Cost per Year: {operational_cost:,.2f} BDT<br/>"
        f"Project Payback Period (Years): {payback_period if payback_period is not None else 'N/A'}<br/>"
        f"Internal Rate of Return (IRR): {f'{irr:.2%}' if irr is not None and not pd.isna(irr) else 'N/A'}<br/>"
        f"Total Water Volume Required: {total_volume} m³<br/>"
        f"Tank Diameter: {tank_diameter} m<br/>"
        f"Total Volume per Tank: {volume_per_tank} m³"
    )
    elements.append(Paragraph(report_text, styles["BodyText"]))
    elements.append(Spacer(1, 12))

    # Cash Flow Table
    elements.append(Paragraph("Cash Flow Chart", styles["Heading2"]))
    table_data = [["Year", "Cash In (BDT)", "Cash Out (BDT)", "Cumulative Cash Flow (BDT)"]]
    for i, row in cash_flow_data.iterrows():
        table_data.append([str(int(row["Year"])), f"{int(row['Cash In']):,}", f"{int(row['Cash Out']):,}", f"{int(row['Cumulative Cash Flow']):,}"])
    table = Table(table_data)
    table.setStyle([
        ("GRID", (0, 0), (-1, -1), 1, "black"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ])
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Financial Analysis and Comments
    elements.append(Paragraph("Financial Analysis and Comments", styles["Heading2"]))
    if pd.isna(irr) or irr is None:
        irr_comment = "The Internal Rate of Return (IRR) could not be calculated due to insufficient or undefined cash flows."
    elif irr > 0.20:
        irr_comment = f"The Internal Rate of Return (IRR) is {irr:.2%}, indicating high profitability."
    elif irr > 0.10:
        irr_comment = f"The Internal Rate of Return (IRR) is {irr:.2%}, suggesting moderate returns."
    else:
        irr_comment = f"The Internal Rate of Return (IRR) is {irr:.2%}, which is low and may indicate risks."

    if payback_period is None:
        payback_comment = "The payback period could not be calculated due to insufficient cash flows."
    elif payback_period < 3:
        payback_comment = f"The payback period is {payback_period} years, a quick return on investment."
    elif payback_period <= 5:
        payback_comment = f"The payback period is {payback_period} years, which is reasonable."
    else:
        payback_comment = f"The payback period is {payback_period} years, which is relatively long."

    combined_comment = f"{irr_comment} {payback_comment}"
    elements.append(Paragraph(combined_comment, styles["BodyText"]))
    elements.append(Spacer(1, 12))

    # Conclusion
    elements.append(Paragraph("Conclusion", styles["Heading2"]))
    if pd.isna(irr) or irr is None or payback_period is None:
        conclusion_text = "Financial viability could not be assessed due to missing data."
    elif irr > 0.20 and payback_period < 3:
        conclusion_text = "The project is highly attractive with excellent IRR and a short payback period."
    elif irr <= 0.10 or payback_period > 5:
        conclusion_text = "The project has low IRR and/or a long payback period, indicating potential risks."
    else:
        conclusion_text = "The project shows moderate viability; further evaluation is recommended."
    elements.append(Paragraph(conclusion_text, styles["BodyText"]))

    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit App Setup
css_code = """
    <style>
        .responsive-header {
            color: black;
        }
        .responsive-header h1 {
            text-decoration: underline;
            font-weight: bold;
            text-align: center;
            font-size: clamp(25px, 4vw, 35px);
            margin-bottom: 0px;
        }
        .responsive-header h2 {
            text-decoration: none;
            font-weight: normal;
            text-align: center;
            font-size: clamp(20px, 2.5vw, 25px);
            margin-top: 0px;
        }
        @media (prefers-color-scheme: dark) {
            .responsive-header {
                color: white;
            }
        }
    </style>
"""
st.markdown(css_code, unsafe_allow_html=True)
st.markdown("""
    <div class="responsive-header">
        <h1>Cost-Benefit Analysis Tool</h1>
        <h2>Developed by ITTI</h2>
    </div>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_section" not in st.session_state:
    st.session_state.current_section = "Project Plan"
if "plan_data" not in st.session_state:
    st.session_state.plan_data = {
        "culture_type": "Intensive",
        "species": "Pabda",
        "yearly_production": 20000.0,
        "tank_number": 4,
        "year_of_investment": 2024,
    }
if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "equipment_cost": 4500000.0,
        "land_cost": 1500000.0,
        "infrastructure_cost": 500000.0,
        "construction_labor_cost": 100000.0,
        "electricity_cost": 30000.0,
        "selling_price": 300.0,
        "fcr": 1.4,
        "salary_payment": 20000.0,
        "maintenance_cost": 120000.0,
        "marketing_cost": 120000.0,
        "fingerlings_cost": 2.0,
        "feed_cost": 110.0,
        "project_lifetime": 10,
    }

# Sidebar Navigation
with st.sidebar:
    st.markdown('<h1 style="color:green; text-decoration:underline; font-weight:bold;">ITTI-BCSIR</h1>', unsafe_allow_html=True)
    st.subheader(":green[Quick navigation]")
    if st.button("Project Plan"):
        st.session_state.current_section = "Project Plan"
    if st.button("Financial Information"):
        st.session_state.current_section = "Financial Information"
    if st.button("Results"):
        st.session_state.current_section = "Results"

# Project Plan Section
if st.session_state.current_section == "Project Plan":
    st.header("Project Plan")
    st.session_state.plan_data["culture_type"] = st.selectbox(
        "Select Culture Type", ["Intensive", "Semi-Intensive"], index=["Intensive", "Semi-Intensive"].index(st.session_state.plan_data["culture_type"])
    )
    st.session_state.plan_data["species"] = st.selectbox(
        "Select Fish Species", ["Pabda", "Gulsha"], index=["Pabda", "Gulsha"].index(st.session_state.plan_data["species"])
    )
    st.session_state.plan_data["yearly_production"] = st.number_input(
        "Desired Yearly Production (kg)", min_value=0.0, value=st.session_state.plan_data["yearly_production"], step=1.0
    )
    st.session_state.plan_data["tank_number"] = st.number_input(
        "Number of Tanks", min_value=1, max_value=10, value=st.session_state.plan_data["tank_number"], step=1
    )
    st.session_state.plan_data["year_of_investment"] = st.selectbox(
        "Year of Investment", [2024, 2025, 2026, 2027], index=[2024, 2025, 2026, 2027].index(st.session_state.plan_data["year_of_investment"])
    )
    if st.button("Next - Financial Information"):
        st.session_state.current_section = "Financial Information"

# Financial Information Section
if st.session_state.current_section == "Financial Information":
    st.header("Financial Information")
    st.subheader("Investment Costs")
    st.session_state.financial_data["equipment_cost"] = st.number_input(
        "Equipment Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["equipment_cost"], step=1000.0
    )
    st.session_state.financial_data["land_cost"] = st.number_input(
        "Land Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["land_cost"], step=1000.0
    )
    st.session_state.financial_data["infrastructure_cost"] = st.number_input(
        "Infrastructure Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["infrastructure_cost"], step=1000.0
    )
    st.session_state.financial_data["construction_labor_cost"] = st.number_input(
        "Construction Labor Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["construction_labor_cost"], step=1000.0
    )

    st.subheader("Operational Costs")
    electric_load_kwh = st.number_input("Electric Load Requirement (kWh)", min_value=0.0, value=30.0, step=10.0)
    hours_per_day, days_per_year = 20, 365
    yearly_electricity_demand = electric_load_kwh * hours_per_day * days_per_year
    electricity_rate = st.number_input("Electricity Rate (BDT per kWh)", min_value=0.0, value=8.0, step=1.0)
    st.session_state.financial_data["electricity_cost"] = yearly_electricity_demand * electricity_rate

    monthly_marketing_cost = st.number_input("Monthly Marketing Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["marketing_cost"] / 12, step=1000.0)
    st.session_state.financial_data["marketing_cost"] = monthly_marketing_cost * 12

    monthly_maintenance_cost = st.number_input("Monthly Maintenance Cost (BDT)", min_value=0.0, value=st.session_state.financial_data["maintenance_cost"] / 12, step=1000.0)
    st.session_state.financial_data["maintenance_cost"] = monthly_maintenance_cost * 12

    st.session_state.financial_data["fingerlings_cost"] = st.number_input("Fingerling Cost per Piece (BDT)", min_value=0.0, value=st.session_state.financial_data["fingerlings_cost"], step=0.1)
    yearly_production = st.session_state.plan_data["yearly_production"]
    fingerling_quantity = (yearly_production * 1000) / 40  # Assuming 40g final weight per fish
    total_fingerling_cost = st.session_state.financial_data["fingerlings_cost"] * fingerling_quantity

    st.subheader("Feed Cost")
    st.session_state.financial_data["fcr"] = st.number_input("Feed Conversion Ratio (FCR)", min_value=0.0, value=st.session_state.financial_data["fcr"], step=0.1)
    feed_cost_per_kg = st.number_input("Feed Cost per kg (BDT)", min_value=0.0, value=st.session_state.financial_data["feed_cost"], step=1.0)
    yearly_feed_requirement = st.session_state.financial_data["fcr"] * yearly_production
    st.session_state.financial_data["feed_cost"] = yearly_feed_requirement * feed_cost_per_kg

    st.subheader("Revenue Inputs")
    st.session_state.financial_data["selling_price"] = st.number_input("Selling Price per Unit (BDT)", min_value=0.0, value=st.session_state.financial_data["selling_price"], step=5.0)

    st.session_state.financial_data["salary_payment"] = st.number_input("Employee Salary per Year (BDT)", min_value=0.0, value=st.session_state.financial_data["salary_payment"], step=5000.0)
    st.session_state.financial_data["project_lifetime"] = st.number_input("Project Lifetime (Years)", min_value=1, value=st.session_state.financial_data["project_lifetime"], step=1)

    if st.button("Next - Results"):
        st.session_state.current_section = "Results"

# Results Section
if st.session_state.current_section == "Results":
    initial_investment = (
        st.session_state.financial_data["equipment_cost"] +
        st.session_state.financial_data["land_cost"] +
        st.session_state.financial_data["infrastructure_cost"] +
        st.session_state.financial_data["construction_labor_cost"]
    )
    operational_cost = (
        st.session_state.financial_data["electricity_cost"] +
        st.session_state.financial_data["marketing_cost"] +
        st.session_state.financial_data["maintenance_cost"] +
        total_fingerling_cost +
        st.session_state.financial_data["feed_cost"] +
        st.session_state.financial_data["salary_payment"]
    )
    revenue = st.session_state.plan_data["yearly_production"] * st.session_state.financial_data["selling_price"]

    cash_flow = [-initial_investment] + [revenue - operational_cost for _ in range(st.session_state.financial_data["project_lifetime"] - 1)]
    cumulative_cash_flow = [sum(cash_flow[:i+1]) for i in range(len(cash_flow))]
    irr = npf.irr(cash_flow)
    payback_period = calculate_payback_period(cumulative_cash_flow)

    total_volume = calculate_water_volume(
        st.session_state.plan_data["culture_type"],
        st.session_state.plan_data["species"],
        st.session_state.plan_data["yearly_production"]
    )
    tank_height, water_height = 1.5, 1.2
    tank_diameter = round(math.sqrt(total_volume * 4 / (3.1416 * water_height)), 2)
    final_water_volume = round((3.1416 * tank_diameter * tank_diameter * tank_height) / 4, 2)
    volume_per_tank = round(final_water_volume / st.session_state.plan_data["tank_number"], 2)

    years = [st.session_state.plan_data["year_of_investment"] + i for i in range(st.session_state.financial_data["project_lifetime"])]
    cash_flow_df = pd.DataFrame({
        "Year": years,
        "Cash In": [0] + [revenue] * (st.session_state.financial_data["project_lifetime"] - 1),
        "Cash Out": [initial_investment] + [operational_cost] * (st.session_state.financial_data["project_lifetime"] - 1),
        "Cumulative Cash Flow": cumulative_cash_flow
    })

    print_results(initial_investment, revenue, operational_cost, payback_period, irr, cash_flow_df, total_volume, tank_diameter, volume_per_tank)
