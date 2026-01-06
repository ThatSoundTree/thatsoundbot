from loguru import logger
from pydantic import BaseModel

class IntegrationsView(BaseModel):
    connected: str
    disconnected: str
    refresh_button_text: str
    already_connected: str

class PipelineView(BaseModel):
    """Pydantic model that implements selected language in pipeline.json"""

    welcome_message: str
    integrations: IntegrationsView


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