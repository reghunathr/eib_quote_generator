import pandas as pd

def build_tree_nodes(df):
    nodes = []

    # Root level - All
    all_node = {
        "label": "All Institutions and Vehicles",
        "value": "all_data",
        "children": []
    }

    # Group by Institution
    for institution, group in df.groupby("Institution Name"):
        institution_node = {
            "label": institution,
            "value": f"institution::{institution}",
            "children": []
        }

        for _, row in group.iterrows():
            reg_no = row["regNo"]
            ins_upto = row.get("vehicleInsuranceUpto", "")
            label = f"{reg_no} (expires {ins_upto.date() if pd.notna(ins_upto) else 'N/A'})"
            institution_node["children"].append({
                "label": label,
                "value": f"bus::{institution}::{reg_no}"
            })

        all_node["children"].append(institution_node)

    nodes.append(all_node)
    return nodes
