import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import pandas as pd

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("cba.json", scopes=scope)
client = gspread.authorize(creds)

# Google Sheets ID
sheet_keys = "1XpA_PibK6so1uLMzVIT7-g32gcp7DdTHV4eBp1_7jcc"

def fetch_sheet_data(sheet_key, sheet_title):
    """Fetches data from the specified Google Sheet."""
    try:
        sheet = client.open_by_key(sheet_key).worksheet(sheet_title)
        data = sheet.get_all_values()
        return data
    except Exception as e:
        st.error(f"Error fetching sheet data: {e}")
        return []

def update_sheet(sheet, values, rows):
    """Updates the specified cells in the Google Sheet."""
    try:
        for row, value in zip(rows, values):
            sheet.update_cell(row, 2, value)
    except Exception as e:
        st.error(f"Error updating sheet: {e}")

def has_empty_values(values):
    """Checks if there are any empty values in the given list."""
    return any(not value.strip() for value in values)

def create_pdf(data, table_data):
    """Creates a PDF from the provided data."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Header
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt="Cost Benefit Analysis - Results Summary", ln=True, align='L')
    pdf.ln(2)  # Line break reduced space

    # Content
    pdf.set_font("Arial", size=10)
    for row in data:
        if len(row) >= 2:
            label, value = row[:2]
            pdf.cell(0, 6, txt=f"{label}: {value}", ln=True, align='L')  # Reduced line height

    # Table Header
    pdf.ln(5)  # Line break reduced space
    pdf.set_font("Arial", style='B', size=10)
    for header in table_data[0]:
        pdf.cell(38, 6, txt=header, border=1, align='C')  # Reduced height
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", size=10)
    for row in table_data[1:]:
        for item in row:
            pdf.cell(38, 6, txt=item, border=1, align='C')  # Reduced height
        pdf.ln()

    # Footer
    pdf.ln(5)  # Line break reduced space
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, txt="Generated by ITTI", ln=True, align='C')

    pdf_file = "result_summary.pdf"
    pdf.output(pdf_file)
    return pdf_file

def main():
    # Custom favicon, browser title, header, and subtitle
    st.markdown("""
        <head>
            <link rel="icon" href="https://example.com/path/to/your/favicon.ico" type="image/x-icon">
            <title>Custom Streamlit App Title</title>
        </head>
        <style>
            /* Header Style */
            .header {
                text-align: center;
                font-size: 40px;
                color: #2E86C1; /* Modern blue color */
                font-family: 'Arial', sans-serif;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            /* Subtitle Style */
            .subtitle {
                text-align: center;
                font-size: 24px;
                color: #1F618D; /* Slightly darker blue for contrast */
                font-family: 'Arial', sans-serif;
                margin-bottom: 30px;
            }
            /* Footer Style */
            .footer {
                text-align: center;
                font-size: 12px;
                color: grey;
                font-family: 'Arial', sans-serif;
                margin-top: 20px;
            }
        </style>
        <div class="header">Cost Benefit Analysis</div>
        <div class="subtitle">Developed by ITTI</div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'dropdown_values' not in st.session_state:
        st.session_state.dropdown_values = {}
    if 'fixed_cost_data' not in st.session_state:
        st.session_state.fixed_cost_data = {}
    if 'yearly_production_set' not in st.session_state:
        st.session_state.yearly_production_set = False

    # Page navigation
    pages = ["Plan", "Details Information", "Results"]

    def navigate_page(direction):
        if direction == "next" and st.session_state.page < len(pages) - 1:
            st.session_state.page += 1
        elif direction == "prev" and st.session_state.page > 0:
            st.session_state.page -= 1

    # Sidebar for page selection
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(" ", pages, index=st.session_state.page)

    if selected_page != pages[st.session_state.page]:
        st.session_state.page = pages.index(selected_page)
        st.rerun()

    # Plan page
    if st.session_state.page == 0:
        st.title("Plan")
        plan_data = fetch_sheet_data(sheet_keys, "Plan")

        if len(plan_data) > 14:
            dropdown_labels = [plan_data[i][0] for i in [0, 3, 9, 14]]
            dropdown_options = [["Select an option"] + plan_data[i][1].split(',') if len(plan_data[i]) > 1 else ["Select an option"] for i in [0, 3, 9, 14]]
        else:
            dropdown_labels = ["Select an option"] * 4
            dropdown_options = [["Select an option"]] * 4

        selected_values = []
        for i, (label, options) in enumerate(zip(dropdown_labels, dropdown_options)):
            key = f"dropdown_{i}"

            if key not in st.session_state.dropdown_values:
                st.session_state.dropdown_values[key] = options[0]  # Initialize with "Select an option"

            selected_value = st.selectbox(label, options=options, index=options.index(st.session_state.dropdown_values[key]), key=key)
            st.session_state.dropdown_values[key] = selected_value
            selected_values.append(selected_value)

        yearly_production_label = plan_data[2][0] if len(plan_data) > 2 else "Yearly Production (Kg)"

        # Flag to track if yearly production has been set
        if st.session_state.yearly_production_set:
            yearly_production_value = plan_data[2][1] if len(plan_data) > 2 else ""
        else:
            yearly_production_value = ""

        new_yearly_production = st.text_input(yearly_production_label, value=yearly_production_value, key="yearly_production_input")

        if new_yearly_production != "":
            st.session_state.yearly_production_set = True

        selected_values.insert(1, new_yearly_production)

        # Align the "Next" button to the right
        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button("Next", key="next_button_plan"):
                sheet = client.open_by_key(sheet_keys).worksheet("Plan")
                update_sheet(sheet, selected_values, rows=[2, 3, 5, 11, 16])

                # Check for empty values and D1 value
                if has_empty_values(selected_values) or float(sheet.cell(1, 4).value) > 0:
                    st.error("Please fill in all financial information fields before proceeding.")
                else:
                    navigate_page("next")
                    st.rerun()

    # Details Information page
    elif st.session_state.page == 1:
        st.title("Details Information")
        fixed_cost_data = fetch_sheet_data(sheet_keys, "Initial Investment")

        names = [row[0] for row in fixed_cost_data[0:14]]
        values = [row[1] for row in fixed_cost_data[0:14]]
        all_filled = True
        for i, name in enumerate(names):
            key = f"input_{i}_fixed"
            if key not in st.session_state.fixed_cost_data:  # Initialize with empty string
                st.session_state.fixed_cost_data[key] = ""

            st.session_state.fixed_cost_data[key] = st.text_input(f"{name}", value=st.session_state.fixed_cost_data[key], key=key)
            if not st.session_state.fixed_cost_data[key].strip():
                all_filled = False

        # Align the "Previous" button to the left and "Next" button to the right
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Previous", key="prev_button_fixed"):
                navigate_page("prev")
                st.rerun()

        with col2:
            if st.button("Next", key="next_button_fixed"):
                if all_filled:
                    values = [st.session_state.fixed_cost_data[f"input_{i}_fixed"] for i in range(14)]
                    sheet = client.open_by_key(sheet_keys).worksheet("Initial Investment")
                    update_sheet(sheet, values, rows=list(range(1, 15)))
                    navigate_page("next")
                    st.rerun()
                else:
                    st.error("Please fill in all financial information fields before proceeding.")

    # Results page
    elif st.session_state.page == 2:
        st.title("Results")
        results_data = fetch_sheet_data(sheet_keys, "Results")

        # Display the results as editable text inputs
        st.write("### Results Summary")
        all_filled = True
        for i, row in enumerate(results_data[0:17]):
            if len(row) >= 2:
                label, value = row[:2]
                input_value = st.text_input(label, value=value, key=f"{i}_{label}_input")  # Added index for uniqueness
                if not input_value.strip():
                    all_filled = False

        # Process table data
        table_data = results_data[20:31]

        # Display table data
        st.write("### Cash Flow Table")
        if table_data:
            # Create a DataFrame for better formatting in Streamlit
            table_df = pd.DataFrame(table_data[1:], columns=table_data[0])
            st.dataframe(table_df, width=800)

        # Align the buttons as requested
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Previous", key="prev_button_results"):
                navigate_page("prev")
                st.rerun()

        with col2:
            pdf_button = st.button("Print PDF", key="print_button")
            if pdf_button:
                pdf_file = create_pdf(results_data[0:16], table_data)
                st.write("PDF generated!")
                with open(pdf_file, "rb") as pdf:
                    st.download_button("Download PDF", pdf, file_name="result_summary.pdf", help="Click to download the PDF")

        with col3:
            if st.button("Next", key="next_button_results"):
                if all_filled:
                    navigate_page("next")
                    st.rerun()
                else:
                    st.error("Please fill in all result fields before proceeding.")

    st.markdown("""
        <div class="footer">Thank you for using ITTI's CBA tool!</div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
