# backend/classroom.py

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']

def get_classroom_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            # Use browser-based OAuth login on fixed port
            creds = flow.run_local_server(port=8080)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('classroom', 'v1', credentials=creds)

def list_courses():
    service = get_classroom_service()
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])
    return [course.get('name', 'Unnamed Course') for course in courses]

def get_assignments(course_id):
    service = get_classroom_service()
    results = service.courses().courseWork().list(courseId=course_id).execute()
    assignments = results.get('courseWork', [])
    return [assignment.get('title', 'Untitled Assignment') for assignment in assignments]
