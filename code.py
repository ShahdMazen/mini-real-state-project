import streamlit as st
import pandas as pd
import re

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="Real Estate Dashboard",
    page_icon="🏘️",
    layout="wide"
)


# -------------------------
# Helper Functions
# -------------------------
def parse_price(price_str):
    if pd.isna(price_str):
        return 0
    price_str = str(price_str).strip().upper()
    match = re.match(r'([\d.]+)\s*([MK]?)', price_str)
    if match:
        number = float(match.group(1))
        multiplier = match.group(2)
        if multiplier == 'M':
            return number * 1_000_000
        elif multiplier == 'K':
            return number * 1_000
        else:
            return number
    return 0


def parse_space(space_str):
    if pd.isna(space_str):
        return 0
    space_str = str(space_str).strip().lower()
    match = re.match(r'([\d.]+)', space_str)
    if match:
        return float(match.group(1))
    return 0


def format_price_for_csv(price_numeric):
    """Convert numeric price back to CSV format (e.g., 2500000 -> 2.5M)"""
    if price_numeric >= 1_000_000:
        return f"{price_numeric / 1_000_000:.1f}M"
    elif price_numeric >= 1_000:
        return f"{price_numeric / 1_000:.1f}K"
    else:
        return str(int(price_numeric))


# -------------------------
# Load Data from CSV
# -------------------------
def load_data():
    """Load data from CSV file - NO CACHING to always get fresh data"""
    try:
        try:
            df = pd.read_csv("projects_data.csv", encoding='utf-8')
        except:
            try:
                df = pd.read_csv("projects_data.csv", encoding='utf-8-sig')
            except:
                df = pd.read_csv("projects_data.csv", encoding='latin-1')
        df.columns = df.columns.str.strip()
        df['Price_Numeric'] = df['Price'].apply(parse_price)
        df['Space_Numeric'] = df['Space'].apply(parse_space)
        return df
    except FileNotFoundError:
        st.error("❌ ملف 'projects_data.csv' مش موجود!")
        st.stop()
    except Exception as e:
        st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
        st.stop()


def save_data(df):
    """Save dataframe back to CSV"""
    # Prepare data for CSV (only original columns)
    save_df = df[['DEV', 'PROJ', 'City', 'Dis', 'Type', 'Price', 'Space']].copy()
    save_df.to_csv("projects_data.csv", index=False, encoding='utf-8')


# -------------------------
# Initialize data
# -------------------------
df = load_data()

# -------------------------
# Title
# -------------------------
st.title("🏘️ Real Estate Management System")
st.markdown("---")

# -------------------------
# Add New Project Section
# -------------------------
with st.expander("➕ Add New Project"):
    st.subheader("Add New Project")

    col1, col2 = st.columns(2)

    with col1:
        new_dev = st.text_input("Developer*", key="new_dev")
        new_proj = st.text_input("Project Name*", key="new_proj")
        new_city = st.text_input("City*", key="new_city")
        new_dis = st.text_input("District*", key="new_dis")

    with col2:
        new_type = st.text_input("Property Type* (e.g., Villa, Loft, Apartment)", key="new_type")
        new_price = st.number_input("Price (AED)*", min_value=0, step=100000, key="new_price")
        new_space = st.number_input("Space (sq ft)*", min_value=0, step=10, key="new_space")

    if st.button("💾 Save Project", type="primary"):
        if new_dev and new_proj and new_city and new_dis and new_type and new_price > 0 and new_space > 0:
            # Create new row
            new_row = pd.DataFrame({
                'DEV': [new_dev],
                'PROJ': [new_proj],
                'City': [new_city],
                'Dis': [new_dis],
                'Type': [new_type],
                'Price': [format_price_for_csv(new_price)],
                'Space': [f"{int(new_space)}ft"],
                'Price_Numeric': [new_price],
                'Space_Numeric': [new_space]
            })

            # Append to dataframe
            df = pd.concat([df, new_row], ignore_index=True)

            # Save to CSV
            save_data(df)

            st.success("✅ Project added successfully! Reloading page...")
            st.rerun()
        else:
            st.error("❌ Please fill all required fields!")

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filter Options")

developers = ["All"] + sorted(df["DEV"].dropna().unique())
selected_dev = st.sidebar.selectbox("Developer:", developers)

projects = ["All"] + sorted(df["PROJ"].dropna().unique())
selected_proj = st.sidebar.selectbox("Project:", projects)

cities = ["All"] + sorted(df["City"].dropna().unique())
selected_city = st.sidebar.selectbox("City:", cities)

districts = ["All"] + sorted(df["Dis"].dropna().unique())
selected_district = st.sidebar.selectbox("District:", districts)

types = ["All"] + sorted(df["Type"].dropna().unique())
selected_type = st.sidebar.selectbox("Property Type:", types)

# Price Range
st.sidebar.subheader("💰 Price Range (AED)")
min_price = int(df["Price_Numeric"].min()) if len(df) > 0 else 0
max_price = int(df["Price_Numeric"].max()) if len(df) > 0 else 10000000
price_from = st.sidebar.number_input("Price From:", min_value=0, max_value=max_price, value=min_price, step=100000)
price_to = st.sidebar.number_input("Price To:", min_value=0, max_value=max_price, value=max_price, step=100000)

# Space Range
st.sidebar.subheader("📐 Space Range (sq ft)")
min_space = int(df["Space_Numeric"].min()) if len(df) > 0 else 0
max_space = int(df["Space_Numeric"].max()) if len(df) > 0 else 1000
space_from = st.sidebar.number_input("Space From:", min_value=0, max_value=max_space, value=min_space, step=10)
space_to = st.sidebar.number_input("Space To:", min_value=0, max_value=max_space, value=max_space, step=10)


# -------------------------
# Filter Function
# -------------------------
def filter_df(df):
    filtered = df.copy()
    if selected_dev != "All":
        filtered = filtered[filtered["DEV"] == selected_dev]
    if selected_proj != "All":
        filtered = filtered[filtered["PROJ"] == selected_proj]
    if selected_city != "All":
        filtered = filtered[filtered["City"] == selected_city]
    if selected_district != "All":
        filtered = filtered[filtered["Dis"] == selected_district]
    if selected_type != "All":
        filtered = filtered[filtered["Type"] == selected_type]
    filtered = filtered[
        (filtered["Price_Numeric"] >= price_from) &
        (filtered["Price_Numeric"] <= price_to) &
        (filtered["Space_Numeric"] >= space_from) &
        (filtered["Space_Numeric"] <= space_to)
        ]
    return filtered


filtered_df = filter_df(df)

# -------------------------
# Display Results with Pagination
# -------------------------
st.subheader(f"📊 Filtered Results ({len(filtered_df)} projects found)")

if len(filtered_df) > 0:
    page_size = 10
    total_pages = max(1, (len(filtered_df) - 1) // page_size + 1)
    page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start = (page_number - 1) * page_size
    end = start + page_size

    display_df = filtered_df.iloc[start:end][['DEV', 'PROJ', 'City', 'Dis', 'Type', 'Price', 'Space']].copy()
    display_df.columns = ['Developer', 'Project', 'City', 'District', 'Type', 'Price (AED)', 'Space (sq ft)']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # -------------------------
    # Delete Project Section
    # -------------------------
    with st.expander("❌ Delete Project"):

        # Get list of projects to delete
        project_list = filtered_df.apply(
            lambda row: f"{row['PROJ']} - {row['City']} ({row['DEV']})", axis=1
        ).tolist()

        if project_list:
            selected_to_delete = st.selectbox(
                "Select project to delete:",
                options=range(len(project_list)),
                format_func=lambda x: project_list[x]
            )

            if st.button("🗑️ Delete Selected Project", type="secondary"):
                # Get the actual index from original dataframe
                idx_to_delete = filtered_df.iloc[start + selected_to_delete].name

                # Remove from dataframe
                df = df.drop(idx_to_delete)

                # Save to CSV
                save_data(df)

                st.success("✅ Project deleted successfully! Reloading page...")
                st.rerun()
        else:
            st.info("No projects to delete")

    # -------------------------
    # Dashboard Metrics
    # -------------------------
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Projects", len(filtered_df))
    with col2:
        avg_price = filtered_df['Price_Numeric'].mean()
        st.metric("Avg Price (AED)", f"{avg_price:,.0f}")
    with col3:
        avg_space = filtered_df['Space_Numeric'].mean()
        st.metric("Avg Space (sq ft)", f"{avg_space:,.0f}")

    # -------------------------
    # Download Filtered Data
    # -------------------------
    st.markdown("---")
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_projects.csv",
        mime="text/csv"
    )
else:
    st.warning("⚠️ No projects found matching your criteria.")

# -------------------------
# Reload Data Button
# -------------------------
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reload Data from CSV"):
    st.rerun()

# -------------------------
# About App
# -------------------------
with st.expander("ℹ️ About this App"):
    st.write("""
    ### Features:
    - ➕ **Add New Projects** - Add projects directly from the app
    - ❌ **Delete Projects** - Remove unwanted projects
    - 🔍 **Advanced Filters** - Filter by Developer, City, Type, Price, Space
    - 📊 **Dashboard Metrics** - View statistics at a glance
    - 📥 **Export Data** - Download filtered results as CSV
    - 🔄 **Auto Refresh** - Data updates automatically

    ### How to Use:
    1. Use filters in sidebar to narrow down results
    2. Click "Add New Project" to add entries
    3. Click "Delete Project" to remove entries
    4. Changes are saved to CSV immediately
    5. Use "Reload Data" button if CSV was edited externally
    """)
