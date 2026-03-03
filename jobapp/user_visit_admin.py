from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from user_visit.models import UserVisit


class UserVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def changelist_view(self, request, extra_context=None):
        """
        Add report link to the changelist view
        """
        extra_context = extra_context or {}
        extra_context['report_url'] = '/admin/user_visit/uservisit/report/'
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('report/', self.admin_site.admin_view(self.report_view), name='uservisit_report'),
            path('report/download/', self.admin_site.admin_view(self.download_report), name='uservisit_download'),
        ]
        return custom_urls + urls
    
    def report_view(self, request):
        """
        Display user visit report with filters
        """
        from django.shortcuts import render
        
        # Get filter parameters
        filter_type = request.GET.get('filter', 'all')
        
        # Get date range based on filter
        now = timezone.now()
        if filter_type == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif filter_type == 'week':
            start_date = now - timedelta(days=7)
            end_date = now
        elif filter_type == 'month':
            start_date = now - timedelta(days=30)
            end_date = now
        else:
            start_date = None
            end_date = None
        
        # Get visits
        if start_date and end_date:
            visits = UserVisit.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).select_related('user').order_by('-timestamp')
        else:
            visits = UserVisit.objects.all().select_related('user').order_by('-timestamp')[:2000]
        
        context = {
            'visits': visits,
            'filter_type': filter_type,
            'title': 'User Visit Report',
        }
        
        return render(request, 'admin/uservisit_report.html', context)
    
    def download_report(self, request):
        """
        Download user visit report as PDF
        """
        filter_type = request.GET.get('filter', 'all')
        
        # Get date range based on filter
        now = timezone.now()
        if filter_type == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            period = 'Today'
        elif filter_type == 'week':
            start_date = now - timedelta(days=7)
            end_date = now
            period = 'Last 7 Days'
        elif filter_type == 'month':
            start_date = now - timedelta(days=30)
            end_date = now
            period = 'Last 30 Days'
        else:
            start_date = None
            end_date = None
            period = 'All Time'
        
        # Get visits
        if start_date and end_date:
            visits = UserVisit.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).select_related('user').order_by('-timestamp')
        else:
            visits = UserVisit.objects.all().select_related('user').order_by('-timestamp')[:2000]
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="user_visit_report_{filter_type}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
        )
        
        # Title
        title = Paragraph(f'User Visit Report - {period}', title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Table data
        data = [['Email', 'Visit Date & Time']]
        for visit in visits:
            data.append([
                visit.user.email,
                visit.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        # Create table
        table = Table(data, colWidths=[3*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = Paragraph(
            f'<b>Total Records:</b> {len(visits)} | <b>Generated:</b> {now.strftime("%Y-%m-%d %H:%M:%S")}',
            styles['Normal']
        )
        elements.append(footer_text)
        
        doc.build(elements)
        return response


# Unregister the default admin if it exists and register with custom admin
try:
    admin.site.unregister(UserVisit)
    admin.site.register(UserVisit, UserVisitAdmin)
except admin.sites.NotRegistered:
    admin.site.register(UserVisit, UserVisitAdmin)
except admin.sites.AlreadyRegistered:
    # If already registered with our custom admin, do nothing
    pass
