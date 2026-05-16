"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-05-16 10:24:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create saved_events table
    op.create_table(
        'saved_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('event_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_events_session_id'), 'saved_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_saved_events_event_id'), 'saved_events', ['event_id'], unique=False)

    # Create search_history table
    op.create_table(
        'search_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('raw_query', sa.Text(), nullable=False),
        sa.Column('parsed_intent_json', sa.Text(), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fallback_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_history_session_id'), 'search_history', ['session_id'], unique=False)

    # Create api_cache table
    op.create_table(
        'api_cache',
        sa.Column('cache_key', sa.String(length=255), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('request_hash', sa.String(length=64), nullable=False),
        sa.Column('response_json', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('cache_key')
    )
    op.create_index(op.f('ix_api_cache_tool_name'), 'api_cache', ['tool_name'], unique=False)
    op.create_index(op.f('ix_api_cache_request_hash'), 'api_cache', ['request_hash'], unique=False)
    op.create_index(op.f('ix_api_cache_expires_at'), 'api_cache', ['expires_at'], unique=False)

    # Create outbound_clicks table
    op.create_table(
        'outbound_clicks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('clicked_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_outbound_clicks_session_id'), 'outbound_clicks', ['session_id'], unique=False)
    op.create_index(op.f('ix_outbound_clicks_event_id'), 'outbound_clicks', ['event_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_outbound_clicks_event_id'), table_name='outbound_clicks')
    op.drop_index(op.f('ix_outbound_clicks_session_id'), table_name='outbound_clicks')
    op.drop_table('outbound_clicks')
    
    op.drop_index(op.f('ix_api_cache_expires_at'), table_name='api_cache')
    op.drop_index(op.f('ix_api_cache_request_hash'), table_name='api_cache')
    op.drop_index(op.f('ix_api_cache_tool_name'), table_name='api_cache')
    op.drop_table('api_cache')
    
    op.drop_index(op.f('ix_search_history_session_id'), table_name='search_history')
    op.drop_table('search_history')
    
    op.drop_index(op.f('ix_saved_events_event_id'), table_name='saved_events')
    op.drop_index(op.f('ix_saved_events_session_id'), table_name='saved_events')
    op.drop_table('saved_events')

# Made with Bob
