from django.db import models
from django.db.models import Count, Max, Avg, Subquery, OuterRef


class PatientManager(models.Manager):
    def filter_by_examinations_results_options(self, results, *args, **kwargs):
        return self.filter(medical_examination_results__result__in=results, *args, **kwargs).distinct()

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(Count('medical_examination_results')).aggregate(
            Max('medical_examination_results__count')
        )['medical_examination_results__count__max']

    def filter_by_examined_hospital_workers(self, hospital_workers, *args, **kwargs):
        return self.filter(medical_examination_results__examined_by__in=hospital_workers, *args, **kwargs).distinct()


class DepartmentManager(models.Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(avg_age_of_patients=Avg('patients_details__person__age'))


class PersonManager(models.Manager):
    def get_sick_persons(self):
        from django_advanced_queries.covid_19.models import MedicalExaminationResult
        exams = MedicalExaminationResult.objects.all()
        return self.annotate(latest_exam_result=Subquery(exams.filter(patient__person=OuterRef('pk')).order_by('-time').values('result')))\
            .exclude(latest_exam_result__in=(MedicalExaminationResult.RESULT_HEALTHY, MedicalExaminationResult.RESULT_DEAD))


class HospitalWorkerManager(models.Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs, exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(Count('medical_examination_results'))\
            .order_by('-medical_examination_results__count').first()

    def get_sick_workers(self):
        from django_advanced_queries.covid_19.models import Person
        sick_persons = Person.objects.get_sick_persons()
        return self.filter(person__in=sick_persons)
