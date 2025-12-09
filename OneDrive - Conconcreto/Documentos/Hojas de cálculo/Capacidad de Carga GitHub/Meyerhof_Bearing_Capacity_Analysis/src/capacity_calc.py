# External Library Imports
import pandas as pd
import numpy as np
import math

# Internal Module Imports (from Block 2: Geotechnical Parameters)
from geotechnical_params import (
    get_stratum_parameters, 
    calculate_effective_overburden, 
    get_stratum_id, 
    get_stratum_description 
)

"===================================================================="

def meyerhof_capacity(df: pd.DataFrame, Df: float, B: float, L: float, GWL: float, Theta: float, epsilon: float) -> tuple:
    """
    Calculates the Ultimate Bearing Capacity (q_ult) using Meyerhof's method (1963), 
    considering a two-layer soil system (Bilayer) if the influence depth extends 
    into the second stratum.

    It implements the layered soil approach detailed in Bowles' Foundation Analysis 
    and Design, Section 4-8.

    Args:
        df (pd.DataFrame): DataFrame with geotechnical properties.
        Df (float): Embedment depth [m].
        B (float): Footing width [m].
        L (float): Footing length [m].
        GWL (float): Groundwater Level [m].
        Theta (float): Load inclination angle [degrees].
        epsilon (float): Small value to handle zero divisions.

    Returns:
        tuple: (q_ult_single_layer, q_ult_bilayer), where q_ult_bilayer 
               is the controlling capacity based on the two-layer check.
    """

    # **********************************************************************************************
    # Get parameters for the embedment layer (1) and the layer below (2)
    # **********************************************************************************************
    c1, fi1, c2, fi2 = get_stratum_parameters(df, Df)

    # Determine influence depth (H) based on fi1
    alpha = 45 + (fi1 / 2)
    H = (B / 2) * math.tan(math.radians(alpha)) # Influence depth for layer interaction
    kp = math.tan(math.radians(45 + (fi1 / 2))) ** 2 # Coefficient of passive earth pressure

    # Determine d1: distance between foundation base (Df) and the end of stratum 1
    design_stratum = get_stratum_id(df, Df)
    final_depth_design_stratum = df.loc[design_stratum, "Final Depth"]
    d1 = final_depth_design_stratum - Df 

    # **************************************************************************************************
    # Calculate Capacity Factors and Correction Factors for Layer 1
    # **************************************************************************************************
    
    # Bearing Capacity Factors (Nc, Nq, N_gamma)
    Nq = (math.exp(math.pi * math.tan(math.radians(fi1)))) * (math.tan(math.radians(45 + (fi1 / 2))) ** 2)
    Nc = (Nq - 1) / (math.tan(math.radians(fi1)))
    Ny = (Nq - 1) * math.tan(math.radians(1.4 * fi1))

    # Shape Factors (Sc, Sq, S_gamma)
    Sc = 1 + (0.2 * kp * (B / L))
    Sq = 1 + 0.1 * kp * (B / L) if fi1 > 10 else 1
    Sy = Sq

    # Depth Factors (dc, dq, d_gamma)
    dc = 1 + 0.2 * (kp ** 0.5) * (Df / B)
    dq = 1 + 0.1 * (kp ** 0.5) * (Df / B) if fi1 > 10 else 1
    dy = dq

    # Inclination Factors (ic, iq, i_gamma)
    ic = (1 - (Theta / 90)) ** 2
    iq = ic
    if fi1 > 0:
        iy = (1 - (Theta / fi1)) ** 2
    elif Theta > 0:
        iy = 0
    else:
        iy = 1
        
    # *******************************************************************************************
    # Calculate Effective Overburden
    # *******************************************************************************************
    q_bar, y_bar = calculate_effective_overburden(df, Df, GWL, B)

    # Ultimate Capacity of the single embedment layer (q_ult_1)
    q_ult_1 = (c1 * Nc * Sc * dc * ic) + (q_bar * Nq * Sq * dq * iq) + (0.5 * y_bar * B * Ny * Sy * dy * iy)

    # ***************************************************************************************************************
    # Calculate Ultimate Capacity for the lower layer (q_ult_2)
    # This is needed for the two-layer check (Case 3 in the original logic).
    # ***************************************************************************************************************
    
    kp2 = math.tan(math.radians(45 + (fi2 / 2))) ** 2
    
    # Bearing Capacity Factors for Layer 2
    Nq2 = (math.exp(math.pi * math.tan(math.radians(fi2)))) * (math.tan(math.radians(45 + (fi2 / 2))) ** 2)
    Nc2 = (Nq2 - 1) / (math.tan(math.radians(fi2)))
    Ny2 = (Nq2 - 1) * math.tan(math.radians(1.4 * fi2))

    # Shape, Depth, and Inclination Factors for Layer 2
    Sc2 = 1 + (0.2 * kp2 * (B / L))
    Sq2 = 1 + 0.1 * kp2 * (B / L) if fi2 > 10 else 1
    Sy2 = Sq2
    dc2 = 1 + 0.2 * (kp2 ** 0.5) * (Df / B)
    dq2 = 1 + 0.1 * (kp2 ** 0.5) * (Df / B) if fi2 > 10 else 1
    dy2 = dq2
    ic2 = (1 - (Theta / 90)) ** 2
    iq2 = ic2
    iy2 = (1 - (Theta / fi2)) ** 2 if fi2 > 0 else (0 if Theta > 0 else 1)

    # Ultimate Capacity assuming embedment in Layer 2 (q_ult_2)
    q_ult_2 = (c2 * Nc2 * Sc2 * dc2 * ic2) + (q_bar * Nq2 * Sq2 * dq2 * iq2) + (0.5 * y_bar * B * Ny2 * Sy2 * dy2 * iy2)

    # *************************************************************************************************
    # Two-Layer (Bilayer) Controlling Capacity Logic
    # *************************************************************************************************
    
    # Default is the single layer capacity
    q_ult_bilayer = q_ult_1

    if d1 >= H:
        # Case A: Influence depth (H) is within the first layer. The single layer result controls.
        q_ult_bilayer = q_ult_1
    else:
        # Case B: Influence depth (H) extends into the second layer. Two-layer logic applies.

        # 1. Determine Case Type (Simplified soil classification based on parameters)
        is_clay1 = fi1 < epsilon
        is_clay2 = fi2 < epsilon
        is_sand1 = c1 < epsilon
        is_sand2 = c2 < epsilon

        if is_clay1 and is_clay2:
            case = "case1" # Clay on Clay
        elif is_sand1 and is_clay2:
            case = "case3_a" # Sand on Clay
        elif is_clay1 and is_sand2:
            case = "case3_b" # Clay on Sand
        else:
            case = "case2" # c-phi on c-phi (using weighted average)

        # 2. Calculate the controlling ultimate capacity based on the case

        if case == "case1":
            # Clay on Clay (Based on Meyerhof/Bowles, uses corrected Nc, Ncs)
            # Assuming c1 > epsilon
            CR = c2 / (c1 + epsilon)
            Ncs = 0 

            if CR < 0.7:
                Ncs = (1.5 * d1 / B) + 5.14 * CR
            elif 0.7 <= CR <= 1:
                Ncs = 0.9 * ((1.5 * d1 / B) + 5.14 * CR)
            elif CR > 1:
                N1s = 4.14 + (0.5 * B / (d1 + epsilon))
                N2s = 4.14 + (1.1 * B / (d1 + epsilon))
                Ncs = 2 * ((N1s * N2s) / (N1s + N2s + epsilon))
            
            # Recalculate q_ult using Ncs instead of Nc
            q_ult_bilayer = (c1 * Ncs * Sc * dc * ic) + (q_bar * Nq * Sq * dq * iq) + (0.5 * y_bar * B * Ny * Sy * dy * iy)

        elif case == "case2":
            # C-phi on C-phi (Uses Weighted Average Parameters)
            fi_avg = (d1 * fi1 + (H - d1) * fi2) / (H + epsilon)
            c_avg = (d1 * c1 + (H - d1) * c2) / (H + epsilon)

            # Recalculate Bearing Factors using averaged parameters
            Nq_avg = (math.exp(math.pi * math.tan(math.radians(fi_avg)))) * (math.tan(math.radians(45 + (fi_avg / 2))) ** 2)
            Nc_avg = (Nq_avg - 1) / (math.tan(math.radians(fi_avg)))
            Ny_avg = (Nq_avg - 1) * math.tan(math.radians(1.4 * fi_avg))

            # Recalculate Shape/Depth/Inclination Factors (using fi_avg)
            kp_avg = math.tan(math.radians(45 + (fi_avg / 2))) ** 2
            
            Sq_avg = 1 + 0.1 * kp_avg * (B / L) if fi_avg > 10 else 1
            Sy_avg = Sq_avg
            dq_avg = 1 + 0.1 * (kp_avg ** 0.5) * (Df / B) if fi_avg > 10 else 1
            dy_avg = dq_avg
            iy_avg = (1 - (Theta / fi_avg)) ** 2 if fi_avg > 0 else (0 if Theta > 0 else 1)

            # Calculate q_ult using averaged parameters
            q_ult_bilayer = (c_avg * Nc_avg * Sc * dc * ic) + \
                            (q_bar * Nq_avg * Sq_avg * dq_avg * iq) + \
                            (0.5 * y_bar * B * Ny_avg * Sy_avg * dy_avg * iy_avg)
        
        elif case == "case3_a" or case == "case3_b":
            # Sand on Clay or Clay on Sand (Punching Shear/Alternative Method)
            P = 2 * (B + L) # Perimeter
            A_f = B * L # Area
            # Calculate vertical stress on the plane d1 below the foundation
            # Note: The original pv calculation seems simplified/approximate. Using the original structure:
            pv = (Df * q_bar * d1) + (9.81 * ((d1 ** 2) / 2)) # Vertical pressure on the failure surface
            
            # Lateral earth pressure coefficient (ks)
            # Using kp for stratum 1 (fi1) from initial calculation:
            ks = kp 

            # Calculate q_ult_prime (q_ult based on punching shear mechanism)
            q_ult_prime = q_ult_2 + \
                          ((P * pv * ks * math.tan(math.radians(fi1))) / (A_f + epsilon)) + \
                          ((P * d1 * c1) / (A_f + epsilon))

            # The controlling capacity is the minimum of q_ult_1 (single layer failure) and q_ult_prime (punching shear)
            q_ult_bilayer = min(q_ult_1, q_ult_prime)
            

    return q_ult_1, q_ult_bilayer

"===================================================================="

def calculate_allowable_capacity(df: pd.DataFrame, Df: float, B: float, L: float, GWL: float, Theta: float, epsilon: float, Code: str) -> tuple:
    """
    Determines the Allowable Bearing Capacity (q_adm) based on the Ultimate Bearing 
    Capacity (q_ult) and the safety factor defined by the applicable design Code.

    Args:
        df, Df, B, L, GWL, Theta, epsilon: Parameters for meyerhof_capacity calculation.
        Code (str): The design code ("NSR_10" or "CCP_14").

    Returns:
        tuple: (ultimate_bearing_capacity, allowable_bearing_capacity) [kPa].
    """
    # 1. Get ultimate capacities
    q_ult_single, q_ult_bilayer = meyerhof_capacity(df, Df, B, L, GWL, Theta, epsilon)
    
    # The ultimate capacity is the controlling bilayer capacity (q_ult_bilayer)
    ultimate_bearing_capacity = q_ult_bilayer
    
    # 2. Define Safety/Resistance Factor based on Code
    if Code == "Bowles_FS_3.0":
        # Factor of Safety of 3.0 (for dead + live loads)
        factor_safety = 3 
        allowable_bearing_capacity = ultimate_bearing_capacity / factor_safety
        
    elif Code == "AASHTO_2020":
        # Resistance Factor (phi) based on Table 10.5.5.2.2-1 in AASHTO LRFD (phi=0.45 for bearing failure)
        # Allowable capacity is usually defined as the factored resistance (phi * q_ult). 
        # Here, we assume the user intends to use the inverse (1/phi) as the Safety Factor:
        factor_safety = 1 / 0.45 
        allowable_bearing_capacity = ultimate_bearing_capacity / factor_safety
    else:
        # Default fallback
        factor_safety = 3
        allowable_bearing_capacity = ultimate_bearing_capacity / factor_safety
        
    return ultimate_bearing_capacity, allowable_bearing_capacity

"===================================================================="

def generate_capacity_table(df_geotech: pd.DataFrame, Df_values: list, B_values: list, L_values: list, GWL: float, Theta: float, epsilon: float, Code: str) -> pd.DataFrame:
    """
    Generates a DataFrame containing ultimate and allowable bearing capacity results 
    for all specified combinations of embedment depth (Df), Footing Base (B), and Footing length (L).

    This data is used to generate capacity charts (abacus).

    Args:
        df_geotech (pd.DataFrame): Geotechnical properties.
        Df_values (list): List of embedment depths [m].
        B_values (list): List of footing Base [m].
        L_values (list): List of footing lengths [m].
        GWL, Theta, epsilon, Code: Parameters for capacity calculation.

    Returns:
        pd.DataFrame: A table containing all calculated capacity combinations.
    """
    results = []

    # Iterate through all combinations of Df, B, and L
    for Df in Df_values:
        for B in B_values:
            for L in L_values:
                # Check if Length is greater than or equal to Base (L >= B)
                if L >= B:
                    
                    # 1. Get Stratum and Capacity values
                    stratum_id = get_stratum_id(df_geotech, Df)
                    stratum_desc = get_stratum_description(df_geotech, Df)
                    q_ult_single, q_ult_bilayer = meyerhof_capacity(df_geotech, Df, B, L, GWL, Theta, epsilon)
                    q_ult_final, q_adm = calculate_allowable_capacity(df_geotech, Df, B, L, GWL, Theta, epsilon, Code)
                    C1, Fi1, C2, Fi2 = get_stratum_parameters(df_geotech, Df)
                    B_L_Ratio = B / L
                    
                    # 2. Append the results to the list
                    results.append([
                        stratum_id, stratum_desc, Df, B, L, B_L_Ratio, C1, Fi1, C2, Fi2, 
                        q_ult_single, q_ult_bilayer, q_ult_final, q_adm
                    ])
                
                else:
                    # Skip calculation if L < B (not a standard footing geometry)
                    continue

    # Create the DataFrame of results
    df_capacity = pd.DataFrame(results, columns=[
        "Embedment Stratum ID", "Embedment Stratum Desc", "Embedment Depth (m)", "Footing Base (m)", 
        "Footing Length (m)", "B/L Ratio", f"Cohesion c\u2081 (kPa)", f"Friction Angle \u03C6\u2081 (\u00B0)",
        f"Cohesion c\u2082 (kPa)", f"Friction Angle \u03C6\u2082 (\u00B0)", "Qult Single Layer (kPa)", 
        "Qult Bilayer (kPa)", "Ultimate Capacity (kPa)", "Allowable Capacity (kPa)"
    ])
    
    return df_capacity

"===================================================================="

def check_structural_design_capacity(df_footing_config: pd.DataFrame, df_geotech: pd.DataFrame, GWL: float, Theta: float, epsilon: float, Code: str) -> pd.DataFrame:
    """
    Performs a bearing capacity check for a pre-defined set of structural footings.

    Args:
        df_footing_config (pd.DataFrame): Structural configurations (Df, B, L, Load).
        df_geotech (pd.DataFrame): Geotechnical properties.
        GWL, Theta, epsilon, Code: Parameters for capacity calculation.

    Returns:
        pd.DataFrame: The input DataFrame with added columns for ultimate capacity, 
                      allowable capacity, design stress, and a pass/fail check.
    """
    
    ultimate_capacities = []
    allowable_capacities = []
    design_stresses = []
    capacity_check = []

    for _, row in df_footing_config.iterrows():
        Df = row["Embedment Depth (m)"]
        B = row["Footing Base (m)"]
        L = row["Footing Length (m)"]
        load = row["Design Load (kN)"]

        # Call the allowable capacity function
        q_ult, q_adm = calculate_allowable_capacity(
            df=df_geotech, Df=Df, B=B, L=L, GWL=GWL, Theta=Theta, epsilon=epsilon, Code=Code
        )

        # Calculate design stress (load / area)
        design_stress = load / (B * L)

        # Check: Pass (✅) if Allowable Capacity >= Design Stress, else Fail (❌)
        is_compliant = "✅" if q_adm >= design_stress else "❌"

        ultimate_capacities.append(q_ult)
        allowable_capacities.append(q_adm)
        design_stresses.append(design_stress)
        capacity_check.append(is_compliant)

    # Add columns to the DataFrame
    df_footing_config["Ultimate Capacity (kPa)"] = ultimate_capacities
    df_footing_config["Allowable Capacity (kPa)"] = allowable_capacities
    df_footing_config["Design Stress (kPa)"] = design_stresses
    df_footing_config["Bearing Capacity Check"] = capacity_check

    return df_footing_config