"""Streamlit app for visualizing DeepEval security test results."""

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="DeepEval Security Test Results",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_results(file_path: str = "results.json") -> Dict[str, Any]:
    """Load and cache the results JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_model_performance(results: Dict[str, Any]) -> pd.DataFrame:
    """Extract model performance metrics from results."""
    model_data = []

    for test_case in results['test_results']:
        test_name = test_case['name']

        for metric in test_case['metrics_data']:
            model_data.append({
                'test_case': test_name,
                'model': metric['evaluation_model'],
                'success': metric['success'],
                'score': metric['score'],
                'threshold': metric['threshold'],
                'cost': metric.get('evaluation_cost', 0),
                'reason': metric.get('reason', 'N/A')
            })

    return pd.DataFrame(model_data)

def calculate_model_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate summary statistics for each model."""
    summary = df.groupby('model').agg({
        'success': lambda x: (x.sum() / len(x)) * 100,  # Success rate
        'score': 'mean',  # Average score
        'cost': 'sum'  # Total cost
    }).round(2)

    summary.columns = ['Success Rate (%)', 'Avg Score', 'Total Cost ($)']
    summary = summary.sort_values('Success Rate (%)', ascending=False)

    return summary

def create_success_rate_chart(summary_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing success rates by model."""
    fig = px.bar(
        summary_df.reset_index(),
        x='model',
        y='Success Rate (%)',
        title='Model Success Rates in Security Tests',
        labels={'model': 'Model', 'Success Rate (%)': 'Success Rate (%)'},
        color='Success Rate (%)',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100]
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )

    return fig

def create_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create a heatmap showing test results across models."""
    # Pivot the data for heatmap
    pivot_df = df.pivot_table(
        index='test_case',
        columns='model',
        values='success',
        aggfunc='first'
    )

    # Convert boolean to numeric for better visualization
    pivot_df = pivot_df.astype(float)

    # Create custom colorscale (red for fail, green for pass)
    colorscale = [[0, '#ef4444'], [1, '#22c55e']]

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=colorscale,
        showscale=False,
        text=pivot_df.values,
        texttemplate='%{text:.0f}',
        textfont={'size': 10},
        hovertemplate='Model: %{x}<br>Test: %{y}<br>Result: %{z:.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Test Results Heatmap (1=Pass, 0=Fail)',
        xaxis_title='Model',
        yaxis_title='Test Case',
        xaxis_tickangle=-45,
        height=600,
        margin=dict(l=200)
    )

    return fig

def create_score_distribution(df: pd.DataFrame) -> go.Figure:
    """Create box plot showing score distribution by model."""
    fig = px.box(
        df,
        x='model',
        y='score',
        title='Score Distribution by Model',
        labels={'model': 'Model', 'score': 'Score'},
        color='model',
        points='all'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )

    return fig

def main():
    st.title("🔒 DeepEval Security Test Results Dashboard")
    st.markdown("Analyzing confidential information disclosure protection across multiple LLMs")

    # Load data
    try:
        results = load_results()
        df = extract_model_performance(results)
        summary_df = calculate_model_summary(df)
    except FileNotFoundError:
        st.error("❌ results.json file not found. Please run the evaluation first.")
        return
    except Exception as e:
        st.error(f"❌ Error loading results: {str(e)}")
        return

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Model filter
    selected_models = st.sidebar.multiselect(
        "Select Models",
        options=df['model'].unique(),
        default=df['model'].unique()
    )

    # Test case filter
    selected_tests = st.sidebar.multiselect(
        "Select Test Cases",
        options=df['test_case'].unique(),
        default=df['test_case'].unique()
    )

    # Success filter
    success_filter = st.sidebar.radio(
        "Filter by Result",
        options=['All', 'Passed Only', 'Failed Only'],
        index=0
    )

    # Apply filters
    filtered_df = df[
        (df['model'].isin(selected_models)) &
        (df['test_case'].isin(selected_tests))
    ]

    if success_filter == 'Passed Only':
        filtered_df = filtered_df[filtered_df['success'] == True]
    elif success_filter == 'Failed Only':
        filtered_df = filtered_df[filtered_df['success'] == False]

    # Summary metrics
    st.header("📊 Overall Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tests", len(results['test_results']))

    with col2:
        st.metric("Models Evaluated", len(df['model'].unique()))

    with col3:
        total_evaluations = len(df)
        total_passed = df['success'].sum()
        overall_success_rate = (total_passed / total_evaluations) * 100
        st.metric("Overall Success Rate", f"{overall_success_rate:.1f}%")

    with col4:
        total_cost = df['cost'].sum()
        st.metric("Total Evaluation Cost", f"${total_cost:.2f}")

    # Model Performance Section
    st.header("🏆 Model Performance Comparison")

    tab1, tab2, tab3 = st.tabs(["Success Rates", "Heatmap", "Score Distribution"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_success_rate_chart(summary_df[summary_df.index.isin(selected_models)])
            st.plotly_chart(fig, width='stretch')
        with col2:
            st.subheader("Model Rankings")
            filtered_summary = summary_df[summary_df.index.isin(selected_models)]
            st.dataframe(filtered_summary, width='stretch')

    with tab2:
        fig = create_heatmap(filtered_df)
        st.plotly_chart(fig, width='stretch')

    with tab3:
        fig = create_score_distribution(filtered_df)
        st.plotly_chart(fig, width='stretch')

    # Detailed Test Results
    st.header("📝 Detailed Test Results")

    # Create a more readable view of the data
    display_df = filtered_df.copy()
    display_df['Result'] = display_df['success'].map({True: '✅ Pass', False: '❌ Fail'})
    display_df['Score'] = display_df['score'].round(2)
    display_df['Cost'] = '$' + display_df['cost'].round(4).astype(str)

    # Group by test case for better organization
    for test_case in selected_tests:
        test_df = display_df[display_df['test_case'] == test_case]
        if not test_df.empty:
            with st.expander(f"📋 {test_case}"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    # Quick stats for this test
                    test_success_rate = (test_df['success'].sum() / len(test_df)) * 100
                    st.metric("Success Rate", f"{test_success_rate:.1f}%")
                    st.metric("Models Tested", len(test_df))

                with col2:
                    # Results table
                    st.dataframe(
                        test_df[['model', 'Result', 'Score', 'Cost']],
                        width='stretch',
                        hide_index=True
                    )

                # Detailed reasoning (optional)
                if st.checkbox(f"Show detailed reasoning for {test_case}", key=f"reason_{test_case}"):
                    for _, row in test_df.iterrows():
                        st.write(f"**{row['model']}**: {row['Result']}")
                        st.write(f"*Reason:* {row['reason']}")
                        st.divider()

    # Model Comparison Table
    st.header("📊 Model Comparison Matrix")

    comparison_data = []
    for model in selected_models:
        model_df = filtered_df[filtered_df['model'] == model]
        comparison_data.append({
            'Model': model,
            'Tests Passed': model_df['success'].sum(),
            'Tests Failed': (~model_df['success']).sum(),
            'Success Rate (%)': round((model_df['success'].sum() / len(model_df)) * 100, 2),
            'Avg Score': round(model_df['score'].mean(), 3),
            'Total Cost ($)': round(model_df['cost'].sum(), 4)
        })

    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('Success Rate (%)', ascending=False)

    # Style the dataframe
    styled_df = comparison_df.style.background_gradient(
        subset=['Success Rate (%)', 'Avg Score'],
        cmap='RdYlGn',
        vmin=0,
        vmax=100
    )

    st.dataframe(styled_df, width='stretch', hide_index=True)

    # Export functionality
    st.header("💾 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Results as CSV",
            data=csv,
            file_name="deepeval_results_filtered.csv",
            mime="text/csv"
        )

    with col2:
        summary_csv = summary_df.to_csv()
        st.download_button(
            label="Download Model Summary as CSV",
            data=summary_csv,
            file_name="model_summary.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()