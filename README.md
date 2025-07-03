# Project Title: My Career Path

### <ins>Overview</ins>

My Career Path is a full stack web application that allows users to search for jobs and track the status of their applications all in one place. Built with Django, Python, JavaScript, CSS and BootStrap while integrating with **Rapid API: JSearch**.

### <ins>Distinctiveness and Complexity</ins>

#### 1. Integration of External API and Data Storage
This application dynamically integrates **JSearch**, an external job search API, while selectively storing relevant data locally. This help avoid hitting API limits unnecessarilly and ensures app functionality and user experience.

#### 2. Integration of API and Custom Job Entries
To create an all-in-one job tracking experience, this application allows users to manage both API-fetched and custom jobs entered manually. This is particularly useful for tracking applications submitted through external platforms that are not covered by the API. Custom job listings are displayed seamlessly alongside API-fetched jobs in the tracker page. Furthermore, users are able to edit or delete them just like API-fetched job, ensuring unified user experience. This was a challenge to implement as API and custom jobs are stored in seperate models, where extra logic has to be added to ensure job is edited or deleted from the model where it belongs.

#### 3. Job Tracking Interface and Custom Status Logic
User can update the job's **status** in the tracker page, with changes reflected instantly. Each status is color-coded for easy visual reference. Whenever a status is updated, the corresponding last updated timestamp is updated, allowing users to see how recent a change was made. Entries are sorted not only by timestamp, but also the status priority, where job marked as **Accepted** or **Offerred** appears at the top, while **Rejected** jobs are listed at the bottom.

#### 4. Dynamic Job Details Section
Job details are displayed dynamically using **JavaScript**, with the presentation tailored to each page's layout. On the **Search** and **Saved** pages, clicking a job loads is detauls into an adjacent section beside the listings. On the **Index** and **Tracker** pages, job details appeare in a **Bootstrap Offcanvas** panel that slides in, blending seamlessly with overall design.

#### 5. Responsiveness and User Interface
Layouts are dynamically adjusted using both Bootstrap and CSS breakpoints. Certain elements and columns are conditionally hiddened or scaled based on screen size, enhancing mobile usability and user experience. **Pagination** is implemented on both Search and Saved pages, with additionaly complexity on the Search page due to the uncertainty of page countes from external API.


### <ins>File Structures and Description</ins>
- **capstone/mycareerpath/** - Main application directory
  - **templates/mycareerpath/**
    - **layout.html** - Defines the overall app layout, including the navigation bar
    - **index.html** - Main landing page featuring search function, summary display, last edited entries, and most recent searched jobs
    - **login.html, register.html** - User authenticaation pages for login and registration
    - **search.html, saved_job.html** - Similar layouts for displaying searched jobs and saved jobs
    - **listing_item.html** - Template for formatting and styling individual job entries
    - **applied_job.html** - Tracker page displaying all user's applied and custom jobs
    - **add.html** - Form page allowing users to input custom job details
  - **static/mycareerpath/**
    - **info.js** - Javascript that handles client-server interactions.
    - **styles.scss, styles.css** - Sass stylesheet and compiled CSS for application styling.
  - **forms.py** - Registration and custom job creation forms.
  - **models.py** - Database models: User, Jobs, Saved, Applied and CustomJobs with class methods.
  - **util.py** - Timestamp conversion function that is used mutiple times in views.
- **requirements.txt** - Python packages: requests, python-dotenv
- **.env (not submitted)** - Contains API keys and SECRET_KEY.

### <ins>How to run</ins>
1. Install dependencies (requirements.txt)
2. Get a free subsciption API Key from **RapidApi: JSeach** ( source= https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch )
3. Create a **.env** file at root with:
   - SECRET_KEY=your_django_secret_key
   - JSEARCH_API_KEY=your_rapidapi_key
4. Run migrations and start the server

