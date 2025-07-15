from enums import EmailType
from registry import register_email_target
from service import EmailTargetService


@register_email_target(EmailType.ONBOARDING)
async def onboarding_handler():
    service = await EmailTargetService.create()
    return await service.get_target_emails()
