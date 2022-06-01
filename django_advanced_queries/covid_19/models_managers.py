from django.db import models
from django.db.models import Avg, Count, Case, When, Q, Value


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


class PatientManager(models.Manager):
    def filter_by_examinations_results_options(self, results, **kwargs):
        return self.filter(medical_examination_results__result__in=results, **kwargs).distinct()

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(m_e_count=Count('medical_examination_results'))\
            .order_by('-m_e_count')\
            .first()\
            .m_e_count
