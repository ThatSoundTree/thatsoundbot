from loguru import logger
from pydantic import BaseModel


class PipelineView(BaseModel):
    """Pydantic model that implements selected language in pipeline.json"""

    welcome_message: str


class PipelinesView(BaseModel):
    """Pydantic model that implements different languages in pipeline.json"""

    RU: PipelineView

    def __getitem__(self, language: str) -> PipelineView:
        pipelines_dict = self.model_dump()
        language_upper = language.upper() if language else "RU"
        if language_upper in pipelines_dict:
            return PipelineView.model_validate(pipelines_dict[language_upper])
        logger.warning("Missing {lang} in pipelines.json", lang=language)
        return self.RU