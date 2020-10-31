from app import app
import json
from flask import Flask,request,jsonify
import sqlite3
import firebase_admin
from firebase_admin import credentials,auth
from werkzeug.utils import secure_filename
import os
upload_folder ="app/uploads"
allowed_extensions = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions

cred = credentials.Certificate(r"app/firebase_creds/dystopia-animal-adoption-app-firebase-adminsdk-1nwez-671835b09a.json")
firebase_admin.initialize_app(cred)
def verify(id_token):
    try:
        print("Starting verification")
        decoded_token = auth.verify_id_token(id_token)
        print(decoded_token)
        uid = decoded_token['uid']
        print("\n_______________user id_______________",uid)
        return uid
    except Exception as e:
        print(e)
        return "Invalid user id"



'''
API REQUIREMENTS:
-add a firebase user (POST) #wait for firebase
-add user profile (POST) with image - done
-get user profile by id(GET) #wait for firebase
-add a new contact form detail(POST) - done
-add a fosterer (POST) - done
-add adopter (POST) - done
-add blog(POST) - done
-display blogs(GET) - done
-add an animal -done
-display animal(basic details)-(GET) -done
-get all details of animal by id - (GET) -done
-get adopters of animal by id - (GET) - done
-add an image - done

'''

def db_connection():
    conn=None
    try:
        conn=sqlite3.connect('./app/dystopiadb.db')
    except sqlite3.Error as e:

        print(e)
    return conn

def add_image(image):
    conn=db_connection()
    cursor=conn.cursor()
    if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(upload_folder,filename))
                imagepath = upload_folder+"/"+filename
    cursor.execute("insert into photo (photo_url) values (?)",(imagepath,))
    conn.commit()
    cursor.execute("select max(photo_id) from photo")
    val=cursor.fetchall()[0][0]
    conn.close()
    return val

def get_animal_id():
    conn=db_connection()
    cursor=conn.cursor()
    cursor.execute("select max(animal_id) from animal")
    val=cursor.fetchall()[0][0]+1
    conn.close()
    return val

    

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

#Need to fix
@app.route('/api/v1/tempuser',methods=['POST'])
def userauth():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == 'POST':
        try:
            uid=request.form['firebase_uid']
            cursor.execute('INSERT INTO userauth (firebase_uid) VALUES (?)',(uid))
            conn.commit()
            conn.close()
            return jsonify({"status":"200 ok","message":"success"}),200
          
        except:
            conn.rollback()
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
            conn.close()
            return response_msg
          

@app.route('/api/v1/adduserprofile',methods=['POST'])
def userprofile():
    conn=db_connection()
    cursor=conn.cursor()
    id_token=request.headers['id_token']
    print(id_token)
    if request.method =='POST':
        try:
            if id_token:
                uid = verify(id_token)
            else:
                return "error in verification"
            firebase_uid=uid
            #profile_pic_id=1
            name=request.form['name']
            dob=request.form['dob']
            contact=request.form['contact']
            user_address=request.form['user_address']
            user_long=request.form['user_long']
            user_lat=request.form['user_lat']
            email=request.form['email']
            occupation=request.form['occupation']
            image = request.files['file']
            profile_pic_id=add_image(image)
            cursor.execute('INSERT INTO user_profile (firebase_uid,profile_pic_id,name,dob,contact,user_address,user_long,user_lat,email,occupation) VALUES (?,?,?,?,?,?,?,?,?,?)',(firebase_uid,profile_pic_id,name,dob,contact,user_address,user_long,user_lat,email,occupation))
            conn.commit()
            response_msg=jsonify({"status":"200 ok","message":"success"}),200
            conn.close()
            return response_msg
        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
            conn.close()
            return response_msg
            

#Incomplete
@app.route('/api/v1/user_profile',methods=['GET'])
def getuserprofile():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == "GET":
        try:
            id_token=request.headers['id_token']
            if id_token:
                uid = verify(id_token)
            else:
                return "error in verification"
            firebase_uid=uid
            conn.row_factory=sqlite3.Row
            cursor.execute("select name,dob,contact,user_address,user_long,user_lat,email,occupation from user_profile where firebase_uid=(?)",(firebase_uid))
            rows=cursor.fetchall()
            list=[]
            for i in rows:
                dict={"name":i[0],"dob":i[1],"contact":i[2],"user_address":i[3],"user_long":i[4],"user_lat":i[5],"email":i[6],"occupation":i[7]}
                list.append(dict)            
            return jsonify({'user_profile':list}),200
        except sqlite3.Error as e:
            print(e)
            return jsonify({"error":"400","message":"Bad request"}),400


@app.route('/api/v1/contact',methods=['POST','GET'])
def contact():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == 'POST':
        try:
            nm=request.form['name']
            em=request.form['email']
            msg=request.form['message']
            cursor.execute('INSERT INTO contact (name,email,message) VALUES (?,?,?)',(nm,em,msg))
            conn.commit()
            response_msg=jsonify({"status":"200 ok","message":"success"}),200
            conn.close()
            return response_msg
           
        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
            conn.close()
            return response_msg
           


@app.route('/api/v1/fosterer',methods=['POST','GET'])
def fosterer():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == 'POST':
        try:
            nm=request.form['name']
            em=request.form['email']
            rsn=request.form['reason']
            contact=request.form['contact']
            animal=request.form['animal_type']
            address=request.form['foster_address']
            longi=request.form['foster_long']
            lat=request.form['foster_lat']
            cursor.execute('INSERT INTO fosterer (name,email,reason,contact,animal_type,foster_address,foster_long,foster_lat) VALUES (?,?,?,?,?,?,?,?)',(nm,em,rsn,contact,animal,address,longi,lat))
            conn.commit()
            response_msg=jsonify({"status":"200 ok","message":"success"}),200
            conn.close()
            return response_msg

        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
           
            conn.close()
            return response_msg

@app.route('/api/v1/adopter',methods=['POST','GET'])
def adopter():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == 'POST':
        try:
            '''
            id_token=request.headers['id_token']
            if id_token:
                uid = verify(id_token)
            else:
                return "error in verification"
            adopter_id=uid
            '''
            animal_id=1
            adopter_id='XXXXX'
            job_dur=request.form['job_duration']
            emp_contact=request.form['employer_contact']
            exp=request.form['experience']
            day_time=request.form['day_time']
            share=request.form['share_household']
            house_type=request.form['house_type']
            cursor.execute('INSERT INTO adopter(adopter_id,animal_id,job_duration,employer_contact,experience,day_time,share_household,house_type) VALUES (?,?,?,?,?,?,?,?)',(adopter_id,animal_id,job_dur,emp_contact,exp,day_time,share,house_type))
            conn.commit()
            response_msg=jsonify({"status":"200 ok","message":"success"}),200
            conn.close()
            return response_msg
        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
            conn.close()
            return response_msg

@app.route('/api/v1/testgetadopters',methods=['POST'])
def testgetadopter():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == "POST":
        try:
            animal_id=request.form['animal_id']
            conn.row_factory=sqlite3.Row
            cursor.execute("select O.name,O.contact,O.email,O.occupation,A.job_duration,A.employer_contact,A.experience,A.day_time,A.share_household,A.house_type from adopter A JOIN user_profile O ON (A.adopter_id=O.firebase_uid) where A.animal_id=(?)",(animal_id))
            rows=cursor.fetchall()
            list=[]
            for i in rows:
                dict={"name":i[0],"contact":i[1],"email":i[2],"occupation":i[3],"job_duration":i[4],"employer_contact":i[5],"experience":i[6],"day_time":i[7],"share_household":i[8],"houste_type":i[9]}
                list.append(dict)            
            return jsonify({'adopter_details':list})
        except sqlite3.Error as e:
            print(e)
            return "Error occured"
@app.route('/api/v1/getadopters/<animal_id>',methods=['GET'])
def getadopter(animal_id):
    if request.method == "GET":
        try:
            conn.row_factory=sqlite3.Row
            cursor.execute("select O.name,O.contact,O.email,O.occupation,A.job_duration,A.employer_contact,A.experience,A.day_time,A.share_household,A.house_type from adopter A JOIN user_profile O ON (A.adopter_id=O.firebase_uid) where A.animal_id=(?)",(animal_id))
            rows=cursor.fetchall()
            list=[]
            for i in rows:
                dict={"name":i[0],"contact":i[1],"email":i[2],"occupation":i[3],"job_duration":i[4],"employer_contact":i[5],"experience":i[6],"day_time":i[7],"share_household":i[8],"houste_type":i[9]}
                list.append(dict)            
            return jsonify({'adopter_details':list})
        except sqlite3.Error as e:
            print(e)
            return "Error occured"

@app.route('/api/v1/blog',methods=['POST','GET'])
def blog():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == 'POST':
        try:
            image = request.files['file']
            cover_photo_id=add_image(image)
            author=request.form['author']
            published=request.form['published_on']
            content=request.form['content']
            cursor.execute('INSERT INTO blog(cover_photo_id,author,published_on,content) VALUES (?,?,?,?)',(cover_photo_id,author,published,content))
            conn.commit()
            response_msg=jsonify({"status":"200 ok","message":"success"}),200
            conn.close()
            return response_msg
        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
            conn.close()
            return response_msg
    elif request.method == "GET":
        try:
            conn.row_factory=sqlite3.Row
            cursor.execute("select P.photo_url,B.author,B.published_on,B.content from blog B JOIN photo P ON (P.photo_id=B.cover_photo_id)")
            rows=cursor.fetchall()
            list=[]
            for i in rows:
                dict={"cover_photo_id":i[0],"author":i[1],"published_on":i[2],"content":i[3]}
                list.append(dict)            
            return jsonify({'blogs':list}),200
           
        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            conn.close()
            return jsonify({"error":"400","message":"Bad request"}),400

@app.route('/api/v1/animal',methods=['POST','GET'])
def animal():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == 'POST':
        try:
            '''
            id_token=request.headers['id_token']
            if id_token:
                uid = verify(id_token)
            else:
                return "error in verification"
            own_id=uid
            '''
            own_id="XXXXX"
            nm=request.form['name']
            age=request.form['age']
            gen=request.form['gender']
            breed=request.form['breed']
            descrip=request.form['descrip']
            adopted=0
            approved=1
            house_trained=request.form['house_trained']
            neutered=request.form['neutered']
            vaccines=request.form['vaccines']
            rehome_reason=request.form['rehome_reason']
            files = request.files.getlist('file')
            for image in files:
                photo_id=add_image(image)
                animal_id=get_animal_id()
                cursor.execute("insert into animal_photo(photo_id,animal_id) values (?,?)",(photo_id,animal_id))
                conn.commit()
            cursor.execute('INSERT INTO animal (owner_id,name,age,gender,breed,descrip,adopted,approved,house_trained,neutered,vaccines,rehome_reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(own_id,nm,age,gen,breed,descrip,adopted,approved,house_trained,neutered,vaccines,rehome_reason))
            conn.commit()
            response_msg=jsonify({"status":"200 ok","message":"success"}),200
            conn.close()
            return response_msg
            
        except sqlite3.Error as e:
            conn.rollback()
            print(e)
            response_msg=jsonify({"error":"400","message":"Bad request"}),400
            conn.close()
            return response_msg
           
    elif request.method == "GET":
        try:
            conn.row_factory=sqlite3.Row
            cursor.execute("select animal_id,name,age,gender from animal where approved=1 and adopted=0")
            rows=cursor.fetchall()
            list=[]
            for i in rows:
                dict={"animal_id":i[0],"name":i[1],"age":i[2],"gender":i[3]}
                cursor.execute("select P.photo_url from photo P JOIN animal_photo A ON (P.photo_id=A.photo_id) where A.animal_id=(?)",(i[0],))
                dict["animal_photos"]=cursor.fetchall()
                list.append(dict)  
                      
            return jsonify({'animals':list}),200
        except sqlite3.Error as e:
            print(e)
            return jsonify({"error":"400","message":"Bad request"}),400
   

@app.route('/api/v1/animaldetail/<animal_id>',methods=['GET'])
def animaldetail(animal_id):
    conn=db_connection()
    cursor=conn.cursor()
    if request.method == "GET":
        try:
            conn.row_factory=sqlite3.Row
            cursor.execute("select A.animal_id,A.name,A.age,A.gender,A.breed,A.descrip,A.house_trained,A.neutered,A.vaccines,A.rehome_reason,O.name,O.contact,O.email,O.user_address,O.user_long,O.user_lat from animal A JOIN user_profile O ON (A.owner_id=O.firebase_uid) where animal_id=(?)",(animal_id))
            rows=cursor.fetchall()
            list=[]
            for i in rows:
                dict={"animal_id":i[0],"name":i[1],"age":i[2],"gender":i[3],"breed":i[4],"descrip":i[5],"house_trained":"Yes" if i[6] else "No","neutered":"Yes" if i[7] else "No","vaccines":i[8],"rehome_reason":i[9],"owner_name":i[10],"owner_contact":i[11],"owner_email":i[12],"address":i[13],"long":i[14],"lat":i[15]}
                cursor.execute("select P.photo_url from photo P JOIN animal_photo A ON (P.photo_id=A.photo_id) where A.animal_id=(?)",(animal_id))
                dict["animal_photos"]=cursor.fetchall()
                list.append(dict)            
            return jsonify({'animal_detail':list}),200
        except sqlite3.Error as e:
            print(e)
            return jsonify({"error":"400","message":"Bad request"}),400


        
