import pandas as pd

def load_and_clean_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)

        # Drop unnamed index columns if present
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Strip whitespace from column names and standardize
        df.columns = df.columns.str.strip()

        # Ensure required columns exist
        required_columns = [
            "Institution Name", "regNo", "vehicleInsuranceUpto", "IDV",
            "Net_Premium", "GST_Amount", "Adv_Paid", "Final_Amount"
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in uploaded file: {', '.join(missing)}")

        # Parse dates
        if 'vehicleInsuranceUpto' in df.columns:
            df['vehicleInsuranceUpto'] = pd.to_datetime(df['vehicleInsuranceUpto'], errors='coerce')

        return df
    except Exception as e:
        raise RuntimeError(f"Error while reading file: {e}")
