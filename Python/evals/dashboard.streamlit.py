#!/usr/bin/env python3
"""
Streamlit Dashboard for DeepEval Security Evaluation Results
Visualizes test results from eval_cast_security.py
"""

import json
import pickle
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Dict, List, Any, Optional
import colorsys

# Define the directory which contains this script.
BASE_DIR = Path(__file__).resolve().parent

# Page config
st.set_page_config(
    page_title="DeepEval Security Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Global styles */
    .main {
        padding: 1rem;
    }

    /* Increase global font size */
    .stMarkdown {
        font-size: 1.1rem;
    }

    .stButton > button {
        font-size: 1.1rem;
    }

    .stSelectbox > label {
        font-size: 1.1rem;
    }

    /* Heatmap cell styling */
    .heatmap-cell {
        cursor: pointer;
        transition: all 0.2s;
        padding: 8px;
        text-align: center;
        border-radius: 4px;
        font-weight: 600;
    }

    .heatmap-cell:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Score badge styling */
    .score-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
    }

    /* Metric card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Detail panel styling */
    .detail-panel {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
        max-height: 600px;
        overflow-y: auto;
    }

    /* Table styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }

    .styled-table th {
        background: #f1f3f4;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }

    .styled-table td {
        padding: 12px;
        border-bottom: 1px solid #e0e0e0;
    }

    .styled-table tr:hover {
        background: #f8f9fa;
    }

    /* Clean expandable sections */
    .stExpander {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        background: white !important;
    }

    .stExpander > div[data-testid="stExpanderDetails"] {
        padding: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_results(dataset: str = "main") -> Dict:
    """Load evaluation results from JSON file"""
    filepath = BASE_DIR.parent / f"results.{dataset}.json"
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Results file not found: {filepath}")
        return {"test_results": []}

@st.cache_data
def load_conversations() -> Dict:
    """Load conversation data from pickle file"""
    filepath = BASE_DIR / "conversation.tests.pkl"
    conversations = {}
    with open(filepath, 'rb') as f:
        dataset = pickle.load(f)
        for test_case in dataset.test_cases:
            conversations[test_case.name] = test_case.turns
    return conversations

def get_score_color(score: float) -> str:
    """Get color for score value using gradient from red to yellow to green"""
    # Normalize score to 0-1 range
    score = max(0.0, min(1.0, float(score)))

    if score >= 1.0:
        return "#27ae60"  # Green
    elif score >= 0.9:
        return "#52c41a"
    elif score >= 0.8:
        return "#73d13d"
    elif score >= 0.7:
        return "#95de64"
    elif score >= 0.6:
        return "#b7eb8f"
    elif score >= 0.5:
        return "#ffd666"  # Yellow
    elif score >= 0.4:
        return "#ffa940"
    elif score >= 0.3:
        return "#ff7a45"
    elif score >= 0.2:
        return "#ff4d4f"
    elif score >= 0.1:
        return "#e74c3c"
    else:
        return "#cf1322"  # Red


def create_heatmap_data(results: Dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create DataFrames for heatmap visualization
    Returns: (scores_df, thresholds_df)
    """
    data = []
    threshold_data = []

    # Track costs per model for the cost row
    model_costs = {}

    for test in results.get("test_results", []):
        test_name = test["name"]

        # Group metrics by evaluation model
        model_scores = {}
        model_thresholds = {}
        for metric in test.get("metrics_data", []):
            model = metric.get("evaluation_model", "unknown")
            score = metric.get("score", 0.0)
            threshold = metric["threshold"]
            # threshold = metric.get("threshold", 1.0)
            cost = metric.get("evaluation_cost", 0.0)
            model_scores[model] = score
            model_thresholds[model] = threshold

            # Accumulate costs per model
            if model not in model_costs:
                model_costs[model] = 0.0
            model_costs[model] += cost

        data.append({
            "test": test_name,
            **model_scores
        })
        threshold_data.append({
            "test": test_name,
            **model_thresholds
        })

    df = pd.DataFrame(data)
    thresholds_df = pd.DataFrame(threshold_data)

    if not df.empty:
        df = df.set_index("test")
        thresholds_df = thresholds_df.set_index("test")

        # Sort test cases alphabetically
        df = df.sort_index()
        thresholds_df = thresholds_df.sort_index()

        # Add cost row at the top
        if model_costs:
            cost_row = pd.DataFrame([model_costs], index=["Cost ($)"])
            # Ensure all columns exist in cost row
            for col in df.columns:
                if col not in cost_row.columns:
                    cost_row[col] = 0.0
            # Reorder columns to match df
            cost_row = cost_row[df.columns]
            # Prepend cost row to the dataframe
            df = pd.concat([cost_row, df])

            # Add dummy threshold row for cost (will be ignored)
            threshold_cost_row = pd.DataFrame([{col: np.nan for col in df.columns}], index=["Cost ($)"])
            thresholds_df = pd.concat([threshold_cost_row, thresholds_df])

    return df, thresholds_df


def display_top_metrics(results: Dict):
    """Display top-level KPI metrics"""
    test_results = results.get("test_results", [])

    # Calculate metrics
    total_tests = len(test_results)

    # Get unique evaluation models
    all_models = set()
    total_cost = 0.0

    for test in test_results:
        for metric in test.get("metrics_data", []):
            all_models.add(metric.get("evaluation_model", ""))
            total_cost += metric.get("evaluation_cost", 0.0)

    total_metrics = len(all_models)

    # Display in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tests", total_tests)

    with col2:
        st.metric("Total Metrics", total_metrics)

    with col3:
        st.metric("Total Cost", f"${total_cost:.2f}")


def display_heatmap(results: Dict, selected_cell_callback):
    """Display the Test x Metric Heatmap"""
    col1, col2 = st.columns([3, 1])
    with col2:
        # Toggle for color mode
        use_threshold = st.toggle("Threshold Mode", value=True,
                                  help="When enabled, scores below their metric-specific threshold show as red (fail). When disabled, shows gradient coloring.")
    with col1:
        # Change header based on mode
        if use_threshold:
            st.subheader("📊 Test × Metric Pass/Fail")
        else:
            st.subheader("📊 Test × Metric Heatmap")

    # Create heatmap data
    df, thresholds_df = create_heatmap_data(results)

    if df.empty:
        st.warning("No data available for heatmap")
        return None, None

    # Separate cost row from score data
    has_cost_row = "Cost ($)" in df.index
    if has_cost_row:
        cost_row = df.loc[["Cost ($)"]]
        score_df = df.drop(["Cost ($)"])
        threshold_score_df = thresholds_df.drop(["Cost ($)"])
    else:
        score_df = df
        threshold_score_df = thresholds_df

    # Create z values with normalized scores (cost row will be set to NaN for no color)
    if has_cost_row:
        # Create z values: NaN for cost row (no color), actual values for scores
        z_values = []
        text_values = []

        # Add cost row with NaN for z (no color) but formatted text
        cost_z = [np.nan] * len(df.columns)
        cost_text = [f"${val:.2f}" for val in cost_row.values[0]]
        z_values.append(cost_z)
        text_values.append(cost_text)

        # Add score rows with threshold-based coloring if enabled
        for idx in score_df.index:
            row_values = score_df.loc[idx].values
            threshold_values = threshold_score_df.loc[idx].values
            if use_threshold:
                # In threshold mode: scores < their specific threshold get max red (value 0)
                # or otherwise, max green (value 1)
                z_row = [0.0 if val < thresh else 1.0 for val,thresh in zip(row_values, threshold_values)]
            else:
                # In gradient mode: use actual values
                z_row = row_values.tolist()
            z_values.append(z_row)
            text_values.append([f"{val:.2f}" for val in row_values])

        z = np.array(z_values)
        text = text_values
    else:
        if use_threshold:
            # Apply threshold coloring for scores without cost row
            z = np.array([[0.0 if val < thresh else val
                          for val, thresh in zip(row, threshold_row)]
                         for row, threshold_row in zip(df.values, thresholds_df.values)])
        else:
            z = df.values
        text = [[f"{val:.2f}" for val in row] for row in df.values]

    # Create plotly heatmap with better color scale
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=df.columns.tolist(),
        y=df.index.tolist(),
        text=text,
        texttemplate="%{text}",
        textfont={"size": 18},  # Increased from 12 to 18 (1.5x)
        colorscale=[
            [0, "#cf1322"],     # Deep red
            [0.2, "#ff4d4f"],   # Red
            [0.4, "#ffa940"],   # Orange
            [0.6, "#ffd666"],   # Yellow
            [0.8, "#95de64"],   # Light green
            [1.0, "#52c41a"]    # Green
        ],
        colorbar=dict(
            title="Score",
            thickness=20,
            len=0.7,
            tickmode="array",
            tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
            ticktext=["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]
        ),
        hovertemplate="Test: %{y}<br>Metric: %{x}<br>Value: %{text}<extra></extra>",
        showscale=True,
        zmin=0,
        zmax=1
    ))

    # Calculate appropriate dimensions based on data
    num_tests = len(df.index)
    num_models = len(df.columns)

    # Make cells taller (30-40px per cell) and narrower
    cell_height = 35
    cell_width = 90

    # Calculate total dimensions
    plot_height = max(400, num_tests * cell_height + 150)  # Add margin for labels
    plot_width = num_models * cell_width + 250  # Add margin for test names

    fig.update_layout(
        title="",
        xaxis_title="Evaluation Model",
        yaxis_title="Test Case",
        height=plot_height,
        width=min(plot_width, 1000),  # Cap maximum width
        margin=dict(l=180, r=50, t=30, b=120),
        xaxis=dict(
            tickangle=45,
            side="bottom",
            tickfont=dict(size=14)  # Increased from 11
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=14)  # Increased from 11
        ),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    # Add visual separator after cost row if it exists
    if has_cost_row:
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=len(df.columns) - 0.5,
            y0=0.5,
            y1=0.5,
            line=dict(color="rgba(0,0,0,0.3)", width=2)
        )

    # Display the heatmap without forcing full container width
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.plotly_chart(
            fig,
            use_container_width=False,
            key="heatmap"
        )

    # Return None since we don't have interactive selection
    return None, None


def display_prompt_performance(results: Dict, selected_metric: Optional[str] = None):
    """Display Prompt Performance section"""
    st.subheader("🎯 Prompt Performance — Per Metric")

    test_results = results.get("test_results", [])

    # Get all unique metrics
    all_metrics = set()
    for test in test_results:
        for metric in test.get("metrics_data", []):
            all_metrics.add(metric.get("evaluation_model", ""))

    # Metric selector
    col1, col2 = st.columns([3, 4])
    with col1:
        if selected_metric and selected_metric in all_metrics:
            default_idx = list(all_metrics).index(selected_metric)
        else:
            default_idx = 0

        selected_model = st.selectbox(
            "Select Evaluation Model",
            sorted(list(all_metrics)),
            index=default_idx,
            key="prompt_metric_selector"
        )

    if not selected_model:
        st.info("Select a metric to view performance analysis")
        return

    # Calculate performance metrics for selected model
    model_data = []
    for test in test_results:
        for metric in test.get("metrics_data", []):
            if metric.get("evaluation_model") == selected_model:
                model_data.append({
                    "test": test["name"],
                    "score": metric.get("score", 0.0),
                    "threshold": metric.get("threshold", 1.0),
                    "success": metric.get("success", False),
                    "reason": metric.get("reason", ""),
                    "verbose_logs": metric.get("verbose_logs", ""),
                    "cost": metric.get("evaluation_cost", 0.0)
                })

    if not model_data:
        st.warning(f"No data available for {selected_model}")
        return

    # Calculate summary statistics
    df_model = pd.DataFrame(model_data)
    pass_rate = (df_model['success'].sum() / len(df_model)) * 100
    fail_rate = 100 - pass_rate
    num_pass = df_model['success'].sum()
    num_fail = len(df_model) - num_pass
    mean_score = df_model['score'].mean()

    # Display summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Pass %", f"{pass_rate:.1f}%")
    with col2:
        st.metric("Fail %", f"{fail_rate:.1f}%")
    with col3:
        st.metric("# Pass", num_pass)
    with col4:
        st.metric("# Fail", num_fail)
    with col5:
        st.metric("Mean Score", f"{mean_score:.3f}")

    # Radio button for ground truth selection
    col1, col2 = st.columns([2, 3])
    with col1:
        true_label_key = f'true_label_prompt_{selected_model}'
        true_label = st.radio(
            "Ground Truth",
            ["Pass", "Fail"],
            index=None,  # No default selection
            key=true_label_key,
            horizontal=True,
            help="Select the correct answer for this metric"
        )

    # Two-column layout for test list and details
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("#### Per-Test Scores")

        # Track which test is selected for details
        if 'selected_test_idx' not in st.session_state:
            st.session_state.selected_test_idx = 0

        # Column headers
        col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1, 1])
        with col1:
            st.markdown("**Test**")
        with col2:
            st.markdown("**Score**")
        with col3:
            st.markdown("**Thresh**")
        with col4:
            st.markdown("**Agree**")
        with col5:
            st.markdown("**Action**")

        # Create table with view buttons
        for idx, row in df_model.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1, 1])

            with col1:
                st.markdown(f"**{row['test']}**")

            with col2:
                score_color = get_score_color(row['score'])
                st.markdown(
                    f"<div style='background: {score_color}; color: white; padding: 4px 8px; "
                    f"border-radius: 15px; text-align: center; font-weight: bold; font-size: 0.85em'>"
                    f"{row['score']:.2f}</div>",
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(f"<div style='text-align: center'>{row['threshold']:.1f}</div>", unsafe_allow_html=True)

            with col4:
                # Agreement icon based on radio selection
                model_pass = row['success']
                if true_label == "Undefined":
                    agreement_icon = "➖"  # Dash for undefined
                else:
                    expected_pass = (true_label == "Pass")
                    agrees = (model_pass == expected_pass)
                    agreement_icon = "✅" if agrees else "❌"
                st.markdown(f"<div style='text-align: center'>{agreement_icon}</div>", unsafe_allow_html=True)

            with col5:
                if st.button("View", key=f"view_btn_{idx}"):
                    st.session_state.selected_test_idx = idx

        selected_test_idx = st.session_state.selected_test_idx

    with col_right:
        st.markdown("#### Detailed Evaluation")

        if selected_test_idx is not None:
            selected_row = df_model.iloc[selected_test_idx]

            # Display selection info
            st.info(f"**Selection:** {selected_row['test']} • {selected_model}")

            # Score display
            col1, col2 = st.columns(2)
            with col1:
                score_color = get_score_color(selected_row['score'])
                st.markdown(
                    f"<div style='padding: 10px; background: {score_color}; color: white; "
                    f"border-radius: 8px; text-align: center; font-size: 1.1em; font-weight: bold'>"
                    f"{selected_row['score']:.3f} / {selected_row['threshold']:.1f}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col2:
                success_color = "#52c41a" if selected_row['success'] else "#ff4d4f"
                st.markdown(
                    f"<div style='padding: 10px; background: {success_color}; color: white; "
                    f"border-radius: 8px; text-align: center; font-size: 1.2em; font-weight: bold'>"
                    f"{'PASS' if selected_row['success'] else 'FAIL'}</div>",
                    unsafe_allow_html=True
                )

            # Reason section
            with st.expander("📝 Evaluation Reason", expanded=True):
                st.markdown(
                    f"<div style='background: white; padding: 15px; border-radius: 8px; "
                    f"line-height: 1.6; font-size: 0.95em'>{selected_row['reason']}</div>",
                    unsafe_allow_html=True
                )

            # Conversation section
            conversations = load_conversations()
            test_name = selected_row.get('test', '')
            if test_name in conversations:
                with st.expander("💬 Conversation", expanded=False):
                    turns = conversations[test_name]
                    for i, turn in enumerate(turns):
                        role = getattr(turn, 'role', 'unknown')
                        content = getattr(turn, 'content', '')
                        tools_called = turn.tools_called
                        tools_called = [ X.model_dump() for X in tools_called ]

                        # Role and turn number
                        if role == 'assistant':
                            role_color = "#3498db"  # Blue for assistant
                            role_icon = "🤖"
                        elif role == 'user':
                            role_color = "#27ae60"  # Green for user
                            role_icon = "👤"
                        else:
                            role_color = "#95a5a6"  # Gray for unknown
                            role_icon = "❓"

                        st.markdown(
                            f"<div style='margin-bottom: 15px; padding: 12px; "
                            f"background: #f8f9fa; border-left: 4px solid {role_color}; "
                            f"border-radius: 4px;'>"
                            f"<div style='font-weight: bold; color: {role_color}; margin-bottom: 8px;'>"
                            f"{role_icon} Turn {i+1}: {role.upper()}</div>",
                            unsafe_allow_html=True
                        )

                        # Content
                        if content:
                            st.markdown(
                                f"<div style='color: #2c3e50; line-height: 1.5;'>{content}</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"<div style='color: #95a5a6; font-style: italic;'>No content</div>",
                                unsafe_allow_html=True
                            )

                        # Tool calls
                        if tools_called:
                            st.markdown(
                                f"<div style='margin-top: 8px; padding: 8px; background: #e8f4fd; "
                                f"border-radius: 4px;'>"
                                f"<div style='font-weight: 600; color: #2c3e50; margin-bottom: 4px;'>"
                                f"🔧 Tool Calls:</div>",
                                unsafe_allow_html=True
                            )
                            st.code(json.dumps(tools_called, indent=2), language="json")
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

        # Verbose logs section
        if selected_row['verbose_logs']:
            with st.expander("🔍 Verbose Logs", expanded=False):
                st.code(selected_row['verbose_logs'], language="text")


def display_judge_performance(results: Dict, selected_test: Optional[str] = None):
    """Display Judge Performance section - same layout as Prompt Performance but for a specific test"""
    st.subheader("⚖️ Judge Performance — Per Test")

    test_results = results.get("test_results", [])

    # Get all test names
    test_names = [test["name"] for test in test_results]

    # Test selector
    col1, col2 = st.columns([3, 4])
    with col1:
        if selected_test and selected_test in test_names:
            default_idx = test_names.index(selected_test)
        else:
            default_idx = 0

        selected_test_name = st.selectbox(
            "Select Test Case",
            test_names,
            index=default_idx if test_names else 0,
            key="judge_test_selector"
        )

    if not selected_test_name:
        st.info("Select a test case to view performance across all evaluation models")
        return

    # Find the selected test data
    test_data = None
    for test in test_results:
        if test["name"] == selected_test_name:
            test_data = test
            break

    if not test_data:
        st.warning(f"No data found for test: {selected_test_name}")
        return

    # Extract metrics for all models
    model_data = []
    for metric in test_data.get("metrics_data", []):
        model_data.append({
            "model": metric.get("evaluation_model", "unknown"),
            "score": metric.get("score", 0.0),
            "threshold": metric.get("threshold", 1.0),
            "success": metric.get("success", False),
            "reason": metric.get("reason", ""),
            "verbose_logs": metric.get("verbose_logs", ""),
            "cost": metric.get("evaluation_cost", 0.0)
        })

    if not model_data:
        st.warning(f"No evaluation data available for {selected_test_name}")
        return

    # Calculate summary statistics
    df_model = pd.DataFrame(model_data)
    pass_rate = (df_model['success'].sum() / len(df_model)) * 100
    fail_rate = 100 - pass_rate
    num_pass = df_model['success'].sum()
    num_fail = len(df_model) - num_pass
    mean_score = df_model['score'].mean()

    # Display summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Pass %", f"{pass_rate:.1f}%")
    with col2:
        st.metric("Fail %", f"{fail_rate:.1f}%")
    with col3:
        st.metric("# Pass", num_pass)
    with col4:
        st.metric("# Fail", num_fail)
    with col5:
        st.metric("Mean Score", f"{mean_score:.3f}")

    # Radio button for ground truth selection
    col1, col2 = st.columns([2, 3])
    with col1:
        true_label_key = f'true_label_judge_{selected_test_name}'
        true_label = st.radio(
            "Ground Truth",
            ["Pass", "Fail", "Undefined"],
            index=0,  # Default to Pass
            key=true_label_key,
            horizontal=True,
            help="Select the correct answer for this test"
        )

    # Two-column layout for model list and details
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("#### Per-Model Scores")

        # Track which model is selected for details
        if 'selected_model_idx' not in st.session_state:
            st.session_state.selected_model_idx = 0

        # Sort by score descending
        df_model = df_model.sort_values('score', ascending=False).reset_index(drop=True)

        # Column headers
        col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1, 1])
        with col1:
            st.markdown("**Model**")
        with col2:
            st.markdown("**Score**")
        with col3:
            st.markdown("**Thresh**")
        with col4:
            st.markdown("**Agree**")
        with col5:
            st.markdown("**Action**")

        # Create table with view buttons
        for idx, row in df_model.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1, 1])

            with col1:
                st.markdown(f"**{row['model']}**")

            with col2:
                score_color = get_score_color(row['score'])
                st.markdown(
                    f"<div style='background: {score_color}; color: white; padding: 4px 8px; "
                    f"border-radius: 15px; text-align: center; font-weight: bold; font-size: 0.85em'>"
                    f"{row['score']:.2f}</div>",
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(f"<div style='text-align: center'>{row['threshold']:.1f}</div>", unsafe_allow_html=True)

            with col4:
                # Agreement icon based on radio selection
                model_pass = row['success']
                if true_label == "Undefined":
                    agreement_icon = "➖"  # Dash for undefined
                else:
                    expected_pass = (true_label == "Pass")
                    agrees = (model_pass == expected_pass)
                    agreement_icon = "✅" if agrees else "❌"
                st.markdown(f"<div style='text-align: center'>{agreement_icon}</div>", unsafe_allow_html=True)

            with col5:
                if st.button("View", key=f"judge_view_btn_{idx}"):
                    st.session_state.selected_model_idx = idx

        selected_model_idx = st.session_state.selected_model_idx

    with col_right:
        st.markdown("#### Detailed Evaluation")

        if selected_model_idx is not None and selected_model_idx < len(df_model):
            selected_row = df_model.iloc[selected_model_idx]

            # Display selection info
            st.info(f"**Selection:** {selected_test_name} • {selected_row['model']}")

            # Store test name in selected_row for conversation lookup
            selected_row['test'] = selected_test_name

            # Score display
            col1, col2 = st.columns(2)
            with col1:
                score_color = get_score_color(selected_row['score'])
                st.markdown(
                    f"<div style='padding: 10px; background: {score_color}; color: white; "
                    f"border-radius: 8px; text-align: center; font-size: 1.1em; font-weight: bold'>"
                    f"{selected_row['score']:.3f} / {selected_row['threshold']:.1f}"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col2:
                success_color = "#52c41a" if selected_row['success'] else "#ff4d4f"
                st.markdown(
                    f"<div style='padding: 10px; background: {success_color}; color: white; "
                    f"border-radius: 8px; text-align: center; font-size: 1.2em; font-weight: bold'>"
                    f"{'PASS' if selected_row['success'] else 'FAIL'}</div>",
                    unsafe_allow_html=True
                )

            # Reason section
            with st.expander("📝 Evaluation Reason", expanded=True):
                st.markdown(
                    f"<div style='background: white; padding: 15px; border-radius: 8px; "
                    f"line-height: 1.6; font-size: 0.95em'>{selected_row['reason']}</div>",
                    unsafe_allow_html=True
                )

            # Conversation section
            conversations = load_conversations()
            test_name = selected_row.get('test', '')
            if test_name in conversations:
                with st.expander("💬 Conversation", expanded=False):
                    turns = conversations[test_name]
                    for i, turn in enumerate(turns):
                        role = getattr(turn, 'role', 'unknown')
                        content = getattr(turn, 'content', '')
                        tools_called = turn.tools_called
                        tools_called = [ X.model_dump() for X in tools_called ]

                        # Role and turn number
                        if role == 'assistant':
                            role_color = "#3498db"  # Blue for assistant
                            role_icon = "🤖"
                        elif role == 'user':
                            role_color = "#27ae60"  # Green for user
                            role_icon = "👤"
                        else:
                            role_color = "#95a5a6"  # Gray for unknown
                            role_icon = "❓"

                        st.markdown(
                            f"<div style='margin-bottom: 15px; padding: 12px; "
                            f"background: #f8f9fa; border-left: 4px solid {role_color}; "
                            f"border-radius: 4px;'>"
                            f"<div style='font-weight: bold; color: {role_color}; margin-bottom: 8px;'>"
                            f"{role_icon} Turn {i+1}: {role.upper()}</div>",
                            unsafe_allow_html=True
                        )

                        # Content
                        if content:
                            st.markdown(
                                f"<div style='color: #2c3e50; line-height: 1.5;'>{content}</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"<div style='color: #95a5a6; font-style: italic;'>No content</div>",
                                unsafe_allow_html=True
                            )

                        # Tool calls
                        if tools_called:
                            st.markdown(
                                f"<div style='margin-top: 8px; padding: 8px; background: #e8f4fd; "
                                f"border-radius: 4px;'>"
                                f"<div style='font-weight: 600; color: #2c3e50; margin-bottom: 4px;'>"
                                f"🔧 Tool Calls:</div>",
                                unsafe_allow_html=True
                            )
                            st.code(json.dumps(tools_called, indent=2), language="json")
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

        # Verbose logs section
        if selected_row['verbose_logs']:
            with st.expander("🔍 Verbose Logs", expanded=False):
                st.code(selected_row['verbose_logs'], language="text")


def main():
    """Main dashboard function"""
    st.title("DeepEval Dashboard")

    # Dataset selector at the top
    col1, _ = st.columns([1, 9])
    with col1:
        dataset = st.selectbox(
            "Dataset",
            ["main", "strict"],
            index=0,
            help="Select which evaluation dataset to view"
        )

    # Load results based on selected dataset
    results = load_results(dataset)

    if not results.get("test_results"):
        st.error(f"No test results available for dataset '{dataset}'. Please run eval_cast_security.py first.")
        st.stop()

    # Display top metrics
    display_top_metrics(results)

    st.divider()

    # Test x Metric Heatmap
    display_heatmap(results, None)

    st.divider()

    # Prompt Performance
    display_prompt_performance(results, None)

    st.divider()

    # Judge Performance
    display_judge_performance(results, None)

    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9em'>
            Dashboard for Chatfield Security Evaluation Suite •
            <a href='https://github.com/yourusername/chatfield' target='_blank'>GitHub</a>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()