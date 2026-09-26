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
Key insight is that Small-sized institutions dominate most of the districts.
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
        'Large' : 'orange'
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






with st.expander("Design Justification"):
    st.write ("""
-**Chart**: This chart was used for the purpose of understanding the distribution of small , medium  and large institutions. Larger bubbles indicate higher number of institutions , while smaller ones indicated low numbers , which can be easier to spot at first glass, and helps with comparison.

-**Multiselect Feature**:  This feature helps users answer the question :**"How do institution sizes vary between districts?" **

The feature was chosen to enhance comparison between districts' institution sizes since it allows users to select multiple districts of their choice . The colors allocated to each size helps increase contrast and makes this comparison easier. Showing every district at once may make the chart cluttered, and allowing users to filter districts and show only those that are relevant to them can help them differentiate between 2 or more districts , an infer insights that may be more relevant to them.

-**Pills Feature**: This feature makes it faster for users to switch between different combinations of institution sizes that they would like to display , as choices are easy to access. 

Essentially it answers the question of : **“How does the selected institution size compare across the different districts?”** It also helps users determine which districts exhibit a similarity in institution size counts. Since users can remove categories that they are not interested in , focus is narrowed down on the specific sizes they wish to examine.

-**Note**: The two features are linked in the sense that when a district is selected through the multiselect feature , the pills feature only displays the size options that are available for that district. The bubble chart also adjusts based on the choice of users and deductions can be made in a simpler way .

 """)







st.header("Commercial Activity Types by District")

st.write ("""
This stacked-bar chart provides a view of various types of commercial activity across districts , with each stack representing a different activity type .

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

available_activities= sorted(
    available_activities,
    key=lambda activity: bar_data [ bar_data['District'].isin(selected_districts)][activity].sum(), reverse=True

)

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
-**Chart**: This chart was chosen to simplify comparison across categories while still showing the overall level of commercial activity in each district. The categories are ordered from the greatest value to the lowest , making it easier to assess the contribution of each to the total.

-**Multiselect Feature**: This feature , similarly to the previous chart , enables users to select and compare and specific districts, but in this chart, it helps users to investigate how the composition of commercial activity differs across the selected district.

-**Checkbox Feature**: The checkbox widget displays the activity types and serves to answer the question: **“How does the composition of commercial activity change, within districts, when different activity types are selected or excluded?”**. 

I selected this widget because it helps users select several activity categories at the same time , and to see which type of commercial activity contributes most to the differences .

-**Note**: These two widgets are also connected where if a district like Hermel for instance , was selected and does not have any public sector activity , then the latter will not be presented as an available checkbox option to be selected for that district.

    """)


with st.expander ("Sidebar Radio Feature Design Justification"):
    st.write( """
I chose to insert 2 radio buttons that affect the visualization of both charts simultaneously . This feature can help users to observe the variation of institution sizes between those districts with the highest and lowest levels of commercial activity .

When the “Top 5 Districts by Commercial Activity” radio button is selected , both charts change and represent the same group of high-level districts .This widget can help viewers identify patterns that would’ve been harder to determine otherwise. For instance, viewers can see whether districts with the highest number of commercial institutions have the same or different institution size distributions amongst themselves, and against the Bottom 5 districts.
    
    """)





