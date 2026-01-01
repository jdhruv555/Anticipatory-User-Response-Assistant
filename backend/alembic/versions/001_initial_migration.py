"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_type', sa.String(), nullable=True),
        sa.Column('total_calls', sa.Integer(), nullable=True),
        sa.Column('satisfaction_avg', sa.Float(), nullable=True),
        sa.Column('resolution_rate', sa.Float(), nullable=True),
        sa.Column('preferred_persona', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)

    # Create call_history table
    op.create_table(
        'call_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=True),
        sa.Column('persona_used', sa.String(), nullable=True),
        sa.Column('intent', sa.String(), nullable=True),
        sa.Column('satisfaction_score', sa.Float(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=True),
        sa.Column('outcome', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_call_history_id'), 'call_history', ['id'], unique=False)

    # Create persona_performance table
    op.create_table(
        'persona_performance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_type', sa.String(), nullable=False),
        sa.Column('persona_type', sa.String(), nullable=False),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('satisfaction_avg', sa.Float(), nullable=True),
        sa.Column('resolution_rate', sa.Float(), nullable=True),
        sa.Column('call_count', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_persona_performance_customer_type'), 'persona_performance', ['customer_type'], unique=False)
    op.create_index(op.f('ix_persona_performance_persona_type'), 'persona_performance', ['persona_type'], unique=False)

    # Create conversation_states table
    op.create_table(
        'conversation_states',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('call_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('current_intent', sa.String(), nullable=True),
        sa.Column('current_sentiment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('selected_persona', sa.String(), nullable=True),
        sa.Column('conversation_context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_states_id'), 'conversation_states', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_states_call_id'), 'conversation_states', ['call_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_conversation_states_call_id'), table_name='conversation_states')
    op.drop_index(op.f('ix_conversation_states_id'), table_name='conversation_states')
    op.drop_table('conversation_states')
    op.drop_index(op.f('ix_persona_performance_persona_type'), table_name='persona_performance')
    op.drop_index(op.f('ix_persona_performance_customer_type'), table_name='persona_performance')
    op.drop_table('persona_performance')
    op.drop_index(op.f('ix_call_history_id'), table_name='call_history')
    op.drop_table('call_history')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')

