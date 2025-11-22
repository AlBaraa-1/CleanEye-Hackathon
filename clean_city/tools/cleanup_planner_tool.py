"""
Cleanup Planning MCP Tool

Analyzes detected trash and generates cleanup action plans.
"""

from typing import Any, Optional
from trash_model import Detection
import llm_client


def plan_cleanup(
    detections: list[Detection],
    location: Optional[str] = None,
    notes: Optional[str] = None,
    use_llm: bool = True  # Default to True for intelligent AI planning
):
    """
    Generate a cleanup plan based on detected trash.
    
    Args:
        detections: List of trash detections from detection tool
        location: Optional location description
        notes: Optional additional context
        use_llm: Whether to use Gemini AI for intelligent planning (default: True)
    
    Returns:
        Dict containing:
            - severity: "low" | "medium" | "high"
            - recommended_volunteers: int
            - estimated_time_minutes: int
            - equipment_needed: list[str]
            - urgency_days: int (recommended action timeframe)
            - environmental_impact: str
            - action_summary: str (AI-generated when use_llm=True)
    """
    if not detections:
        return {
            "severity": "low",
            "recommended_volunteers": 0,
            "estimated_time_minutes": 0,
            "equipment_needed": [],
            "urgency_days": 0,
            "environmental_impact": "No trash detected - area appears clean.",
            "action_summary": "No cleanup action needed at this time."
        }
    
    # Rule-based analysis
    count = len(detections)
    avg_confidence = sum(d["score"] for d in detections) / count
    categories = set(d["label"] for d in detections)
    
    # Calculate severity
    if count >= 15 or len(categories) >= 6:
        severity = "high"
        urgency_days = 1
        volunteers = 4 + (count // 10)
        time_estimate = 90 + (count * 3)
    elif count >= 7 or len(categories) >= 4:
        severity = "medium"
        urgency_days = 3
        volunteers = 2 + (count // 8)
        time_estimate = 45 + (count * 2)
    else:
        severity = "low"
        urgency_days = 7
        volunteers = 1 + (count // 5)
        time_estimate = 20 + (count * 2)
    
    # Equipment recommendations
    equipment = ["Heavy-duty trash bags", "Gloves", "Grabber tools"]
    
    if "glass_bottle" in categories:
        equipment.append("Safety goggles")
        equipment.append("Puncture-resistant bags")
    
    if count > 10:
        equipment.append("Wheeled collection bin")
    
    # Environmental impact assessment
    impact_descriptions = {
        "high": "Significant environmental concern. Risk of wildlife harm, water contamination, and community health issues. Immediate action recommended.",
        "medium": "Moderate environmental impact. Potential for wildlife interaction and visual pollution. Timely cleanup will prevent escalation.",
        "low": "Minor environmental impact. Early intervention will maintain area cleanliness and prevent accumulation."
    }
    
    plan = {
        "severity": severity,
        "recommended_volunteers": volunteers,
        "estimated_time_minutes": time_estimate,
        "equipment_needed": equipment,
        "urgency_days": urgency_days,
        "environmental_impact": impact_descriptions[severity],
        "action_summary": _generate_action_summary(
            severity, volunteers, time_estimate, count, categories
        )
    }
    
    # Optionally enhance with LLM
    if use_llm:
        plan["action_summary"] = _enhance_with_llm(plan, detections, location, notes)
    
    return plan


def _generate_action_summary(
    severity: str,
    volunteers: int,
    time_minutes: int,
    count: int,
    categories: set[str]
) -> str:
    """Generate human-readable action summary."""
    category_list = ", ".join(sorted(categories)[:3])
    if len(categories) > 3:
        category_list += f" and {len(categories) - 3} other types"
    
    summary = f"""**Cleanup Plan - {severity.upper()} Priority**

Detected {count} trash items including {category_list}.

**Recommended Resources:**
- {volunteers} volunteer(s)
- Approximately {time_minutes} minutes
- Standard cleanup equipment

**Next Steps:**
1. Gather volunteers and equipment
2. Coordinate cleanup date/time
3. Execute cleanup operation
4. Dispose of collected waste properly
5. Document completion for tracking
"""
    return summary


def _enhance_with_llm(
    plan,
    detections: list[Detection],
    location: Optional[str],
    notes: Optional[str]
) -> str:
    """Use Gemini AI to create intelligent, context-aware cleanup plans."""
    import os
    
    # Try Gemini first for intelligent planning
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Build detailed context for Gemini
            detection_details = []
            category_counts = {}
            for d in detections:
                label = d.get("label", "unknown")
                category_counts[label] = category_counts.get(label, 0) + 1
            
            for label, count in sorted(category_counts.items(), key=lambda x: -x[1]):
                detection_details.append(f"- {label}: {count} item(s)")
            
            context = f"""**Trash Detection Analysis:**
{chr(10).join(detection_details)}

**Total Items:** {len(detections)}
**Categories:** {len(category_counts)} types
**Severity:** {plan['severity']}
**Location:** {location or 'Not specified'}
**Notes:** {notes or 'None'}

**Baseline Estimates:**
- Volunteers needed: {plan['recommended_volunteers']}
- Time estimate: {plan['estimated_time_minutes']} minutes
- Equipment: {', '.join(plan['equipment'])}
"""

            prompt = f"""You are an expert environmental cleanup coordinator with years of field experience. 

Analyze this trash situation and create an intelligent, actionable cleanup plan:

{context}

Generate a comprehensive cleanup plan that includes:

1. **Situation Assessment** - What's the severity and why? What environmental risks exist?

2. **Resource Optimization** - Are the baseline estimates right? Should we adjust volunteers, time, or equipment based on:
   - Specific trash types detected (sharp objects need safety gear, electronics need special disposal, etc.)
   - Quantity and distribution
   - Location characteristics
   - Potential hazards

3. **Specific Action Steps** - Not generic steps, but SPECIFIC to this situation:
   - What should be prioritized first?
   - What special handling is needed?
   - What safety precautions?
   - What disposal methods?

4. **Environmental Impact** - Why does THIS specific cleanup matter? What habitat/ecosystem benefits?

5. **Smart Recommendations** - Any location-specific tips or efficiency strategies?

Be SPECIFIC and PRACTICAL. This is a real cleanup, not a template. If you see hazardous items, mention them. If the time estimate seems wrong, adjust it. Make it actionable."""

            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
                
        except Exception as e:
            print(f"Gemini AI planning failed: {e}")
    
    # Fallback to basic LLM client
    detection_summary = f"{len(detections)} items detected: "
    detection_summary += ", ".join(set(d["label"] for d in detections))
    
    context_parts = [
        f"Trash detection summary: {detection_summary}",
        f"Severity assessment: {plan['severity']}",
        f"Recommended volunteers: {plan['recommended_volunteers']}",
        f"Estimated time: {plan['estimated_time_minutes']} minutes"
    ]
    
    if location:
        context_parts.append(f"Location: {location}")
    if notes:
        context_parts.append(f"Additional context: {notes}")
    
    prompt = f"""Based on this trash detection analysis, create a clear, actionable cleanup plan summary:

{chr(10).join(context_parts)}

Write a brief, practical summary that:
1. States the situation clearly
2. Recommends specific actions
3. Estimates resources needed
4. Explains why this matters for the environment

Keep it concise (3-4 sentences)."""
    
    try:
        enhanced = llm_client.generate_text(
            prompt,
            system_prompt="You are a helpful environmental cleanup coordinator. Be practical and encouraging.",
            max_tokens=300,
            temperature=0.7
        )
        return enhanced
    except Exception as e:
        print(f"LLM enhancement failed: {e}")
        return plan["action_summary"]
