import streamlit as st
import numpy_financial as npf  # For IRR calculation
import pandas as pd  # For data table display
from fpdf import FPDF
import numpy as np
import math
import io



def calculate_water_volume(culture_type, species, yearly_production):  #this code is okay.

    # Set the culture density based on culture type
    if culture_type == "Intensive":
        culture_density = 80  # kg per m³
    elif culture_type == "Semi-Intensive":
        culture_density = 60  # kg per m³
    else:
        raise ValueError("Invalid culture type")

    # Set the batch per year based on species
    if species == "Pabda":
        batch_per_year = 2.4  # batches per year
        final_size = 45 # gm
    elif species == "Gulsha":
        batch_per_year = 2.6  # batches per year
        final_size = 35 # gm
    else:
        raise ValueError("Invalid species")

    # Calculate the total volume
    total_volume = yearly_production / (culture_density * batch_per_year)
    return round(total_volume,2)

# Example usage
culture_type = "Intensive"
species = "Gulsha"
yearly_production = 3000  # kg


try:
    volume = calculate_water_volume(culture_type, species, yearly_production)
    print(f"Total water volume required: {volume:.2f} m³")
except ValueError as e:
    print(e)


# Function to calculate payback period
def calculate_payback_period(cumulative_cash_flow):
    """
    Calculate the payback period, i.e., the year at which cumulative cash flow becomes positive.
    Returns the year (payback period).
    """
    for year, cash in enumerate(cumulative_cash_flow):
        if cash >= 0:
            return year  # Return the year (payback period)
    return None  # If no payback, return None

# Function to print all results as text output
def print_results(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data):
    report_text = (
        f"Initial Investment: {initial_investment} BDT\n"
        f"Estimated Annual Revenue: {estimated_revenue} BDT\n"
        f"Operational Cost per Year: {operational_cost} BDT\n"
        f"Project Payback Period (Years): {payback_period}\n"
        f"Internal Rate of Return (IRR): {irr:.2%}\n"
        f"Total Water Volume Required: {total_volume} m³\n"
        f"Tank Diameter: {tank_diameter} m\n"
        f"Total Volume per Tank: {volume_per_tank} m³\n"
    )

    # Display the report as text in Streamlit
    st.markdown(
    """
    <style>
        .responsive-header h1 {
            color: green;
            text-decoration: underline;
            font-weight: bold;
            text-align: center;
            font-size: clamp(25px, 4vw, 35px); /* Min: 25px, Preferred: 4vw, Max: 35px */
            margin-bottom: 0px;
        }
    </style>
    <div class="responsive-header">
        <h1>Report Details</h1>

    </div>
    """,
    unsafe_allow_html=True
)

    st.text_area("", report_text, height=300,)

    # Display cash flow table
    st.subheader("Cash Flow Table")
    st.write(cash_flow_data)

    # Add download button for the PDF
    if st.button("Prepare Report"):
        pdf_output = generate_pdf_report(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data)
        st.download_button("Download PDF Report", data=pdf_output, file_name="financial_report.pdf")




def generate_pdf_report(initial_investment, estimated_revenue, operational_cost, payback_period, irr, cash_flow_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Times", 'B', size=16)
    pdf.cell(200, 10, txt="Cost-Benefit Analysis Report", ln=True, align="C")
    pdf.ln(10)


# Project Plan Section
    #pdf.set_font("Times", 'BU', size=12)
    #pdf.cell(200, 10, txt="Project Plan", ln=True, align='L')
    #pdf.set_font("Times", size=10)

    #report_text = (

    #f"Fish Species: {species}\n"
    #f"Yearly Production: {yearly_production:,.2f} Kg\n"
     # )
#
 #   pdf.multi_cell(0, 7, report_text) # Space between lines
  #  pdf.ln(1)





    # General Information Section
    pdf.set_font("Times", 'BU', size=12)
    pdf.cell(200, 10, txt="Project Overview", ln=True, align='L')
    pdf.set_font("Times", size=10)
    report_text = (

    f"Initial Investment: {initial_investment:,.2f} BDT\n"
    f"Estimated Annual Revenue: {estimated_revenue:,.2f} BDT\n"
    f"Operational Cost per Year: {operational_cost:,.2f} BDT\n"
    f"Project Payback Period (Years): {payback_period if payback_period is not None else 'N/A'}\n"
    f"Internal Rate of Return (IRR): {round(irr*100,2) if irr is not None and not pd.isna(irr) else 'N/A'}\n"

    )
    pdf.multi_cell(0, 7, report_text) # Space between lines
    pdf.ln(1)







    # Cash Flow Table Header
    pdf.set_font("Times", 'BU', size=12)
    pdf.cell(200, 10, txt="Cash Flow Chart", ln=True, align='L')


    pdf.set_font("Times", 'B', size=10)
    pdf.cell(30, 10, "Year", border=1, align="C")
    pdf.cell(45, 10, "Cash In (BDT)", border=1, align="C")
    pdf.cell(45, 10, "Cash Out (BDT)", border=1, align="C")
    pdf.cell(60, 10, "Cumulative Cash Flow (BDT)", border=1, align="C")
    pdf.ln()

    # Cash Flow Table Data
    pdf.set_font("Times", size=10)
    for i, row in cash_flow_data.iterrows():
        pdf.cell(30, 10, str(int(row['Year'])), border=1, align="C")
        pdf.cell(45, 10, f"{int(row['Cash In']):,}", border=1, align="R")
        pdf.cell(45, 10, f"{int(row['Cash Out']):,}", border=1, align="R")
        pdf.cell(60, 10, f"{int(row['Cumulative Cash Flow']):,}", border=1, align="R")
        pdf.ln()

    # Comments Section with Customized Text for IRR, Payback Period, and General Summary
    pdf.ln(10)  # Add some space before the comments
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(200, 10, txt="Financial Analysis and Comments", ln=True)
    pdf.set_font("Times", size=10)

    # Handling None or NaN values for IRR and Payback Period
    if pd.isna(irr) or irr is None:
        irr_comment = "The Internal Rate of Return (IRR) could not be calculated due to insufficient or undefined cash flows. Further analysis may be required."
    elif irr > 0.20:
        irr_comment = (
            f"The Internal Rate of Return (IRR) is {irr:.2%}, which is excellent. This indicates the project will likely generate high returns and is highly attractive for investors. "
            "The project is considered highly viable, and you can expect significant profitability over the project's life."
        )
    elif irr > 0.10:
        irr_comment = (
            f"The Internal Rate of Return (IRR) is {irr:.2%}, which suggests a good but moderate return on investment. "
            "While this indicates financial viability, the returns are not extraordinary, so it is important to carefully evaluate other factors, such as risk and market conditions."
        )
    else:
        irr_comment = (
            f"The Internal Rate of Return (IRR) is {irr:.2%}, which is on the lower side. "
            "This suggests that the project may not meet typical profitability thresholds and could be considered risky for investors. "
            "You may need to reconsider the project's assumptions or look for ways to improve its financial outlook."
        )

    # Handling None or NaN values for Payback Period
    if payback_period is None:
        payback_comment = "The payback period could not be calculated due to insufficient or undefined cash flows. Further analysis may be required."
    elif payback_period < 3:
        payback_comment = (
            f"The payback period is estimated to be {payback_period} years, which is considered a quick return on investment. "
            "This is an attractive feature for investors as they can recoup their initial investment within a short period."
        )
    elif payback_period <= 5:
        payback_comment = (
            f"The payback period is estimated to be {payback_period} years, which is reasonable. "
            "While this is a moderate return period, it is still within an acceptable range for most investors who are comfortable with moderate investment horizons."
        )
    else:
        payback_comment = (
            f"The payback period is estimated to be {payback_period} years, which is relatively long. "
            "This means that the project will take a longer time to recoup the initial investment. "
            "Some investors might find this less attractive, particularly those looking for quicker returns."
        )

    # Combine IRR and Payback Period Comments
    combined_comment = f"{irr_comment} {payback_comment}"

    # Add the combined comment using multi_cell for proper text wrapping
    pdf.multi_cell(0, 5, combined_comment)
    pdf.ln(10)

    # Conclusion Section - Dynamic Summary
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(200, 10, txt="Conclusion", ln=True)
    pdf.set_font("Times", size=10)

    # Dynamic Conclusion based on IRR and Payback Period
    if pd.isna(irr) or irr is None or pd.isna(payback_period) or payback_period is None:
        conclusion_text = (
            "The financial viability of this project could not be assessed due to missing or insufficient data. "
            "Further analysis is required to calculate the IRR and Payback Period accurately before making any investment decisions."
        )
    elif irr > 0.20 and payback_period < 3:
        conclusion_text = (
            "The project has an excellent IRR and a short payback period, indicating strong financial viability. "
            "This project is highly attractive for investors seeking quick returns and high profitability. "
            "Based on these factors, the project appears to be an excellent investment opportunity."
        )
    elif irr > 0.20 and payback_period <= 5:
        conclusion_text = (
            "The project has a high IRR and a reasonable payback period, indicating solid financial viability. "
            "While the payback period is not the shortest, the strong return on investment makes this a favorable project. "
            "It is a good opportunity for investors seeking moderate to high returns."
        )
    elif irr <= 0.20 and irr > 0.10 and payback_period <= 5:
        conclusion_text = (
            "The project shows a moderate IRR and a reasonable payback period, suggesting that it is financially viable, "
            "but the returns are not extraordinary. Investors with a moderate risk appetite and investment horizon may find this project suitable."
        )
    elif irr <= 0.10 or payback_period > 5:
        conclusion_text = (
            "The project has a low IRR and/or a long payback period, which indicates potential financial risks. "
            "It may not be an attractive option for investors looking for quick returns or high profitability. "
            "Further analysis and a careful assessment of risks are recommended before proceeding with the investment."
        )

    pdf.multi_cell(0, 5, conclusion_text)
    pdf.ln(2)

    # Footer with page number
# Set the position to be near the bottom of the page
    #pdf.set_y(-15)  # Set the vertical position for the footer (near bottom)

# Footer with page number
    #pdf.set_font("Arial", 'I', size=8)
    #pdf.cell(200, 10, txt="Page %s" % pdf.page_no(), ln=True, align="C")

    # Output PDF to memory
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Sample DataFrame for Cash Flow (for testing purposes)
data = {
    "Year": [2024, 2025, 2026, 2027, 2028],
    "Cash In": [100000, 150000, 200000, 250000, 300000],
    "Cash Out": [50000, 60000, 70000, 80000, 90000],
    "Cumulative Cash Flow": [100000, 190000, 290000, 390000, 490000]
}
cash_flow_df = pd.DataFrame(data)

# Example Function Call (Pass the required parameters)
generate_pdf_report(1000000, 1500000, 300000, 4, 0.18, cash_flow_df)



# Initialize Streamlit app

css_code = """
    <style>
        .responsive-header {
            color: black; /* Default color for light mode */
        }

        .responsive-header h1 {
            text-decoration: underline;
            font-weight: bold;
            text-align: center;
            font-size: clamp(25px, 4vw, 35px); /* Min: 25px, Preferred: 4vw, Max: 35px */
            margin-bottom: 0px;
        }

        .responsive-header h2 {
            text-decoration: none;
            font-weight: normal;
            text-align: center;
            font-size: clamp(20px, 2.5vw, 25px); /* Min: 20px, Preferred: 2.5vw, Max: 25px */
            margin-top: 0px;
        }

        /* Dark mode styling */
        @media (prefers-color-scheme: dark) {
            .responsive-header {
                color: white; /* White for dark mode */
            }
        }
    </style>
"""

# Display the CSS and HTML in Streamlit
st.markdown(css_code, unsafe_allow_html=True)

# Add the HTML content
st.markdown("""
    <div class="responsive-header">
        <h1>Cost-Benefit Analysis Tool</h1>
        <h2>Developed by ITTI</h2>
    </div>
""", unsafe_allow_html=True)



# Initialize session state for navigation and persistent values
if "current_section" not in st.session_state:
    st.session_state.current_section = "Project Plan"
if "plan_data" not in st.session_state:
    st.session_state.plan_data = {
        "culture_type": "Intensive",
        "species": "Pabda",
        "yearly_production": 20000.0,  # Start with a float value for production
        "tank_number": 4,
        "year_of_investment": 2024,
    }
if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "initial_investment": 4500000.0,  # Realistic initial investment (BDT)
        "equipment_cost": 4500000.0,
        "land_cost": 1500000.0,
        "infrastructure_cost": 500000.0,
        "construction_labor_cost": 100000.0,
        "electricity_cost": 30000.0,
        "selling_price": 300.0,  # Selling price per kg of fish
        "fcr": 1.4,  # Feed Conversion Ratio
        "salary_payment": 20000.0,  # Annual salary payments
        "maintenance_cost": 120000.0,
        "marketing_cost": 120000.0,
        "other_cost": 120000.0,
        "fingerlings_cost": 2.0,  # Cost per fingerling
        "feed_cost": 110.0,  # Cost per kg of feed
        "project_lifetime": 10,
    }

# Sidebar Navigation
with st.sidebar:

    st.markdown(
    '<h1 style="color:green; text-decoration:underline; font-weight:bold;">ITTI-BCSIR</h1>',
    unsafe_allow_html=True
)
    st.subheader(":green[Quick navigation]")
    if st.button("Project Plan"):
        st.session_state.current_section = "Project Plan"
    if st.button("Financial Information"):
        st.session_state.current_section = "Financial Information"
    if st.button("Results"):
        st.session_state.current_section = "Results"

# Section: Project Plan
if st.session_state.current_section == "Project Plan":
    st.header("Project Plan")

    # Persist Plan data
    st.session_state.plan_data["culture_type"] = st.selectbox(
        "Select Culture Type",
        ["Intensive", "Semi-Intensive"],
        index=["Intensive", "Semi-Intensive"].index(st.session_state.plan_data["culture_type"]),
    )
    st.session_state.plan_data["species"] = st.selectbox(
        "Select Fish Species",
        ["Pabda", "Gulsha"],
        index=["Pabda", "Gulsha"].index(st.session_state.plan_data["species"]),
    )



    st.session_state.plan_data["yearly_production"] = st.number_input(
        "Desired Yearly Production (kg)",
        min_value=0.0,  # Float to ensure consistency
        value=st.session_state.plan_data["yearly_production"],
        step=1.0,  # Step should also be a float for consistency

    )



    st.session_state.plan_data["tank_number"] = st.number_input(
        "Number of Tanks",
        min_value=1,
        max_value=10,
        value=st.session_state.plan_data["tank_number"],
        step=1,
    )
    st.session_state.plan_data["year_of_investment"] = st.selectbox(
        "Year of Investment",
        [2024, 2025, 2026, 2027],
        index=[2024, 2025, 2026, 2027].index(st.session_state.plan_data["year_of_investment"]),
    )


    if st.button("Next - Financial Information"):
        st.session_state.current_section = "Financial Information"

# Section: Financial Information
if st.session_state.current_section == "Financial Information":
    st.header("Financial Information")

    # Financial Inputs Section
    st.subheader("Investment Costs")
    st.session_state.financial_data["equipment_cost"] = st.number_input(
        "Equipment Cost (BDT)",
        min_value=0.0,
        value=st.session_state.financial_data["equipment_cost"],
        step=1000.0,
    )
    st.session_state.financial_data["land_cost"] = st.number_input(
        "Land Cost (BDT)",
        min_value=0.0,
        value=st.session_state.financial_data["land_cost"],
        step=1000.0,
    )
    st.session_state.financial_data["infrastructure_cost"] = st.number_input(
        "Infrastructure Cost (BDT)",
        min_value=0.0,
        value=st.session_state.financial_data["infrastructure_cost"],
        step=1000.0,
    )
    st.session_state.financial_data["construction_labor_cost"] = st.number_input(
        "Construction Labor Cost (BDT)",
        min_value=0.0,
        value=st.session_state.financial_data["construction_labor_cost"],
        step=1000.0,
    )

    # Operational Costs
    st.subheader("Operational Costs")



    # Input for Electric Load Requirement
    electric_load_kwh = st.number_input(
    "Electric Load Requirement (kWh)",
    min_value=0.0,
    value=st.session_state.financial_data.get("electric_load_kwh", 30.0),
    step=100.0,
    )
    st.session_state.financial_data["electric_load_kwh"] = electric_load_kwh

    # Assuming 20 hours of operation per day
    hours_per_day = 20
    days_per_year = 365
    yearly_electricity_demand = electric_load_kwh * hours_per_day * days_per_year
    st.session_state.financial_data["electricity_demand"] = yearly_electricity_demand

    # Input for Electricity Rate
    electricity_rate = st.number_input(
    "Electricity Rate (BDT per kWh)",
    min_value=0.0,
    value=st.session_state.financial_data.get("electricity_rate", 8.0),
    step=1.0,
    )
    st.session_state.financial_data["electricity_rate"] = electricity_rate

    # Calculate Yearly Electric Cost
    yearly_electric_cost = yearly_electricity_demand * electricity_rate
    st.session_state.financial_data["yearly_electric_cost"] = yearly_electric_cost

    # Display Yearly Electric Cost
   # st.write(f"Yearly Electric Cost: {yearly_electric_cost:.2f} BDT")





    # Input for Monthly Marketing Cost (BDT)
    monthly_marketing_cost = st.number_input(
    "Monthly Marketing Cost (BDT)",
    min_value=0.0,
    value=st.session_state.financial_data["marketing_cost"] / 12,  # Default to 1/12th of yearly value if already set
    step=1000.0,
    )

    # Update the monthly marketing cost in session state
    st.session_state.financial_data["marketing_cost"] = monthly_marketing_cost * 12  # Calculate yearly cost

    # Display the calculated yearly marketing cost
   # st.write(f"Yearly Marketing Cost: {st.session_state.financial_data['marketing_cost']:.2f} BDT")



    # Input for Monthly Maintenance Cost (BDT)
    monthly_maintenance_cost = st.number_input(
    "Monthly Maintenance Cost (BDT)",
    min_value=0.0,
    value=st.session_state.financial_data["maintenance_cost"] / 12,  # Default to 1/12th of yearly value if already set
    step=1000.0,
    )

    # Update the monthly maintenance cost in session state
    st.session_state.financial_data["maintenance_cost"] = monthly_maintenance_cost * 12  # Calculate yearly cost

    # Display the calculated yearly maintenance cost
   # st.write(f"Yearly Maintenance Cost: {st.session_state.financial_data['maintenance_cost']:.2f} BDT")






    # Input for Fingerling Cost per piece (BDT)
    fingerling_cost_per_piece = st.number_input(
    "Fingerling Cost per Piece (BDT)",
    min_value=0.0,
    value=st.session_state.financial_data["fingerlings_cost"],
    step=10.0,
    )

    # Store the fingerling cost per piece
    st.session_state.financial_data["fingerlings_cost"] = fingerling_cost_per_piece

    # Get yearly production from the plan_data dictionary (already set in your previous code)
    yearly_production = st.session_state.plan_data.get("yearly_production", 3000)  # in kg



    # Calculate fingerling quantity
    fingerling_quantity = (yearly_production * 1000) / 40  # Fingerling quantity in pieces

    # Calculate total fingerling cost
    total_fingerling_cost = fingerling_cost_per_piece * fingerling_quantity

    #  Display the calculated fingerling quantity and total cost
   # st.write(f"Total Fingerling Quantity: {fingerling_quantity:.0f} pieces")
    st.write(f"Total Fingerling Cost: {total_fingerling_cost:.2f} BDT")



    # Feed Cost Calculation
    st.subheader("Feed Cost")


    # Input for Feed Conversion Ratio (FCR) and Yearly Production
    fcr = st.number_input(
    "Feed Conversion Ratio (FCR)",
    min_value=0.0,
    value=st.session_state.financial_data.get("fcr", 0.0),
    step=0.1,
    )
    st.session_state.financial_data["fcr"] = fcr


    feed_cost_per_kg = st.number_input(
    "Feed Cost per kg (BDT)",
    min_value=0.0,
    value=st.session_state.financial_data.get("feed_cost_per_kg", 110.0),
    step=1.0,
    )
    st.session_state.financial_data["feed_cost_per_kg"] = feed_cost_per_kg
    yearly_production = st.session_state.plan_data["yearly_production"]
    st.session_state.financial_data["yearly_production"] = yearly_production


    # Calculate Yearly Feed Cost
    yearly_feed_requirement = fcr * yearly_production  # Total feed required in kg
    yearly_feed_cost = yearly_feed_requirement * feed_cost_per_kg  # Cost for the total feed
    st.session_state.financial_data["feed_cost"] = yearly_feed_cost

    # Display Yearly Feed Cost
    st.write(f"Yearly Feed Cost: {yearly_feed_cost:.2f} BDT")



    # Revenue Inputs
    st.subheader("Revenue Inputs")
    st.session_state.financial_data["selling_price"] = st.number_input(
        "Selling Price per Unit (BDT)",
        min_value=0.0,
        value=st.session_state.financial_data["selling_price"],
        step=5.0,
    )


    # Employee Salary Inputs
    st.session_state.financial_data["salary_payment"] = st.number_input(
        "Employee Salary per Year (BDT)",
        min_value=0.0,
        value=st.session_state.financial_data["salary_payment"],
        step=5000.0,
    )

    # Project Lifetime
    st.session_state.financial_data["project_lifetime"] = st.number_input(
        "Project Lifetime (Years)",
        min_value=1,
        value=st.session_state.financial_data["project_lifetime"],
        step=1,
    )

    # Calculate financial results on button click
    if st.button("Next - Results"):
        st.session_state.current_section = "Results"

# Section: Results
if st.session_state.current_section == "Results":
    # Results calculation and display
    initial_investment = (
        st.session_state.financial_data["equipment_cost"] +
        st.session_state.financial_data["land_cost"] +
        st.session_state.financial_data["infrastructure_cost"] +
        st.session_state.financial_data["construction_labor_cost"]
    )

    # Operational costs
    operational_cost = (
        st.session_state.financial_data["electricity_cost"] +
        st.session_state.financial_data["marketing_cost"] +
        st.session_state.financial_data["maintenance_cost"] +
        st.session_state.financial_data["fingerlings_cost"] +
        st.session_state.financial_data["feed_cost"] +
        st.session_state.financial_data["salary_payment"]
    )

    # Revenue calculation
    revenue = st.session_state.plan_data["yearly_production"] * st.session_state.financial_data["selling_price"]

    # Cash flow calculation
    cash_flow = []
    cumulative_cash_flow = []
    for year in range(st.session_state.financial_data["project_lifetime"]):
        if year == 0:
            cash_flow.append(-initial_investment)
        else:
            cash_flow.append(revenue - operational_cost)

        # Add cumulative cash flow
        cumulative_cash_flow.append(sum(cash_flow))

    # Calculate IRR
    irr = npf.irr(cash_flow)
    payback_period = calculate_payback_period(cumulative_cash_flow)



  # Calculate water volume
    total_volume = round(
        calculate_water_volume(
            st.session_state.plan_data["culture_type"],
            st.session_state.plan_data["species"],
            st.session_state.plan_data["yearly_production"],
        ),
        2,
    )
    st.session_state.plan_data["total_water_volume"] = total_volume

    # Tank Calculation (diameter and volume)
    if total_volume:
        tank_height = 1.5  # meters
        water_height = 1.2  # meters
        tank_diameter = round(math.sqrt(total_volume * 4 / (3.1416 * water_height)), 2)
        final_water_volume = round((3.1416 * tank_diameter * tank_diameter * tank_height / 4), 2)

        # Calculate the volume per tank
        volume_per_tank = round(final_water_volume / st.session_state.plan_data["tank_number"],2)

# Initialize session_state attributes for tank data
    st.session_state.tank_diameter = tank_diameter
    st.session_state.final_water_volume = final_water_volume
    st.session_state.volume_per_tank = volume_per_tank
#
    st.write(f"Total Water Volume Required: {total_volume} m³")
    st.write(f"Tank Diameter: {tank_diameter} m")
    st.write(f"Total Volume per Tank: {volume_per_tank} m³")





 # Create Cash Flow Table
    years = [st.session_state.plan_data["year_of_investment"] + i for i in range(st.session_state.financial_data["project_lifetime"])]
    cash_flow_df = pd.DataFrame({
        "Year": years,
        "Cash In": [revenue] * st.session_state.financial_data["project_lifetime"],
        "Cash Out": [operational_cost] * st.session_state.financial_data["project_lifetime"],
        "Cumulative Cash Flow": cumulative_cash_flow
    })

    # Display Results and Full Report
    print_results(initial_investment, revenue, operational_cost, payback_period, irr, cash_flow_df)
