import streamlit as st 
import pandas as pd 
import plotly.express as px
import ftfy

@st.cache_data
def load_data (path):
    df=pd.read_csv(path)
   
    df.columns=[c.strip() for c in df.columns]
    
    df = df[df['refArea'].str.contains('resource', na=False)]
    
    df['District'] = (df['refArea']
                  .str.split('/').str[-1]
                  .str.replace('_District', '', regex=False)
                  .str.replace(',_Lebanon', '', regex=False)
                  .str.replace('_', ' ', regex=False)
                  .str.strip())
    df['District'] = df['District'].apply(ftfy.fix_text)
    columns_to_keep= [
        'Town',
        'District',
        'Total number of commercial institutions by size - number of small institutions',
        'Total number of commercial institutions by size - number of medium-sized institutions',
        'Total number of commercial institutions by size - number of large-sized institutions',
        'Existence of commercial and service activities by type - self employment',
        'Existence of commercial and service activities by type - commerce',
        'Existence of commercial and service activities by type - public sector',
        'Existence of commercial and service activities by type - banking institutions',
        'Existence of commercial and service activities by type - service institutions'

    ]
    df =df[columns_to_keep]
    return df

file_path= "trade data.csv"
df =load_data(file_path)


df=df.rename(columns={
    'Total number of commercial institutions by size - number of small institutions' : 'Small',
    'Total number of commercial institutions by size - number of medium-sized institutions': 'Medium',
    'Total number of commercial institutions by size - number of large-sized institutions': 'Large',
    'Existence of commercial and service activities by type - self employment' :'Self Employment',
    'Existence of commercial and service activities by type - commerce' :'Commerce',
    'Existence of commercial and service activities by type - public sector' :'Public Sector',
    'Existence of commercial and service activities by type - banking institutions' : 'Banking Institutions',
    'Existence of commercial and service activities by type - service institutions': 'Service Institutions'
})


district_df =df.groupby('District').agg({
    'Small' : 'sum',
    'Medium' : 'sum',
    'Large' : 'sum',
    'Self Employment' : 'sum',
    'Commerce' : 'sum',
    'Public Sector' : 'sum',
    'Banking Institutions' : 'sum',
    'Service Institutions' : 'sum'
}).reset_index()



district_df['Total Activity'] = district_df[
    [
        'Self Employment',
        'Commerce',
        'Public Sector',
        'Banking Institutions',
        'Service Institutions'
    ]
].sum(axis=1)

district_totals = df.groupby(
    'District'
)[['Small', 'Medium', 'Large']].sum().reset_index()




bubble_data = pd.melt(
    district_totals,
    id_vars='District',
    value_vars=['Small', 'Medium', 'Large'],
    var_name='Size',
    value_name='Count'
)





st.title("Lebanon's Institutions and Commercial Activity by District")

with st.sidebar:
    st.header("District View")

    district_view = st.radio(
        "Choose districts:",
        [
            "All Districts",
            "Top 5 Districts By Commercial Activity",
            "Bottom 5 Districts By Commercial Activity"
        ]
    )

if district_view == "Top 5 Districts By Commercial Activity":
    sidebar_districts = (
        district_df
        .sort_values("Total Activity", ascending=False)
        .head(5)["District"]
        .tolist()
    )

elif district_view == "Bottom 5 Districts By Commercial Activity":
    sidebar_districts = (
        district_df
        .sort_values("Total Activity", ascending=True)
        .head(5)["District"]
        .tolist()
    )

else:
    sidebar_districts = sorted(district_df['District'].unique())





st.header("How Big Are Lebanon's Businesses?")

st.write("""
The bubble chart shows how institutions are distributed across 18 Lebanese districts based on their size.
Small-sized institutions dominate most of the districts.
Note: Not all 26 Lebanese Districts were recorded; notably the absence of Beirut and Chouf is a limitation , and their inclusion would've shifted the overall distribution of sizes and commercial activity
""")






all_districts = sorted(bubble_data['District'].unique())

selected_district = st.multiselect(
    'Select Districts',
    options=sidebar_districts,
    default=sidebar_districts
)


if not selected_district or 'All' in selected_district:
    if district_view == "All Districts":
        selected_district = all_districts
    else:
        selected_district = sidebar_districts


available_sizes = sorted(
    bubble_data[
        (bubble_data['District'].isin(selected_district)) &
        (bubble_data ['Count'] > 0)
    ]['Size'].unique()
)

selected_sizes = st.pills(
    "**Select institution sizes:**",
    options=available_sizes,
    default=available_sizes,
    selection_mode="multi"
)

if not selected_sizes:
    selected_sizes = available_sizes





filtered_bubble= bubble_data[
    
    (bubble_data['District'].isin(selected_district)) &
    (bubble_data['Size'].isin(selected_sizes))
    
    ]







fig_bubble= px.scatter(
    filtered_bubble,
    x='District',
    y='Count',
    size='Count',
    color='Size',
    color_discrete_map ={
        'Small' : 'Pink',
        'Medium' : 'blue',
        'Large' : 'green'
    },
    title= f'The size of Institutions across Districts',
    labels={'Count': 'Number of Institutions'},
    size_max=60
)

fig_bubble.update_layout (
    xaxis_tickangle=-45,
    plot_bgcolor='white',
    showlegend=True,
)


st.plotly_chart(fig_bubble, use_container_width=True)






with st.expander("Design Justification :Bubble Chart"):
    st.write ("""
   CHART:
   
   A Bubble Chart was selected to make it easier to visualize two variables at once. The x-axis shows the district names , and the y-axis represents the number of institutions.
   The bubble sizes were adjusted to make larger counts more visible , and each size was allocated a specific color to increase contrast. Both of these decisions help focus viewers' attention on a specific size category.
   
   
   To make comparison between districts easier I added a dropdown list with the option of multiselecting districts , so that users can see the difference in institution sizes between the selected districts of their choice.
   These two features are linked , where when a district is selected the multiselect options only displays the size categories that are available for the chosen districts.The bubble chart would then adjust based on user choice, and insight can be deducted in an easier way.

   
   Important Note: Even though the data does not record all 26 districts , we still chose to display the sizes by district to reduce the clutter as a result of choosing towns, or the lack of depth from choosing governorates.However, this is a limitation and it is important to note that if Beirut and Chouf trade data was recorded, it would have impacted the dominating category.

   

 """)







st.header("Commercial Activity Types by District")

st.write ("""

TEXTTTTTTTTTTT

""")





district_options = ['All'] + sidebar_districts



selected_districts = st.multiselect(
    "Select Districts:",
    options=district_options,
    default=['All']
)

if not selected_districts or 'All' in selected_districts:
    if district_view == "All Districts":
        selected_districts = all_districts
    else:
        selected_districts = sidebar_districts



activity_columns = [
    'Self Employment',
    'Commerce',
    'Public Sector',
    'Banking Institutions',
    'Service Institutions'
]

bar_data = district_df[['District'] + activity_columns]

available_activities = [
    activity
    for activity in activity_columns
    if bar_data[
        bar_data['District'].isin(selected_districts)
    ][activity].sum() > 0
]

st.write("**Select activity types:**")

selected_activity = []

cols = st.columns(3)

for i, activity in enumerate(available_activities):
    with cols[i % 3]:
        if st.checkbox(activity, value=True):
            selected_activity.append(activity)


display_columns = selected_activity



filtered_bar = pd.melt(
    bar_data[bar_data['District'].isin(selected_districts)],
    id_vars='District',
    value_vars=display_columns,
    var_name='Activity',
    value_name='Count'
)

fig_bar=px.bar(
    filtered_bar,
    x='District',
    y='Count',
    color='Activity',
    title='Commercial Activity Types per District',
    labels={'Count': 'Count'}

)

fig_bar.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor='white'
)

st.plotly_chart(fig_bar,use_container_width=True)









with st.expander("Design Justification: Stacked Bar Chart "):
    st.write("""
    TEXTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
    """)








