from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Jobs)
admin.site.register(Saved)
admin.site.register(Applied)
admin.site.register(CustomJobs)