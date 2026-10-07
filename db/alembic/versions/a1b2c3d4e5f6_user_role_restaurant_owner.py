"""user 新增 role 取代 is_admin、restaurant 新增 owner_id

Revision ID: a1b2c3d4e5f6
Revises: 34c949168dc6
Create Date: 2026-10-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '34c949168dc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('role', sa.String(length=20), server_default=sa.text("'user'"), nullable=False, comment='角色:user / owner / super_admin'), schema='restaurant')
    # 既有管理員轉為超級管理員
    op.execute("UPDATE restaurant.\"user\" SET role = 'super_admin' WHERE is_admin = true")
    op.drop_column('user', 'is_admin', schema='restaurant')

    op.add_column('restaurant', sa.Column('owner_id', sa.UUID(), nullable=True, comment='業者(擁有者) ID'), schema='restaurant')
    op.create_index(op.f('ix_restaurant_restaurant_owner_id'), 'restaurant', ['owner_id'], unique=False, schema='restaurant')
    op.create_foreign_key(
        'fk_restaurant_owner_id_user', 'restaurant', 'user', ['owner_id'], ['id'],
        source_schema='restaurant', referent_schema='restaurant', onupdate='CASCADE', ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_restaurant_owner_id_user', 'restaurant', schema='restaurant', type_='foreignkey')
    op.drop_index(op.f('ix_restaurant_restaurant_owner_id'), table_name='restaurant', schema='restaurant')
    op.drop_column('restaurant', 'owner_id', schema='restaurant')

    op.add_column('user', sa.Column('is_admin', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='是否為管理員'), schema='restaurant')
    op.execute("UPDATE restaurant.\"user\" SET is_admin = true WHERE role = 'super_admin'")
    op.drop_column('user', 'role', schema='restaurant')
