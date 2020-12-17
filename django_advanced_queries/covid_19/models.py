# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Count, Max, OuterRef, Subquery, Q


class Hospital(models.Model):
    name = models.CharField(db_index=True, max_length=255, blank=False,
                            null=False, )
    city = models.CharField(max_length=255, blank=False, null=False, )

    def __repr__(self):
        return '<Hospital {name}>'.format(name=self.name, )

    def __unicode__(self):
        return repr(self)


class Department(models.Model):
    name = models.CharField(db_index=True, max_length=255, blank=False,
                            null=False, )
    hospital = models.ForeignKey(
        to=Hospital,
        related_name='departments',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    def __repr__(self):
        return '<Department {department_name} in hospital {hospital}>'.format(
            department_name=self.name,
            hospital=self.hospital,
        )

    def __unicode__(self):
        return repr(self)


class PersonManager(models.Manager):
    def get_sick_persons(self):
        results_subquery = MedicalExaminationResult.objects.filter(
            patient__person=OuterRef('pk')).order_by('-time')

        return self.annotate(
            last_result=Subquery(
                results_subquery.values('result')[:1])).exclude(
            last_result__in=[MedicalExaminationResult.RESULT_DEAD,
                             MedicalExaminationResult.RESULT_HEALTHY])

    def persons_with_multiple_jobs(self, jobs=[]):
        jobs_filter = {'hospital_jobs__position': job for job in jobs}
        count_positions_filter = {} if len(jobs) == 0 else {
            'count_positions': len(jobs)}

        return self.annotate(count_positions=Count('hospital_jobs__position',
                                                   distinct=True)).filter(
            **jobs_filter).annotate(
            count_jobs=Count('hospital_jobs')).filter(
            count_jobs__gt=1, **count_positions_filter)


class Person(models.Model):
    GENDER_MALE = 'Male'
    GENDER_FEMALE = 'Female'
    GENDER_UNDEFINED = 'Other'

    name = models.CharField(db_index=True, max_length=255, blank=False,
                            null=False)
    age = models.PositiveSmallIntegerField(null=False)
    gender = models.CharField(max_length=6, blank=False, null=False, choices=(
        (GENDER_MALE, GENDER_MALE),
        (GENDER_FEMALE, GENDER_FEMALE),
        (GENDER_UNDEFINED, GENDER_UNDEFINED),
    ))

    objects = PersonManager()

    def __repr__(self):
        return '<Person {name} age {age}>'.format(name=self.name, age=self.age)

    def __unicode__(self):
        return repr(self)


class HospitalWorkerManager(models.Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs,
                                                       exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(
            examination_count=Count(
                'medical_examination_results')).order_by(
            '-examination_count').first()


class HospitalWorker(models.Model):
    POSITION_DOCTOR = 'Doctor'
    POSITION_NURSE = 'Nurse'

    person = models.ForeignKey(
        to=Person,
        related_name='hospital_jobs',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        to=Department,
        related_name='hospital_workers',
        null=False,
        on_delete=models.CASCADE,
    )
    position = models.CharField(max_length=255, blank=False, null=False,
                                choices=(
                                    (POSITION_DOCTOR, POSITION_DOCTOR),
                                    (POSITION_NURSE, POSITION_NURSE),
                                ))

    objects = HospitalWorkerManager()

    def __repr__(self):
        return '<Hospital worker {person}, working in {department} position {position}>'.format(
            person=self.person,
            department=self.department,
            position=self.position,
        )

    def __unicode__(self):
        return repr(self)


class PatientManager(models.Manager):
    def filter_by_examinations_results_options(self, results):
        return self.filter(
            medical_examination_results__result__in=results).distinct()

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(results=Count(
            'medical_examination_results')).aggregate(
            max_results=Max('results'))['max_results']


class Patient(models.Model):
    person = models.ForeignKey(
        to=Person,
        related_name='patients_details',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        to=Department,
        related_name='patients_details',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    objects = PatientManager()

    def __repr__(self):
        return '<Patient {person} in {department}>'.format(
            person=self.person,
            department=self.department
        )

    def __unicode__(self):
        return repr(self)


class MedicalExaminationResult(models.Model):
    RESULT_HEALTHY = 'Healthy'
    RESULT_CORONA = 'Corona'
    RESULT_BOT = 'Botism'
    RESULT_DEAD = 'Dead'

    time = models.DateTimeField(auto_now=False, auto_now_add=False, )
    examined_by = models.ForeignKey(
        to=HospitalWorker,
        related_name='medical_examination_results',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    patient = models.ForeignKey(
        to=Patient,
        related_name='medical_examination_results',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    result = models.CharField(max_length=255, blank=False, null=False, choices=(
        (RESULT_HEALTHY, RESULT_HEALTHY),
        (RESULT_CORONA, RESULT_CORONA),
        (RESULT_BOT, RESULT_BOT),
        (RESULT_DEAD, RESULT_DEAD),
    ))

    def __repr__(self):
        return '<Medical examination result of {patient}, examined_by {examined_by}>'.format(
            patient=self.patient,
            examined_by=self.examined_by,
        )

    def __unicode__(self):
        return repr(self)
