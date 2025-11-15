"""
KPI Generator Tool - Generate business KPIs from data
"""
import logging
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import parse_json_safe, safe_divide

logger = logging.getLogger(__name__)


def generate_kpis(data: str, metrics: List[str] = None) -> Dict[str, Any]:
    """
    Generate KPI report from business data.
    
    Args:
        data: JSON string containing business data
        metrics: List of metrics to calculate (revenue, growth, efficiency, etc.)
        
    Returns:
        Dictionary with calculated KPIs and insights
    """
    try:
        import json
        
        # Parse input data
        try:
            business_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
        
        if metrics is None:
            metrics = ["revenue", "growth", "efficiency"]
        
        kpis = {}
        trends = []
        
        # Calculate different KPIs based on requested metrics
        for metric in metrics:
            if metric == "revenue":
                revenue_kpis = _calculate_revenue_kpis(business_data)
                kpis.update(revenue_kpis)
                
            elif metric == "growth":
                growth_kpis = _calculate_growth_kpis(business_data)
                kpis.update(growth_kpis)
                
            elif metric == "efficiency":
                efficiency_kpis = _calculate_efficiency_kpis(business_data)
                kpis.update(efficiency_kpis)
                
            elif metric == "customer":
                customer_kpis = _calculate_customer_kpis(business_data)
                kpis.update(customer_kpis)
                
            elif metric == "operational":
                operational_kpis = _calculate_operational_kpis(business_data)
                kpis.update(operational_kpis)
        
        # Generate trends
        trends = _identify_trends(kpis, business_data)
        
        # Generate executive summary
        summary = _generate_summary(kpis, trends)
        
        return {
            "kpis": kpis,
            "summary": summary,
            "trends": trends,
            "metrics_analyzed": metrics,
            "data_points": len(business_data) if isinstance(business_data, list) else len(business_data.keys())
        }
        
    except Exception as e:
        logger.error(f"Error generating KPIs: {e}")
        raise


def _calculate_revenue_kpis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate revenue-related KPIs"""
    kpis = {}
    
    try:
        # Total Revenue
        if "revenue" in data:
            if isinstance(data["revenue"], list):
                kpis["total_revenue"] = sum(data["revenue"])
                kpis["average_revenue"] = sum(data["revenue"]) / len(data["revenue"])
                kpis["min_revenue"] = min(data["revenue"])
                kpis["max_revenue"] = max(data["revenue"])
            else:
                kpis["total_revenue"] = data["revenue"]
        
        # Revenue per customer
        if "revenue" in data and "customers" in data:
            revenue = data["revenue"] if not isinstance(data["revenue"], list) else sum(data["revenue"])
            customers = data["customers"] if not isinstance(data["customers"], list) else sum(data["customers"])
            kpis["revenue_per_customer"] = safe_divide(revenue, customers)
        
        # Profit margin
        if "revenue" in data and "costs" in data:
            revenue = data["revenue"] if not isinstance(data["revenue"], list) else sum(data["revenue"])
            costs = data["costs"] if not isinstance(data["costs"], list) else sum(data["costs"])
            profit = revenue - costs
            kpis["profit"] = profit
            kpis["profit_margin_percent"] = safe_divide(profit * 100, revenue)
        
    except Exception as e:
        logger.warning(f"Error calculating revenue KPIs: {e}")
    
    return kpis


def _calculate_growth_kpis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate growth-related KPIs"""
    kpis = {}
    
    try:
        # Year-over-year growth
        if "current_revenue" in data and "previous_revenue" in data:
            growth = data["current_revenue"] - data["previous_revenue"]
            growth_rate = safe_divide(growth * 100, data["previous_revenue"])
            kpis["revenue_growth"] = growth
            kpis["revenue_growth_rate_percent"] = growth_rate
        
        # Customer growth
        if "current_customers" in data and "previous_customers" in data:
            customer_growth = data["current_customers"] - data["previous_customers"]
            customer_growth_rate = safe_divide(customer_growth * 100, data["previous_customers"])
            kpis["customer_growth"] = customer_growth
            kpis["customer_growth_rate_percent"] = customer_growth_rate
        
        # Monthly growth rate (if time series data provided)
        if "monthly_revenue" in data and isinstance(data["monthly_revenue"], list):
            revenues = data["monthly_revenue"]
            if len(revenues) >= 2:
                recent_growth = safe_divide((revenues[-1] - revenues[-2]) * 100, revenues[-2])
                kpis["recent_monthly_growth_percent"] = recent_growth
        
    except Exception as e:
        logger.warning(f"Error calculating growth KPIs: {e}")
    
    return kpis


def _calculate_efficiency_kpis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate efficiency-related KPIs"""
    kpis = {}
    
    try:
        # Cost per acquisition
        if "marketing_costs" in data and "new_customers" in data:
            kpis["cost_per_acquisition"] = safe_divide(data["marketing_costs"], data["new_customers"])
        
        # Operational efficiency
        if "revenue" in data and "operational_costs" in data:
            revenue = data["revenue"] if not isinstance(data["revenue"], list) else sum(data["revenue"])
            kpis["operational_efficiency_ratio"] = safe_divide(revenue, data["operational_costs"])
        
        # Employee productivity
        if "revenue" in data and "employees" in data:
            revenue = data["revenue"] if not isinstance(data["revenue"], list) else sum(data["revenue"])
            kpis["revenue_per_employee"] = safe_divide(revenue, data["employees"])
        
        # ROI
        if "revenue" in data and "investment" in data:
            revenue = data["revenue"] if not isinstance(data["revenue"], list) else sum(data["revenue"])
            roi = safe_divide((revenue - data["investment"]) * 100, data["investment"])
            kpis["roi_percent"] = roi
        
    except Exception as e:
        logger.warning(f"Error calculating efficiency KPIs: {e}")
    
    return kpis


def _calculate_customer_kpis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate customer-related KPIs"""
    kpis = {}
    
    try:
        # Customer lifetime value
        if "average_purchase_value" in data and "purchase_frequency" in data and "customer_lifespan" in data:
            clv = data["average_purchase_value"] * data["purchase_frequency"] * data["customer_lifespan"]
            kpis["customer_lifetime_value"] = clv
        
        # Churn rate
        if "churned_customers" in data and "total_customers" in data:
            kpis["churn_rate_percent"] = safe_divide(data["churned_customers"] * 100, data["total_customers"])
        
        # Retention rate
        if "retained_customers" in data and "total_customers" in data:
            kpis["retention_rate_percent"] = safe_divide(data["retained_customers"] * 100, data["total_customers"])
        
        # Net Promoter Score (if provided)
        if "nps_score" in data:
            kpis["net_promoter_score"] = data["nps_score"]
        
    except Exception as e:
        logger.warning(f"Error calculating customer KPIs: {e}")
    
    return kpis


def _calculate_operational_kpis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate operational KPIs"""
    kpis = {}
    
    try:
        # Inventory turnover
        if "cost_of_goods_sold" in data and "average_inventory" in data:
            kpis["inventory_turnover"] = safe_divide(data["cost_of_goods_sold"], data["average_inventory"])
        
        # Order fulfillment rate
        if "orders_fulfilled" in data and "total_orders" in data:
            kpis["fulfillment_rate_percent"] = safe_divide(data["orders_fulfilled"] * 100, data["total_orders"])
        
        # Average response time
        if "total_response_time" in data and "ticket_count" in data:
            kpis["average_response_time"] = safe_divide(data["total_response_time"], data["ticket_count"])
        
    except Exception as e:
        logger.warning(f"Error calculating operational KPIs: {e}")
    
    return kpis


def _identify_trends(kpis: Dict[str, Any], data: Dict[str, Any]) -> List[str]:
    """Identify key trends from KPIs"""
    trends = []
    
    try:
        # Check growth trends
        if "revenue_growth_rate_percent" in kpis:
            rate = kpis["revenue_growth_rate_percent"]
            if rate > 20:
                trends.append(f"Strong revenue growth of {rate:.1f}%")
            elif rate > 0:
                trends.append(f"Positive revenue growth of {rate:.1f}%")
            else:
                trends.append(f"Revenue decline of {abs(rate):.1f}%")
        
        # Check profitability
        if "profit_margin_percent" in kpis:
            margin = kpis["profit_margin_percent"]
            if margin > 20:
                trends.append(f"Healthy profit margin at {margin:.1f}%")
            elif margin > 0:
                trends.append(f"Modest profit margin at {margin:.1f}%")
            else:
                trends.append(f"Operating at a loss with {abs(margin):.1f}% negative margin")
        
        # Check efficiency
        if "roi_percent" in kpis:
            roi = kpis["roi_percent"]
            if roi > 100:
                trends.append(f"Excellent ROI of {roi:.1f}%")
            elif roi > 0:
                trends.append(f"Positive ROI of {roi:.1f}%")
        
        # Check customer metrics
        if "churn_rate_percent" in kpis:
            churn = kpis["churn_rate_percent"]
            if churn > 10:
                trends.append(f"High customer churn rate of {churn:.1f}%")
            else:
                trends.append(f"Healthy churn rate of {churn:.1f}%")
        
    except Exception as e:
        logger.warning(f"Error identifying trends: {e}")
    
    return trends if trends else ["Insufficient data for trend analysis"]


def _generate_summary(kpis: Dict[str, Any], trends: List[str]) -> str:
    """Generate executive summary"""
    summary_parts = []
    
    summary_parts.append("Executive KPI Summary:")
    summary_parts.append(f"- Analyzed {len(kpis)} key performance indicators")
    
    if trends:
        summary_parts.append("- Key insights:")
        for trend in trends[:3]:  # Top 3 trends
            summary_parts.append(f"  • {trend}")
    
    return "\n".join(summary_parts)
