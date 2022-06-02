from django.db import models
from django.db.models import Avg, Count, OuterRef, Subquery


class DepartmentManager(models.Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(avg_age_of_patients=Avg('patients_details__person__age'))


class HospitalWorkerManager(models.Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs, exclude_kwargs):
        return self.annotate(m_e_count=Count('medical_examination_results'))\
            .filter(**filter_kwargs)\
            .exclude(**exclude_kwargs)\
            .order_by('-m_e_count')\
            .first()

    def get_sick_workers(self):
        from django_advanced_queries.covid_19.models import Person

        sick_persons = Person.objects.get_sick_persons()
        return self.filter(person__in=sick_persons.all())


class PatientManager(models.Manager):
    def filter_by_examinations_results_options(self, results, **kwargs):
        return self.filter(medical_examination_results__result__in=results, **kwargs).distinct()

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(m_e_count=Count('medical_examination_results'))\
            .order_by('-m_e_count')\
            .first()\
            .m_e_count

    def filter_by_examined_hospital_workers(self, hospital_workers, **kwargs):
        return self.filter(medical_examination_results__examined_by__in=hospital_workers, **kwargs).distinct()


class PersonManager(models.Manager):
    # taken from Asaf's solution
    def get_sick_persons(self):
        from django_advanced_queries.covid_19.models import MedicalExaminationResult

        chronological_results = MedicalExaminationResult.objects\
            .filter(patient__person=OuterRef('pk'))\
            .order_by('-time')
        return self.exclude(patients_details__isnull=True)\
            .annotate(last_m_e=Subquery(chronological_results.values('result')[:1]))\
            .exclude(last_m_e__in=(MedicalExaminationResult.RESULT_DEAD, MedicalExaminationResult.RESULT_HEALTHY))
