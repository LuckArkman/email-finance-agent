"""Initial schema with IVA fields and TenantSettings

Revision ID: 0001_initial_iva_schema
Revises: 
Create Date: 2026-05-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_iva_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # Create tables if they don't exist, then add new columns safely
    # =========================================================================

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # --- tenant_settings (NEW table) ---
    if 'tenant_settings' not in existing_tables:
        op.create_table(
            'tenant_settings',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id'), nullable=False, unique=True),
            sa.Column('iva_rate', sa.Float(), nullable=True, server_default='0.23'),
            sa.Column('currency', sa.String(), nullable=True, server_default='EUR'),
            sa.Column('fiscal_name', sa.String(), nullable=True),
            sa.Column('fiscal_country', sa.String(), nullable=True, server_default='PT'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    # --- invoices table: add new columns if missing ---
    if 'invoices' in existing_tables:
        existing_cols = {c['name'] for c in inspector.get_columns('invoices')}

        new_columns = {
            'document_type': sa.Column('document_type', sa.String(), nullable=True, server_default='accounts_payable'),
            'net_amount': sa.Column('net_amount', sa.Float(), nullable=True, server_default='0.0'),
            'iva_rate': sa.Column('iva_rate', sa.Float(), nullable=True, server_default='0.23'),
            'iva_amount': sa.Column('iva_amount', sa.Float(), nullable=True, server_default='0.0'),
            'payment_reference': sa.Column('payment_reference', sa.String(), nullable=True),
        }

        for col_name, col_def in new_columns.items():
            if col_name not in existing_cols:
                op.add_column('invoices', col_def)

        # Fix currency default from BRL to EUR
        if 'currency' in existing_cols:
            op.execute("UPDATE invoices SET currency = 'EUR' WHERE currency = 'BRL'")

    # --- email_messages: ensure body column exists ---
    if 'email_messages' in existing_tables:
        existing_cols = {c['name'] for c in inspector.get_columns('email_messages')}
        if 'body' not in existing_cols:
            op.add_column('email_messages', sa.Column('body', sa.Text(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'tenant_settings' in existing_tables:
        op.drop_table('tenant_settings')

    if 'invoices' in existing_tables:
        existing_cols = {c['name'] for c in inspector.get_columns('invoices')}
        for col_name in ['document_type', 'net_amount', 'iva_rate', 'iva_amount', 'payment_reference']:
            if col_name in existing_cols:
                op.drop_column('invoices', col_name)
