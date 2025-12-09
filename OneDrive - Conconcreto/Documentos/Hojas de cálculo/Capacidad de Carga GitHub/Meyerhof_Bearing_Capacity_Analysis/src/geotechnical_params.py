# src/geotechnical_params.py

# External Library Imports
import pandas as pd
import numpy as np
import math
from itertools import product
import os
import openpyxl # For type hinting the sheet argument

# Internal Module Imports (Utility functions from data_io.py)
# CORRECTED: Using the confirmed function names for data extraction
from data_io import read_column_vector, read_row_vector 

# Note: The global variable WATER_UNIT_WEIGHT is defined here for calculation functions
WATER_UNIT_WEIGHT = 9.81 # Default unit weight of water [kN/m³]

"==================================================================================================="

def get_stratum_id(df: pd.DataFrame, Df: float) -> str:
    """
    Determines the stratum ID where the shallow foundation is placed, 
    based on the embedment depth (Df).

    Args:
        df: DataFrame containing the geotechnical properties, indexed by 'Estrato'.
        Df: Embedment depth (Df) of the foundation [m].
        
    Returns:
        The ID (str) of the stratum where the foundation base is located.
    """
    # Ensure that the index is the 'Estrato' column
    if "Stratum ID" in df.columns:
        df = df.set_index("Stratum ID")
        
    # Iterate over each stratum to find the one where Df falls
    for stratum_id, row in df.iterrows():
        # Check if Df is between the initial and final depths 
        if row["Initial Depth"] <= Df < row["Final Depth"]:
            return stratum_id  # Returns the found stratum ID
        
"==================================================================================================="

def get_stratum_description(df: pd.DataFrame, Df: float) -> str:
    """
    Determines the description of the stratum where the foundation is placed, 
    based on the embedment depth (Df).

    Args:
        df: DataFrame containing the geotechnical properties.
        Df: Embedment depth (Df) of the foundation [m].
        
    Returns:
        The description (str) of the stratum where the foundation base is located.
    """
    # Ensure that the index is the "Stratum Description" column
    if "Stratum Description" in df.columns:
        df = df.set_index("Stratum Description")
        
    # Iterate over each stratum description to find the matching depth range
    for stratum_description, row in df.iterrows():
        # Check if Df is between the initial and final depths (Profundidad Inicial/Final)
        if row["Initial Depth"] <= Df < row["Final Depth"]:
            return stratum_description  # Returns the found stratum description
        
"==================================================================================================="

def process_geotechnical_data(sheet_1: openpyxl.worksheet.worksheet.Worksheet, epsilon: float = 1e-12) -> dict:
    """
    Processes and organizes all geotechnical data, project parameters, and 
    geometric combinations from the Excel sheet.

    Args:
        sheet_1: The openpyxl Worksheet object containing the geotechnical data.
        epsilon: Small value to prevent division by zero (default: 1e-12).
    
    Returns:
        A dictionary containing all processed data and parameters (df, Df_values, B_values, etc.).
    """
    
    # ***********************************************************************************************************
    # Geotechnical Property Vectors (Using read_raw_vector)
    # ***********************************************************************************************************
    
    stratum_ids = read_column_vector(sheet_1, row=13, col_start=2)
    stratum_names = read_column_vector(sheet_1, row=13, col_start=3)
    initial_depth = read_column_vector(sheet_1, row=13, col_start=4)
    final_depth = read_column_vector(sheet_1, row=13, col_start=5)
    unit_weight_moist = read_column_vector(sheet_1, row=13, col_start=6)
    unit_weight_saturated = read_column_vector(sheet_1, row=13, col_start=7)
    cohesion = read_column_vector(sheet_1, row=13, col_start=8)
    friction_angle = read_column_vector(sheet_1, row=13, col_start=9)
    
    # ***********************************************************************************************************
    # Creation of Vectors for Combinations (Df, B, L) (Using read_column_vector)
    # ***********************************************************************************************************
   
    Df_values = read_row_vector(sheet_1, row=9, col_start=3)
    B_values = read_row_vector(sheet_1, row=10, col_start=3)
    
    # Create the values for Length (L) to evaluate
    scalars = [1, 1.25, 1.5, 2, 5, 10] 
    L_values = [b * e for b, e in product(B_values, scalars)] 
    L_values = sorted(set(L_values))
    
    # ***********************************************************************************************************
    # Input Parameters
    # ***********************************************************************************************************
    
    code = sheet_1['C4'].value      
    GWL = sheet_1['C5'].value       
    beta = sheet_1['C6'].value      
    theta = sheet_1['C7'].value     
    
    # Define Paths and Titles
    output_dir = os.getcwd()
    output_filename = "Results_Bearing_Capacity" 
    header_title = sheet_1['C2'].value
    chart_dir = os.getcwd()
    chart_filename = "Charts_bearing_capacity.xlsx"
    
    # Transformation of Cohesion and Friction Angle Vectors to avoid division by zero
    cohesion_adj = [x + epsilon for x in cohesion]
    friction_angle_adj = [x + epsilon for x in friction_angle]
    
    # Create the DataFrame
    data = {
        "Stratum ID": stratum_ids,
        "Stratum Description": stratum_names,
        "Initial Depth": initial_depth,
        "Final Depth": final_depth,
        "Unit Weight Moist": unit_weight_moist,
        "Unit Weight Saturated": unit_weight_saturated,
        "Cohesion": cohesion_adj,
        "Friction Angle": friction_angle_adj
    }
    df = pd.DataFrame(data).set_index("Stratum ID")
    
    # Return all values in a dictionary
    return {
        'df': df,
        'Df_values': Df_values,
        'B_values': B_values,
        'L_values': L_values,
        'water_unit_weight': WATER_UNIT_WEIGHT,
        'epsilon': epsilon,
        'code': code,
        'GWL': GWL,
        'beta': beta,
        'Theta': theta,
        'header_title': header_title,
        'chart_dir': chart_dir,
        'output_dir': output_dir,
        'output_filename': output_filename,
        'chart_filename': chart_filename
    }

"==================================================================================================="

def load_footing_configuration(sheet_2: openpyxl.worksheet.worksheet.Worksheet) -> pd.DataFrame:
    """
    Creates a DataFrame with the configurations of footings to be analyzed 
    from the Excel sheet.
    
    Args:
        sheet_2: The openpyxl Worksheet object containing the footing configurations.
    
    Returns:
        A pandas DataFrame with the following columns:
        - Support Name: Identifier for the footing.
        - Footing Base (m): Width dimension in meters (B).
        - Footing Length (m): Length dimension in meters (L).
        - Embedment Depth (m): Embedment depth in meters (Df).
        - Design Load (kN): Applied vertical load in kilonewtons (Q).
    """
    
    # Extract data from the Excel sheet using the corrected utility function
    support_names = read_column_vector(sheet_2, row=3, col_start=2)
    widths = read_column_vector(sheet_2, row=3, col_start=3)
    lengths = read_column_vector(sheet_2, row=3, col_start=4)
    embedments = read_column_vector(sheet_2, row=3, col_start=5)
    loads = read_column_vector(sheet_2, row=3, col_start=6)
    
    # Create the DataFrame
    df_footing_config = pd.DataFrame({
        'Support Name': support_names,
        'Footing Base (m)': widths,
        'Footing Length (m)': lengths,
        'Embedment Depth (m)': embedments,
        'Design Load (kN)': loads
    })
    
    # Convert the load column to float type
    df_footing_config['Design Load (kN)'] = df_footing_config['Design Load (kN)'].astype(float)
    
    return df_footing_config

"==================================================================================================="

def get_stratum_parameters(df: pd.DataFrame, Df: float) -> tuple:
    """
    Determines the geotechnical parameters (Cohesion and Friction Angle) 
    for the current stratum and the stratum immediately below it.

    Args:
        df: DataFrame with geotechnical properties (indexed by Stratum ID).
        Df: Embedment depth (Df) [m].
        
    Returns:
        A tuple containing (c1, phi1, c2, phi2):
        - c1: Cohesion of the current stratum [kN/m²].
        - phi1: Friction angle of the current stratum [degrees].
        - c2: Cohesion of the stratum below (or c1 if it's the last stratum) [kN/m²].
        - phi2: Friction angle of the stratum below (or phi1 if it's the last stratum) [degrees].
    """
    # 1. Determine the current stratum ID
    current_stratum_id = get_stratum_id(df, Df)
    
    # 2. Get parameters for the current stratum (Index 1)
    c1 = df.loc[current_stratum_id, "Cohesion"]        # Retrieve Cohesion
    phi1 = df.loc[current_stratum_id, "Friction Angle"] # Retrieve Friction Angle
    
    # 3. Check for the lower stratum (Index 2)
    stratum_index = df.index.get_loc(current_stratum_id)  # Get the position of the index
    
    if stratum_index < len(df) - 1:  # Check if there is a stratum below
        # Get parameters from the stratum below
        c2 = df.iloc[stratum_index + 1]["Cohesion"]
        phi2 = df.iloc[stratum_index + 1]["Friction Angle"]
    else:
        # If it's the last stratum, use the current stratum's parameters for the lower layer
        c2 = c1
        phi2 = phi1
    
    return c1, phi1, c2, phi2

"==================================================================================================="

def calculate_effective_overburden(df: pd.DataFrame, Df: float, GWL: float, B: float) -> tuple:
    """
    Calculates the effective overburden pressure (q_bar) at the foundation level 
    and the effective unit weight (gamma_bar) for bearing capacity factors.

    The calculation accounts for multiple soil strata and the Groundwater Level (GWL).

    Args:
        df: DataFrame with geotechnical properties.
        Df: Embedment depth [m].
        GWL: Groundwater Level (NAF) [m].
        B: Width of the footing [m].

    Returns:
        A tuple containing (q_bar, gamma_bar):
        - q_bar: Effective overburden pressure at foundation level [kN/m²].
        - gamma_bar: Effective unit weight for capacity factor calculations [kN/m³].
    """
    q_bar = 0.0
    # The 'peso_acumulado' variable in the original code is redundant for the final return
    
    # Standard unit weight of water
    y_water = WATER_UNIT_WEIGHT  
    
    # Iterate through all strata to calculate q_bar
    for _, row in df.iterrows():
        # Determine the portion of the stratum within the embedment depth (Df)
        if row["Final Depth"] <= Df:
            stratum_thickness = row["Final Depth"] - row["Initial Depth"]
        elif row["Initial Depth"] <= Df <= row["Final Depth"]:
            stratum_thickness = Df - row["Initial Depth"]
        else:
            continue  # If the stratum is entirely below Df, ignore it

        # Define unit weights
        y_stratum = row["Unit Weight Moist"]
        y_sat = row["Unit Weight Saturated"]
        y_submerged = y_sat - y_water

        # Calculate effective overburden based on the groundwater level (GWL)
        if GWL >= Df:
            # GWL is below the stratum depth → use moist unit weight
            q_bar += stratum_thickness * y_stratum
        elif GWL <= row["Initial Depth"]:
            # GWL is above the stratum → use submerged unit weight
            q_bar += stratum_thickness * y_submerged
        else:
            # GWL is within the stratum → consider both moist and submerged fractions
            h_moist = GWL - row["Initial Depth"]
            h_submerged = stratum_thickness - h_moist
            
            # Ensure h_moist does not exceed the stratum thickness above GWL
            h_moist = max(0, min(h_moist, stratum_thickness))
            h_submerged = max(0, stratum_thickness - h_moist)

            q_bar += h_moist * y_stratum + h_submerged * y_submerged

    # ***********************************************************************************************************
    # Calculate Effective Unit Weight (gamma_bar) for Capacity Factors (Terzaghi/Meyerhof)
    # ***********************************************************************************************************
    
    if GWL < Df:
        # Case 1: GWL above Df, gamma_bar = submerged unit weight (simplified)
        gamma_bar = y_submerged
    elif (GWL - Df) < B:
        # Case 2: GWL is between Df and Df + B
        # Interpolation: R_w factor (R_w = 0.5 + 0.5 * (GWL - Df) / B)
        # Simplified equivalent of R_w application to get gamma_bar:
        gamma_bar = y_submerged + ((GWL - Df) / B) * (y_stratum - y_submerged)
    else:
        # Case 3: GWL is below Df + B → use moist unit weight
        gamma_bar = y_stratum

    return q_bar, gamma_bar
