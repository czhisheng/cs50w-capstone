from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
from django.conf import settings
import requests

# Create your models here.
class User(AbstractUser):
    pass


class Jobs(models.Model):
    job_id = models.CharField(max_length=64, unique=True)
    job_title = models.CharField(max_length=200)
    employer_name = models.CharField(max_length=200)
    job_location = models.CharField(max_length=100)
    employer_logo = models.URLField(null=True)
    job_employment_type = models.CharField(max_length=50)
    job_description = models.TextField(null=True)
    job_apply_link = models.URLField(null=True)
    job_min_salary = models.IntegerField(null=True)
    job_max_salary = models.IntegerField(null=True)
    job_salary_period = models.CharField(max_length=50, null=True)
    job_posted_at_timestamp = models.IntegerField(null=True)
    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def add(cls, job_id):
        url = "https://jsearch.p.rapidapi.com/job-details"
        querystring = {"job_id":f"{job_id}"}
        headers = {
            "x-rapidapi-key": settings.JSEARCH_API_KEY,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response = response.json()
            print(response["data"])
            data = response["data"][0]
            job = cls(
                job_id = data["job_id"],
                job_title = data["job_title"],
                employer_name = data["employer_name"],
                job_location = data["job_location"],
                employer_logo = data["employer_logo"],
                job_employment_type = data["job_employment_type"],
                job_description = data["job_description"],
                job_apply_link = data["job_apply_link"],
                job_min_salary = data["job_min_salary"],
                job_max_salary = data["job_max_salary"],
                job_salary_period = data["job_salary_period"],
                job_posted_at_timestamp = data["job_posted_at_timestamp"],
            )
            job.save()
            return True
        
        except IntegrityError:
            print(f"IntegrityError: Job (job_id:{job_id}) already exist.")
            return False
        
        except KeyError:
            print(f"KeyError: Key 'data' for job_id:'{job_id}' does not exist.")
            return False
    
    def serialized(self):
        return {
            "job_id": self.job_id,
            "job_title": self.job_title,
            "employer_name": self.employer_name,
            "job_location": self.job_location,
            "employer_logo": self.employer_logo,
            "job_employment_type": self.job_employment_type,
            "job_description": self.job_description,
            "job_apply_link": self.job_apply_link,
            "job_min_salary": self.job_min_salary,
            "job_max_salary": self.job_max_salary,
            "job_salary_period": self.job_salary_period,
            "job_posted_at_timestamp": self.job_posted_at_timestamp
        }
    
    def __str__(self):
        return f"{self.job_title} at {self.employer_name}"


class Saved(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved")
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name="saved")

    @classmethod
    def checksave(cls, data, user):
        saved_jobs = cls.objects.filter(user=user)
        saved_id = [saved.job.job_id for saved in saved_jobs]
        for job in data:
            job_id = job["job_id"] if isinstance(job, dict) else job.job_id
            if job_id in saved_id:
                if isinstance(job, dict):
                    job["is_saved"] = True
                else:
                    job.is_saved = True
        return data
    
    def __str__(self):
        return f"{self.user.username}: {self.job.job_title}"


class Applied(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applied")
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name="applied")
    status = models.CharField(max_length=100, null=True)
    offer = models.IntegerField(null=True)

    @classmethod
    def checkapply(cls, data, user):
        applied_jobs = cls.objects.filter(user=user)
        applied_id = [applied.job.job_id for applied in applied_jobs]
        for job in data:
            job_id = job["job_id"] if isinstance(job, dict) else job.job_id
            if job_id in applied_id:
                if isinstance(job, dict):
                    job["is_applied"] = True
                else:
                    job.is_applied = True
        return data
    
    def serialized(self):
        return {
            "timestamp": self.timestamp,
            "updated": self.updated.isoformat(),
            "user": self.user.username,
            "job": self.job.serialized(),
            "status": self.status,
            "offer": self.offer
        }
    
    def __str__(self):
        return f"{self.user.username}: {self.job.job_title} ({self.status})"


class CustomJobs(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="custom_job")
    job_title = models.CharField(max_length=200)
    employer_name = models.CharField(max_length=200)
    job_location = models.CharField(max_length=100)
    job_apply_link = models.URLField(null=True)
    status = models.CharField(max_length=100, null=True)
    offer = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user.username}: {self.job_title}"