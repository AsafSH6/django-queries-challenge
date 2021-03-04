# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class SickPersonsMixin:
    """Mixin that responsible fetching sick objects from manager."""

    def get_sick_records(self, patient_id_attribute):
        """Get sick objects from current class.

        patient_id_attribute (str): Reference to patient id of current model.

        Example:
            self.get_sick_objects("person__patients_details__id")
            "person__patients_details__id" - Points to the current model
            patient id.
        """
        # Extract latest exam.
        latest_exam = MedicalExaminationResult.objects.filter(
            patient__id=models.OuterRef(patient_id_attribute)
        ).order_by('-time').values("result")

        # Attach for each record - the latest exam result he got.
        records_with_latest_results = self.annotate(
            latest_result=models.Subquery(latest_exam[:1]),
        )

        # Get only results that are not healthy/dead.
        sick_records = records_with_latest_results.filter(
            ~models.Q(latest_result=MedicalExaminationResult.RESULT_HEALTHY) &
            ~models.Q(latest_result=MedicalExaminationResult.RESULT_DEAD)
        )

        return sick_records


class PatientQuerySet(models.QuerySet, SickPersonsMixin):
    """Custom Queryset methods to patient model."""

    def filter_by_examinations_results_options(self, results):
        # Get matching patients ids.
        patients_with_matching_examinations = \
            MedicalExaminationResult.objects.filter(
                result__in=results
            ).values_list("patient", flat=True)

        # Filter those ids from patients table.
        return self.filter(
            id__in=models.Subquery(patients_with_matching_examinations)
        )

    def get_highest_num_of_patient_medical_examinations(self):
        exams = MedicalExaminationResult.objects.filter(
            patient_id=models.OuterRef("id")
        ).values("patient_id")

        # For each exam - attach it's patient's occurrences count.
        count_exams_for_patient = exams.annotate(
            count=models.Count("patient_id")
        ).values("count")

        # For each patient - attach it's exam count.
        exams_king = self.annotate(
            exam_count=models.Subquery(count_exams_for_patient)
        ).order_by("-exam_count").values("exam_count").first()

        return exams_king["exam_count"]

    def get_sick_patients(self):
        return self.get_sick_records(patient_id_attribute="id")

    def filter_by_examined_hospital_workers(self, hospital_workers):
        # TODO: Add hospital workers.
        # TODO: Check it 1 query.
        sick_workers = HospitalWorker.objects.get_sick_workers().values("id")
        sick_workers_patients = MedicalExaminationResult.objects.filter(
            examined_by__in=sick_workers
        ).values("patient__id")
        return self.filter(id__in=sick_workers_patients)


class DepartmentQuerySet(models.QuerySet):
    def annotate_avg_age_of_patients(self):
        return self.annotate(
            avg_age_of_patients=models.Avg("patients_details__person__age")
        )


class HospitalManager(models.Manager):
    def get_queryset(self):
        # Load departments once.
        return super(HospitalManager,
                     self).get_queryset().prefetch_related("departments")


class HospitalWorkerManager(models.Manager, SickPersonsMixin):
    """Custom hospital worker model Queryset manager."""

    def get_queryset(self):
        # Fetch person (foreign key) in each query.
        return super(HospitalWorkerManager,
                     self).get_queryset().select_related("person")

    def get_worker_performed_most_medical_examinations(self,
                                                       filter_kwargs,
                                                       exclude_kwargs):
        # TODO: Figure out what is exclude_kwargs aim?

        # Get specific worker exams.
        filter_worker_exams = MedicalExaminationResult.objects.filter(
            examined_by__id=models.OuterRef("id")
        ).values("examined_by__id")

        # For each worker - count the amount of exams he performed.
        count_worker_exams = filter_worker_exams.annotate(
            count=models.Count("examined_by__id")
        ).values("count")  # Extract only count field (Subquery).

        # Attach the count values to the workers.
        exams_performed_annotation = self.annotate(
            count=models.Subquery(count_worker_exams)
        )

        # Extract the highest value count (best worker).
        best_worker_ever = exams_performed_annotation.filter(
            **filter_kwargs
        ).order_by("-count").first()

        return best_worker_ever

    def get_sick_workers(self):
        return self.get_sick_records(patient_id_attribute=
                                     "person__patients_details__id")


class PersonQuerySet(models.QuerySet, SickPersonsMixin):
    """Person extra queryset functionality."""

    def get_sick_persons(self):
        return self.get_sick_records(patient_id_attribute=
                                     "patients_details__id")


#################### MODELS ###############################


class Hospital(models.Model):
    name = models.CharField(db_index=True, max_length=255, blank=False,
                            null=False, )
    city = models.CharField(max_length=255, blank=False, null=False, )

    objects = HospitalManager()

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

    objects = DepartmentQuerySet.as_manager()

    def __repr__(self):
        return '<Department {department_name} in hospital {hospital}>'.format(
            department_name=self.name,
            hospital=self.hospital,
        )

    def __unicode__(self):
        return repr(self)


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

    objects = PersonQuerySet.as_manager()

    def __repr__(self):
        return '<Person {name} age {age}>'.format(name=self.name, age=self.age)

    def __unicode__(self):
        return repr(self)


class HospitalWorker(models.Model):
    POSITION_DOCTOR = 'Doctor'
    POSITION_NURSE = 'Nurse'

    objects = HospitalWorkerManager()

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

    def __repr__(self):
        return '<Hospital worker {person}, working in {department} position {position}>'.format(
            person=self.person,
            department=self.department,
            position=self.position,
        )

    def __unicode__(self):
        return repr(self)


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

    objects = PatientQuerySet.as_manager()

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
    result = models.CharField(max_length=255, blank=False, null=False,
                              choices=(
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
