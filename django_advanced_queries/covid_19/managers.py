from django.db import models
from django.db.models import Max, Count, Avg


class DepartmentManager(models.Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(avg_age_of_patients = Avg('patients_details__person__age'))


class HospitalWorkerManager(models.Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs, exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(pref_exams = Count('medical_examination_results')).order_by('-pref_exams')[0] 


class PatientManager(models.Manager):
    def filter_by_examination_results(self, results):
        return self.filter(medical_examination_results__result__in=results)

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(exam_res_count = Count('medical_examination_results')).aggregate(max_exam_res = Max('exam_res_count'))['max_exam_res']