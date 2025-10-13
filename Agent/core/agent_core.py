from Model.pipline import pipeline
# the core agent part 
# it does not contains the model directly, but the pipeline does for it 


class AgentCore:
    def __init__(self,
                 Pipeline):
        self.pipeline: pipeline = Pipeline
        