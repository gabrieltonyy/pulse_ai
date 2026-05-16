"""
Unit tests for RankingService.
Tests the deterministic scoring algorithm and label assignment.
"""

import pytest
from datetime import date, datetime, timedelta
from app.services.ranking_service import RankingService
from app.models.search import SearchIntent


class TestRankingService:
    """Test suite for RankingService."""
    
    @pytest.fixture
    def ranking_service(self):
        """Create a RankingService instance."""
        return RankingService()
    
    @pytest.fixture
    def sample_intent(self):
        """Create a sample SearchIntent."""
        today = date.today()
        return SearchIntent(
            raw_query="electronic music in Berlin this weekend under $100",
            city="Berlin",
            country="Germany",
            category="music",
            keyword="electronic",
            date_from=today + timedelta(days=5),
            date_to=today + timedelta(days=7),
            budget_max=100.0,
            currency="USD",
            preferences=["electronic", "music", "nightlife"]
        )
    
    @pytest.fixture
    def sample_event(self):
        """Create a sample event dictionary."""
        today = date.today()
        return {
            "id": "event-1",
            "title": "Electronic Music Festival",
            "description": "Amazing electronic music event with top DJs",
            "category": "Music",
            "venue_name": "Berlin Arena",
            "venue_city": "Berlin",
            "venue_country": "Germany",
            "latitude": 52.5200,
            "longitude": 13.4050,
            "start_datetime": (datetime.now() + timedelta(days=6)).isoformat(),
            "price_min": 50.0,
            "price_max": 80.0,
            "currency": "USD",
            "image_url": "https://example.com/image.jpg",
            "provider": "ticketmaster"
        }
    
    def test_relevance_score_exact_category_match(self, ranking_service, sample_event, sample_intent):
        """Test that exact category match gives high relevance score."""
        score = ranking_service._calculate_relevance_score(sample_event, sample_intent)
        assert score >= 50, "Exact category match should give at least 50 points"
    
    def test_relevance_score_keyword_match(self, ranking_service, sample_intent):
        """Test that keyword in title gives high relevance score."""
        event = {
            "id": "event-1",
            "title": "Electronic Dance Party",
            "description": "Great party",
            "category": "Music"
        }
        score = ranking_service._calculate_relevance_score(event, sample_intent)
        assert score >= 80, "Keyword in title should give high score"
    
    def test_date_match_score_inside_range(self, ranking_service, sample_intent):
        """Test that event inside date range gets perfect score."""
        today = date.today()
        event = {
            "id": "event-1",
            "start_datetime": (datetime.now() + timedelta(days=6)).isoformat()
        }
        score = ranking_service._calculate_date_match_score(event, sample_intent)
        assert score == 100.0, "Event inside date range should get 100"
    
    def test_date_match_score_outside_range(self, ranking_service, sample_intent):
        """Test that event outside date range gets lower score."""
        event = {
            "id": "event-1",
            "start_datetime": (datetime.now() + timedelta(days=30)).isoformat()
        }
        score = ranking_service._calculate_date_match_score(event, sample_intent)
        assert score < 100.0, "Event outside date range should get less than 100"
    
    def test_date_match_score_no_date(self, ranking_service, sample_intent):
        """Test that event without date gets low score."""
        event = {"id": "event-1"}
        score = ranking_service._calculate_date_match_score(event, sample_intent)
        assert score == 10.0, "Event without date should get 10"
    
    def test_affordability_score_free_event(self, ranking_service, sample_intent):
        """Test that free event gets perfect affordability score."""
        event = {
            "id": "event-1",
            "price_min": 0.0,
            "price_max": 0.0
        }
        score = ranking_service._calculate_affordability_score(event, sample_intent)
        assert score == 100.0, "Free event should get 100"
    
    def test_affordability_score_within_budget(self, ranking_service, sample_intent):
        """Test that event within budget gets high score."""
        event = {
            "id": "event-1",
            "price_min": 50.0,
            "price_max": 80.0
        }
        score = ranking_service._calculate_affordability_score(event, sample_intent)
        assert score == 100.0, "Event within budget should get 100"
    
    def test_affordability_score_above_budget(self, ranking_service, sample_intent):
        """Test that event above budget gets lower score."""
        event = {
            "id": "event-1",
            "price_min": 150.0,
            "price_max": 200.0
        }
        score = ranking_service._calculate_affordability_score(event, sample_intent)
        assert score < 50.0, "Event above budget should get low score"
    
    def test_affordability_score_no_price(self, ranking_service, sample_intent):
        """Test that event without price gets default score."""
        event = {"id": "event-1"}
        score = ranking_service._calculate_affordability_score(event, sample_intent)
        assert score == 60.0, "Event without price should get 60"
    
    def test_popularity_score_with_metadata(self, ranking_service):
        """Test that event with rich metadata gets high popularity score."""
        event = {
            "id": "event-1",
            "image_url": "https://example.com/image.jpg",
            "description": "Great event",
            "venue_name": "Berlin Arena"
        }
        score = ranking_service._calculate_popularity_score(event)
        assert score == 100.0, "Event with all metadata should get 100"
    
    def test_popularity_score_minimal_metadata(self, ranking_service):
        """Test that event with minimal metadata gets base score."""
        event = {"id": "event-1"}
        score = ranking_service._calculate_popularity_score(event)
        assert score == 50.0, "Event with no metadata should get base score of 50"
    
    def test_context_score_many_places(self, ranking_service):
        """Test that venue with many nearby places gets high score."""
        venue_context = {
            "nearby_places": [
                {"name": f"Place {i}", "category": "restaurant", "distance_meters": 100}
                for i in range(6)
            ]
        }
        score = ranking_service._calculate_context_score(venue_context)
        assert score == 90.0, "Venue with 5+ nearby places should get 90"
    
    def test_context_score_no_context(self, ranking_service):
        """Test that event without venue context gets default score."""
        score = ranking_service._calculate_context_score(None)
        assert score == 30.0, "Event without venue context should get 30"
    
    def test_weather_score_good_weather(self, ranking_service):
        """Test that good weather gets perfect score."""
        event = {"id": "event-1", "category": "Sports"}
        weather_context = {"outdoor_suitability": "good"}
        score = ranking_service._calculate_weather_score(weather_context, event)
        assert score == 100.0, "Good weather should get 100"
    
    def test_weather_score_poor_weather(self, ranking_service):
        """Test that poor weather gets low score."""
        event = {"id": "event-1", "category": "Sports"}
        weather_context = {"outdoor_suitability": "poor"}
        score = ranking_service._calculate_weather_score(weather_context, event)
        assert score == 25.0, "Poor weather should get 25"
    
    def test_weather_score_indoor_event(self, ranking_service):
        """Test that indoor event gets default good score."""
        event = {"id": "event-1", "category": "Theater"}
        weather_context = None
        score = ranking_service._calculate_weather_score(weather_context, event)
        assert score == 70.0, "Indoor event should get 70"
    
    def test_rank_events_sorting(self, ranking_service, sample_intent):
        """Test that events are sorted by total score descending."""
        enriched_events = [
            {
                "event": {
                    "id": "event-1",
                    "title": "Low Score Event",
                    "category": "Other",
                    "start_datetime": (datetime.now() + timedelta(days=30)).isoformat(),
                    "price_min": 200.0
                },
                "venue_context": None,
                "weather_context": None
            },
            {
                "event": {
                    "id": "event-2",
                    "title": "Electronic Music Festival",
                    "description": "Amazing electronic music",
                    "category": "Music",
                    "start_datetime": (datetime.now() + timedelta(days=6)).isoformat(),
                    "price_min": 50.0,
                    "price_max": 80.0,
                    "image_url": "https://example.com/image.jpg",
                    "venue_name": "Berlin Arena"
                },
                "venue_context": None,
                "weather_context": None
            }
        ]
        
        ranked = ranking_service.rank_events(enriched_events, sample_intent)
        
        assert len(ranked) == 2
        assert ranked[0]["event"]["id"] == "event-2", "Higher scoring event should be first"
        assert ranked[0]["recommendation"]["total_score"] > ranked[1]["recommendation"]["total_score"]
    
    def test_label_assignment_best_overall(self, ranking_service, sample_intent, sample_event):
        """Test that highest scoring event gets 'Best Overall' label."""
        enriched_events = [
            {
                "event": sample_event,
                "venue_context": None,
                "weather_context": None
            }
        ]
        
        ranked = ranking_service.rank_events(enriched_events, sample_intent)
        
        assert ranked[0]["recommendation"]["label"] == "Best Overall"
    
    def test_label_assignment_budget_pick(self, ranking_service, sample_intent):
        """Test that affordable event gets 'Best Budget Pick' label."""
        enriched_events = [
            {
                "event": {
                    "id": "event-1",
                    "title": "Electronic Music Festival",
                    "description": "Amazing electronic music",
                    "category": "Music",
                    "start_datetime": (datetime.now() + timedelta(days=6)).isoformat(),
                    "price_min": 50.0,
                    "price_max": 80.0,
                    "image_url": "https://example.com/image.jpg",
                    "venue_name": "Berlin Arena"
                },
                "venue_context": None,
                "weather_context": None
            },
            {
                "event": {
                    "id": "event-2",
                    "title": "Free Electronic Party",
                    "description": "Free electronic music party",
                    "category": "Music",
                    "start_datetime": (datetime.now() + timedelta(days=6)).isoformat(),
                    "price_min": 0.0,
                    "price_max": 0.0,
                    "image_url": "https://example.com/image.jpg"
                },
                "venue_context": None,
                "weather_context": None
            }
        ]
        
        ranked = ranking_service.rank_events(enriched_events, sample_intent)
        
        labels = [e["recommendation"]["label"] for e in ranked]
        assert "Best Budget Pick" in labels, "Should have a budget pick label"
    
    def test_missing_data_does_not_fail(self, ranking_service, sample_intent):
        """Test that ranking works even with missing event data."""
        enriched_events = [
            {
                "event": {
                    "id": "event-1",
                    "title": "Minimal Event"
                    # Missing most fields
                },
                "venue_context": None,
                "weather_context": None
            }
        ]
        
        ranked = ranking_service.rank_events(enriched_events, sample_intent)
        
        assert len(ranked) == 1
        assert ranked[0]["recommendation"]["total_score"] >= 0
        assert ranked[0]["recommendation"]["total_score"] <= 100


# Made with Bob