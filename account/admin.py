from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class AddUserForm(forms.ModelForm):
    """
    New User Form. Requires password confirmation.
    """
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirm password', widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'role', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UpdateUserForm(forms.ModelForm):
    """
    Update User Form. Doesn't allow changing password in the Admin.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'email', 'password', 'first_name', 'gender', 'role', 'last_name', 'is_active',
            'is_staff'
        )

    def clean_password(self):
# Password can't be changed in the admin
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UpdateUserForm
    add_form = AddUserForm

    list_display = ('email', 'first_name', 'last_name', 'gender', 'role', 'is_staff')
    list_filter = ('is_staff', )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender', 'role', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email', 'first_name', 'last_name', 'gender', 'role', 'password1',
                    'password2'
                )
            }
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

from .models import UserLogin
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from django.db.models import Q


class UserLoginAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'login_time', 'ip_address')
    list_filter = ('login_time', 'user')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ip_address')
    readonly_fields = ('user', 'login_time', 'ip_address', 'user_agent')
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('report/', self.admin_site.admin_view(self.report_view), name='userlogin_report'),
            path('report/download/', self.admin_site.admin_view(self.download_report), name='userlogin_download'),
        ]
        return custom_urls + urls
    
    def report_view(self, request):
        """
        Display login report with filters
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
        
        # Get logins
        if start_date and end_date:
            logins = UserLogin.objects.filter(
                login_time__gte=start_date,
                login_time__lte=end_date
            ).select_related('user').order_by('-login_time')
        else:
            logins = UserLogin.objects.all().select_related('user').order_by('-login_time')[:1000]
        
        context = {
            'logins': logins,
            'filter_type': filter_type,
            'title': 'User Login Report',
        }
        
        return render(request, 'admin/userlogin_report.html', context)
    
    def download_report(self, request):
        """
        Download login report as PDF
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
        
        # Get logins
        if start_date and end_date:
            logins = UserLogin.objects.filter(
                login_time__gte=start_date,
                login_time__lte=end_date
            ).select_related('user').order_by('-login_time')
        else:
            logins = UserLogin.objects.all().select_related('user').order_by('-login_time')[:1000]
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="user_login_report_{filter_type}.pdf"'
        
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
        title = Paragraph(f'User Login Report - {period}', title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Table data
        data = [['Email', 'Login Time', 'IP Address']]
        for login in logins:
            data.append([
                login.user.email,
                login.login_time.strftime('%Y-%m-%d %H:%M:%S'),
                login.ip_address or 'N/A'
            ])
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = Paragraph(
            f'<b>Total Records:</b> {len(logins)} | <b>Generated:</b> {now.strftime("%Y-%m-%d %H:%M:%S")}',
            styles['Normal']
        )
        elements.append(footer_text)
        
        doc.build(elements)
        return response


admin.site.register(UserLogin, UserLoginAdmin)
