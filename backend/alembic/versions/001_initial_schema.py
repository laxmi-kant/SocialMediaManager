"""Initial schema - 9 core tables.

Revision ID: 001
Revises:
Create Date: 2026-03-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_users_email", "users", ["email"])

    # --- platform_accounts ---
    op.create_table(
        "platform_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("platform_user_id", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "platform", name="uq_platform_accounts_user_platform"),
    )
    op.create_index("idx_platform_accounts_user", "platform_accounts", ["user_id"])

    # --- content_sources ---
    op.create_table(
        "content_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("score", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_type", "external_id", name="uq_content_sources_type_external"),
    )
    op.create_index("idx_content_sources_type_score", "content_sources", ["source_type", sa.text("score DESC")])
    op.create_index("idx_content_sources_fetched", "content_sources", [sa.text("fetched_at DESC")])

    # --- schedules ---
    op.create_table(
        "schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("content_types", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("cron_expression", sa.String(100), nullable=False),
        sa.Column("timezone", sa.String(100), server_default=sa.text("'UTC'"), nullable=True),
        sa.Column("auto_approve", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_schedules_user", "schedules", ["user_id"])

    # --- generated_posts ---
    op.create_table(
        "generated_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_platform", sa.String(50), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("tone", sa.String(50), server_default=sa.text("'professional'"), nullable=True),
        sa.Column("hashtags", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("prompt_used", sa.Text(), nullable=True),
        sa.Column("token_usage", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(30), server_default=sa.text("'draft'"), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["content_source_id"], ["content_sources.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_generated_posts_user_status", "generated_posts", ["user_id", "status"])
    op.create_index("idx_generated_posts_status", "generated_posts", ["status"])

    # --- published_posts ---
    op.create_table(
        "published_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("generated_post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform_post_id", sa.String(255), nullable=True),
        sa.Column("platform_url", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("status", sa.String(30), server_default=sa.text("'success'"), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["generated_post_id"], ["generated_posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["platform_account_id"], ["platform_accounts.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_published_posts_generated", "published_posts", ["generated_post_id"])
    op.create_index("idx_published_posts_account", "published_posts", ["platform_account_id"])
    op.create_index("idx_published_posts_time", "published_posts", [sa.text("published_at DESC")])

    # --- analytics_snapshots ---
    op.create_table(
        "analytics_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("published_post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("impressions", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("likes", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("comments", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("shares", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("clicks", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("engagement_rate", sa.Numeric(7, 4), nullable=True),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["published_post_id"], ["published_posts.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_analytics_post_time", "analytics_snapshots", ["published_post_id", sa.text("snapshot_at DESC")])

    # --- comments ---
    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("published_post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("platform_comment_id", sa.String(255), nullable=False),
        sa.Column("commenter_name", sa.String(255), nullable=True),
        sa.Column("commenter_username", sa.String(255), nullable=True),
        sa.Column("commenter_profile_url", sa.Text(), nullable=True),
        sa.Column("commenter_follower_count", sa.Integer(), nullable=True),
        sa.Column("comment_text", sa.Text(), nullable=False),
        sa.Column("is_mention", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("is_reply_to_reply", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("parent_comment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column("comment_type", sa.String(30), nullable=True),
        sa.Column("commented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["published_post_id"], ["published_posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_comment_id"], ["comments.id"]),
        sa.UniqueConstraint("platform", "platform_comment_id", name="uq_comments_platform_comment"),
    )
    op.create_index("idx_comments_post", "comments", ["published_post_id"])

    # --- comment_replies ---
    op.create_table(
        "comment_replies",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("comment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reply_text", sa.Text(), nullable=False),
        sa.Column("ai_suggested_text", sa.Text(), nullable=True),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("token_usage", postgresql.JSONB(), nullable=True),
        sa.Column("reply_mode", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), server_default=sa.text("'draft'"), nullable=True),
        sa.Column("platform_reply_id", sa.String(255), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_comment_replies_comment", "comment_replies", ["comment_id"])
    op.create_index("idx_comment_replies_status", "comment_replies", ["status"])


def downgrade() -> None:
    op.drop_table("comment_replies")
    op.drop_table("comments")
    op.drop_table("analytics_snapshots")
    op.drop_table("published_posts")
    op.drop_table("generated_posts")
    op.drop_table("schedules")
    op.drop_table("content_sources")
    op.drop_table("platform_accounts")
    op.drop_table("users")
