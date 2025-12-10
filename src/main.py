# =================================================================================
# 1. IMPORTS MODULUS
# =================================================================================

import sys
import os

# Imports data_io.py
from data_io import (
    load_geotechnical_data,         
    export_multiple_dataframes,
    export_charts_to_excel
)

# Imports geotechnical_params.py
from geotechnical_params import (
    process_geotechnical_data,
    load_footing_configuration,
    get_stratum_id, 
    get_stratum_description, 
    get_stratum_parameters, 
    calculate_effective_overburden 
)

# Imports capacity_calc.py
from capacity_calc import (
    meyerhof_capacity,              
    calculate_allowable_capacity,  
    generate_capacity_table,     
    check_structural_design_capacity
)

# Imports plotting.py
from plotting import (
    generate_capacity_charts
)


# =================================================================================
# 2. CI/CD FIX: ENSURE OUTPUT DIRECTORY EXISTS
# =================================================================================

OUTPUT_DIR = 'output'

# Sheet configuration for Results file (DataFrames)
SHEET_NAME_1 = "Capacity_Charts"
SHEET_TITLE_1 = "Surface Bearing Capacity Results"
SHEET_NAME_2 = "bearing_capacity_check"
SHEET_TITLE_2 = "Bearing Capacity Check"

# File names for separate outputs
RESULTS_FILENAME = "Results_Bearing_Capacity"  # Tables/DataFrames
CHARTS_FILENAME = "Charts_bearing_capacity"    # Matplotlib plots

# This ensures that the 'output' folder is created if it does not exist,
# preventing the CI error when attempting to save results.
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    

# =================================================================================
# 3. MAIN ORCHESTRATION FUNCTION
# =================================================================================

def run_geotechnical_analysis(input_excel_path: str):
    
    # -----------------------------------------------------------------------------
    # A. DATA LOADING (Using load_geotechnical_data function)
    # -----------------------------------------------------------------------------
    
    # Here we call your loading function, which accepts the path
    workbook, sheet_geo, sheet_conf = load_geotechnical_data(input_excel_path)
    
    if workbook is None:
        print("❌ Process stopped due to a file loading error.")
        return

    # -----------------------------------------------------------------------------
    # B. INITIAL PROCESSING AND PARAMETER EXTRACTION
    # -----------------------------------------------------------------------------
    
    geotech_data = process_geotechnical_data(sheet_geo)
    df_geotech = geotech_data['df']
    
    # Extraction of global variables
    Df_values = geotech_data['Df_values']
    B_values = geotech_data['B_values']
    L_values = geotech_data['L_values']
    NAF = geotech_data['GWL'] # Groundwater Level
    Teta = geotech_data['Theta'] # Load Inclination
    Norma = geotech_data['code'] # Design Code
    epsilon = geotech_data['epsilon']

    df_footing_config = load_footing_configuration(sheet_conf)
    
    # -----------------------------------------------------------------------------
    # C. CALL TO COMPLEMENTARY FUNCTIONS (Validation and Testing)
    # -----------------------------------------------------------------------------
    
    # Definition of initial variables
    Df_test = Df_values[0] if Df_values else epsilon
    B_test = B_values[0] if B_values else epsilon
    L_test = L_values[0] if L_values else epsilon
    
    print("\n--- Starting Validation Checks ---")
    
    # The following calls are for verification only
    get_stratum_id(df_geotech, Df_test)
    get_stratum_parameters(df_geotech, Df_test)
    calculate_effective_overburden(df_geotech, Df_test, NAF, B_test)
    meyerhof_capacity(df_geotech, Df_test, B_test, L_test, NAF, Teta, epsilon)
    calculate_allowable_capacity(df_geotech, Df_test, B_test, L_test, NAF, Teta, epsilon, Norma)
    
    print("--- Validation Checks Completed ---")
    
    # -----------------------------------------------------------------------------
    # D. MAIN CALCULATIONS
    # -----------------------------------------------------------------------------

    # Structural design capacity check (df_conf_cimentaciones)
    df_footing_results = check_structural_design_capacity(
        df_footing_config=df_footing_config, 
        df_geotech=df_geotech, 
        GWL=NAF, 
        Theta=Teta, 
        epsilon=epsilon, 
        Code=Norma
    )
    print("✅ Structural check completed.")

    # Generation of the capacity chart table (results)
    df_capacity_table = generate_capacity_table(
        df_geotech=df_geotech, 
        Df_values=Df_values,
        B_values=B_values, 
        L_values=L_values, 
        GWL=NAF, 
        Theta=Teta, 
        epsilon=epsilon, 
        Code=Norma
    )
    print("✅ Capacity chart table (combinations) generated.")

    # -----------------------------------------------------------------------------
    # E. DATAFRAME EXPORT TO RESULTS FILE
    # -----------------------------------------------------------------------------
    
    # Export DataFrames to Results_Bearing_Capacity.xlsx
    export_multiple_dataframes(
        df_1=df_capacity_table,
        df_2=df_footing_results,
        output_dir=OUTPUT_DIR, 
        excel_filename=RESULTS_FILENAME,  # Results_Bearing_Capacity (without .xlsx)
        sheet_name_1=SHEET_NAME_1,     
        sheet_title_1=SHEET_TITLE_1,   
        sheet_name_2=SHEET_NAME_2,      
        sheet_title_2=SHEET_TITLE_2     
    )
    print(f"📊 DataFrames exported to: {OUTPUT_DIR}/{RESULTS_FILENAME}.xlsx\n")

    # -----------------------------------------------------------------------------
    # F. CHARTS EXPORT TO SEPARATE FILE
    # -----------------------------------------------------------------------------
    
    # 1. Generate Matplotlib figures
    dictionary_of_figures = generate_capacity_charts(df_capacity_table)
    print(f"✅ Generated {len(dictionary_of_figures)} chart(s).")

    # 2. Export charts to Charts_bearing_capacity.xlsx (separate file)
    export_charts_to_excel(
        figures_dict=dictionary_of_figures, 
        output_dir=OUTPUT_DIR, 
        excel_filename=CHARTS_FILENAME  # Charts_bearing_capacity (without .xlsx)
    )
    print(f"📈 Charts exported to: {OUTPUT_DIR}/{CHARTS_FILENAME}.xlsx\n")
    
    print("✨ Workflow completed successfully. ✨")
    print(f"📁 Output files:")
    print(f"   1. {OUTPUT_DIR}/{RESULTS_FILENAME}.xlsx  (DataFrames)")
    print(f"   2. {OUTPUT_DIR}/{CHARTS_FILENAME}.xlsx   (Charts)")


# =================================================================================
# 4. ENTRY POINT (Command-line argument handling)
# =================================================================================

if __name__ == "__main__":
    # Checks if the user provided a path to the Excel file
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
        run_geotechnical_analysis(input_file_path)
    else:
        # If a path is not provided, use the default value
        default_path = "Geotech_InputData.xlsx" 
        print("⚠️  No file path provided. Attempting to load the default file:")
        print(f"   Command: python app.py {default_path}\n")
        run_geotechnical_analysis(default_path)