from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from collections import defaultdict
import random

POPULATION_SIZE = 30
NUMB_OF_ELITE_SCHEDULES = 2
TOURNAMENT_SELECTION_SIZE = 8
MUTATION_RATE = 0.05
VARS = {'generationNum': 0,
        'terminateGens': False}


class Population:
    def __init__(self, size):
        self._size = size
        self._data = data
        self._schedules = [Schedule().initialize() for i in range(size)]

    def getSchedules(self):
        return self._schedules


class Data:
    def __init__(self):
        self._rooms = Room.objects.all()
        self._meetingTimes = MeetingTime.objects.all()
        self._instructors = Instructor.objects.all()
        self._courses = Course.objects.all()
        self._depts = Department.objects.all()
        self._sections = Section.objects.all()

    def get_rooms(self):
        return self._rooms

    def get_instructors(self):
        return self._instructors

    def get_courses(self):
        return self._courses

    def get_depts(self):
        return self._depts

    def get_meetingTimes(self):
        return self._meetingTimes

    def get_sections(self):
        return self._sections


class Class:
    def __init__(self, dept, section, course):
        self.department = dept
        self.course = course
        self.instructor = None
        self.meeting_time = None
        self.room = None
        self.section = section

    def get_id(self):
        return self.section_id

    def get_dept(self):
        return self.department

    def get_course(self):
        return self.course

    def get_instructor(self):
        return self.instructor

    def get_meetingTime(self):
        return self.meeting_time

    def get_room(self):
        return self.room

    def set_instructor(self, instructor):
        self.instructor = instructor

    def set_meetingTime(self, meetingTime):
        self.meeting_time = meetingTime

    def set_room(self, room):
        self.room = room


class Schedule:
    def __init__(self):
        self._data = data
        self._classes = []
        self._numberOfConflicts = 0
        self._fitness = -1
        self._isFitnessChanged = True

    def getClasses(self):
        self._isFitnessChanged = True
        return self._classes

    def getNumbOfConflicts(self):
        return self._numberOfConflicts

    def getFitness(self):
        if self._isFitnessChanged:
            self._fitness = self.calculateFitness()
            self._isFitnessChanged = False
        return self._fitness

    def addCourse(self, data, course, courses, dept, section):
        newClass = Class(dept, section.section_id, course)

        available_meeting_times = list(data.get_meetingTimes())
        
        for existing_class in self._classes:
            if existing_class.meeting_time in available_meeting_times:
                available_meeting_times.remove(existing_class.meeting_time)

        if available_meeting_times:
            newClass.set_meetingTime(available_meeting_times[random.randrange(0, len(available_meeting_times))])
        else:
            newClass.set_meetingTime(data.get_meetingTimes()[random.randrange(0, len(data.get_meetingTimes()))])


        available_rooms = list(data.get_rooms())
        for existing_class in self._classes:
            if existing_class.meeting_time == newClass.meeting_time:
                if existing_class.room in available_rooms:
                    available_rooms.remove(existing_class.room)

        if available_rooms:
            newClass.set_room(available_rooms[random.randrange(0, len(available_rooms))])
        else:
            newClass.set_room(data.get_rooms()[random.randrange(0, len(data.get_rooms()))])

        crs_inst = course.instructors.all()
        newClass.set_instructor(
            crs_inst[random.randrange(0, len(crs_inst))])

        self._classes.append(newClass)

    def initialize(self):
        sections = Section.objects.all()
        for section in sections:
            dept = section.department
            n = section.num_class_in_week()

            if n > len(data.get_meetingTimes()):
                n = len(data.get_meetingTimes())

            courses = dept.courses.all()
            for course in courses:
                for i in range(n // len(courses)):
                    self.addCourse(data, course, courses, dept, section)

            for course in courses.order_by('?')[:(n % len(courses))]:
                self.addCourse(data, course, courses, dept, section)

        return self

    def calculateFitness(self):
        self._numberOfConflicts = 0
        classes = self.getClasses()

        for i in range(len(classes)):
            # Seating capacity less them course student
            if classes[i].room.seating_capacity < int(classes[i].course.max_numb_students):
                self._numberOfConflicts += 1

            # print(classes[i].course.course_name, classes[i].meeting_time, classes[i].section, classes[i].room, classes[i].instructor)

            for j in range(i + 1, len(classes)):
                # Same course on same day
                if (classes[i].course.course_name == classes[j].course.course_name and \
                    str(classes[i].meeting_time).split()[1] == str(classes[j].meeting_time).split()[1]):
                    self._numberOfConflicts += 1

                # Teacher with lectures in different timetable at same time
                if (classes[i].section != classes[j].section and \
                    classes[i].meeting_time == classes[j].meeting_time and \
                    classes[i].instructor == classes[j].instructor):
                    self._numberOfConflicts += 1

                # Duplicate time in a department
                if (classes[i].section == classes[j].section and \
                    classes[i].meeting_time == classes[j].meeting_time):
                    self._numberOfConflicts += 1

                 # Room conflict
                if (classes[i].meeting_time == classes[j].meeting_time and \
                    classes[i].room == classes[j].room):
                    self._numberOfConflicts += 1
        return 1 / (self._numberOfConflicts + 1)

import random

class GeneticAlgorithm:
    def evolve(self, population):
        """Evolve the population by performing crossover and mutation."""
        return self._mutate_population(self._crossover_population(population))

    def _crossover_population(self, population):
        """Perform crossover to produce a new population."""
        crossover_population = Population(0)
        schedules = population.getSchedules()

        # Retain elite schedules
        crossover_population.getSchedules().extend(schedules[:NUMB_OF_ELITE_SCHEDULES])

        # Perform crossover for the rest of the population
        for _ in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            schedule_x = self._tournament_population(population)
            schedule_y = self._tournament_population(population)
            crossover_population.getSchedules().append(
                self._crossover_schedule(schedule_x, schedule_y)
            )
        return crossover_population

    def _mutate_population(self, population):
        """Apply mutation to the population."""
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.getSchedules()[i])
        return population

    def _crossover_schedule(self, schedule_x, schedule_y):
        """Perform single-point crossover between two schedules."""
        crossover_schedule = Schedule().initialize()
        classes = crossover_schedule.getClasses()
        x_classes = schedule_x.getClasses()
        y_classes = schedule_y.getClasses()

        for i in range(len(classes)):
            classes[i] = x_classes[i] if random.random() > 0.5 else y_classes[i]
        return crossover_schedule

    def _mutate_schedule(self, mutate_schedule):
        """Mutate the given schedule based on mutation rate."""
        new_schedule = Schedule().initialize()
        mutate_classes = mutate_schedule.getClasses()
        new_classes = new_schedule.getClasses()

        for i in range(len(mutate_classes)):
            if random.random() < MUTATION_RATE:
                mutate_classes[i] = new_classes[i]

    def _tournament_population(self, population):
        """Select the best schedule from a tournament subset."""
        schedules = random.sample(population.getSchedules(), TOURNAMENT_SELECTION_SIZE)
        return max(schedules, key=lambda x: x.getFitness())


def context_manager(schedule):
    classes = schedule.getClasses()
    context = []
    for i in range(len(classes)):
        clas = {}
        clas['section'] = classes[i].section_id
        clas['dept'] = classes[i].department.dept_name
        clas['course'] = f'{classes[i].course.course_name} ({classes[i].course.course_number} {classes[i].course.max_numb_students})'
        clas['room'] = f'{classes[i].room.r_number} ({classes[i].room.seating_capacity})'
        clas['instructor'] = f'{classes[i].instructor.name} ({classes[i].instructor.uid})'
        clas['meeting_time'] = [
            classes[i].meeting_time.pid,
            classes[i].meeting_time.day,
            classes[i].meeting_time.time
        ]
        context.append(clas)
    return context


def apiGenNum(request):
    return JsonResponse({'genNum': VARS['generationNum']})

def apiterminateGens(request):
    VARS['terminateGens'] = True
    return redirect('home')



#@login_required
def timetable(request):
    global data
    data = Data()
    population = Population(POPULATION_SIZE)
    VARS['generationNum'] = 0
    VARS['terminateGens'] = False
    population.getSchedules().sort(key=lambda x: x.getFitness(), reverse=True)
    geneticAlgorithm = GeneticAlgorithm()
    schedule = population.getSchedules()[0]

    while (schedule.getFitness() != 1.0) and (VARS['generationNum'] < 100):
        if VARS['terminateGens']:
            return HttpResponse('')

        population = geneticAlgorithm.evolve(population)
        population.getSchedules().sort(key=lambda x: x.getFitness(), reverse=True)
        schedule = population.getSchedules()[0]
        VARS['generationNum'] += 1
    return render(
        request, 'timetable.html', {
            'schedule': schedule.getClasses(),
            'sections': data.get_sections(),
            'times': data.get_meetingTimes(),
            'timeSlots': TIME_SLOTS,
            'weekDays': DAYS_OF_WEEK
        })


'''
Page Views
'''

def home(request):
    return render(request, 'index.html', {})


#@login_required
def instructorAdd(request):
    form = InstructorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('instructorAdd')
    context = {'form': form}
    return render(request, 'instructorAdd.html', context)


#@login_required
def instructorEdit(request):
    context = {'instructors': Instructor.objects.all()}
    return render(request, 'instructorEdit.html', context)


#@login_required
def instructorDelete(request, pk):
    inst = Instructor.objects.filter(pk=pk)
    if request.method == 'POST':
        inst.delete()
        return redirect('instructorEdit')


#@login_required
def roomAdd(request):
    form = RoomForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('roomAdd')
    context = {'form': form}
    return render(request, 'roomAdd.html', context)


#@login_required
def roomEdit(request):
    context = {'rooms': Room.objects.all()}
    return render(request, 'roomEdit.html', context)


#@login_required
def roomDelete(request, pk):
    rm = Room.objects.filter(pk=pk)
    if request.method == 'POST':
        rm.delete()
        return redirect('roomEdit')


#@login_required
def meetingTimeAdd(request):
    form = MeetingTimeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('meetingTimeAdd')
        else:
            print('Invalid')
    context = {'form': form}
    return render(request, 'meetingTimeAdd.html', context)


#@login_required
def meetingTimeEdit(request):
    context = {'meeting_times': MeetingTime.objects.all()}
    return render(request, 'meetingTimeEdit.html', context)


#@login_required
def meetingTimeDelete(request, pk):
    mt = MeetingTime.objects.filter(pk=pk)
    if request.method == 'POST':
        mt.delete()
        return redirect('meetingTimeEdit')


#@login_required
def courseAdd(request):
    form = CourseForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('courseAdd')
        else:
            print('Invalid')
    context = {'form': form}
    return render(request, 'courseAdd.html', context)


#@login_required
def courseEdit(request):
    instructor = defaultdict(list)
    for course in Course.instructors.through.objects.all():
        course_number = course.course_id
        instructor_name = Instructor.objects.filter(
            id=course.instructor_id).values('name')[0]['name']
        instructor[course_number].append(instructor_name)

    context = {'courses': Course.objects.all(), 'instructor': instructor}
    return render(request, 'courseEdit.html', context)


#@login_required
def courseDelete(request, pk):
    crs = Course.objects.filter(pk=pk)
    if request.method == 'POST':
        crs.delete()
        return redirect('courseEdit')


#@login_required
def departmentAdd(request):
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('departmentAdd')
    context = {'form': form}
    return render(request, 'departmentAdd.html', context)


#@login_required
def departmentEdit(request):
    course = defaultdict(list)
    for dept in Department.courses.through.objects.all():
        dept_name = Department.objects.filter(
            id=dept.department_id).values('dept_name')[0]['dept_name']
        course_name = Course.objects.filter(
            course_number=dept.course_id).values(
                'course_name')[0]['course_name']
        course[dept_name].append(course_name)

    context = {'departments': Department.objects.all(), 'course': course}
    return render(request, 'departmentEdit.html', context)


#@login_required
def departmentDelete(request, pk):
    dept = Department.objects.filter(pk=pk)
    if request.method == 'POST':
        dept.delete()
        return redirect('departmentEdit')


#@login_required
def sectionAdd(request):
    form = SectionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('sectionAdd')
    context = {'form': form}
    return render(request, 'sectionAdd.html', context)


#@login_required
def sectionEdit(request):
    context = {'sections': Section.objects.all()}
    return render(request, 'sectionEdit.html', context)


#@login_required
def sectionDelete(request, pk):
    sec = Section.objects.filter(pk=pk)
    if request.method == 'POST':
        sec.delete()
        return redirect('sectionEdit')




'''
Error pages
'''

def error_404(request, exception):
    return render(request,'errors/404.html', {})

def error_500(request, *args, **argv):
    return render(request,'errors/500.html', {})
