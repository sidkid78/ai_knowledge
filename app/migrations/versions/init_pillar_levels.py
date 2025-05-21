"""Initialize Pillar Levels

Revision ID: init_pillar_levels
Create Date: 2024-03-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# Create a temp table reference
pillar_levels = table('pillar_levels',
    column('id', sa.String),
    column('name', sa.String),
    column('description', sa.String),
    column('domain_type', sa.String),
    column('parent_id', sa.String),
    column('schema_extensions', sa.JSON)
)

def upgrade():
    # Example pillar levels (extend as needed)
    example_pillars = [
        # Root domains
        {
            'id': 'PL01',
            'name': 'Mathematics',
            'description': 'Mathematical concepts and theories',
            'domain_type': 'STEM',
            'parent_id': None,
            'schema_extensions': {
                'notation_systems': ['LaTeX', 'MathML'],
                'proof_requirements': True
            }
        },
        {
            'id': 'PL02',
            'name': 'Computer Science',
            'description': 'Computing theory and practice',
            'domain_type': 'STEM',
            'parent_id': None,
            'schema_extensions': {
                'programming_paradigms': True,
                'computational_complexity': True
            }
        },
        # Mathematics sub-domains
        {
            'id': 'PL03',
            'name': 'Algebra',
            'description': 'Study of mathematical structures',
            'domain_type': 'Mathematics',
            'parent_id': 'PL01',
            'schema_extensions': {}
        },
        {
            'id': 'PL04',
            'name': 'Quantum Computing',
            'description': 'Computing using quantum phenomena',
            'domain_type': 'Computer Science',
            'parent_id': 'PL02',
            'schema_extensions': {
                'quantum_gates': True,
                'qubit_operations': True
            }
        },
        # Add more pillars as needed...
    ]
    
    op.bulk_insert(pillar_levels, example_pillars)

def downgrade():
    op.execute(
        pillar_levels.delete()
    ) 