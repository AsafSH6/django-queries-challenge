# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import Coalesce


class SickPersonsMixin(object):
    """Mixin that responsible fetching sick objects from manager.

    Help us fetching sick persons from each person that is patient model.
    """

    def get_sick_records(self, patient_id_attribute):
        """Get sick objects from current class.

        patient_id_attribute (str): Reference to patient id of current model.

        Example:
            self.get_sick_objects("person__patients_details")
            "person__patients_details" - Points to the current model
            patient id.
        """
        # Extract latest exam.
        latest_exam = \
            MedicalExaminationResult.objects.get_patient_examination_results(
                patient_id=models.OuterRef(patient_id_attribute)
            )[:1]

        # Attach for each record - the latest exam result he got.
        records_with_latest_results = self.annotate(
            latest_result=models.Subquery(latest_exam),
        )

        # Get only results that are not healthy/dead.
        sick_records = records_with_latest_results.filter(
            ~models.Q(latest_result=MedicalExaminationResult.RESULT_HEALTHY) &
            ~models.Q(latest_result=MedicalExaminationResult.RESULT_DEAD)
        )

        return sick_records


# Managers


class PatientManager(models.Manager, SickPersonsMixin):
    """Custom Queryset methods to patient model."""

    def filter_by_examinations_results_options(self, results):
        # Get the patients that have result which appear in results list.
        return self.filter(
            medical_examination_results__result__in=results
        ).distinct()

    def get_highest_num_of_patient_medical_examinations(self):
        # For each patient - attach it's exam count.
        # It possible to count medical_examination_results because it queryset.
        exams_king = self.annotate(
            exam_count=models.Count("medical_examination_results")
        ).order_by("-exam_count").values("exam_count").first()

        return exams_king["exam_count"]

    def get_sick_patients(self):
        return self.get_sick_records(patient_id_attribute="id")

    def filter_by_examined_hospital_workers(self, hospital_workers):
        sick_workers_patients = self.filter(
            medical_examination_results__examined_by__in=hospital_workers
        ).values("id")

        return self.filter(id__in=sick_workers_patients)

    def get_dead_details(self):
        """Get for each patient if he is dead and why."""
        patients = MedicalExaminationResult.objects. \
            get_patient_examination_results(patient_id=models.OuterRef("id"))

        return self.annotate(
            is_dead=models.Subquery(patients[:1]),
            reason_of_dead=models.Subquery(patients[1:2]),
        ).filter(
            is_dead=MedicalExaminationResult.RESULT_DEAD,
            reason_of_dead=MedicalExaminationResult.RESULT_CORONA
        )


class DepartmentManager(models.Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(
            avg_age_of_patients=models.Avg("patients_details__person__age")
        )


class HospitalManager(models.Manager):
    def annotate_by_num_of_hospital_workers_in_risk_of_corona(self):
        # Someone who is in risk group of corona is person that is older
        # than 60
        workers_in_risk = HospitalWorker.objects.filter(
            person__age__gte=60,
            department__hospital=models.OuterRef("id")
        ).values("department__hospital", "id").distinct()

        # Count with risky counter.
        risk_per_hospital = workers_in_risk.annotate(
            risky_count=models.Count("department__hospital")
        ).values("risky_count")

        # Perform group by aggregation with workers in risk count.
        hospitals_with_risk_counter = self.annotate(
            num_of_hospital_workers_in_risk_of_corona=
            models.Subquery(risk_per_hospital,
                            output_field=models.IntegerField())
        )

        return hospitals_with_risk_counter

    def annotate_by_num_of_dead_from_corona(self):
        # Filter all corona dead persons.
        dead_corona_patient_details = Patient.objects.get_dead_details()

        # Annotate with dead corona patients counter.
        hospitals_per_dead_patient = dead_corona_patient_details.filter(
            department__hospital=models.OuterRef("id"),
        ).values(
            "department__hospital"
        ).annotate(
            count=models.Count("id")
        ).values("count")

        hospital_with_corona_dead_details = self.annotate(
            # Coalesce to prevent None values (Take the first non-none value).
            num_of_dead_from_corona=Coalesce(
                models.Subquery(hospitals_per_dead_patient,
                                output_field=
                                models.IntegerField()), 0)
        )

        return hospital_with_corona_dead_details

    def annotate_hospitals_with_time_of_first_corona_sick(self):
        # Filter by parent query id and corona result -> Get the earliest.
        first_corona_time = MedicalExaminationResult.objects.filter(
            patient__department__hospital=models.OuterRef("id"),
            result=MedicalExaminationResult.RESULT_CORONA,
        ).order_by("time").values("time")[:1]

        hospital_with_corona_dead_details = self.annotate(
            first_corona_time=models.Subquery(first_corona_time)
        )

        return hospital_with_corona_dead_details


class HospitalWorkerManager(models.Manager, SickPersonsMixin):
    """Custom hospital worker model Queryset manager."""

    def get_queryset(self):
        # Fetch person (foreign key) in each query.
        return super(HospitalWorkerManager,
                     self).get_queryset().select_related("person")

    def get_worker_performed_most_medical_examinations(self,
                                                       filter_kwargs,
                                                       exclude_kwargs):
        # For each worker - count the amount of exams he performed.
        count_worker_exams = self.annotate(
            count=models.Count("medical_examination_results")
        )

        # Extract the highest value count (best worker).
        best_worker_ever = count_worker_exams.filter(
            **filter_kwargs
        ).exclude(
            **exclude_kwargs
        ).order_by("-count").first()

        return best_worker_ever

    def get_sick_workers(self):
        return self.get_sick_records(patient_id_attribute=
                                     "person__patients_details")


class MedicalExaminationsManager(models.Manager):
    def get_patient_examination_results(self, patient_id):
        return self.filter(
            patient=patient_id
        ).order_by("-time").values("result")


class PersonManager(models.Manager, SickPersonsMixin):
    """Person extra manager functionality."""

    def get_sick_persons(self):
        """Get the sick persons using their patient_id related field."""
        return self.get_sick_records(patient_id_attribute=
                                     "patients_details")

    def persons_with_multiple_jobs(self, jobs=None):
        """Take only persons with multiple jobs that has the given jobs.

        For every person:
           > Filter all conditions and validate it empty
           ===> Not contains different positions (from the given).

           > Annotate which each position in the given jobs.
           > Take only the persons with '1' value on all the positions
           annotations.
           ===> Exactly only given positions.
        """
        not_given_job_condition = models.Q()

        if jobs is not None:
            # Defining the given jobs conditions for matching worker.
            matching_workers_conditions = {
                job: 1 for job in jobs
            }

            # Value for job existence annotation per each person.
            jobs_existence_annotation = {
                job: models.Count(
                    models.Subquery(
                        HospitalWorker.objects.filter(
                            position=job,
                            person=models.OuterRef("person")
                        ).values("position")
                    )
                )
                for job in jobs
            }

            # Make the for detecting person with not given job.
            for job in jobs:
                not_given_job_condition &= ~models.Q(position=job)

            # Search matching workers.
            matching_workers = HospitalWorker.objects.annotate(
                not_matching_jobs=models.Count(
                    models.Subquery(
                        HospitalWorker.objects.filter(
                            not_given_job_condition,
                            person=models.OuterRef("person")
                        ).values("person")
                    )
                ),
                **jobs_existence_annotation
            ).filter(
                # Filter only the workers with 0 not matching jobs.
                not_matching_jobs=0,
                **matching_workers_conditions
            ).values("person")

        else:
            # All of the workers are in potential matching workers.
            matching_workers = HospitalWorker.objects.all().values("person")

        multiple_jobs_workers = HospitalWorker.objects.filter(
            person__in=matching_workers
        ).values(
            "person", "position", "department"
        ).annotate(
            jobs=models.Count("person")
        ).filter(
            jobs__gte=2,
        ).values("person")

        return self.filter(
            id__in=multiple_jobs_workers
        )


# Models


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

    objects = DepartmentManager()

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

    objects = PersonManager()

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
    result = models.CharField(max_length=255, blank=False, null=False,
                              choices=(
                                  (RESULT_HEALTHY, RESULT_HEALTHY),
                                  (RESULT_CORONA, RESULT_CORONA),
                                  (RESULT_BOT, RESULT_BOT),
                                  (RESULT_DEAD, RESULT_DEAD),
                              ))

    objects = MedicalExaminationsManager()

    def __repr__(self):
        return '<Medical examination result of {patient}, examined_by {examined_by}>'.format(
            patient=self.patient,
            examined_by=self.examined_by,
        )

    def __unicode__(self):
        return repr(self)
