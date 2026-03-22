"""Add leads and lead_engagements tables.

Revision ID: 002
Revises: 001
Create Date: 2026-03-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "linkedin_leads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("linkedin_member_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("headline", sa.Text),
        sa.Column("current_company", sa.String(255)),
        sa.Column("profile_url", sa.Text),
        sa.Column("email", sa.String(255)),
        sa.Column("location", sa.String(255)),
        sa.Column("industry", sa.String(255)),
        sa.Column("ai_status", sa.String(50)),
        sa.Column("tags", ARRAY(sa.Text)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_linkedin_leads_user", "linkedin_leads", ["user_id"])
    op.create_index("idx_linkedin_leads_member", "linkedin_leads", ["linkedin_member_id"])

    op.create_table(
        "lead_engagements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lead_id", UUID(as_uuid=True), sa.ForeignKey("linkedin_leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("published_post_id", UUID(as_uuid=True), sa.ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engagement_type", sa.String(30), nullable=False),
        sa.Column("engagement_text", sa.Text),
        sa.Column("engaged_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_lead_engagements_lead", "lead_engagements", ["lead_id"])


def downgrade() -> None:
    op.drop_table("lead_engagements")
    op.drop_table("linkedin_leads")
