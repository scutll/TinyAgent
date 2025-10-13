# to config the pipeline
from dataclasses import dataclass
@dataclass
class PipelineConfig:
    model_path: str = "model/deepseek-1.3b/snapshots/model"
    