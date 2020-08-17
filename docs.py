from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
from ocr import image_to_text
from flask import Flask, request, jsonify
import json


app = Flask(__name__)


def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/classroom.coursework.students',
              'https://www.googleapis.com/auth/classroom.courses']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    doc_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    class_service = build('classroom', 'v1', credentials=creds)

    # Retrieve the documents contents from the Docs service.
    # document = doc_service.documents().get(documentId=DOCUMENT_ID).execute()

    # print('The title of the document is: {}'.format(document.get('title')))
    '''
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, folders(id, name)").execute()
    items = results.get('folders', [])

    if not items:
        print('No folders found.')
    else:
        print('Folders:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    '''
    return (doc_service, drive_service, class_service)


def id_by_name(name, folder_id, service):
    page_token = None
    id = ""
    while True:
        if (folder_id is None):
            response = service.files().list(q="name = '" + name + "'",
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()
        else:
            response = service.files().list(q="name = '" + name + "' and '" + folder_id + "' in parents",
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            id = file.get('id')
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return id


def create_document(title, folder_id, service):
    if folder_id is None:
        metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
    else:
        metadata = {
            'name': title,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.document'
        }
    doc = service.files().create(body=metadata, fields='id').execute()

    doc_id = doc.get('id')
    return doc_id

def add_attachment(course_id, assignment_id, submission_id, attachment_id, service):

    request = {
        'addAttachments': [
            {'driveFile': {'id': attachment_id}}
        ]
    }
    print(course_id)
    print(assignment_id)
    print(submission_id)
    service.courses().courseWork().studentSubmissions().modifyAttachments(
        courseId=course_id,
        courseWorkId=assignment_id,
        id=submission_id,
        body=request).execute()

def insert_text(text, id, service):

    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': text
            }
        }
    ]

    result = service.documents().batchUpdate(
        documentId=id, body={'requests': requests}).execute()

def create_assignment(course_id, attachment_ids, title, description, service):
    materials = []
    for id in attachment_ids:
        materials.append({'driveFile': {'driveFile': {'id': id}}})
    print(course_id)
    print(attachment_ids)
    print(title)
    print(description)
    print(materials)
    courseWork = {
        'title': title,
        'description': description,
        'materials': materials,
        'workType': 'ASSIGNMENT',
        'state': 'PUBLISHED',
    }

    courseWork = service.courses().courseWork().create(
        courseId=course_id, body=courseWork).execute()

    print('Assignment created with ID {0}'.format(courseWork.get('id')))
    return courseWork.get('id')

def download_file(id, service):
    request = service.files().get_media(fileId=id)
    fh = io.FileIO('image.jpg', 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def find_course_id(name, service):
    courses = service.courses().list().execute()
    course_id = None
    print(courses)
    for c in courses['courses']:
        if (c['name'] == name):
            course_id = c['id']
            return course_id


def classwork(course, assignment, service):
    submissions = []

    course_id = find_course_id(course, service)

    assignments = service.courses().courseWork().list(courseId=course_id).execute()

    assignment_id = None
    print(assignments)
    for a in assignments['courseWork']:
        if (a['title'] == assignment):
            assignment_id = a['id']
            break

    result = service.courses().courseWork().studentSubmissions().list(courseId=course_id,
                                                                      courseWorkId=assignment_id).execute()
    print(result)
    for item in result['studentSubmissions']:
        s_id = item['id']
        file = item['assignmentSubmission']['attachments'][0]['driveFile']
        title = file['title']
        d_id = file['id']
        submissions.append({"title": title, "submission_id": s_id, "drive_id": d_id})
    print(submissions)
    return (submissions, course_id, assignment_id)

@app.route("/generate_docs", methods=["GET"])
def generate_docs():
    service = main()
    args = request.args
    if (args['course'] != "") & (args['assignment'] != ""):
        print(args['assignment'])
        print(args['course'])
        sub = classwork(args['course'], args['assignment'], service[2])
        classroom = id_by_name(args['assignment'], None, service[1])
        for item in sub[0]:
            download_file(item['drive_id'], service[1])
            new_id = create_document(item['title'], classroom, service[1])
            insert_text(image_to_text(), new_id, service[0])
            add_attachment(sub[1], sub[2], item['submission_id'], new_id, service[2])

    return jsonify({"status": "success"})

@app.route("/publish", methods=["GET"])
def publish():
    service = main()
    args = request.args
    if (args['files'] != "") & (args['description'] != "") & (args['title'] != "") & (args['course'] != ""):
        files = json.loads(args['files'])['files']
        print(args['description'])
        print(args['title'])
        attachment_ids = []
        for item in files:
            attachment_id = id_by_name(item, None, service[1])
            download_file(attachment_id, service[1])
            new_id = create_document(item.split(".")[0], None, service[1])
            insert_text(image_to_text(), new_id, service[0])
            attachment_ids.append(attachment_id)
            attachment_ids.append(new_id)
        course_id = find_course_id(args['course'], service[2])
        assignment_id = create_assignment(course_id, attachment_ids, args['title'], args['description'], service[2])

    return jsonify({"status": "success"})

app.run()