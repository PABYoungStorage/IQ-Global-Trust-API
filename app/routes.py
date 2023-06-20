import os
from werkzeug.utils import secure_filename
from flask import Blueprint, current_app, jsonify, request, session, flash
from .lib.mailservice import MailSender
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import time

# Create blueprint for authentication routes
auth_routes = Blueprint('auth', __name__, url_prefix='/auth')


@auth_routes.get("/usercheck")
def UserCheck():
    try:
        id = request.args.get("id")
        if current_app.config["SESSION_ID"] == id:
            return jsonify({"message": "userVerified", "status": True}), 200
        else:
            return jsonify({"message": "Please Login And Continue", "status": False}), 401
    except Exception as e:
        return jsonify({'message': str(e), "status": False}), 401

 
@auth_routes.post('/signin')
def signin():
    try:
        data = request.json
        admin_name = current_app.config['ADMIN_USER']
        admin_pwd = current_app.config['ADMIN_PASSWORD']

        username = data.get('username')
        password = data.get('password')

        if username == admin_name and password == admin_pwd:
            return {"message": "Logged In Successfully", "status": True,'data': current_app.config["SESSION_ID"]}
        else:
            return {"message": "Enter Valid Credentials", "status": False}

    except Exception as e:
        return jsonify({'message': str(e), "status": False}), 404


@auth_routes.get('/signout')
def signout():
    # Implement signout logic here
    session.pop('user')
    return jsonify({"message": "Signout Successful", "status": True})


# Create blueprint for main routes
main_routes = Blueprint('main', __name__, static_folder='public')


@main_routes.route('/')
def index():
    # # Access the MongoDB instance using the Flask app's context
    # db = current_app.config['MONGO']

    # # Access a collection and perform operations
    # collection = db.users
    # data = collection.find_one()
    # print(data)
    return jsonify({"message": "welcome to the trust API service", "status": True})


@main_routes.route('/send_email')
def send_email(email, otp):
    # Access the Mail instance using the Flask app's context
    mail = current_app.config['MAIL']
    to = f"{email}"
    body = f"{otp}"
    message = "OTP Testing"

    MailSender(mail, to, body, message)

    return jsonify({"message": "Email sent"})


# To get the list of events using GET Method
# Using Same Function We can Also Get The Number Of events by setting count(query Parameter) to 1
# query parameter example = http://localhost:8000/events?count=1

@main_routes.get("/events")
def events_get_all():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        # title = request.args.get('title')
        title = request.args.get('count')
        if title == "1":
            data = list(db.events.find())
            return {"message": len(data), "status": True}
        else:

            data1 = list(db.events.find())
            for i, doc in enumerate(data1):
                data1[i]['_id'] = str(doc['_id'])

            return jsonify(data1)

    except Exception as e:
        return {"message": str(e), "status": False}


# To Get All The Details required for Event page
# The Details are Title,event,description,amount expected,amount collected and thumbnail images
@main_routes.post("/events")
def events():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        title = request.form.get('title')
        event = request.form.get('event')
        desc = request.form.get('description')
        amt_exp = request.form.get('amount expected')
        amt_col = request.form.get('amount collected')

        if not title or not event or not desc or not amt_exp or not amt_col:
            return {"message": "Please Enter All Fields", "status": False}

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_image = title + "_" + filename
                new_dest = current_app.config['UPLOAD_FOLDER'] + \
                    "/thumbnail" + "/" + title
                if os.path.exists(new_dest):
                    file.save(os.path.join(new_dest, new_image))
                else:
                    os.makedirs(new_dest)
                    file.save(os.path.join(new_dest, new_image))

        db.events.insert_one(
            {"title": title, "event": event, "description": desc, "event_image": new_dest})
        return {"message": "Image Uploaded Successfully", "status": True}

    except Exception as e:
        return {"message": str(e), "status": False}


# This is the GET method for gallery page to get all the images path from the database to showcase
# in the Gallery Page

@main_routes.get("/gallery")
def gallery_get():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        title = request.args.get('title')
        dbdata = dict(db.gallery.find_one({"title": title}))
        dbdata['_id'] = str(dbdata["_id"])
        return {"message": dbdata, "status": True}

    except Exception as e:
        return {"message": str(e), "status": False}


# This Is The POST Method For The Gallery Page to Upload The images of the Event For the First Time
# After Adding The Event . We Can Get Multiple Images In This Route

@main_routes.post("/gallery")
def gallery():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        title = request.form.get('title')
        if not title:
            return {"message": "Please Enter Event Name", "status": False}
        if db.gallery.find_one({"title": title}):
            return {"message": "Event Already Exists", "status": False}
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
            file = request.files.getlist('file')
            data = []
            i = 1
            for img in file:
                if img.filename == '':
                    flash('No selected file')
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    new_image = title + "_" + filename
                    new_dest = current_app.config['UPLOAD_FOLDER'] + \
                        "/gallery" + "/" + title
                    if os.path.exists(new_dest):
                        img.save(os.path.join(new_dest, new_image))
                    else:
                        os.makedirs(new_dest)
                        img.save(os.path.join(new_dest, new_image))
                data.append(f"{new_image}")
                i += 1

            db.gallery.insert_one({"title": title, "images": data})

        return {"message": "Images Uploaded Successfully", "status": True}

    except Exception as e:
        return {"message": str(e), "status": False}


# This is The PATCH Method for the gallery page to Updata the Images Of the particular event
# We can upload Multiple Images In this Route

@main_routes.patch("/gallery")
def gallery_add():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        title = request.form.get('title')

        if request.method == 'PATCH':
            if 'file' not in request.files:
                flash('No file part')
            file = request.files.getlist('file')
            dbdata = dict(db.gallery.find_one({"title": title}))
            for img in file:
                if img.filename == '':
                    flash('No selected file')
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    new_image = title + "_" + filename
                    if new_image in dbdata["images"]:
                        continue
                    new_dest = current_app.config['UPLOAD_FOLDER'] + \
                        "/gallery" + "/" + title
                    if os.path.exists(new_dest):
                        img.save(os.path.join(new_dest, new_image))
                    else:
                        os.makedirs(new_dest)
                        img.save(os.path.join(new_dest, new_image))
                dbdata["images"].append(f"{new_image}")

            db.gallery.update_one(
                {"title": title}, {"$set": {"images": dbdata["images"]}})

        return {"message": "Images Uploaded Successfully", "status": True}

    except Exception as e:
        return {"message": str(e), "status": False}


# This Is the Delete Method for the Gallery Page To Delete The Images In The Gallery Page
# We can delete both single and a set of images using this Route

@main_routes.delete("/gallery")
def gallery_delete():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}
        title = request.json.get('title')
        data = request.json.get('images')
        if isinstance(data, list):
            for i in data:
                img = i
                gallery_del_many(title, img)
        else:
            gallery_del_one(title, data)
        return {"message": "Image Deleted Successfully", "status": True}
    except Exception as e:
        return {"message": str(e), "status": False}


@main_routes.get("/volunteers")
def volunteers_show():
    try:
        db = current_app.config['MONGO']

        title = request.args.get('count')
        if title == "true":
            data = db.events.find({"status": True})
            return {"message": data, "status": True}
        else:

            data1 = list(db.events.find())
            for i, doc in enumerate(data1):
                data1[i]['_id'] = str(doc['_id'])

            return jsonify(data1)

    except Exception as e:
        return {"message": str(e), "status": False}

# This Route is for getting all the inputs required for applying as an volunteer in the organisation
# This Route also gets image of the volunteer


@main_routes.post("/volunteers")
def volunteers_apply():
    try:
        db = current_app.config['MONGO']

        formdata = request.form
        check = ['firstname', 'lastname', 'address', 'district', 'state', 'country',
                 'pincode', 'email', 'phone', 'areaofintrest', 'profession', 'availability']

        finaldata = {}
        for txt in check:
            inputdata = formdata.get(txt)
            if not inputdata:
                return {"message": "Please Enter All Fields"}
            else:
                finaldata[txt] = inputdata

        data_id = db.volunteers.insert_one(finaldata).inserted_id

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_image = finaldata["firstname"] + "_" + \
                    str(int(time.time())) + "_" + filename
                new_dest = current_app.config['UPLOAD_FOLDER'] + "/volunteers"
                if os.path.exists(new_dest):
                    file.save(os.path.join(new_dest, new_image))
                else:
                    os.makedirs(new_dest)
                    file.save(os.path.join(new_dest, new_image))

            db.volunteers.update_one(
                {"_id": data_id}, {"$set": {"image_name": new_image, "status": False}})
        return {"Message": "Volunteer Applied Successfully", "status": True}

    except Exception as e:
        return {"message": str(e), "status": False}

# To Show All The Volunteers applied to the admin page


@main_routes.get("/admin_volunteers")
def admin_volunteers_show():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        data = list(db.volunteers.find())
        for i, doc in enumerate(data):
            data[i]['_id'] = str(doc['_id'])

        return jsonify(data)

    except Exception as e:
        return {"message": str(e), "status": False}

# This Route is used To approve The Volunteers who applied to be an volunteer
# If the url comes with image id as paramter then the volunteer is approve


@main_routes.patch("/admin_volunteers")
def admin_volunteers_approve():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        image = request.args.get("image_id")

        if image:
            db.volunteers.update_one({"image_name": image}, {
                                     "$set": {"status": True}})
            return {"message": "Volunteer Approved Successfully", "status": True}
        else:
            return {"message": "Please Provide Image ID", "status": False}

    except Exception as e:
        return {"message": str(e), "status": False}


@main_routes.delete("/admin_volunteers")
def admin_volunteers_reject():
    try:
        if "user" not in session:
            return {"message": "Please Login And Continue", "status": False}

        db = current_app.config['MONGO']
        image = request.args.get("image_id")

        if image:
            db.volunteers.delete_one({"image_name": image})
            return {"message": "Volunteer Rejected Successfully", "status": True}
        else:
            return {"message": "Please Provide Image ID", "status": False}

    except Exception as e:
        return {"message": str(e), "status": False}


# This Function is to delete a single image from the gallery page based on the condition in the above
# Function

def gallery_del_one(title, data):
    try:
        db = current_app.config['MONGO']
        db.gallery.update_one({"title": title}, {"$pull": {"images": data}})
        # os.remove(current_app.config['UPLOAD_FOLDER'] + "/gallery" + data)

    except Exception as e:
        return {"message": str(e), "status": False}


# This Function is to delete multiple images from the gallery page based on the condition in the above
# Function

def gallery_del_many(title, img):
    try:
        db = current_app.config['MONGO']
        db.gallery.update_one({"title": title}, {"$pull": {"images": img}})
        # os.remove(current_app.config['UPLOAD_FOLDER'] + "/gallery" + item)

    except Exception as e:
        return {"message": str(e), "status": False}

# This Function is used to check the extensions of the file to be uploaded in the images section
# This Method Only allows a set of extensions that are defined in the config.py file


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in current_app.config["ALLOWED_EXTENSIONS"]
