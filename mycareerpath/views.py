from django.db import IntegrityError
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import formats
from django.core.paginator import Paginator
from django.conf import settings
from datetime import datetime, timezone
import requests
import json

from .models import *
from .forms import RegisterForm, NewJobForm
from .util import *


def index(request):
    if request.user.is_authenticated:
        applied_jobs = Applied.objects.filter(user=request.user)
        counts = dict()
        if applied_jobs.exists():
            for job in applied_jobs:
                job.updated = convert_time(datetime.now(timezone.utc) - job.updated)
                if job.status.lower() not in counts:
                    counts[job.status.lower()] = 1
                else:
                    counts[job.status.lower()] += 1
            applied_jobs = sorted(applied_jobs, key=lambda job: job.updated, reverse=True)[:2]
        
        return render(request, 'mycareerpath/index.html', {
            "counts": counts,
            "jobs": applied_jobs
        })
    else:
        jobs = Jobs.objects.filter(job_posted_at_timestamp__isnull=False)
        if jobs.exists():
            jobs = sorted(jobs, key=lambda job: job.timestamp, reverse=True)[:4]
        else:
            jobs = []
        return render(request, "mycareerpath/index.html", {
            "jobs": jobs
        })


def register(request):
    # Redirect index if user is already logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    
    if request.method == "POST":
        form = RegisterForm(request.POST)

        # Checks if form is valid
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirmation = form.cleaned_data["confirmation"]

            # Check if password matches
            if password != confirmation:
                form.add_error("confirmation", "Passwords must match.")
                return render(request, "mycareerpath/register.html", {
                    "form": form
                })
            
            # Attempt to create user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request,user)
                return HttpResponseRedirect(reverse("index"))
            except IntegrityError:
                form.add_error("username", "Username already exist.")
                return render(request, "mycareerpath/register.html", {
                    "form": form
                })

        # If form is not valid
        else:
            return render(request, "mycareerpath/register.html", {
                "form": form
            })

    # Render default register page    
    return render(request, "mycareerpath/register.html", {
        "form": RegisterForm()
    })


def login_user(request):
    # Redirect index if user is already logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        
        else:
            return render(request, "mycareerpath/login.html", {
                "message": "Incorrect username or password."
            })

    # Render default login page
    return render(request, "mycareerpath/login.html")


@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def error(request):
    return render(request, "mycareerpath/error.html")


def search(request):
    q = request.GET.get("q")
    if not q:
        return HttpResponseRedirect(reverse("index"))
    country = request.GET.get("country")
    if country:
        s_country = f"in {country}"
    else:
        s_country = ""
        country = ""
    page = request.GET.get("page")
    if not page:
        page = 1
    try:
        page = int(page)
    except TypeError:
        return HttpResponseRedirect(reverse("error"))
    
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        
        querystring = {"query": f"{q} {s_country}",
                    "page": page,
                    "num_pages": "1",
                    "date_posted": "all"}

        headers = {
            "x-rapidapi-key": settings.JSEARCH_API_KEY,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()["data"]
    except Exception as e:
        print("JSearch API error:", e)
        return render(request, "mycareerpath/error.html", {
            "message" : "An error occurred while fetching job listings."
        })

    # Save entry if it is not in the database
    for entry in data:
        if not Jobs.objects.filter(job_id=entry["job_id"]).exists():
            job = Jobs( 
                job_id=entry["job_id"],
                job_title=entry["job_title"],
                employer_name=entry["employer_name"],
                job_location=entry["job_location"],
                employer_logo=entry["employer_logo"],
                job_employment_type=entry["job_employment_type"],
                job_description=entry["job_description"],
                job_apply_link=entry["job_apply_link"],
                job_min_salary=entry["job_min_salary"],
                job_max_salary=entry["job_max_salary"],
                job_salary_period=entry["job_salary_period"],
                job_posted_at_timestamp=entry["job_posted_at_timestamp"],
            )
            job.save()

    if request.user.is_authenticated:
    # Add Save and Applied tags to each entry
        data = Saved.checksave(data, request.user)
        data = Applied.checkapply(data, request.user)

    return render(request, "mycareerpath/search.html", {
        "results": data,
        "query": q,
        "country": country,
        "page": page,
        "pages": range(max(page - 3, 1), page + 1)
    })


@login_required
def saved_job(request, page=1):
    # If other pages are accessed
    if request.GET.get("page"):
        page = request.GET.get("page")

    if not Saved.objects.filter(user=request.user).exists():
        jobs = None
        p = None
    else:
        saves = Saved.objects.filter(user=request.user)
        jobs = []
        for save in saves:
            save.job = Saved.checksave([save.job], request.user)[0]
            save.job = Applied.checkapply([save.job], request.user)[0]
            jobs.append(save.job)

        # Sort by newest to latest and pagnify them
        jobs = sorted(jobs, key=lambda job: job.timestamp, reverse=True)
        p = Paginator(jobs, 10)
        jobs = p.get_page(page)

    return render(request, 'mycareerpath/saved_job.html', {
        "jobs": jobs,
        "p": p
    })


@login_required
def tracker(request):
    custom_jobs = CustomJobs.objects.filter(user=request.user)
    applied_jobs = Applied.objects.filter(user=request.user)
    jobs = []
    if applied_jobs.exists():
        for applied in applied_jobs:
            applied.job = Saved.checksave([applied.job], request.user)[0]
            applied.job = Applied.checkapply([applied.job], request.user)[0]
            jobs.append(applied)
    if custom_jobs.exists():
        for custom_job in custom_jobs:
            custom_job.custom = True
            jobs.append(custom_job)

    jobs = sorted(jobs, key=lambda job: job.updated, reverse=True)
    for job in jobs:    
        job.updated = convert_time(datetime.now(timezone.utc) - job.updated)
    order = ["Accepted", "Offer", "Interviewing", "Applied", "Reject"]
    jobs = sorted(jobs, key=lambda job: order.index(job.status))

    return render(request, "mycareerpath/applied_job.html", {
        "jobs": jobs
    })


@login_required
def add(request):
    if request.method == "POST":
        form = NewJobForm(request.POST)

        if form.is_valid():
            job_title = form.cleaned_data["job_title"]
            employer_name = form.cleaned_data["employer_name"]
            job_location = form.cleaned_data["job_location"]
            job_apply_link = form.cleaned_data["job_apply_link"]

            new_job = CustomJobs(
                user=request.user,
                job_title=job_title, 
                employer_name=employer_name, 
                job_location=job_location, 
                job_apply_link=job_apply_link,
                status="Applied"
            )
            new_job.save()
            return HttpResponseRedirect(reverse("tracker"))
        
        return render(request, "mycareerpath/add.html", {
            "form": form
        })
    return render(request, 'mycareerpath/add.html', {
        "form": NewJobForm()
    })


# API Routes

@login_required
def save(request):

    if request.method == "POST":

        # Get id value, return error if it is empty
        id = json.loads(request.body).get("id")
        if not id:
            return JsonResponse({"error": "job_id is empty"}, status=400)
        
        # Checks if job already exist in database, if it does not exist, add job
        if not Jobs.objects.filter(job_id=id).exists():

            # Add job by fetch via class method. If invalid job id, return False
            if not Jobs.add(id):
                return JsonResponse({"error": "Invalid job_id or Job already exist"}, status=400)
        
        # Check if it is saved by the user already, Saved => Unsave and vise versa
        if Saved.objects.filter(job__job_id=id, user=request.user).exists():
            # Unsave job
            saved_job = Saved.objects.filter(job__job_id=id, user=request.user)
            saved_job.delete()
            saved = False
        
        else:
            # Save Job
            job = Jobs.objects.get(job_id=id)
            save_job = Saved(job=job, user=request.user)
            save_job.save() 
            saved = True
                
        return JsonResponse({"message": "Job like status updated", "saved": saved})
    
    return JsonResponse({"error": "Post request required"}, status=400)


@login_required
def apply(request):

    if request.method == "POST":

        # Get id value, return error if it is empty
        id = json.loads(request.body).get("id")
        if not id:
            return JsonResponse({"error": "job_id is empty"}, status=400)
        
        # Checks if job already exist in database, if it does not exist, add job
        if not Jobs.objects.filter(job_id=id).exists():

            # Add job by fetch via class method. If invalid job id, return False
            if not Jobs.add(id):
                return JsonResponse({"error": "Invalid job_id or Job already exist"}, status=400)
        
        # Check if it is saved by the user already, Saved => Unsave and vise versa
        if Applied.objects.filter(job__job_id=id, user=request.user).exists():
            # Unsave job
            applied_job = Applied.objects.filter(job__job_id=id, user=request.user)
            applied_job.delete()
            applied = False
        
        else:
            # Save Job
            job = Jobs.objects.get(job_id=id)
            applied_job = Applied(job=job, user=request.user, status="Applied")
            applied_job.save()
            applied = True
                
        return JsonResponse({"message": "Job apply status updated", "applied": applied, "success": True})
    
    return JsonResponse({"error": "Post request required"}, status=400)


@login_required
def status(request):
    
    statuses = ["Applied", "Interviewing", "Reject", "Offer", "Accepted"]

    if request.method == "POST":
        custom = json.loads(request.body).get("custom")
        id = json.loads(request.body).get("id")
        print(id)
        if not id:
            return JsonResponse({"error": "job_id is empty"}, status=400)
        status = json.loads(request.body).get("status")
        if status not in statuses:
            return JsonResponse({"error": "Invalid status"}, status=400)
        
        if custom:
            if CustomJobs.objects.filter(id=id, user=request.user).exists():
                custom_job = CustomJobs.objects.get(id=id, user=request.user)
                custom_job.status = status
                custom_job.save()
                return JsonResponse({"message": "Job status updated", 
                                    "status": custom_job.status, 
                                     "updated": convert_time(datetime.now(timezone.utc) - custom_job.updated)
                                     }, status=201)
        else:
            if Applied.objects.filter(job__job_id=id, user=request.user).exists():
                applied_job = Applied.objects.get(job__job_id=id, user=request.user)
                applied_job.status = status
                applied_job.save()
                return JsonResponse({"message": "Job status updated", 
                                    "status": applied_job.status, 
                                     "updated": convert_time(datetime.now(timezone.utc) - applied_job.updated)
                                     }, status=201)
            
    return JsonResponse({"error": "Post request required"}, status=400)


@login_required
def remove_custom(request):

    if request.method == "POST":
        
        id = json.loads(request.body).get("id")
        if not id:
            return JsonResponse({"error": "job_id is empty"}, status=400)
        
        custom_job = CustomJobs.objects.filter(user=request.user, id=id)
        if custom_job.exists():
            custom_job.delete()
            return JsonResponse({"message": "Custom job deleted", "success": True})

        else:
            return JsonResponse({"error": "Job does not exist or belongs to user"}, status=400)
        
    return JsonResponse({"error": "Post request required"}, status=400)
