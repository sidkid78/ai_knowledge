"""
Algorithm model for the nexus_ukg system.
"""
from sqlalchemy import Column, String, JSON, DateTime, event
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base
import datetime
import importlib
from app.db.models_base import Base

class Algorithm(Base):
    """
    Represents an algorithm that can be executed by agents on knowledge nodes.
    """
    __tablename__ = "algorithms"

    # Core fields
    id = Column(String(50), primary_key=True)  # E.g. "knowledge_discovery"
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    version = Column(String(20), default="1.0")
    
    # Algorithm configuration
    axis_parameters = Column(JSON, default=[])  # List of required/optional axes with weights
    implementation_ref = Column(String(200), nullable=False)  # Dotted path to implementation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    @validates('axis_parameters')
    def validate_axis_parameters(self, key, value):
        """Validate axis parameters structure"""
        if not isinstance(value, list):
            raise ValueError("axis_parameters must be a list")
        
        for param in value:
            if not isinstance(param, dict):
                raise ValueError("Each axis parameter must be a dictionary")
            if 'axis' not in param:
                raise ValueError("Each axis parameter must specify an 'axis'")
            if 'required' not in param:
                param['required'] = True
            if 'weight' not in param:
                param['weight'] = 1.0
        return value

    @validates('implementation_ref')
    def validate_implementation_ref(self, key, value):
        """Validate that the implementation reference points to a real function"""
        try:
            module_path, function_name = value.rsplit('.', 1)
            module = importlib.import_module(module_path)
            if not hasattr(module, function_name):
                raise ValueError(f"Function {function_name} not found in module {module_path}")
        except Exception as e:
            raise ValueError(f"Invalid implementation reference: {str(e)}")
        return value

    def __repr__(self):
        return f"<Algorithm(id={self.id}, name={self.name}, version={self.version})>"

# SQLAlchemy event listeners
@event.listens_for(Algorithm, 'before_insert')
@event.listens_for(Algorithm, 'before_update')
def timestamp_update(mapper, connection, target):
    """Update timestamp on change"""
    target.updated_at = datetime.datetime.utcnow()

