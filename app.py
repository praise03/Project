from flask import Flask
from flask import render_template, url_for, flash, redirect, request
from PIL import Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from wtforms import SubmitField, validators
import os, secrets
import datetime
import time
from wtforms.validators import ValidationError
import pandas as panda
from pymerkle import *
from hashlib import sha256
from PIL import Image, ImageDraw, ImageFont
import qrcode
from pyzbar.pyzbar import decode
from pymongo import MongoClient
import random, string

app = Flask(__name__)
app.config['SECRET_KEY'] = "5791628bb0b13ce0c676dfde280ba245"
client = MongoClient()
database = client.blockchain_database.certificates
blockchain_db = client.blockchain_database.blocks
private_key = ''
authenticated = 0


def authenticate():
    global authenticated
    authenticated = 1


class UploadForm(FlaskForm):
    picture = FileField("Upload", validators=[DataRequired(), FileAllowed(['xlsx','xls'])])
    submit = SubmitField('Upload')


class VerifyForm(FlaskForm):
    picture = FileField("Upload",  validators=[DataRequired(), FileAllowed(['png'])])
    submit = SubmitField('Verify')


@app.route("/login", methods=['GET', 'POST'])
def login():
    global private_key
    global authenticated
    global authenticate
    if authenticated == 1:
        return redirect(url_for('home'))
    private_key = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    return render_template('login.html', private_key=private_key, authenticate=authenticate)


@app.route("/", methods=['GET', 'POST'])
def home():
    form = UploadForm()
    if form.validate_on_submit():
        start = time.time()
        if form.picture.data:
            dataFrame = panda.read_excel(form.picture.data)
            tempStudentsArray = []
            studentsArray = []
            remainder = len(dataFrame)
            for i in range(len(dataFrame)):
                remainder -= 1
                for j in range(len(list(dataFrame))):
                    tempStudentsArray.append(dataFrame.iloc[i, j])
                c = tempStudentsArray
                tempStudentsArray = []

                if len(studentsArray) < 10:
                    studentsArray.append(c)
                else:
                    studentsArray = []
                    studentsArray.append(c)
                if len(studentsArray) == 10:
                    merkleTree = MerkleTree(security=False, raw_bytes=False)
                    for student in studentsArray:
                        student[3] = str(student[3])
                        concat = ''
                        try:
                            concat = "+".join(student)
                        except:
                            flash('An Error Occured While Uploading Credentials. Ensure Spreadsheet is of Valid Format and Does Not Contain Duplicate Values', 'danger')
                            return redirect(url_for('home'))
                        studentHash = sha256(concat.encode()).hexdigest()
                        newuser = ({
                            "name": student[0],
                            "Matric No": student[1],
                            "Course": student[2],
                            "Year": student[3],
                            "Hash": studentHash
                        })
                        database.insert_one(newuser)
                        merkleTree.encryptRecord(concat)
                    for student in studentsArray:
                        student[3] = str(student[3])
                        concat = ''
                        try:
                            concat = "+".join(student)
                        except:
                            flash('An Error Occured While Uploading Credentials. Ensure Spreadsheet is of Valid Format and Does Not Contain Duplicate Values', 'danger')
                            return redirect(url_for('home'))
                        studentHash = sha256(concat.encode()).hexdigest()
                        img = Image.open('Certificate_Template.png')
                        qr = qrcode.QRCode(box_size=1)
                        qr.add_data([str(studentHash), merkleTree.get_commitment().decode("utf-8")], optimize=0)
                        qr.make()
                        test = qr.make_image(fill_color="black", back_color="white").convert('RGB')

                        img.paste(test, (355, 490))

                        I1 = ImageDraw.Draw(img)
                        font = ImageFont.truetype('font.ttf', 30)
                        I1.text((300, 160), student[0], font=font, fill=(0, 0, 0))
                        I1.text((288, 256), student[1], font=font, fill=(0, 0, 0))
                        I1.text((240, 345), student[2], font=font, fill=(0, 0, 0))
                        I1.text((342, 425), student[3], font=font, fill=(0, 0, 0))

                        student[1] = student[1].replace('/', '')
                        img.save('uploads/certs/' + student[1] + '.png')
                    timestamp = datetime.datetime.now()
                    previous_hash = ''

                    if (blockchain_db.count_documents({}) > 0):
                        Block = blockchain_db.find().sort('_id', -1).limit(1)
                        for b in Block:
                            previous_hash = b["root_hash"]
                    else:
                        previous_hash = "None"
                    root_hash = merkleTree.get_commitment().decode("utf-8")
                    block = ({
                        "timestamp": timestamp,
                        "previous_hash": previous_hash,
                        "root_hash": root_hash
                    })
                    blockchain_db.insert_one(block)
                    with open('structure', 'w') as f:
                        f.write(merkleTree.__repr__())
                    merkleTree.export('uploads/trees/' + merkleTree.get_commitment().decode("utf-8") + '.json')

            if remainder < 1:
                merkleTree = MerkleTree(security=False, raw_bytes=False)
                for student in studentsArray:
                    student[3] = str(student[3])
                    concat = ''
                    try:
                        concat = "+".join(student)
                    except:
                        flash('An Error Occured While Uploading Credentials. Ensure Spreadsheet is of Valid Format and Does Not Contain Duplicate Values', 'danger')
                        return redirect(url_for('home'))
                    studentHash = sha256(concat.encode()).hexdigest()
                    newuser = ({
                        "name": student[0],
                        "Matric No": student[1],
                        "Course": student[2],
                        "Year": student[3],
                        "Hash": studentHash
                    })
                    database.insert_one(newuser)
                    merkleTree.encryptRecord(concat)
                for student in studentsArray:
                    student[3] = str(student[3])
                    concat = ''
                    try:
                        concat = "+".join(student)
                    except:
                        flash('An Error Occured While Uploading Credentials. Ensure Spreadsheet is of Valid Format and Does Not Contain Duplicate Values', 'danger')
                        return redirect(url_for('home'))
                    studentHash = sha256(concat.encode()).hexdigest()
                    img = Image.open('Certificate_template.png')
                    qr = qrcode.QRCode(box_size=1)
                    qr.add_data([str(studentHash), merkleTree.get_commitment().decode("utf-8")], optimize=0)
                    qr.make()
                    test = qr.make_image(fill_color="black", back_color="white").convert('RGB')

                    img.paste(test, (355, 490))

                    I1 = ImageDraw.Draw(img)
                    font = ImageFont.truetype('font.ttf', 30)
                    I1.text((300, 160), student[0], font=font, fill=(0, 0, 0))
                    I1.text((288, 256), student[1], font=font, fill=(0, 0, 0))
                    I1.text((240, 345), student[2], font=font, fill=(0, 0, 0))
                    I1.text((342, 425), student[3], font=font, fill=(0, 0, 0))

                    student[1] = student[1].replace('/', '')
                    img.save('uploads/certs/' + student[1] + '.png')

                timestamp = datetime.datetime.now()
                previous_hash = ''

                if (blockchain_db.count_documents({}) > 0):
                    Block = blockchain_db.find().sort('_id', -1).limit(1)
                    for b in Block:
                        previous_hash = b["root_hash"]
                else:
                    previous_hash = "None"
                root_hash = merkleTree.get_commitment().decode("utf-8")
                block = ({
                    "timestamp": timestamp,
                    "previous_hash": previous_hash,
                    "root_hash": root_hash
                })
                blockchain_db.insert_one(block)
                with open('structure', 'w') as f:
                    f.write(merkleTree.__repr__())
                merkleTree.export('uploads/trees/' + merkleTree.get_commitment().decode("utf-8") + '.json')
            stop = time.time()
            timeelapsed = round(stop - start, 2)
            flash('Sucess! Uploaded ' + str(len(dataFrame)) + ' credentials in ' + str(timeelapsed) + 'sec(s)',
                  'success')

    return render_template("home.html", form=form, private_key=private_key)


@app.route("/verify", methods=['GET', 'POST'])
def verify():
    form = VerifyForm()
    info = []

    if(form.validate_on_submit()):
        if form.picture.data:
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(form.picture.data.filename)
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(app.root_path, 'uploads', picture_fn)
            i = Image.open(form.picture.data)
            i.save(picture_path)
            # i = Image.open(form.picture.data)
            decocdeQR = decode(Image.open('uploads/' + picture_fn))

            if(not decocdeQR):
                flash('Credentials Not Found. Image Does Not Contain A Valid QR Code', 'danger')
                return redirect(url_for('verify'))
            decodedCert = ''
            try:
                decodedCert = decocdeQR[0].data.decode('ascii')
            except:
                flash('Credentials Not Found. Invalid QR Code', 'danger')
                return redirect(url_for('verify'))
            certhash = decodedCert[2:66]
            roothash = decodedCert[70:134]

            if (blockchain_db.count_documents({'root_hash': roothash})):
                loaded_tree = MerkleTree.loadFromFile('uploads/trees/' + roothash + '.json')
                challenge = {'checksum': certhash}
                merkle_proof = loaded_tree.merkleProof(challenge)

                if (validateProof(merkle_proof)):
                    flash("Credentials Exists!!!", "success")
                    for i in database.find({'Hash': certhash}):
                        info = i
            else:
                flash("Credentials Not Found", "danger")
    return render_template('verify.html', form=form, info=info)


@app.route("/reset", methods=['GET', 'POST'])
def reset():
    blockchain_db.delete_many({})
    database.delete_many({})
    return redirect(url_for('home'))
