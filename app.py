import streamlit as st 
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import ftfy

@st.cache_data
def load_data (path):
    df=pd.read_csv(path)
   
    df.columns=[c.strip() for c in df.columns]
    
    df = df[df['refArea'].str.contains('resource')] 
    
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
    'Total number of commercial institutions by size - number of small institutions' : 'Small Institutions',
    'Total number of commercial institutions by size - number of medium-sized institutions': 'Medium Institutions',
    'Total number of commercial institutions by size - number of large-sized institutions': 'Large Institutions',
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

district_totals = df.groupby ('District')[['Small','Medium','Large']].sum().reset_index()



bubble_data=pd.melt (
    district_totals,
    id_vars='District',
    value_vars=['Small','Medium','Large'],
    var_name= 'Size',
    value_name= 'Count'
)

district_totals['Total'] = district_totals['Small'] + district_totals['Medium'] + district_totals['Large']
bubble_data = bubble_data.merge(district_totals[['District', 'Total']], on='District')






st.title("Lebanon's Insitutions and Commercial Activity by District")

st.header("How Big Are Lebanon's Businesses?")

st.write("""
The bubble chart shows how insitutions are distributed across 18 Lebanese dsitricts based on their size. 
Small-sized institutions dominate most of the districts.
Note: Not all 26 Lebanese Districts were recorded; notably the absence of Beirut and Chouf is a limitation , and their inclusion would've shifted the overall distribution of sizes and commercial activity
""")






all_districts =sorted(bubble_data['District'].unique())
selected_district =st.multiselect(
    'Select Districts',
    options= all_districts,
    default=[all_districts[0]], )


if not selected_district :
    selected_district= all_districts


selected_sizes= st.multiselect(
    'Filter by institution size',
    options=['Small','Medium','Large'],
    default= ['Small','Medium','Large']
)

if not selected_sizes :
    selected_sizes =['Small','Medium','Large']

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
    title= f'The size of Institutions across 18 Districts',
    labels={'Count': 'Number of Institutions'},
    size_max=60
)

fig_bubble.update_layout (
    xaxis_tickangle=-45,
    plot_bgcolor='white'
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




activity_columns = ['Self Employment', 'Commerce', 'Public Sector', 'Banking Institutions', 'Service Institutions']
bar_data = district_df[['District'] + activity_columns]

 
activity_options = ['All'] + activity_columns
selected_activity = st.radio(
    "Focus on an activity type:",
    options=activity_options,
    horizontal=True
)





grouped = st.toggle("Switch to grouped view")

if grouped:
    barmode = 'group'
else:
    barmode = 'stack'




if selected_activity == 'All':
    display_columns = activity_columns
else:
    display_columns = [selected_activity]



filtered_bar = pd.melt(
    bar_data,
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
    barmode=barmode,
    title='Commercial Activity Types per District',
    labels={'count': 'Number of Towns'}

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