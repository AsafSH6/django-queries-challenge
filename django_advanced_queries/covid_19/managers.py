from django.db.models import Manager, IntegerField, Max, Count, Avg, F, Case, When, OuterRef, Sum, Subquery, Q


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
    
    def annotate_by_num_of_dead_from_corona(self):
        from django_advanced_queries.covid_19.models import Patient
        patients = Patient.objects.get_patients_that_died_from_a_reason(reason='Corona')

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
        sick_persons = Person.objects.get_sick_persons()
        return self.filter(person__in=sick_persons)


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

    def get_patients_that_died_from_a_reason(self, reason):
        from django_advanced_queries.covid_19.models import MedicalExaminationResult
        med_exams_res = MedicalExaminationResult.objects.filter(patient=OuterRef('pk')).order_by('-time').values('result')

        return self.annotate(
            last_exam_res=Subquery(med_exams_res[0:1]),
            death_reason=Subquery(med_exams_res[1:2])
        ).filter(
            last_exam_res='Dead',
            death_reason=reason
        )

class PersonManager(Manager):
    def get_sick_persons(self):
        from django_advanced_queries.covid_19.models import MedicalExaminationResult
        sub = MedicalExaminationResult.objects.filter(
            patient__person=OuterRef('pk')
        ).order_by('-time').values('result')

        return self.filter(
            patients_details__isnull=False
        ).annotate(
            latest_exam_res=Subquery(sub[0:1])
        ).exclude(
            latest_exam_res__in=['Healthy', 'Dead']
        )
    
    def persons_with_multiple_jobs(self, jobs=None):
        """Get all persons who have multiple jobs and in the positions defined by `jobs` and only them (iff relation).
        If `None`, return all persons that hold more than one job (any).

        Keyword Arguments:
            jobs {list} -- A list of positions each person must hold (default: {None})
        """
        from django_advanced_queries.covid_19.models import HospitalWorker
        annotations = {}
        filters = Q()

        if jobs:
            annotations['cnt_positions'] = Count('hospital_jobs__position', distinct=True)
            filters &= Q(cnt_positions=len(jobs))
            operator_ = "gt" if len(jobs) == 1 else "gte"
            for pos in jobs:
                sub =  HospitalWorker.objects.filter(
                    person=OuterRef('pk'),
                    position=pos
                ).values('person').annotate(c=Count('*')).values_list('c')
                annotations['cnt_{}'.format(pos)] = Subquery(
                    sub,
                    output_field=IntegerField()
                )
                filters &= Q(**{'cnt_{}__{}'.format(pos, operator_): 1})
        else:
            annotations['cnt_positions'] = Count('hospital_jobs__position')
            filters &= Q(cnt_positions__gt=1)

        return self.filter(hospital_jobs__isnull=False).annotate(**annotations).filter(filters)