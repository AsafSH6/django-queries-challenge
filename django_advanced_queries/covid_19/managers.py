from django.db.models import Manager, IntegerField, Max, Count, Avg, F, Case, When, OuterRef, Sum, Subquery


class HospitalManager(Manager):
    def annotate_by_num_of_hospital_workers_in_risk_of_corona(self):
        return self.annotate(
            num_of_hospital_workers_in_risk_of_corona=Count(
                Case(
                    When(departments__hospital_workers__person__age__gte=60, then=1),
                    output_field=IntegerField
                ),
                distinct=True
            )
        )

    def get_patients_that_died_from_a_reason(self, reason):
        from django_advanced_queries.covid_19.models import Patient, MedicalExaminationResult
        med_exams_res = MedicalExaminationResult.objects.filter(patient=OuterRef('pk')).order_by('-time').values('result')

        return Patient.objects.filter(department__hospital=OuterRef('pk')).annotate(
            last_exam_res=Subquery(med_exams_res[0:])
        ).filter(last_exam_res='Dead').annotate(
            death_reason=Subquery(med_exams_res[1:])
        ).filter(death_reason=reason)
    
    def annotate_by_num_of_dead_from_corona(self):
        patients = self.get_patients_that_died_from_a_reason('Corona')
        return self.annotate(
            num_of_dead_from_corona=Sum(
                Case(
                    When(
                        departments__patients_details__in=Subquery(patients.values('id')),
                        then=1
                    ),
                    output_field=IntegerField(),
                    default=0)
                )
            )

    def get_hospitals_with_min_amount_of_dead_from_corona(self, min_dead):
        return self.annotate_by_num_of_dead_from_corona().filter(num_of_dead_from_corona__gte=min_dead)


class DepartmentManager(Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(avg_age_of_patients=Avg('patients_details__person__age'))


class HospitalWorkerManager(Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs, exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(
            num_pref_exams=Count('medical_examination_results')
        ).order_by('-num_pref_exams').first()

    def get_sick_workers(self):
        from django_advanced_queries.covid_19.models import Person
        return self.filter(person__in=Person.objects.get_sick_persons())


class PatientManager(Manager):
    def filter_by_examination_results(self, results, *args, **kwargs):
        return self.filter(medical_examination_results__result__in=results, *args, **kwargs)

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(
                num_of_patient_medical_examinations=Count('medical_examination_results')
                ).aggregate(
                    highest_num_of_patient_medical_examinations=Max('num_of_patient_medical_examinations')
                )['highest_num_of_patient_medical_examinations']

    def filter_by_examined_hospital_workers(self, hospital_workers):
        return self.filter(
            medical_examination_results__examined_by__in=hospital_workers
        ).distinct()

class PersonManager(Manager):
    def get_sick_persons(self):
        from django_advanced_queries.covid_19.models import MedicalExaminationResult
        sub = MedicalExaminationResult.objects.filter(patient__person=OuterRef('pk')).order_by('-time').values('result')

        return self.annotate(
            latest_exam_res=Subquery(sub)
        ).exclude(
            latest_exam_res__in=['Healthy', 'Dead']
        )