from sqlalchemy import Column, String, JSON 

class Algorithm(Base):
    __tablename__ = "algorithms"

    id = Column(String(50), primary_key=True)  # E.g. "knowledge_discovery"
    name = Column(String(100), nullable=False)
    axis_parameters = Column(JSON, default=[]) # E.g. [{"axis": "pillar_function", "weight":1.0},...]
    logic_ref = Column(String(100))            # Dotted import path to implement

