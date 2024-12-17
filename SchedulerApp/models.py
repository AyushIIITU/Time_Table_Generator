from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete


TIME_SLOTS = (
    ('9:00 - 9:50'  , '9:00 - 9:50'),
    ('9:50 - 10:40', '9:50 - 10:40'),
    ('11:00 - 11:50', '11:00 - 11:50'),
    ('11:50 - 12:40', '11:50 - 12:40'),
    ('14:00 - 14:50', '14:00 - 14:50'),
    ('14:50 - 15:40', '14:50 - 15:40'),
    ('15:40 - 16:30', '15:40 - 16:30'),
    ('16:30 - 17:20', '16:30 - 17:20'),
)

# TIME_SLOTS = (
#     ('9:30 - 10:30', '9:30 - 10:30'),
#     ('10:30 - 11:30', '10:30 - 11:30'),
#     ('11:30 - 12:30', '11:30 - 12:30'),
#     ('12:30 - 1:30', '12:30 - 1:30'),
#     ('2:30 - 3:30', '2:30 - 3:30'),
#     ('3:30 - 4:30', '3:30 - 4:30'),
#     ('4:30 - 5:30', '4:30 - 5:30'),
# )

DAYS_OF_WEEK = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
)
    # ('Saturday', 'Saturday'),


class Room(models.Model):
    r_number = models.CharField(max_length=66, unique=True)
    seating_capacity = models.IntegerField(default=0)
    is_lab = models.BooleanField(default=False)
    associated_courses = models.ManyToManyField('Course', blank=True)

    def __str__(self):
        return self.r_number


class Instructor(models.Model):
    uid = models.CharField(max_length=6)
    name = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.uid} {self.name}'


class MeetingTime(models.Model):
    pid = models.CharField(max_length=4, primary_key=True)
    time = models.CharField(max_length=50,
                            choices=TIME_SLOTS,
                            default='11:30 - 12:30')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'{self.pid} {self.day} {self.time}'
    
    def is_continuous_with(self, other):
        # Assuming TIME_SLOTS are ordered and continuous
        time_slots = [slot[0] for slot in TIME_SLOTS]
        current_index = time_slots.index(self.time)
        next_index = (current_index + 1) % len(time_slots)
        return self.day == other.day and time_slots[next_index] == other.time

class Course(models.Model):
    course_number = models.CharField(max_length=5, primary_key=True)
    course_name = models.CharField(max_length=40)
    max_numb_students = models.CharField(max_length=65)
    instructors = models.ManyToManyField(Instructor)
    number_of_tutorials = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    number_of_lectures = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    number_of_labs = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f'{self.course_number} {self.course_name}'


class Department(models.Model):
    dept_name = models.CharField(max_length=50)
    courses = models.ManyToManyField(Course)

    @property
    def get_courses(self):
        return self.courses

    def __str__(self):
        return self.dept_name


class Section(models.Model):
    section_id = models.CharField(max_length=25, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    #num_class_in_week = models.IntegerField(default=0)
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    meeting_time = models.ForeignKey(MeetingTime,
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True)
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    instructor = models.ForeignKey(Instructor,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True)

    def set_room(self, room):
        section = Section.objects.get(pk=self.section_id)
        section.room = room
        section.save()

    def set_meetingTime(self, meetingTime):
        section = Section.objects.get(pk=self.section_id)
        section.meeting_time = meetingTime
        section.save()

    def set_instructor(self, instructor):
        section = Section.objects.get(pk=self.section_id)
        section.instructor = instructor
        section.save()
    def num_class_in_week(self):
        total_lectures = 0
        total_tutorials = 0
        for course in self.department.courses.all():
            total_lectures += course.number_of_lectures
            total_tutorials += course.number_of_tutorials
        return total_lectures + total_tutorials
    
    def num_labs_in_week(self):
        total_labs = 0
        for course in self.department.courses.all():
            total_labs += course.number_of_labs
        return total_labs

    def is_valid_lab_start_time(self, meeting_time):
        invalid_start_times = [2, 4]
        return meeting_time.pid[-1] not in invalid_start_times
    
    def are_consecutive_meeting_times(self, mt1, mt2):
        return mt1.pid[0] == mt2.pid[0] and abs(int(mt1.pid[-1]) - int(mt2.pid[-1])) == 1

'''
class Data(models.Manager):
    def __init__(self):
        self._rooms = Room.objects.all()
        self._meetingTimes = MeetingTime.objects.all()
        self._instructors = Instructor.objects.all()
        self._courses = Course.objects.all()
        self._depts = Department.objects.all()

    def get_rooms(self): return self._rooms

    def get_instructors(self): return self._instructors

    def get_courses(self): return self._courses

    def get_depts(self): return self._depts

    def get_meetingTimes(self): return self._meetingTimes

    def get_numberOfClasses(self): return self._numberOfClasses

'''
