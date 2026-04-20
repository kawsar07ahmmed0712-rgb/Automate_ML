    from enum import Enum

    class Severity(str, Enum):
        low = "low"
        medium = "medium"
        high = "high"

    class SemanticType(str, Enum):
        identifier = "identifier"
        binary_flag = "binary_flag"
        categorical = "categorical"
        numeric_continuous = "numeric_continuous"
        numeric_discrete = "numeric_discrete"
        datetime = "datetime"
        text = "text"
        unknown = "unknown"
    
