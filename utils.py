from flask import json, Response
from app import app
from PIL import Image
import os
import jwt


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


upload_path = app.config['UPLOAD_FOLDER']


def json_response(data, status=200):
    response = Response(
        response=json.dumps(data),
        status=status,
        mimetype='application/json',
    )

    return response


class ValidationError(Exception):
    pass


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extenstion(filename):
    if not filename:
        raise ValidationError('File name invalid')

    return filename.rsplit('.', 1)[1].lower()


def upload_file(request, new_file_name):
    if request.method == 'POST':

        if 'file' not in request.files:
            raise ValidationError('No file part')

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            raise ValidationError('No selected file')

        if file and allowed_file(file.filename):
            file_name = '{}.png'.format(new_file_name)
            file.filename = file_name

            file_path = os.path.join(upload_path, file_name)
            file.save(file_path)

            Image.open(file_path).save(file_path)

            return file_name

        elif not allowed_file(file.filename):
            raise ValidationError('File extension not allowed')
        else:
            raise ValidationError('File extension not Valid')
    else:
        raise ValidationError('Please don\'t user POST')


def check_if_file_exists(uuid):
    file_name = '{}.png'.format(uuid)
    file_path = os.path.join(upload_path, file_name)

    return os.path.isfile(file_path)


def verify_token(token):
    
    secret_key = app.config['SECRET_KEY']
    
    try:
        # Must be encoded with same secret key defined in settings
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256', ])
        try:
            token_uuid = decoded_token['uuid']

        except KeyError:
            return False

        return token_uuid

    except jwt.exceptions.PyJWTError as e:
        return False
