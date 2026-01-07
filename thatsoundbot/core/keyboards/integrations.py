from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from thatsoundbot.core.models.pipelines_view import PipelineView, IntegrationsView
from thatsoundbot.settings import get_tsapi_settings


def create_integrate_button(service_name: str, is_connected: bool, auth_url: str, integration_pipelines: IntegrationsView) -> list[InlineKeyboardButton]:
    template_text = "{service}: {status}"
    if is_connected:
        return [
            InlineKeyboardButton(text=template_text.format(service=service_name.capitalize(), status=integration_pipelines.connected), callback_data="integration:connected")
        ]

    else:
        return [
            InlineKeyboardButton(
                text=template_text.format(service=service_name.capitalize(), status=integration_pipelines.disconnected), url=auth_url
            )
        ]


def prepare_integrate_keyboard(hgramid: str, integrations: dict[str, bool], pipeline: PipelineView) -> InlineKeyboardMarkup:
    """Create inline keyboard with integration buttons."""
    tsapi_settings = get_tsapi_settings()
    integration_pipelines = pipeline.integrations
    auth_urls = tsapi_settings.get_auth_urls(hgramid=hgramid)

    buttons = []
    for service_name, is_connected in integrations.items():
        buttons.append(
            create_integrate_button(
                service_name=service_name,
                is_connected=is_connected,
                auth_url=auth_urls[service_name],
                integration_pipelines=integration_pipelines
            )
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=integration_pipelines.refresh_button_text,
                callback_data="integration:refresh",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
