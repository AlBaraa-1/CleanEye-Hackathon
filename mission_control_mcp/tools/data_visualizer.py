"""
Data Visualizer Tool - Create charts from data
"""
import logging
from typing import Dict, Any
import io
import base64
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import parse_json_safe

logger = logging.getLogger(__name__)


def visualize_data(
    data: str, 
    chart_type: str = "bar", 
    x_column: str = None, 
    y_column: str = None,
    title: str = "Data Visualization"
) -> Dict[str, Any]:
    """
    Create a chart visualization from data.
    
    Args:
        data: JSON or CSV string data
        chart_type: Type of chart - 'bar', 'line', 'pie', 'scatter'
        x_column: X-axis column name
        y_column: Y-axis column name
        title: Chart title
        
    Returns:
        Dictionary with base64 encoded image and metadata
    """
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import json
        
        # Parse data
        try:
            # Try JSON first
            data_dict = json.loads(data)
            df = pd.DataFrame(data_dict)
        except json.JSONDecodeError:
            # Try CSV
            from io import StringIO
            df = pd.read_csv(StringIO(data))
        
        if df.empty:
            raise ValueError("Data is empty")
        
        # Auto-select columns if not specified
        if x_column is None and len(df.columns) > 0:
            x_column = df.columns[0]
        if y_column is None and len(df.columns) > 1:
            y_column = df.columns[1]
        elif y_column is None:
            y_column = df.columns[0]
        
        # Validate columns exist
        if x_column not in df.columns:
            raise ValueError(f"Column '{x_column}' not found in data")
        if y_column not in df.columns:
            raise ValueError(f"Column '{y_column}' not found in data")
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Generate chart based on type
        if chart_type == "bar":
            plt.bar(df[x_column], df[y_column])
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            
        elif chart_type == "line":
            plt.plot(df[x_column], df[y_column], marker='o')
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.grid(True, alpha=0.3)
            
        elif chart_type == "pie":
            plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')
            
        elif chart_type == "scatter":
            plt.scatter(df[x_column], df[y_column], alpha=0.6)
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.grid(True, alpha=0.3)
            
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
        
        plt.title(title)
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return {
            "image_base64": image_base64,
            "dimensions": {"width": 1000, "height": 600},
            "chart_type": chart_type,
            "title": title,
            "columns_used": {"x": x_column, "y": y_column}
        }
        
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        raise


def create_multi_chart(data: str, chart_configs: list) -> Dict[str, Any]:
    """
    Create multiple charts from the same dataset.
    
    Args:
        data: JSON or CSV string data
        chart_configs: List of chart configuration dictionaries
        
    Returns:
        Dictionary with multiple chart images
    """
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import json
        
        # Parse data once
        try:
            data_dict = json.loads(data)
            df = pd.DataFrame(data_dict)
        except json.JSONDecodeError:
            from io import StringIO
            df = pd.read_csv(StringIO(data))
        
        charts = []
        for idx, config in enumerate(chart_configs):
            try:
                result = visualize_data(
                    data,
                    chart_type=config.get("chart_type", "bar"),
                    x_column=config.get("x_column"),
                    y_column=config.get("y_column"),
                    title=config.get("title", f"Chart {idx+1}")
                )
                charts.append(result)
            except Exception as e:
                logger.error(f"Error creating chart {idx+1}: {e}")
                charts.append({"error": str(e)})
        
        return {
            "total_charts": len(charts),
            "charts": charts
        }
        
    except Exception as e:
        logger.error(f"Error creating multi-chart: {e}")
        raise


def generate_statistics_chart(data: str) -> Dict[str, Any]:
    """
    Generate a statistical summary chart from numeric data.
    
    Args:
        data: JSON or CSV string with numeric data
        
    Returns:
        Dictionary with statistics chart
    """
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import json
        
        # Parse data
        try:
            data_dict = json.loads(data)
            df = pd.DataFrame(data_dict)
        except json.JSONDecodeError:
            from io import StringIO
            df = pd.read_csv(StringIO(data))
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns found in data")
        
        # Create statistics summary
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Box plot
        df[numeric_cols].boxplot(ax=axes[0])
        axes[0].set_title("Distribution (Box Plot)")
        axes[0].set_ylabel("Values")
        
        # Histogram
        df[numeric_cols].hist(ax=axes[1], bins=20, alpha=0.7)
        axes[1].set_title("Distribution (Histogram)")
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        # Calculate statistics
        stats = df[numeric_cols].describe().to_dict()
        
        return {
            "image_base64": image_base64,
            "statistics": stats,
            "numeric_columns": list(numeric_cols)
        }
        
    except Exception as e:
        logger.error(f"Error generating statistics chart: {e}")
        raise
