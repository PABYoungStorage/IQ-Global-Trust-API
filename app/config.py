# Flask Configuration
SECRET_KEY = 'dev'
DEBUG = True

# MongoDB Configuration
MONGO_URI = 'mongodb://trustadmin:dotmail123@mongodb.youngstorage.in:27017/?authSource=trust'
MONGO_DBNAME = 'trust'

# Email Configuration
MAIL_SERVER = 'smtp.office365.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'flora63mcdaniel@outlook.com'
MAIL_PASSWORD = 'flora63@mcdaniel'
MAIL_DEFAULT_SENDER = 'flora63mcdaniel@outlook.com'

# Admin Credentials
ADMIN_USER = 'trustadmin'
ADMIN_PASSWORD = 'dotmail123'

# Image Config
UPLOAD_FOLDER = '/home/bhadri/project/global_trust_api/app/public'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])