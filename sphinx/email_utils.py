from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
import traceback

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def _write_fallback_log(subject: str, message: str, recipients: Iterable[str], error: Optional[str] = None) -> None:
    try:
        log_dir = Path(getattr(settings, 'EMAIL_FILE_PATH', Path('tmp') / 'emails'))
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        safe_to = '-'.join([str(r).replace('@', '_at_').replace(' ', '') for r in recipients]) or 'no-recipient'
        log_file = log_dir / f"fallback-{timestamp}-{safe_to}.log"
        error_msg = f"\n\nERROR: {error}" if error else ""
        log_file.write_text(f"SUBJECT: {subject}\nTO: {', '.join(recipients)}\n\n{message}{error_msg}")
    except Exception:
        # As a last resort, swallow errors to avoid breaking user flows
        pass


def send_email(subject: str, message: str, to: Iterable[str], *, fail_silently: bool = False, 
               html_template: Optional[str] = None, context: Optional[dict] = None) -> bool:
    recipients = [r for r in to if r]
    if not recipients:
        logger.warning(f"send_email: No valid recipients for subject '{subject}'")
        return False
    
    context = context or {}
    context['subject'] = subject
    
    try:
        email_subject = f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')}{subject}"
        
        if html_template:
            try:
                # Render HTML template
                html_message = render_to_string(html_template, context)
                # Create plain text version
                text_message = strip_tags(html_message)
            except Exception as e:
                error_msg = f"Template rendering error for '{html_template}': {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                # Fallback to plain text if template fails
                text_message = message
                html_message = None
            
            if html_message:
                # Send HTML email
                email = EmailMultiAlternatives(
                    subject=email_subject,
                    body=text_message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    to=list(recipients),
                )
                email.attach_alternative(html_message, "text/html")
                count = email.send(fail_silently=fail_silently)
            else:
                # Fallback to plain text if HTML template failed
                count = send_mail(
                    subject=email_subject,
                    message=text_message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    recipient_list=list(recipients),
                    fail_silently=fail_silently,
                )
        else:
            # Send plain text email
            count = send_mail(
                subject=email_subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=list(recipients),
                fail_silently=fail_silently,
            )
        
        if count > 0:
            logger.info(f"Email sent successfully: '{subject}' to {recipients}")
            return True
        else:
            logger.warning(f"Email send returned 0: '{subject}' to {recipients}")
            _write_fallback_log(subject, message, recipients, "Send returned 0")
            return False
            
    except Exception as e:
        error_msg = f"Error sending email '{subject}' to {recipients}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        _write_fallback_log(subject, message, recipients, error_msg)
        if fail_silently:
            return False
        raise


