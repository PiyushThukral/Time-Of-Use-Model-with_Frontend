import plotly.graph_objs as go

def get_cluster_plot_figure(
    final_clustered_data,
    final_medoid_data,
    category,
    load_bin,
    consumption_bin,
    time_blocks,
    consumption_values
):
    """
    Returns a Plotly figure for a given category, load_bin, and consumption_bin.

    Parameters:
        final_clustered_data (pd.DataFrame): Clustered consumers.
        final_medoid_data (pd.DataFrame): Medoid representatives.
        category (str): Filter category.
        load_bin (str or float): Load bin label.
        consumption_bin (str or float): Consumption bin label.

    Returns:
        go.Figure: Plotly figure to be used in dcc.Graph
    """

    # cluster_subset = final_clustered_data[
    #     (final_clustered_data['Category'] == category) &
    #     (final_clustered_data['load_bin'] == load_bin) &
    #     (final_clustered_data['consumption_bin'] == consumption_bin)
    # ]

    # medoid_subset = final_medoid_data[
    #     (final_medoid_data['Category'] == category) &
    #     (final_medoid_data['load_bin'] == load_bin) &
    #     (final_medoid_data['consumption_bin'] == consumption_bin)
    # ]

    # Start with all dataAdd commentMore actions
    cluster_subset = final_clustered_data.copy()
    medoid_subset = final_medoid_data.copy()

     # Dynamically apply filters based on which parameters are not NoneAdd commentMore actions
    if category is not None:
        cluster_subset = cluster_subset[cluster_subset['Category'] == category]
        medoid_subset = medoid_subset[medoid_subset['Category'] == category]

    if load_bin is not None:
        cluster_subset = cluster_subset[cluster_subset['load_bin'] == load_bin]
        medoid_subset = medoid_subset[medoid_subset['load_bin'] == load_bin]

    if consumption_bin is not None:
        cluster_subset = cluster_subset[cluster_subset['consumption_bin'] == consumption_bin]
        medoid_subset = medoid_subset[medoid_subset['consumption_bin'] == consumption_bin]

    # Handle empty cluster case

    if cluster_subset.empty:
        return go.Figure().update_layout(
            #title=f"No data for Category: {category}, Load: {load_bin}, Consumption: {consumption_bin}"
            title="No data available for the selected filters."
        )



    hours = list(range(time_blocks['first'], time_blocks['last'] + 1))
    fig = go.Figure()


    # Plot all consumer profiles in grey
    for _, row in cluster_subset.iterrows():
        if consumption_values is None:
            cons_values = [row[f'Consumption_Hr_{h}'] for h in hours]
        else:
            cons_values = [row[col] for col in consumption_values]
        fig.add_trace(go.Scatter(
            x=hours,
            y=cons_values,
            mode='lines',
            line=dict(color='grey', width=1),
            opacity=0.5,
            showlegend=False
        ))

    # Plot medoid profiles in black
    if not medoid_subset.empty:
        for _, row in medoid_subset.iterrows():
            if consumption_values is None:
                cons_values = [row[f'Consumption_Hr_{h}'] for h in hours]
            else:
                cons_values = [row[col] for col in consumption_values]
            fig.add_trace(go.Scatter(
                x=hours,
                y=cons_values,
                mode='lines',
                line=dict(color='black', width=3),
                #name='Medoid',
                name= f"Cluster Medoid - {row['Cluster']}"
            ))
    
    fig.update_xaxes(tickmode='linear')
    
    fig.update_xaxes(
        tickmode='array',
        tickvals=hours,
        ticktext=[str(h) for h in hours]
    )

    # Build dynamic title componentsAdd commentMore actions
    title_parts = []
    if category is not None:
        title_parts.append(f"Category: {category}")
    if load_bin is not None:
        title_parts.append(f"Load Bin: {load_bin}")
    if consumption_bin is not None:
        title_parts.append(f"Consumption Bin: {consumption_bin}")

    # Join the parts with separatorsAdd commentMore actions
    title_text = " | ".join(title_parts) if title_parts else ""



    fig.update_layout(
        #title=f"Category: {category} | Load Bin: {load_bin} | Consumption Bin: {consumption_bin}",
        title = title_text,
        xaxis_title='Hour of Day',
        #yaxis_title='Consumption',
        #template='plotly_white',
        yaxis_title='Consumption Load(kW)'

    )

    return fig
