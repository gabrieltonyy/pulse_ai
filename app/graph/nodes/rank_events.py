"""
Rank Events Node - Ranks and scores events based on user preferences.
"""
from app.graph.state import PulseGraphState
from app.services.ranking_service import RankingService
from app.models.search import SearchIntent
from datetime import date


async def rank_events_node(state: PulseGraphState) -> PulseGraphState:
    """
    Rank events using multi-factor scoring algorithm.
    
    Scoring factors:
    - Relevance to search query
    - Date match
    - Affordability
    - Popularity
    - Venue context
    - Weather suitability
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with ranked_events
    """
    ranking_service = RankingService()
    
    # Reconstruct SearchIntent from state
    intent = SearchIntent(
        raw_query=state.get("raw_query", ""),
        city=state.get("city"),
        country=state.get("country"),
        category=state.get("category"),
        keyword=state.get("keyword"),
        date_from=_parse_date(state.get("date_from")),
        date_to=_parse_date(state.get("date_to")),
        budget_max=state.get("budget_max"),
        currency=state.get("currency", "USD"),
        preferences=state.get("preferences", [])
    )
    
    # Rank events
    ranked_events = ranking_service.rank_events(
        enriched_events=state.get("enriched_events", []),
        intent=intent
    )
    
    return {
        **state,
        "ranked_events": ranked_events,
        "workflow_trace": [
            *state.get("workflow_trace", []),
            {
                "node_name": "rank_events",
                "status": "completed",
                "events_ranked": len(ranked_events)
            }
        ]
    }


def _parse_date(date_str: str | None) -> date | None:
    """Parse date string to date object."""
    if not date_str:
        return None
    
    try:
        # Handle ISO format strings
        if isinstance(date_str, str):
            from datetime import datetime
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        return date_str
    except Exception:
        return None


# Made with Bob
