# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from django_advanced_queries.covid_19.models import (
    Hospital,
    Department,
    Person,
    HospitalWorker,
    Patient,
    MedicalExaminationResult,
)


class Covid19Tests(TestCase):

    def setUp(self):
        # Not using fixtures to make it easier to understand the created models.

        ####################################
        ###  Asaf Harofeh Medical Center ###
        ####################################
        self.hospital1 = Hospital.objects.create(
            name='Asaf Harofeh Medical Center',
            city='Be\'er Ya\'akov',
        )
        department1 = Department.objects.create(
            name='Critical Care',
            hospital=self.hospital1
        )
        person1 = Person.objects.create(name='Alon', age=65, gender='Male')
        self.hospital_worker1 = HospitalWorker.objects.create(
            person=person1,
            department=department1,
            position='Doctor',
        )
        person2 = Person.objects.create(name='Ahmed', age=34, gender='Male')
        self.hospital_worker2 = HospitalWorker.objects.create(
            person=person2,
            department=department1,
            position='Nurse',
        )
        person3 = Person.objects.create(name='Rony', age=33, gender='Female')
        self.patient1 = Patient.objects.create(
            person=person3,
            department=department1
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=3,
                day=21,
                hour=14,
                minute=3
            ),
            examined_by=self.hospital_worker1,
            patient=self.patient1,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=3,
                day=21,
                hour=14,
                minute=13
            ),
            examined_by=self.hospital_worker1,
            patient=self.patient1,
            result='Botism'
        )
        self.patient2 = Patient.objects.create(
            person=person1,
            department=department1
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=3,
                day=21,
                hour=16,
                minute=13
            ),
            examined_by=self.hospital_worker2,
            patient=self.patient2,
            result='Corona'
        )
        person4 = Person.objects.create(name='Dana', age=25, gender='Female')
        HospitalWorker.objects.create(
            person=person4,
            department=department1,
            position='Doctor',
        )
        self.patient3 = Patient.objects.create(
            person=person4,
            department=department1
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=3,
                day=21,
                hour=17,
                minute=54
            ),
            examined_by=self.hospital_worker2,
            patient=self.patient3,
            result='Healthy'
        )
        person5 = Person.objects.create(name='Yoav', age=21, gender='Other')
        self.patient4 = Patient.objects.create(
            person=person5,
            department=department1
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=3,
                day=20,
                hour=12,
                minute=13
            ),
            examined_by=self.hospital_worker2,
            patient=self.patient4,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=3,
                day=26,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker2,
            patient=self.patient4,
            result='Healthy'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=26,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker2,
            patient=self.patient4,
            result='Healthy'
        )

        ####################################
        ###          Hadassah            ###
        ####################################
        self.hospital2 = Hospital.objects.create(
            name='Hadassah',
            city='Jerusalem',
        )
        department2 = Department.objects.create(
            name='Critical Care',
            hospital=self.hospital2
        )
        self.person6 = Person.objects.create(name='Ron', age=60, gender='Male')
        self.hospital_worker3 = HospitalWorker.objects.create(
            person=self.person6,
            department=department2,
            position='Doctor',
        )
        self.hospital_worker4 = HospitalWorker.objects.create(
            person=self.person6,
            department=department2,
            position='Doctor',
        )

        self.hospital_worker5 = HospitalWorker.objects.create(
            person=self.person6,
            department=department2,
            position='Nurse',
        )
        person7 = Person.objects.create(name='Shalom', age=87, gender='Male')
        self.patient5 = Patient.objects.create(
            person=person7,
            department=department2
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=26,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient5,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=27,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient5,
            result='Dead'
        )
        person8 = Person.objects.create(name='Lea', age=90, gender='Female')
        self.patient6 = Patient.objects.create(
            person=person8,
            department=department2
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=26,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient6,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=27,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient6,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=28,
                hour=18,
                minute=1
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient6,
            result='Dead'
        )
        person9 = Person.objects.create(name='Daniel', age=3, gender='Male')
        self.patient7 = Patient.objects.create(
            person=person9,
            department=department2
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=26,
                hour=15,
                minute=15
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient7,
            result='Healthy'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=27,
                hour=21,
                minute=53
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient7,
            result='Botism'
        )
        self.person10 = Person.objects.create(
            name='Ruby',
            age=15,
            gender='Male'
        )
        self.patient8 = Patient.objects.create(
            person=self.person10,
            department=department2
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=26,
                hour=16,
                minute=10
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient8,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=27,
                hour=22,
                minute=12
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient8,
            result='Healthy'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=28,
                hour=11,
                minute=1
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient8,
            result='Botism'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(
                year=2020,
                month=4,
                day=28,
                hour=11,
                minute=10
            ),
            examined_by=self.hospital_worker3,
            patient=self.patient8,
            result='Dead'
        )

        self.person11 = Person.objects.create(
            name='Abdul',
            age=29,
            gender='Male'
        )
        self.hospital_worker6 = HospitalWorker.objects.create(
            person=self.person11,
            department=department2,
            position='Nurse',
        )

        self.hospital_worker7 = HospitalWorker.objects.create(
            person=self.person11,
            department=department2,
            position='Nurse',
        )

    def test_num_of_hospitalized_because_of_botism(self):
        with self.assertNumQueries(1):
            num_of_hospitalized_because_of_botism = Patient.objects.filter_by_examinations_results_options(
                results=('Botism',)
            ).count()
            self.assertEqual(num_of_hospitalized_because_of_botism, 3)

    def test_num_of_hospitalized_because_of_botism_or_corona(self):
        with self.assertNumQueries(1):
            num_of_hospitalized_because_of_botism_or_corona = Patient.objects.filter_by_examinations_results_options(
                results=('Botism', 'Corona')
            ).count()
            self.assertEqual(num_of_hospitalized_because_of_botism_or_corona, 7)

    def test_highest_num_of_patient_medical_examinations(self):
        with self.assertNumQueries(1):
            highest_num_of_patient_m_e = Patient.objects.get_highest_num_of_patient_medical_examinations()
            self.assertEqual(highest_num_of_patient_m_e, 4)

    def test_average_age_of_patients_in_every_department(self):
        with self.assertNumQueries(1):
            departments_with_avg_age_of_patients = Department.objects.annotate_avg_age_of_patients()

            actual_result = [department.avg_age_of_patients
                             for department in
                             departments_with_avg_age_of_patients.order_by()]
            self.assertEqual(actual_result, [36, 48.75])

    def test_doctor_performed_the_most_medical_examinations(self):
        with self.assertNumQueries(1):
            doctor_performed_the_most_m_e = HospitalWorker.objects.get_worker_performed_most_medical_examinations(
                filter_kwargs={'position': 'Doctor'},
                exclude_kwargs={}
            )

            self.assertEqual(
                doctor_performed_the_most_m_e,
                self.hospital_worker3
            )

    def test_num_of_sick_persons(self):
        with self.assertNumQueries(1):
            sick_persons = Person.objects.get_sick_persons()
            self.assertEqual(sick_persons.count(), 3)

    def test_num_of_sick_hospital_workers(self):
        with self.assertNumQueries(1):
            sick_hospital_workers = HospitalWorker.objects.get_sick_workers()
            self.assertEqual(sick_hospital_workers.count(), 1)

    def test_detect_potential_infected_patients_because_of_sick_hospital_worker(
            self):
        with self.assertNumQueries(2):
            patient_examined_by_sick_hospital_worker = Patient.objects.filter_by_examined_hospital_workers(
                hospital_workers=HospitalWorker.objects.get_sick_workers()
            )

            self.assertEqual(
                patient_examined_by_sick_hospital_worker.count(),
                1
            )
            self.assertListEqual(
                list(patient_examined_by_sick_hospital_worker),
                [self.patient1]
            )

        # Now improve the test to hit DB once only
        with self.assertNumQueries(1):
            patient_examined_by_sick_hospital_worker = Patient.objects.filter_by_examined_hospital_workers(
                hospital_workers=HospitalWorker.objects.get_sick_workers()
            )

            self.assertEqual(len(patient_examined_by_sick_hospital_worker), 1)
            self.assertListEqual(
                list(patient_examined_by_sick_hospital_worker),
                [self.patient1]
            )

    def test_number_of_hospital_workers_that_in_risk_group_of_corona_per_hospital(
            self):
        # Someone who is in risk group of corona is person that is older than 60
        with self.assertNumQueries(1):
            result = list(Hospital.objects.annotate_by_num_of_hospital_workers_in_risk_of_corona().order_by())

            hospital1_num_of_hospital_workers_in_risk_of_corona = result[
                0].num_of_hospital_workers_in_risk_of_corona
            self.assertEqual(
                hospital1_num_of_hospital_workers_in_risk_of_corona, 1)

            hospital2_num_of_hospital_workers_in_risk_of_corona = result[
                1].num_of_hospital_workers_in_risk_of_corona
            self.assertEqual(
                hospital2_num_of_hospital_workers_in_risk_of_corona,
                1
            )

    def test_annotate_by_num_of_dead_from_corona(self):
        # Dead from corona is someone who had corona and then died
        with self.assertNumQueries(1):
            result = list(Hospital.objects. \
                annotate_by_num_of_dead_from_corona().order_by())

            hospital1_num_of_dead_from_corona = result[
                0].num_of_dead_from_corona
            self.assertEqual(hospital1_num_of_dead_from_corona, 0)

            hospital2_num_of_dead_from_corona = result[
                1].num_of_dead_from_corona
            self.assertEqual(hospital2_num_of_dead_from_corona, 2)

    def test_hospitals_with_at_least_two_dead_patients_from_corona(self):
        # Dead from corona is someone who had corona and then died
        with self.assertNumQueries(1):
            # Define query by yourself
            hospitals_with_more_than_two_dead_patients_from_corona = Hospital.objects. \
                annotate_by_num_of_dead_from_corona().filter(
                num_of_dead_from_corona__gte=2
            )

            self.assertListEqual(
                list(hospitals_with_more_than_two_dead_patients_from_corona),
                [self.hospital2]
            )

    def test_get_persons_with_specific_multiple_jobs(self):
        """Author: Arthur
        persons_with_multiple_jobs:
            Get all persons who have multiple jobs and in the positions defined
             by `jobs` and only them (iff relation).
            If `None`, return all persons that hold more than one job (any).
        """
        # Note: `Count(Case(When(...)))`` won't work here
        with self.assertNumQueries(4):
            hospital_workers = Person.objects.persons_with_multiple_jobs()
            self.assertListEqual(list(hospital_workers),
                                 [self.person6, self.person11])

            hospital_workers = Person.objects.persons_with_multiple_jobs(
                jobs=['Nurse'])
            self.assertListEqual(list(hospital_workers), [self.person11])

            hospital_workers = Person.objects.persons_with_multiple_jobs(
                jobs=['Doctor'])
            self.assertListEqual(list(hospital_workers), [])

            hospital_workers = Person.objects.persons_with_multiple_jobs(
                jobs=['Doctor', 'Nurse'])
            self.assertListEqual(list(hospital_workers), [self.person6])

    def test_define_new_test_and_send_to_me(self):
        # Define test that use at least one function
        # that was not used in the previous tests and send to me
        # include the solution
        self.assertTrue(True)
