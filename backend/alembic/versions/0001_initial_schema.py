"""initial schema: donors, blood_requests, blood_units"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "donors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("blood_group", sa.String(length=3), nullable=False),
        sa.Column("email", sa.String(length=160), nullable=False, unique=True),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("last_donation_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')", name="ck_donors_blood_group"),
    )
    op.create_index("ix_donors_blood_group", "donors", ["blood_group"])
    op.create_index("ix_donors_city", "donors", ["city"])

    op.create_table(
        "blood_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hospital", sa.String(length=160), nullable=False),
        sa.Column("patient_ref", sa.String(length=60), nullable=False),
        sa.Column("blood_group", sa.String(length=3), nullable=False),
        sa.Column("component", sa.String(length=20), nullable=False),
        sa.Column("units_needed", sa.Integer(), nullable=False),
        sa.Column("urgency", sa.String(length=10), nullable=False, server_default="ROUTINE"),
        sa.Column("status", sa.String(length=12), nullable=False, server_default="PENDING"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("units_needed > 0", name="ck_requests_units_positive"),
    )
    op.create_index("ix_blood_requests_status", "blood_requests", ["status"])

    op.create_table(
        "blood_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("donor_id", sa.Integer(), sa.ForeignKey("donors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("blood_group", sa.String(length=3), nullable=False),
        sa.Column("component", sa.String(length=20), nullable=False),
        sa.Column("volume_ml", sa.Integer(), nullable=False),
        sa.Column("collected_on", sa.Date(), nullable=False),
        sa.Column("expires_on", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False, server_default="AVAILABLE"),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("blood_requests.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("expires_on >= collected_on", name="ck_units_expiry_after_collection"),
    )
    op.create_index("ix_blood_units_donor_id", "blood_units", ["donor_id"])
    op.create_index("ix_blood_units_blood_group", "blood_units", ["blood_group"])
    op.create_index("ix_blood_units_expires_on", "blood_units", ["expires_on"])
    op.create_index("ix_blood_units_status", "blood_units", ["status"])


def downgrade():
    op.drop_table("blood_units")
    op.drop_table("blood_requests")
    op.drop_table("donors")
