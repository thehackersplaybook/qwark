from typing import TypedDict, Optional, List, Dict


class ColumnInfo(TypedDict):
    column_name: str
    data_type: str
    is_nullable: str  # "YES" or "NO"
    column_default: Optional[str]


# Schema dict maps table name -> list of columns
SchemaDict = Dict[str, List[ColumnInfo]]


class BuffersInfo(TypedDict, total=False):
    Shared_Hit_Blocks: Optional[int]
    Shared_Read_Blocks: Optional[int]
    Shared_Dirtied_Blocks: Optional[int]
    Shared_Written_Blocks: Optional[int]
    Local_Hit_Blocks: Optional[int]
    Local_Read_Blocks: Optional[int]
    Local_Dirtied_Blocks: Optional[int]
    Local_Written_Blocks: Optional[int]
    Temp_Read_Blocks: Optional[int]
    Temp_Written_Blocks: Optional[int]


class PlanNode(TypedDict):
    Node_Type: str
    Total_Cost: float
    Actual_Rows: int
    Buffers: Optional[BuffersInfo]
    Plans: Optional[List["PlanNode"]]  # Recursive list of child plan nodes


class ExplainPlan(TypedDict):
    Plan: PlanNode
    Execution_Time: float
    # You can add other optional fields like Triggers, JIT info, etc. if needed


ExplainPlanDict = ExplainPlan


class GeneratedQuery(TypedDict):
    error: Optional[str]
    query: str
    explanation: str
