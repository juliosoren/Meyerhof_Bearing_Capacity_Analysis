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
    
    output_filename = geotech_data['output_filename']
    chart_dir = geotech_data['chart_dir']
    chart_filename = geotech_data['chart_filename']

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
    # The variable 'epsilon' is added to the call, as it was in your 'abacos' function
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
    # E. DATAFRAME EXPORT
    # -----------------------------------------------------------------------------

    # Export results (charts + structural check) to a single Excel file
    export_multiple_dataframes(
        df_1=df_capacity_table,
        df_2=df_footing_results
    )
    print(f"💾 Tables exported to '{output_filename}.xlsx'.")

    # -----------------------------------------------------------------------------
    # F. PLOTTING AND EXPORT
    # -----------------------------------------------------------------------------

    # 1. Generate figures
    dictionary_of_figures = generate_capacity_charts(df_capacity_table)

    # 2. Export figures
    export_charts_to_excel(dictionary_of_figures, chart_dir, chart_filename)
    print(f"💾 Charts exported to '{chart_filename}'.")
    
    print("\n✨ Workflow completed successfully. ✨")


# =================================================================================
# 4. ENTRY POINT (Command-line argument handling)
# =================================================================================

if __name__ == "__main__":
    # Checks if the user provided a path to the Excel file
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
        run_geotechnical_analysis(input_file_path)
    else:
        # If a path is not provided, use the default value from your function
        default_path = "Geotech_InputData.xlsx" 
        print("⚠️ No file path provided. Attempting to load the default file:")
        print(f"Command: python app.py {default_path}")
        run_geotechnical_analysis(default_path)