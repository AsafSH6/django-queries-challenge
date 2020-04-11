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
        department1 = Department.objects.create(name='Critical Care', hospital=self.hospital1)
        person1 = Person.objects.create(name='Alon', age=65, gender='Male') # Corona
        self.person1 = person1
        self.hospital_worker1 = HospitalWorker.objects.create(
            person=person1,
            department=department1,
            position='Doctor',
        )
        person2 = Person.objects.create(name='Ahmed', age=34, gender='Male')
        self.person2 = person2
        self.hospital_worker2 = HospitalWorker.objects.create(
            person=person2,
            department=department1,
            position='Nurse',
        ) # Racist
        person3 = Person.objects.create(name='Rony', age=33, gender='Female') # Corona bot
        self.patient1 = Patient.objects.create(person=person3, department=department1)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=3, day=21, hour=14, minute=3),
            examined_by=self.hospital_worker1,
            patient=self.patient1,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=3, day=21, hour=14, minute=13),
            examined_by=self.hospital_worker1,
            patient=self.patient1,
            result='Botism'
        )
        self.patient2 = Patient.objects.create(person=person1, department=department1)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=3, day=21, hour=16, minute=13),
            examined_by=self.hospital_worker2,
            patient=self.patient2,
            result='Corona'
        )
        person4 = Person.objects.create(name='Dana', age=25, gender='Female')
        HospitalWorker.objects.create(
            person=person4,
            department=department1,
            position='Doctor',
        ) # Successful, very hot
        self.patient3 = Patient.objects.create(person=person4, department=department1)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=3, day=21, hour=17, minute=54),
            examined_by=self.hospital_worker2,
            patient=self.patient3,
            result='Healthy'
        )
        person5 = Person.objects.create(name='Yoav', age=21, gender='Other') # Maman healed from corona
        self.patient4 = Patient.objects.create(person=person5, department=department1)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=3, day=20, hour=12, minute=13),
            examined_by=self.hospital_worker2,
            patient=self.patient4,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=3, day=26, hour=18, minute=01),
            examined_by=self.hospital_worker2,
            patient=self.patient4,
            result='Healthy'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=26, hour=18, minute=01),
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
        department2 = Department.objects.create(name='Critical Care', hospital=self.hospital2)
        person6 = Person.objects.create(name='Ron', age=60, gender='Male')
        self.hospital_worker3 = HospitalWorker.objects.create(
            person=person6,
            department=department2,
            position='Doctor',
        )
        person7 = Person.objects.create(name='Shalom', age=87, gender='Male')
        self.patient5 = Patient.objects.create(person=person7, department=department2)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=26, hour=18, minute=01),
            examined_by=self.hospital_worker3,
            patient=self.patient5,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=27, hour=18, minute=01),
            examined_by=self.hospital_worker3,
            patient=self.patient5,
            result='Dead'
        ) # SAD
        person8 = Person.objects.create(name='Lea', age=90, gender='Female')
        self.patient6 = Patient.objects.create(person=person8, department=department2)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=26, hour=18, minute=01),
            examined_by=self.hospital_worker3,
            patient=self.patient6,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=27, hour=18, minute=01),
            examined_by=self.hospital_worker3,
            patient=self.patient6,
            result='Corona'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=28, hour=18, minute=01),
            examined_by=self.hospital_worker3,
            patient=self.patient6,
            result='Dead'
        ) # SAD
        person9 = Person.objects.create(name='Daniel', age=3, gender='Male') # Young bot
        self.patient7 = Patient.objects.create(person=person9, department=department2)
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=26, hour=15, minute=15),
            examined_by=self.hospital_worker3,
            patient=self.patient7,
            result='Healthy'
        )
        MedicalExaminationResult.objects.create(
            time=datetime.datetime(year=2020, month=4, day=27, hour=21, minute=53),
            examined_by=self.hospital_worker3,
            patient=self.patient7,
            result='Botism'
        )

    def test_num_of_hospitalized_because_of_botism(self):
        with self.assertNumQueries(1):
            num_of_hospitalized_because_of_botism = Patient.objects.filter_by_examination_results(
                results=['Botism']
            ).count()
            self.assertEqual(num_of_hospitalized_because_of_botism, 2)

    def test_highest_num_of_patient_medical_examinations(self):
        with self.assertNumQueries(1):
            highest_num_of_patient_m_e = Patient.objects.get_highest_num_of_patient_medical_examinations()
            self.assertEqual(highest_num_of_patient_m_e, 3)

    def test_average_age_of_patients_in_every_department(self):
        with self.assertNumQueries(1):
            departments_with_avg_age_of_patients = Department.objects.annotate_avg_age_of_patients()

            actual_result = [department.avg_age_of_patients
                             for department in departments_with_avg_age_of_patients.order_by()]
            self.assertEqual(actual_result, [36, 60])

    def test_doctor_performed_the_most_medical_examinations(self):
        with self.assertNumQueries(1):
            doctor_performed_the_most_m_e = HospitalWorker.objects.get_worker_performed_most_medical_examinations(
                filter_kwargs={'position': 'Doctor'},
                exclude_kwargs={}
            )

            self.assertEqual(doctor_performed_the_most_m_e, self.hospital_worker3)

    def test_num_of_sick_persons(self):
        with self.assertNumQueries(1):
            sick_persons = Person.objects.get_sick_persons()
            self.assertEqual(sick_persons.count(), 3)

    def test_num_of_sick_hospital_workers(self):
        with self.assertNumQueries(1):
            sick_hospital_workers = HospitalWorker.objects.get_sick_workers()
            self.assertEqual(sick_hospital_workers.count(), 1)

    def test_detect_potential_infected_patients_because_of_sick_hospital_worker(self):
        with self.assertNumQueries(2):
            patient_examined_by_sick_hospital_worker = Patient.objects.filter_by_examined_hospital_workers(
                hospital_workers=HospitalWorker.objects.get_sick_workers()
            )
            num_of_patient_examined_by_sick_hospital_worker = patient_examined_by_sick_hospital_worker.count()

            self.assertEqual(num_of_patient_examined_by_sick_hospital_worker, 1)
            self.assertListEqual(list(patient_examined_by_sick_hospital_worker), [self.patient1])

        # Now improve the test to hit DB once only
        with self.assertNumQueries(1):
            patient_examined_by_sick_hospital_worker = Patient.objects.filter_by_examined_hospital_workers(
                hospital_workers=HospitalWorker.objects.get_sick_workers()
            )
            # Using `count()` will access the DB again to run the qeury (`COUNT(*)`). Since we already have the data from the
            # previous line and we don't want to query the DB again, we will use `len()` on the resulting `QuerySet`.
            num_of_patient_examined_by_sick_hospital_worker = len(patient_examined_by_sick_hospital_worker)

            self.assertEqual(num_of_patient_examined_by_sick_hospital_worker, 1)
            self.assertListEqual(list(patient_examined_by_sick_hospital_worker), [self.patient1])

    def test_number_of_hospital_workers_that_in_risk_group_of_corona_per_hospital(self):
        # Someone who is in risk group of corona is person that is older than 60
        with self.assertNumQueries(1):
            result = list(Hospital.objects.annotate_by_num_of_hospital_workers_in_risk_of_corona().order_by())

            hospital1_num_of_hospital_workers_in_risk_of_corona = result[0].num_of_hospital_workers_in_risk_of_corona
            self.assertEqual(hospital1_num_of_hospital_workers_in_risk_of_corona, 1)

            hospital2_num_of_hospital_workers_in_risk_of_corona = result[1].num_of_hospital_workers_in_risk_of_corona
            self.assertEqual(hospital2_num_of_hospital_workers_in_risk_of_corona, 1)

    def test_annotate_by_num_of_dead_from_corona(self):
        # Dead from corona is someone who had corona and then died
        with self.assertNumQueries(1):
            # Using `list` to force the query to evaluate only once (insted of every access to the annotated field)
            result = list(Hospital.objects.\
                annotate_by_num_of_dead_from_corona().order_by())

            hospital1_num_of_dead_from_corona = result[0].num_of_dead_from_corona
            self.assertEqual(hospital1_num_of_dead_from_corona, 0)

            hospital2_num_of_dead_from_corona = result[1].num_of_dead_from_corona
            self.assertEqual(hospital2_num_of_dead_from_corona, 2)

    def test_hospitals_with_at_least_two_dead_patients_from_corona(self):
        # Dead from corona is someone who had corona and then died
        with self.assertNumQueries(1):
            # Define query by yourself
            hospitals_with_more_than_two_dead_patients_from_corona = \
                Hospital.objects.get_hospitals_with_min_amount_of_dead_from_corona(2)

            self.assertListEqual(list(hospitals_with_more_than_two_dead_patients_from_corona),
                                 [self.hospital2])

    def test_define_new_test_and_send_to_me(self):
        # Define test that use at least one function that was not used in the previous tests and send to me
        # Include the solution
        # To dear Asaf sharmit: this is psuedo, not sure how it should look like yet.

        department2 = Department.objects.create(name='Emergency', hospital=self.hospital1)
        self.hospital_worker4 = HospitalWorker.objects.create(
            person=self.person1,
            department=department2,
            position='Doctor',
        )
        self.hospital_worker5 = HospitalWorker.objects.create(
            person=self.person2,
            department=department2,
            position='Nurse',
        )
        
        department3 = Department.objects.create(name='Cardiology', hospital=self.hospital1)
        self.hospital_worker6 = HospitalWorker.objects.create(
            person=self.person1,
            department=department3,
            position='Nurse',
        )

        with self.assertNumQueries(4):
            hospital_workers = Person.objects.persons_with_multiple_jobs()
            self.assertListEqual(list(hospital_workers), [self.person1, self.person2])
            
            hospital_workers = Person.objects.persons_with_multiple_jobs(jobs=['Nurse'])
            self.assertListEqual(list(hospital_workers), [self.person2])

            hospital_workers = Person.objects.persons_with_multiple_jobs(jobs=['Doctor'])
            self.assertListEqual(list(hospital_workers), [])

            hospital_workers = Person.objects.persons_with_multiple_jobs(jobs=['Doctor', 'Nurse'])
            self.assertListEqual(list(hospital_workers), [self.person1])
