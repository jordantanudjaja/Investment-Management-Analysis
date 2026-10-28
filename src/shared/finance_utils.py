import logging
from datetime import datetime
import pandas as pd

# Configure the logger globally (Python handles the caching automatically)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Dataframe Display Settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)  # Prevents columns from wrapping to a new line

# Defining Utility Functions
# Aligns multiple financial DataFrames so they all contain the union of unique column dates
def align_financial_statements(*dfs: pd.DataFrame) -> list[pd.DataFrame]:
    """Dates are sorted from most recent to oldest.
    Missing date columns are filled with NaN values.
    """
    # 1. Collect all unique column dates across all DataFrames
    all_dates = pd.Index([])
    for df in dfs:
        all_dates = all_dates.union(df.columns)
        
    # 2. Sort dates in descending order (newest date first, consistent with yfinance)
    sorted_dates = all_dates.sort_values(ascending=False)
    
    # 3. Reindex each DataFrame against the complete set of column dates
    aligned_dfs = []
    for df in dfs:
        aligned_df = df.reindex(columns=sorted_dates)
        aligned_dfs.append(aligned_df)
        
    return aligned_dfs

# Function to reformat the date columns into a full date string in the financial statements
def format_date_columns(financial_stmt):
    # Transpose so dates are in rows
    df_transposed = financial_stmt.T

    # Convert the index to datetime (if it isn't already) and format it
    df_transposed.index = pd.to_datetime(df_transposed.index)
    df_transposed.index = df_transposed.index.strftime('%d %B %Y')

    # Transpose back so dates are columns again
    formatted_df = df_transposed.T

    return formatted_df

# Function to convert a raw numeric large amount of money (e.g: Market Cap) into an explicit text suffix string
def format_large_money(number):
    if number is None or not isinstance(number, (int, float)):
        return "N/A"
    if abs(number) >= 1_000_000_000_000:
        return f"${number / 1_000_000_000_000:.2f} Trillion"
    elif abs(number) >= 1_000_000_000:
        return f"${number / 1_000_000_000:.2f} Billion"
    elif abs(number) >= 1_000_000:
        return f"${number / 1_000_000:.2f} Million"
    return f"${number:,.0f}"

# Function to format dates from YYYY-MM-DD format (e.g: 2026-10-17) to DD mmm YYYY format (e.g: 17 October 2026) but still of type string
def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{date_obj.day} {date_obj.strftime('%B %Y')}"

# Function to calculate the growth of a specific metric in any of the financial statements
def calculate_growth(parent_metric, financial_stmt):
    # Extract the parent metric from the specific financial statement (handles potential missing rows safely)
    if parent_metric in financial_stmt.index:
        parent_metric_name = financial_stmt.loc[parent_metric]
        
        # Calculate % growth relative to the previous year (which is 1 column to the right)
        # shift(-1) moves the column to the right (older year) to the left for calculation
        prev_year_parent_metric_name = parent_metric_name.shift(-1, axis=0)
        growth = ((parent_metric_name - prev_year_parent_metric_name) / abs(prev_year_parent_metric_name))
        
        return growth.round(4)

# Function to format the rows in any of financial statements using its required units
def format_row(row, percentage_rows=[], quantity_rows=[], pershare_rows=[], ratio_rows=[]):
    """
    This function only applies to dataframes and not series. If there is a series, it must be
    first converted into a dataframe.
    """
    # Getting the metric name from the index through the row.name Series property
    metric_name = row.name
    
    # Category A: Percentage Rows
    if metric_name in percentage_rows:
        # Multiplies by 100 and adds % sign with 2 decimal places
        return row.apply(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "-")
        
    # Category B: Unitless or Number of Share Rows
    elif metric_name in quantity_rows:
        return row.apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "-")
        
    # Category C: Monetary Value per Share Rows (Dollar sign with 2 decimal places for cents)
    elif metric_name in pershare_rows:
        return row.apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "-")

    # Category D: Ratio Rows (Unitless with 3 decimal places)
    elif metric_name in ratio_rows:
        return row.apply(lambda x: f"{x:,.3f}" if pd.notnull(x) else "-")
        
    # Category E: Standard Financial Rows (Dollar sign, rounded to nearest whole integer)
    else:
        return row.apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "-")

# Function to add sub-headers in the dataframe and make the display prettier
def format_financial_statement(financial_stmt, statement_structure, date_columns):
     # Process and restructure the rows sequentially
    formatted_rows = []
    
    for category, labels in statement_structure.items():
        # Add the main structural header row (all numeric columns remain empty/None)
        header_row = {"Metric": category}
        for date_col in date_columns:
            header_row[date_col] = None
        formatted_rows.append(header_row)
        
        # Add the indented labels underneath
        for label in labels:
            # Non-breaking space (\u00A0) forces Streamlit to render spaces
            row_data = {"Metric": f"\u00A0\u00A0\u00A0\u00A0{label}"}
            
            for date_col in date_columns:
                val = financial_stmt.loc[label, date_col]
                # If value is multiple rows/series, grab the first element
                if isinstance(val, pd.Series):
                    val = val.iloc[0]
                row_data[date_col] = val
                
            formatted_rows.append(row_data)

    # Build final structured DataFrame by also invoking the custom format_date_columns
    final_df = pd.DataFrame(formatted_rows)
    final_df = final_df.set_index("Metric")
    try:
        final_df = format_date_columns(final_df)
    except Exception as e:
        # Logs the event cleanly to Streamlit Community Cloud without cluttering or degrading performance
        logger.info(f"Skipped date formatting: {e}. (Expected behavior for non-date dataframes)")
    
    return final_df.reset_index()

# Function to highlight exact cells in a dataframe with background color (Default: yellow) and font-weight bold, identified by index label and column number
def highlight_exact_cells(row, target_cells, background_color="#ffeb3b"):
    """
    row: Pandas Series passed by df.style.apply
    target_cells: list of tuples -> [(row_label_1, col_idx_1), (row_label_2, col_idx_2), ...]
    """
    styles = [''] * len(row)
    
    # Check each (target_row, target_col) pair in your list
    for target_row, target_col_index in target_cells:
        if row.name == target_row:
            styles[target_col_index] = f"background-color: {background_color}; font-weight: bold;"
            
    return styles

# Function to highlight cells in a dataframe based on value1 <= value2 having a negative connotation
def conditional_highlight_negative(value1, value2):
    # Small condition to include "-" as 0
    if value1 == "-":
        value1 = "0"

    try:
        if float(value1.replace("$", "").replace("%", "").replace(",", "")) <= value2:
            return "background-color: #ffcccc; color: #cc0000;" # Light red bg, dark red text
        else:
            return "background-color: #d1ffbd; color: #003333;" # Light green bg, dark green text
    except:
        return None

# Function to highlight cells in a dataframe based on value1 <= value2 having a positive connotation
def conditional_highlight_positive(value1, value2):
    # Small condition to include "-" as 0
    if value1 == "-":
        value1 = "0"

    try:
        if float(value1.replace("$", "").replace("%", "").replace(",", "")) <= value2:
            return "background-color: #d1ffbd; color: #003333;" # Light green bg, dark green text
        else:
            return "background-color: #ffcccc; color: #cc0000;" # Light red bg, dark red text
    except:
        return None

# Function to highlight cells in a dataframe based on value1 = value2 having a positive connotation
def conditional_highlight_equal(value1, value2):
    # Small condition to include "-" as 0
    if value1 == "-":
        value1 = "0"

    try:
        if float(value1.replace("$", "").replace("%", "").replace(",", "")) == value2:
            return "background-color: #d1ffbd; color: #003333;" # Light green bg, dark green text
        else:
            return "background-color: #ffcccc; color: #cc0000;" # Light red bg, dark red text
    except:
        return None

# Function to highlight cells in a dataframe based on lower_limit <= value1 <= upper_limit having a positive connotation
def conditional_highlight_between(value1, lower_limit, upper_limit):
    # Small condition to include "-" as 0
    if value1 == "-":
        value1 = "0"

    try:
        clean_value = float(value1.replace("$", "").replace("%", "").replace(",", ""))
        if clean_value >= lower_limit and clean_value <= upper_limit:
            return "background-color: #d1ffbd; color: #003333;" # Light green bg, dark green text
        else:
            return "background-color: #ffcccc; color: #cc0000;" # Light red bg, dark red text
    except:
        return None