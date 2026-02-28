from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_shortlisted_email(applicant):
    """
    Send email to candidate when they are shortlisted
    """
    try:
        subject = f"Great News! You've been Shortlisted for {applicant.job.title}"
        
        context = {
            'candidate_name': applicant.user.get_full_name(),
            'job_title': applicant.job.title,
            'company_name': applicant.job.company_name,
            'job_location': applicant.job.location,
        }
        
        html_message = render_to_string('jobapp/emails/shortlisted_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [applicant.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending shortlisted email to {applicant.user.email}: {str(e)}")


def send_rejected_email(applicant):
    """
    Send email to candidate when they are rejected
    """
    try:
        subject = f"Application Status Update for {applicant.job.title}"
        
        context = {
            'candidate_name': applicant.user.get_full_name(),
            'job_title': applicant.job.title,
            'company_name': applicant.job.company_name,
        }
        
        html_message = render_to_string('jobapp/emails/rejected_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [applicant.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending rejected email to {applicant.user.email}: {str(e)}")


def send_interview_scheduled_email(interview):
    """
    Send email to candidate when interview is scheduled
    """
    try:
        subject = f"Interview Scheduled for {interview.applicant.job.title}"
        
        context = {
            'candidate_name': interview.applicant.user.get_full_name(),
            'job_title': interview.applicant.job.title,
            'company_name': interview.applicant.job.company_name,
            'interview_date': interview.scheduled_date.strftime('%B %d, %Y'),
            'interview_time': interview.scheduled_date.strftime('%I:%M %p'),
            'meeting_link': interview.meeting_link,
            'notes': interview.notes,
        }
        
        html_message = render_to_string('jobapp/emails/interview_scheduled_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [interview.applicant.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending interview scheduled email to {interview.applicant.user.email}: {str(e)}")


def send_interview_updated_email(interview):
    """
    Send email to candidate when interview is updated
    """
    try:
        subject = f"Interview Details Updated for {interview.applicant.job.title}"
        
        context = {
            'candidate_name': interview.applicant.user.get_full_name(),
            'job_title': interview.applicant.job.title,
            'company_name': interview.applicant.job.company_name,
            'interview_date': interview.scheduled_date.strftime('%B %d, %Y'),
            'interview_time': interview.scheduled_date.strftime('%I:%M %p'),
            'meeting_link': interview.meeting_link,
            'notes': interview.notes,
        }
        
        html_message = render_to_string('jobapp/emails/interview_updated_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [interview.applicant.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending interview updated email to {interview.applicant.user.email}: {str(e)}")
