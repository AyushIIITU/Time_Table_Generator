from django.forms import ModelForm
from .models import *
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'UserName',
            'id': 'id_username'
        }))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
            'placeholder': 'Password',
            'id': 'id_password',
        }))


class RoomForm(ModelForm):
    class Meta:
        model = Room
        labels = {'r_number': 'Room Number'}
        fields = ['r_number', 'seating_capacity', 'is_lab', 'associated_courses']
    def clean_r_number(self):
        r_number = self.cleaned_data.get('r_number')
        if Room.objects.filter(r_number=r_number).exists():
            raise forms.ValidationError("Room number must be unique.")
        return r_number

class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        labels = {'uid': 'Instructor ID', 'name': 'Instructor Name'}
        fields = ['uid', 'name']


class MeetingTimeForm(ModelForm):
    class Meta:
        model = MeetingTime
        fields = ['pid', 'time', 'day']
        widgets = {
            'pid': forms.TextInput(),
            'time': forms.Select(),
            'day': forms.Select(),
        }


class CourseForm(ModelForm):
    class Meta:
        model = Course
        labels = {
            'course_name': 'Course Name',
            'course_number': 'Course Number',
            'max_numb_students': 'Max Number of Students',
            'instructors': 'Instructors',
            'number_of_lectures': 'Number of Lectures',
            'number_of_labs': 'Number of Labs',
            'number_of_tutorials': 'Number of Tutorials',
        }
        fields = ['course_number', 'course_name','max_numb_students', 'instructors', 'number_of_lectures', 'number_of_labs', 'number_of_tutorials']
class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        labels = {'dept_name': 'Department name'}
        fields = ['dept_name', 'courses']


class SectionForm(ModelForm):
    class Meta:
        model = Section
        labels = {'num_class_in_week': 'Total classes in a week'}
        fields = ['section_id', 'department']
