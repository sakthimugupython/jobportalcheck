from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib import auth

from jobapp.models import *
from ckeditor.widgets import CKEditorWidget


    

class JobForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['title'].label = "Job Title :"
        self.fields['location'].label = "Job Location :"
        self.fields['salary'].label = "Salary :"
        self.fields['description'].label = "Job Description :"
        self.fields['tags'].label = "Tags :"
        self.fields['last_date'].label = "Submission Deadline :"
        self.fields['company_name'].label = "Company Name :"


        self.fields['title'].widget.attrs.update(
            {
                'placeholder': 'eg : Software Developer',
            }
        )        
        self.fields['location'].widget.attrs.update(
            {
                'placeholder': 'eg : Bangladesh',
            }
        )
        self.fields['salary'].widget.attrs.update(
            {
                'placeholder': '$800 - $1200',
            }
        )
        self.fields['tags'].widget.attrs.update(
            {
                'placeholder': 'Use comma separated. eg: Python, JavaScript ',
            }
        )                        
        self.fields['last_date'].widget.attrs.update(
            {
                'placeholder': 'YYYY-MM-DD ',
                
            }
        )        
        self.fields['company_name'].widget.attrs.update(
            {
                'placeholder': 'Company Name',
            }
        )    


    class Meta:
        model = Job

        fields = [
            "title",
            "location",
            "job_type",
            "salary",
            "description",
            "tags",
            "last_date",
            "company_name",
            "company_description"
            ]

    def clean_job_type(self):
        job_type = self.cleaned_data.get('job_type')

        if not job_type:
            raise forms.ValidationError("Service is required")
        return job_type


    def save(self, commit=True):
        job = super(JobForm, self).save(commit=False)
        if commit:
            
            job.save()
        return job




class JobApplyForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={
                'class': 'custom-file-input',
                'accept': '.pdf,.doc,.docx',
                'required': True
            })
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            raise forms.ValidationError("Resume is required to apply for this job.")
        
        # Check file size (5MB max)
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Resume file size must not exceed 5MB.")
        
        # Check file extension
        allowed_extensions = ['pdf', 'doc', 'docx']
        file_ext = resume.name.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
        
        return resume

class JobBookmarkForm(forms.ModelForm):
    class Meta:
        model = BookmarkJob
        fields = ['job']




class JobEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['title'].label = "Job Title :"
        self.fields['location'].label = "Job Location :"
        self.fields['salary'].label = "Salary :"
        self.fields['description'].label = "Job Description :"
        self.fields['last_date'].label = "Dead Line :"
        self.fields['company_name'].label = "Company Name :"


        self.fields['title'].widget.attrs.update(
            {
                'placeholder': 'eg : Software Developer',
            }
        )        
        self.fields['location'].widget.attrs.update(
            {
                'placeholder': 'eg : Bangladesh',
            }
        )
        self.fields['salary'].widget.attrs.update(
            {
                'placeholder': '$800 - $1200',
            }
        )
        self.fields['last_date'].widget.attrs.update(
            {
                'placeholder': 'YYYY-MM-DD ',
            }
        )        
        self.fields['company_name'].widget.attrs.update(
            {
                'placeholder': 'Company Name',
            }
        )    

    
        last_date = forms.CharField(widget=forms.TextInput(attrs={
                    'placeholder': 'Service Name',
                    'class' : 'datetimepicker1'
                }))

    class Meta:
        model = Job

        fields = [
            "title",
            "location",
            "job_type",
            "salary",
            "description",
            "last_date",
            "company_name",
            "company_description"
            ]

    def clean_job_type(self):
        job_type = self.cleaned_data.get('job_type')

        if not job_type:
            raise forms.ValidationError("Job Type is required")
        return job_type


    def save(self, commit=True):
        job = super(JobEditForm, self).save(commit=False)
      
        if commit:
            job.save()
        return job



class ApplicantStatusForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }


class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['scheduled_date', 'meeting_link', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/xxx-xxxx-xxx'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Interview instructions or notes'
            })
        }
