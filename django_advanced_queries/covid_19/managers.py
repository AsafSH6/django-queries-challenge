from django.db.models import Manager, Max, Count, Avg


class DepartmentManager(Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(avg_age_of_patients=Avg('patients_details__person__age'))


class HospitalWorkerManager(Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs, exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(
            num_pref_exams=Count('medical_examination_results')
        ).order_by('-num_pref_exams').first()


class PatientManager(Manager):
    def filter_by_examination_results(self, results):
        return self.filter(medical_examination_results__result__in=results)

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(
            num_of_patient_medical_examinations=Count('medical_examination_results')
            ).aggregate(
                highest_num_of_patient_medical_examinations=Max('num_of_patient_medical_examinations')
            )['highest_num_of_patient_medical_examinations']