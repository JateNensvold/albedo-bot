"""Added player timezones and availability to database v2

Revision ID: a644106254d1
Revises: 
Create Date: 2022-08-14 08:55:56.801635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a644106254d1'
down_revision = None
branch_labels = None
depends_on = None


availability_enum = sa.Enum('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
                            name='availabilityenum')
elder_tree_type_enum = sa.Enum('SUSTENANCE', 'SORCERY', 'MIGHT', 'FORTITUDE', 'CELERITY',
                               name='eldertreetypesenum')
timezone_enum = sa.Enum('GMT-12', 'GMT-11', 'GMT-10', 'GMT-9', 'GMT-8', 'GMT-7', 'GMT-6', 'GMT-5', 'GMT-4', 'GMT-3', 'GMT-2', 'GMT-1', 'GMT+0', 'GMT+1', 'GMT+2', 'GMT+3', 'GMT+4', 'GMT+5', 'GMT+6', 'GMT+7', 'GMT+8', 'GMT+9', 'GMT+10', 'GMT+11', 'GMT+12',
                        name='timezoneenum')


def upgrade() -> None:
    # availability_enum.create(op.get_bind(), checkfirst=True)
    # elder_tree_type_enum.create(op.get_bind(), checkfirst=True)
    timezone_enum.create(op.get_bind(), checkfirst=True)
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player_availability',
                    sa.Column('player_id', sa.BIGINT(), nullable=False),
                    sa.Column('availability',
                              availability_enum, nullable=False),
                    sa.ForeignKeyConstraint(
                        ['player_id'], ['players.discord_id'], ),
                    sa.PrimaryKeyConstraint('player_id', 'availability')
                    )
    op.create_table('player_elder_tree',
                    sa.Column('player_id', sa.BIGINT(), nullable=False),
                    sa.Column('branch_level', sa.Integer(), nullable=True),
                    sa.Column('tree_branch', elder_tree_type_enum,
                              nullable=False),
                    sa.ForeignKeyConstraint(
                        ['player_id'], ['players.discord_id'], ),
                    sa.PrimaryKeyConstraint('player_id', 'tree_branch')
                    )
    op.add_column('players', sa.Column(
        'resonating_crystal_level', sa.Integer(), nullable=True))
    op.add_column('players', sa.Column(
        'timezone', timezone_enum, nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('players', 'timezone')
    op.drop_column('players', 'resonating_crystal_level')
    op.drop_table('player_elder_tree')
    op.drop_table('player_availability')
    # ### end Alembic commands ###

    availability_enum.drop(op.get_bind(), checkfirst=False)
    timezone_enum.drop(op.get_bind(), checkfirst=False)
    elder_tree_type_enum.drop(op.get_bind(), checkfirst=False)
