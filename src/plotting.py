# External Library Imports
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager 
import seaborn as sns
import io 

def generate_capacity_charts(results: pd.DataFrame) -> dict:
    """
    Creates capacity charts (abacuses) showing Ultimate and Allowable Bearing 
    Capacity vs. B/L Ratio for different embedment depths (Df).

    Args:
        results (pd.DataFrame): DataFrame containing the capacity analysis results 
                                (output from generate_capacity_table).

    Returns:
        dict: A dictionary where keys are the Df values and the values are the 
              corresponding Matplotlib Figure objects.
    """
    # Define color palette (can be defined globally in the file)
    color_palette = ["black", "yellow", "green", "red", "magenta", "cyan", "blue", "orange"]

    # Verify that the DataFrame contains the necessary columns
    required_columns = {"Embedment Depth (m)", "B/L Ratio", "Ultimate Capacity (kPa)",
                        "Allowable Capacity (kPa)", "Footing Base (m)", "Embedment Stratum ID"}
    if not required_columns.issubset(results.columns):
        raise ValueError("Missing required columns in the 'results' DataFrame.")

    # Get list of unique embedment depths
    depths = results["Embedment Depth (m)"].unique()

    # Configure font (assuming Montserrat is installed or handled elsewhere)
    # The font configuration block is left out for simplicity, assuming a standard setup.
    
    # Dictionary to store the figures
    figures = {}

    # Create individual charts for each embedment depth
    for Df in depths:
        df_filter = results[results["Embedment Depth (m)"] == Df]
        stratum = df_filter["Embedment Stratum ID"].iloc[0]  # Get the corresponding stratum ID

        # Get min/max values to adjust Y-axes dynamically
        min_qult = df_filter["Ultimate Capacity (kPa)"].min()
        max_qult = df_filter["Ultimate Capacity (kPa)"].max()
        min_qadm = df_filter["Allowable Capacity (kPa)"].min()
        max_qadm = df_filter["Allowable Capacity (kPa)"].max()

        # Apply a 10% margin for better visualization
        margin_qult = (max_qult - min_qult) * 0.10
        margin_qadm = (max_qadm - min_qadm) * 0.10

        # Create figure and subplots
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Filter B/L Ratio to standard range
        df_filter = df_filter[(df_filter["B/L Ratio"] >= 0.1) & (df_filter["B/L Ratio"] <= 1)]

        # --- Ultimate Capacity Chart ---
        sns.lineplot(
            x="B/L Ratio",
            y="Ultimate Capacity (kPa)",
            hue="Footing Base (m)", 
            data=df_filter,
            ax=axes[0],
            palette=color_palette[:df_filter["Footing Base (m)"].nunique()],
            style="Footing Base (m)",
            dashes=[(2, 2)] * df_filter["Footing Base (m)"].nunique(),
            markers=True,
            errorbar=None
        )
        axes[0].set_title(f"Ultimate Bearing Capacity for Df= {Df:.2f} m - {stratum}",
                          fontsize=14, fontweight='bold')
        axes[0].set_xlabel("B/L Ratio", fontweight='bold')
        axes[0].set_ylabel("Ultimate Bearing Capacity (kPa)", fontweight='bold')
        axes[0].set_ylim(min_qult - margin_qult, max_qult + margin_qult)
        axes[0].grid(color='#D3D3D3', linestyle="--", linewidth=0.7)

        # --- Allowable Capacity Chart ---
        sns.lineplot(
            x="B/L Ratio",
            y="Allowable Capacity (kPa)",
            hue="Footing Base (m)",  
            data=df_filter,
            ax=axes[1],
            palette=color_palette[:df_filter["Footing Base (m)"].nunique()],
            style="Footing Base (m)",
            dashes=[(2, 2)] * df_filter["Footing Base (m)"].nunique(),
            markers=True,
            errorbar=None
        )
        axes[1].set_title(f"Allowable Bearing Capacity for Df= {Df:.2f} m - {stratum}",
                          fontsize=14, fontweight='bold')
        axes[1].set_xlabel("B/L Ratio", fontweight='bold')
        axes[1].set_ylabel("Allowable Bearing Capacity (kPa)", fontweight='bold')
        axes[1].set_ylim(min_qadm - margin_qadm, max_qadm + margin_qadm)
        axes[1].grid(color='#D3D3D3', linestyle="--", linewidth=0.7)

        plt.tight_layout()
        figures[f"Df_{Df:.2f}m"] = fig # Store the figure in the dictionary

    return figures # Returns a dictionary of figures