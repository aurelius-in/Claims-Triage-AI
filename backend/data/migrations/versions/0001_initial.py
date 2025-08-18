"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE casetype AS ENUM ('auto_insurance', 'health_insurance', 'property_insurance', 'life_insurance', 'fraud_review', 'legal_case', 'bank_dispute', 'healthcare_prior_auth', 'general')")
    op.execute("CREATE TYPE urgencylevel AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE risklevel AS ENUM ('low', 'medium', 'high', 'extreme')")
    op.execute("CREATE TYPE casestatus AS ENUM ('pending', 'in_progress', 'escalated', 'resolved', 'closed', 'rejected')")
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'supervisor', 'agent', 'auditor')")
    
    # Create teams table
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('current_load', sa.Integer(), nullable=True),
        sa.Column('sla_target_hours', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('role', postgresql.ENUM('admin', 'supervisor', 'agent', 'auditor', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Create cases table
    op.create_table('cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('case_type', postgresql.ENUM('auto_insurance', 'health_insurance', 'property_insurance', 'life_insurance', 'fraud_review', 'legal_case', 'bank_dispute', 'healthcare_prior_auth', 'general', name='casetype'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('urgency_level', postgresql.ENUM('low', 'medium', 'high', 'critical', name='urgencylevel'), nullable=False),
        sa.Column('risk_level', postgresql.ENUM('low', 'medium', 'high', 'extreme', name='risklevel'), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'escalated', 'resolved', 'closed', 'rejected', name='casestatus'), nullable=False),
        sa.Column('assigned_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sla_target', sa.DateTime(), nullable=True),
        sa.Column('sla_deadline', sa.DateTime(), nullable=True),
        sa.Column('priority_score', sa.Float(), nullable=True),
        sa.Column('estimated_value', sa.Float(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('triaged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_cases_external_id'), 'cases', ['external_id'], unique=False)
    op.create_index('idx_cases_external_id', 'cases', ['external_id'], unique=False)
    op.create_index('idx_cases_status_created', 'cases', ['status', 'created_at'], unique=False)
    op.create_index('idx_cases_team_status', 'cases', ['assigned_team_id', 'status'], unique=False)
    op.create_index('idx_cases_urgency_risk', 'cases', ['urgency_level', 'risk_level'], unique=False)
    
    # Create documents table
    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.Column('processing_status', sa.String(length=50), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extracted_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_redacted', sa.Boolean(), nullable=True),
        sa.Column('redaction_reason', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create triage_results table
    op.create_table('triage_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('classifier_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_scorer_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('router_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('decision_support_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('compliance_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('overall_confidence', sa.Float(), nullable=False),
        sa.Column('processing_time_ms', sa.Integer(), nullable=False),
        sa.Column('agent_errors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('circuit_breaker_triggered', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=True),
        sa.Column('redacted_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('previous_hash', sa.String(length=64), nullable=True),
        sa.Column('current_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_case_action', 'audit_logs', ['case_id', 'action'], unique=False)
    op.create_index('idx_audit_logs_created', 'audit_logs', ['created_at'], unique=False)
    
    # Create analytics_snapshots table
    op.create_table('analytics_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_unit', sa.String(length=20), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('case_type', postgresql.ENUM('auto_insurance', 'health_insurance', 'property_insurance', 'life_insurance', 'fraud_review', 'legal_case', 'bank_dispute', 'healthcare_prior_auth', 'general', name='casetype'), nullable=True),
        sa.Column('urgency_level', postgresql.ENUM('low', 'medium', 'high', 'critical', name='urgencylevel'), nullable=True),
        sa.Column('risk_level', postgresql.ENUM('low', 'medium', 'high', 'extreme', name='risklevel'), nullable=True),
        sa.Column('aggregation_period', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_analytics_snapshot_date_type', 'analytics_snapshots', ['snapshot_date', 'metric_type'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index('idx_analytics_snapshot_date_type', table_name='analytics_snapshots')
    op.drop_table('analytics_snapshots')
    op.drop_index('idx_audit_logs_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_case_action', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_table('triage_results')
    op.drop_table('documents')
    op.drop_index('idx_cases_urgency_risk', table_name='cases')
    op.drop_index('idx_cases_team_status', table_name='cases')
    op.drop_index('idx_cases_status_created', table_name='cases')
    op.drop_index('idx_cases_external_id', table_name='cases')
    op.drop_index(op.f('ix_cases_external_id'), table_name='cases')
    op.drop_table('cases')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_table('teams')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS casestatus")
    op.execute("DROP TYPE IF EXISTS risklevel")
    op.execute("DROP TYPE IF EXISTS urgencylevel")
    op.execute("DROP TYPE IF EXISTS casetype")
