"""
Streamlit web interface for LLM Conversation Manager.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

from ..database.models import Conversation, Artifact, Tag
from ..database.connection import get_db_connection

# Page configuration
st.set_page_config(
    page_title="LLM Conversation Manager",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .conversation-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .platform-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
        color: white;
    }
    .chatgpt { background-color: #10a37f; }
    .claude { background-color: #d97706; }
    .typingmind { background-color: #7c3aed; }
    .markdown { background-color: #6b7280; }
</style>
""", unsafe_allow_html=True)

def get_platform_color(platform: str) -> str:
    """Get color for platform badge."""
    colors = {
        'chatgpt': '#10a37f',
        'claude': '#d97706', 
        'typingmind': '#7c3aed',
        'markdown': '#6b7280'
    }
    return colors.get(platform, '#6b7280')

def format_timestamp(timestamp) -> str:
    """Format timestamp for display."""
    if timestamp is None:
        return "Unknown"
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return timestamp
    return timestamp.strftime("%Y-%m-%d %H:%M")

def display_conversation_card(conversation: Conversation):
    """Display a conversation card."""
    platform_color = get_platform_color(conversation.platform)
    
    with st.container():
        st.markdown(f"""
        <div class="conversation-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <h3 style="margin: 0; color: #1f77b4;">{conversation.title}</h3>
                <span class="platform-badge" style="background-color: {platform_color};">
                    {conversation.platform.upper()}
                </span>
            </div>
            <p style="margin: 0.5rem 0; color: #666;">{conversation.preview}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.875rem; color: #888;">
                <span>📅 {format_timestamp(conversation.create_time)}</span>
                <span>💬 {conversation.num_messages} messages</span>
                <span>🤖 {conversation.model_name or 'Unknown'}</span>
                {f'<span>💰 ${conversation.cost:.4f}</span>' if conversation.cost > 0 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application."""
    st.markdown('<h1 class="main-header">💬 LLM Conversation Manager</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Search
        search_query = st.text_input("Search conversations", placeholder="Enter keywords...")
        
        # Platform filter
        platforms = st.multiselect(
            "Platform",
            ["chatgpt", "claude", "typingmind", "markdown"],
            default=["chatgpt", "claude", "typingmind", "markdown"]
        )
        
        # Model filter
        model_filter = st.selectbox(
            "Model",
            ["All"] + ["GPT-4", "GPT-3.5", "Claude 3 Opus", "Claude 3 Sonnet", "Claude 3 Haiku"]
        )
        
        # Date range
        st.subheader("📅 Date Range")
        date_range = st.date_input(
            "Select date range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        # Cost filter
        st.subheader("💰 Cost Filter")
        min_cost = st.number_input("Minimum cost", min_value=0.0, value=0.0, step=0.001)
        max_cost = st.number_input("Maximum cost", min_value=0.0, value=100.0, step=0.001)
        
        # Message count filter
        st.subheader("💬 Message Count")
        min_messages = st.number_input("Minimum messages", min_value=0, value=0)
        max_messages = st.number_input("Maximum messages", min_value=0, value=1000)
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💬 Conversations", "🔍 Search", "📈 Analytics"])
    
    with tab1:
        st.header("📊 Dashboard")
        
        # Get statistics
        try:
            stats = Conversation.get_stats()
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_conversations = sum(platform_stats['total_conversations'] for platform_stats in stats.values())
            total_messages = sum(platform_stats['total_messages'] for platform_stats in stats.values())
            total_cost = sum(platform_stats['total_cost'] for platform_stats in stats.values())
            unique_models = sum(platform_stats['unique_models'] for platform_stats in stats.values())
            
            with col1:
                st.metric("Total Conversations", f"{total_conversations:,}")
            with col2:
                st.metric("Total Messages", f"{total_messages:,}")
            with col3:
                st.metric("Total Cost", f"${total_cost:.2f}")
            with col4:
                st.metric("Unique Models", unique_models)
            
            # Platform breakdown
            st.subheader("Platform Breakdown")
            
            platform_data = []
            for platform, platform_stats in stats.items():
                platform_data.append({
                    'Platform': platform.upper(),
                    'Conversations': platform_stats['total_conversations'],
                    'Messages': platform_stats['total_messages'],
                    'Cost': platform_stats['total_cost'],
                    'Avg Cost': platform_stats['avg_cost']
                })
            
            if platform_data:
                df = pd.DataFrame(platform_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(df, values='Conversations', names='Platform', title='Conversations by Platform')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(df, x='Platform', y='Cost', title='Cost by Platform')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Data table
                st.subheader("Platform Statistics")
                st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading statistics: {e}")
    
    with tab2:
        st.header("💬 Conversations")
        
        # Get conversations
        try:
            conversations = Conversation.search(
                query=search_query if search_query else "",
                platform=platforms[0] if len(platforms) == 1 else None,
                limit=50
            )
            
            if not conversations:
                st.info("No conversations found matching your criteria.")
            else:
                st.write(f"Found {len(conversations)} conversations")
                
                # Display conversations
                for conversation in conversations:
                    display_conversation_card(conversation)
                    
                    # Show conversation details in expander
                    with st.expander(f"View details for: {conversation.title}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Basic Info**")
                            st.write(f"**ID:** {conversation.id}")
                            st.write(f"**Source:** {conversation.source}")
                            st.write(f"**Platform:** {conversation.platform}")
                            st.write(f"**Model:** {conversation.model_name}")
                            st.write(f"**Messages:** {conversation.num_messages}")
                            st.write(f"**Cost:** ${conversation.cost:.4f}")
                            st.write(f"**Created:** {format_timestamp(conversation.create_time)}")
                            st.write(f"**Modified:** {format_timestamp(conversation.datemodified)}")
                        
                        with col2:
                            st.write("**Content Preview**")
                            st.text_area("Preview", conversation.preview, height=200, disabled=True)
                        
                        # Show artifacts if any
                        artifacts = conversation.get_artifacts()
                        if artifacts:
                            st.write("**Artifacts**")
                            for artifact in artifacts:
                                st.write(f"- **{artifact.title}** ({artifact.artifact_type})")
                                if artifact.content:
                                    st.code(artifact.content[:500] + "..." if len(artifact.content) > 500 else artifact.content)
        
        except Exception as e:
            st.error(f"Error loading conversations: {e}")
    
    with tab3:
        st.header("🔍 Advanced Search")
        
        # Search form
        with st.form("search_form"):
            search_query = st.text_input("Search Query", placeholder="Enter search terms...")
            search_platform = st.selectbox("Platform", ["All", "chatgpt", "claude", "typingmind", "markdown"])
            search_model = st.selectbox("Model", ["All", "GPT-4", "GPT-3.5", "Claude 3 Opus", "Claude 3 Sonnet"])
            limit = st.slider("Results Limit", 10, 100, 20)
            
            submitted = st.form_submit_button("Search")
            
            if submitted and search_query:
                try:
                    conversations = Conversation.search(
                        query=search_query,
                        platform=search_platform if search_platform != "All" else None,
                        model=search_model if search_model != "All" else None,
                        limit=limit
                    )
                    
                    if conversations:
                        st.write(f"Found {len(conversations)} conversations")
                        
                        for conversation in conversations:
                            display_conversation_card(conversation)
                    else:
                        st.info("No conversations found matching your search criteria.")
                
                except Exception as e:
                    st.error(f"Search error: {e}")
    
    with tab4:
        st.header("📈 Analytics")
        
        try:
            # Get recent conversations for analysis
            recent_conversations = Conversation.search(limit=1000)
            
            if recent_conversations:
                # Convert to DataFrame
                data = []
                for conv in recent_conversations:
                    data.append({
                        'title': conv.title,
                        'platform': conv.platform,
                        'model_name': conv.model_name,
                        'num_messages': conv.num_messages,
                        'cost': conv.cost,
                        'create_time': conv.create_time,
                        'datemodified': conv.datemodified
                    })
                
                df = pd.DataFrame(data)
                
                # Time series analysis
                st.subheader("Conversations Over Time")
                df['date'] = pd.to_datetime(df['create_time']).dt.date
                daily_counts = df.groupby(['date', 'platform']).size().reset_index(name='count')
                
                fig = px.line(daily_counts, x='date', y='count', color='platform', 
                            title='Daily Conversation Count by Platform')
                st.plotly_chart(fig, use_container_width=True)
                
                # Cost analysis
                st.subheader("Cost Analysis")
                cost_data = df[df['cost'] > 0]
                if not cost_data.empty:
                    fig = px.box(cost_data, x='platform', y='cost', title='Cost Distribution by Platform')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Message count analysis
                st.subheader("Message Count Analysis")
                fig = px.histogram(df, x='num_messages', color='platform', 
                                 title='Message Count Distribution by Platform')
                st.plotly_chart(fig, use_container_width=True)
                
                # Model usage
                st.subheader("Model Usage")
                model_counts = df['model_name'].value_counts()
                fig = px.pie(values=model_counts.values, names=model_counts.index, 
                           title='Model Usage Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading analytics: {e}")

if __name__ == "__main__":
    main()
