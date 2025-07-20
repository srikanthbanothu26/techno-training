from decouple import config


class Config:
    SECRET_KEY = "secret-key"
    SQLALCHEMY_DATABASE_URI = "mysql://avnadmin:AVNS_mEQfCEIkupo_GdLjlhc@mysql-323302ad-banothusrikanth267-d588.a.aivencloud.com:26621/defaultdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDERS = {
        'python': {
            'notes': 'upload_python_notes',
            'recordings': 'upload_python_recordings',
            'assignments': 'upload_python_assignments',
            'assessments': 'upload_python_assessments'
        },
        'java': {
            'notes': 'upload_java_notes',
            'recordings': 'upload_java_recordings',
            'assignments': 'upload_java_assignments',
            'assessments': 'upload_java_assessments'
        },
        'digitalmarketing': {
            'notes': 'upload_DigitalMarketing_notes',
            'recordings': 'upload_digitalmarketing_recordings',
            'assignments': 'upload_DigitalMarketing_assignments',
            'assessments': 'upload_DigitalMarketing_assessments'
        },
        'testingtools': {
            'notes': 'upload_testingtools_notes',
            'recordings': 'upload_testingtools_recordings',
            'assignments': 'upload_testingtools_assignments',
            'assessments': 'upload_testingtools_assessments'
        }
    }
