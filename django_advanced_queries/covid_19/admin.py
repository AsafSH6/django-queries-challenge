# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import *

admin.site.register(Hospital)
admin.site.register(Department)
admin.site.register(Person)
admin.site.register(HospitalWorker)
admin.site.register(Patient)
admin.site.register(MedicalExaminationResult)

# Register your models here.
