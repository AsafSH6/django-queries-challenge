from django.db import models
from django.db.models import (
    Q,
    Max,
    Sum,
    Avg,
    Case,
    When,
    Value,
    Count,
    OuterRef,
    Subquery,
    IntegerField,
)


class PatientManager(models.Manager):
    def filter_by_examinations_results_options(self, results, *args, **kwargs):
        return self.filter(
            medical_examination_results__result__in=results,
            *args, **kwargs
        ).distinct()

    def filter_by_examined_hospital_workers(self, hospital_workers, *args,
                                            **kwargs):
        return self.filter(
            medical_examination_results__examined_by__in=hospital_workers,
            *args, **kwargs
        ).distinct()

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(
            num_of_patient_medical_examinations=Count(
                'medical_examination_results'
            )
        ).aggregate(
            highest_num_of_patient_medical_examinations=Max(
                'num_of_patient_medical_examinations'
            )
        )['highest_num_of_patient_medical_examinations']

    def get_patients_died_from_specific_reason(
            self,
            reason,
            **medical_examination_result_filter_kwargs):
        from django_advanced_queries.covid_19.models import \
            MedicalExaminationResult

        mer_of_given_reason_or_dead = MedicalExaminationResult.objects.filter(
            patient=OuterRef(name='pk'),
            **medical_examination_result_filter_kwargs
        ).order_by('-time')

        return self.annotate(
            last_mer=Subquery(mer_of_given_reason_or_dead.values('result')[:1]),
            one_before_last_mer=Subquery(
                mer_of_given_reason_or_dead.values('result')[1:2]),
        ).filter(
            last_mer='Dead',
            one_before_last_mer=reason,
        )


class PersonManager(models.Manager):
    def get_sick_persons(self):
        from django_advanced_queries.covid_19.models import \
            MedicalExaminationResult
        mer_subquery = MedicalExaminationResult.objects.filter(
            patient__person=OuterRef(name='pk')
        ).order_by('-time')

        return self.filter(
            patients_details__isnull=False
            # Filter persons that aren't hospitalized
        ).annotate(
            last_mer=Subquery(mer_subquery.values('result')[:1])
        ).exclude(last_mer__in=('Healthy', 'Dead'))

    def persons_with_multiple_jobs(self, jobs=None):
        from django_advanced_queries.covid_19.models import HospitalWorker
        annotations = {}
        filters = Q()

        if jobs:
            annotations['cnt_positions'] = Count('hospital_jobs__position',
                                                 distinct=True)
            filters &= Q(cnt_positions=len(jobs))
            operator_ = "gt" if len(jobs) == 1 else "gte"
            for pos in jobs:
                sub = HospitalWorker.objects.filter(
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

        return self.filter(hospital_jobs__isnull=False).annotate(
            **annotations).filter(filters)


class HospitalWorkerManager(models.Manager):

    def get_sick_workers(self):
        from django_advanced_queries.covid_19.models import Person
        sick_persons = Person.objects.get_sick_persons()

        return self.filter(person__pk__in=sick_persons)

    def get_worker_performed_most_medical_examinations(self, filter_kwargs,
                                                       exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(
            num_of_medical_examinations=Count('medical_examination_results')
        ).order_by('-num_of_medical_examinations').first()


class HospitalManager(models.Manager):
    def annotate_by_num_of_dead_from_corona(self):
        from django_advanced_queries.covid_19.models import Patient

        dead_from_corona = Patient.objects.get_patients_died_from_specific_reason(
            reason='Corona',
        )

        return self.annotate(
            num_of_dead_from_corona=Sum(
                Case(
                    When(departments__patients_details__in=dead_from_corona,
                         then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        )

        # Another option is:
        # return self.annotate(
        #     num_of_dead_from_corona=Subquery(
        #         dead_from_corona.filter(
        #             department__hospital=OuterRef('pk')
        #         ).values('department__hospital').annotate(count=Count('pk')).values('count'),
        #         output_field=IntegerField())
        # )

    def annotate_by_num_of_hospital_workers_in_risk_of_corona(self):
        from django_advanced_queries.covid_19.models import Person
        persons_in_risk_of_corona = Person.objects.filter(
            age__gte=60,
            hospital_jobs__isnull=False
        )

        return self.annotate(
            num_of_hospital_workers_in_risk_of_corona=Subquery(
                persons_in_risk_of_corona.filter(
                    hospital_jobs__department__hospital=OuterRef('pk')
                ).annotate(count=Count('pk', distinct=True)).values('count'),
                output_field=IntegerField())
        )

        # return self.annotate(
        #         num_of_hospital_workers_in_risk_of_corona=Sum(
        #             Case(
        #                 When(departments__hospital_workers__person__age__gte=60, then=Value(1)),
        #                 default=Value(0),
        #                 output_field=IntegerField()
        #             ),
        #             distinct=True,
        #         )
        #     )


class DepartmentManager(models.Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(
            avg_age_of_patients=Avg('patients_details__person__age')
        )
