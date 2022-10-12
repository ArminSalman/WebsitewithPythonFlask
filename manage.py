from flask import Flask,redirect,render_template,flash,url_for,session,logging,request
from flask_wtf import FlaskForm
from wtforms import Form,validators,form,StringField,TextAreaField,PasswordField,SelectField
from sqlite3 import IntegrityError,InterfaceError
import sqlite3 as sql
from flask_wtf import FlaskForm
from SchoolList import schoolList,findSchoolWebAdress,teacherVerifyControl
from passlib.hash import sha256_crypt
from functools import wraps
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ogretmenim.com/wdasdsdadada"
UPLOAD_FOLDER = 'C:\\Users\\armin\\Desktop\\ogretmenim.com\\static\\img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Extension Check
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Login Form
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre",[validators.DataRequired(message="Şifrenizi giriniz")])

#Teacher Register Form
class TeacherRegisterForm(Form):
    name = StringField('İsim',[validators.DataRequired(message="İsim giriniz")])
    familyname = StringField('Soyisim',[validators.DataRequired(message="Soyisim giriniz")])
    username = StringField("Kullanıcı Adı",[validators.DataRequired(message="Kullanıcı adı giriniz"),validators.Length(min=3,max=15,message="Kullanıcı adınız en az 3 en fazla 15 karakter olmalıdır")])
    email = StringField('Email',[validators.email(message="Lütfen email giriniz")])
    branch = StringField('Branş',[validators.DataRequired(message="Branşınızı giriniz")])
    city = SelectField('Çalıştığınız Okulun Bulunduğu Şehir',choices=[('1','Adana'),('2','Adıyaman'),('3','Afyon'),('4','Ağrı'),('5','Amasya'),('6','Ankara'),('7','Antalya'),('8','Artvin'),('9','Aydın'),('10','Balıkesir'),('11','Bilecik'),('12','Bingöl'),('13','Bitlis'),('14','Bolu'),('15','Burdur'),('16','Bursa'),('17','Çanakkale'),('18','Çankırı'),('19','Çorum'),('20','Denizli'),('21','Diyarbakır'),('22','Edirne'),('23','Elazığ'),('24','Erzincan'),('25','Erzurum'),('26','Eskişehir'),('27','Gaziantep'),('28','Giresun'),('29','Gümüşhane'),('30','Hakkari'),('31','Hatay'),('32','Isparta'),('33','İçel'),('34','İstanbul'),('35','İzmir'),('36','Kars'),('37','Kastamonu'),('38','Kayseri'),('39','Kırklareli'),('40','Kırşehir'),('41','Kocaeli'),('42','Konya'),('43','Kütahya'),('44','Malatya'),('45','Manisa'),('46','Kahramanmaraş'),('47','Mardin'),('48','Muğla'),('49','Muş'),('50','Nevşehir'),('51','Niğde'),('52','Ordu'),('53','Rize'),('54','Sakarya'),('55','Samsun'),('56','Siirt'),('57','Sinop'),('58','Sivas'),('59','Tekirdağ'),('60','Tokat'),('61','Trabzon'),('62','Tunceli'),('63','Şanlıurfa'),('64','Uşak'),('65','Van'),('66','Yozgat'),('67','Zonguldak'),('68','Aksaray'),('69','Bayburt'),('70','Karaman'),('71','Kırıkkale'),('72','Batman'),('73','Şırnak'),('74','Bartın'),('75','Ardahan'),('76','Iğdır'),('77','Yalova'),('78','Karabük'),('79','Kilis'),('80','Osmaniye'),('81','Düzce')])
    password = PasswordField("Şifre", [validators.DataRequired(message="Bir parola belirleyiniz!"), validators.EqualTo("confirm", message="Şifre eşleşmedi")])
    confirm = PasswordField("Şifre Doğrulama")

#Normal Register Form
class NormalRegisterForm(Form):
    name = StringField('İsim',[validators.DataRequired(message="İsim giriniz")])
    familyname = StringField('Soyisim',[validators.DataRequired(message="Soyisim giriniz")])
    username = StringField("Kullanıcı Adı",[validators.DataRequired(message="Kullanıcı adı giriniz"),validators.Length(min=3,max=15,message="Kullanıcı adınız en az 3 en fazla 15 karakter olmalıdır")])
    email = StringField('Email',[validators.email(message="Lütfen email giriniz")])
    password = PasswordField("Şifre", [validators.DataRequired(message="Bir parola belirleyiniz!"), validators.EqualTo("confirm", message="Şifre eşleşmedi")])
    confirm = PasswordField("Şifre Doğrulama")

#Change Username Form
class ChangeUsernameForm(Form):
    fusername = StringField('Şuanki Kullanıcı Adınız',[validators.DataRequired(message="Şuanki kullanıcı adınızı giriniz")])
    lusername = StringField('Kullanmak İstediğiniz Kullanıcı Adınız',[validators.DataRequired(message="Kullanmak istediğiniz kullanıcı adını giriniz")])
    password = PasswordField('Şifre', [validators.DataRequired(message="Şifrenizi giriniz")])

#Change Password Form
class ChangePasswordForm(Form):
    oldPassword = PasswordField('Eski Şifreniz',[validators.DataRequired(message="Eski şifrenizi giriniz")])
    newPassword = PasswordField('Yeni Şifreniz',[validators.DataRequired(message="Yeni şifrenizi giriniz"), validators.EqualTo("confirm", message="Şifre eşleşmedi")])
    confirm = PasswordField('Şifre Doğrulama',[validators.DataRequired(message="Şifre doğrulamanızı giriniz")])
    

#Change Email Form
class ChangeEmailForm(Form):
    femail = StringField('Şuanki Email Hesabınız',[validators.DataRequired(message="Şuanki email hesabınızı giriniz")])
    lemail = StringField('Kullanmak İstediğiniz Email Hesabınız',[validators.DataRequired(message="Kullanmak istediğiniz email hesabını giriniz")])
    password = PasswordField('Şifre', [validators.DataRequired(message="Şifrenizi giriniz")])
    

#Question Form
class QuestionForm(Form):
    title = StringField("Başlık", [validators.Length(min=5,max=20)])
    content = TextAreaField("Soru", _name = "textarea")

#Login User Decorater
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if session["logined"]:
                return f(*args, **kwargs)
            else:
                flash("Bu işlemi gerçekleştirmek için giriş yapmalısınız","danger")
                return redirect(url_for("login"))
        except KeyError:
            flash("Bu işlemi gerçekleştirmek için giriş yapmalısınız","danger")
            return redirect(url_for("login"))
    return decorated_function

#Index
@app.route('/')
def index():
    return render_template("index.html")

#Register Page
@app.route('/register')
def register():
    return render_template("register.html")

#Teacher Register
@app.route('/teacher-register',methods=["POST","GET"])
def teacherRegister():
    form = TeacherRegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        familyname = form.familyname.data
        username = form.username.data
        email = form.email.data
        branch = form.branch.data
        password = form.password.data
        secretpassword = sha256_crypt.hash(password)
        teacher = 1
        cityCode = form.city.data
        teacherVerify = 0
        note = 0
        admin = 0

        try:
            dataBase = sql.connect("ogretmenim.com.db")
            cursor = dataBase.cursor()
            query = "Insert into Accounts(name,familyname,username,email,branch,password,teacher,cityCode,teacherVerify,note,admin) Values (?,?,?,?,?,?,?,?,?,?,?) "
            userList = (name,familyname,username,email,branch,secretpassword,teacher,cityCode,teacherVerify,note,admin)
            cursor.execute(query,userList)
            dataBase.commit()
            cursor.close()
            dataBase.close()
            flash("Başarıyla kayıt oldunuz","success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("Kullanıcı adınız kullanılıyor","warning")
            return redirect(url_for("teacherRegister"))
    else:
        return render_template("teacherregister.html",form=form)

#Normal Register
@app.route('/normal-register',methods=["GET","POST"])
def normalRegister():
    form = NormalRegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        familyname = form.familyname.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        secretpassword = sha256_crypt.hash(password)
        teacher = 0
        teacherVerify = 2
        note = 0
        admin = 0

        try:
            dataBase = sql.connect("ogretmenim.com.db")
            cursor = dataBase.cursor()
            query = "Insert into Accounts(name,familyname,username,email,password,teacher,teacherVerify,note,admin) Values (?,?,?,?,?,?,?,?,?) "
            userList = (name,familyname,username,email,secretpassword,teacher,teacherVerify,note,admin)
            cursor.execute(query,userList)
            dataBase.commit()
            cursor.close()
            dataBase.close()
            flash("Başarıyla kayıt olundu","success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("Girdiğiniz kullanıcı adı kullanılıyor","danger")
            return redirect(url_for("normalRegister"))

    else:
        return render_template("normalregister.html",form=form)

#Login Page
@app.route('/login',methods=["POST","GET"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data
        
        query = "Select * from Accounts where username = ?"
        dataBase = sql.connect("ogretmenim.com.db")
        cursor = dataBase.cursor()
        cursor.execute(query,(username,))
        data = cursor.fetchone()
        if data is not None:
            userPassword = data[5]
            userid = data[0]
            name = data[1]
            familyname = data[2]
            email = data[4]
            school = data[7]
            cityCode = data[9]
            branch = data[8]
            teacher = data[6]
            teacherVerify = data[10]
            admin = data[13]

            if sha256_crypt.verify(password,userPassword):
                flash("Başarıyla giriş yaptınız","success")
                session["logined"] = True
                session["username"] = username
                session["userid"] = userid
                session["name"] = name
                if admin == 1:
                    session["admin"] = True
                if admin == 0:
                    session["admin"] = False
                if school is not None:
                    session["school"] = school
                if branch is not None:
                    session["branch"] = branch
                session["email"] = email
                session["familyname"] = familyname
                if cityCode is not None:
                    session["cityCode"] = cityCode
                
                if teacher == 1:
                    session["teacher"] = True
                    if teacherVerify == 0:
                        session["teacherVerify"] = False
                    elif teacherVerify == 1:
                        session["teacherVerify"] = True
                else:
                    session["teacher"] = False

                return redirect(url_for("index"))
            else:
                flash("Şifreniz yanlış!","danger")
                return redirect(url_for("login"))
        else:
            flash("Girdiğiniz kullanıcı adı yanlış","danger")
            return redirect(url_for("login"))
        
        cursor.close()
        dataBase.close()
        
    else:
        return render_template("login.html",form = form)

#Logout User
@app.route('/logout')
@login_required
def logout():
    session["logined"] = False
    session["username"] = None
    session["teacher"] = None
    session["teacherVerify"] = None
    session["userid"] = None
    session["name"] = None
    session["school"] = None
    session["email"] = None
    session["familyname"] = None
    session["cityCode"] = None
    session["branch"] = None
    return redirect(url_for("index"))

#My Account Page
@app.route('/my-account')
@login_required
def myAccount():
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    queryNote = "Select note from Accounts where id = ?"
    cursor.execute(queryNote,(session["userid"],))
    dataNote = cursor.fetchone()
    note = dataNote[0]
    cursor.close()
    dataBase.close()
    return render_template("myaccount.html",note=note)

#Change Username Page
@app.route('/change-username',methods=["GET","POST"])
@login_required
def changeUsername():
    form = ChangeUsernameForm(request.form)
    if request.method == "POST":
        fusername = form.fusername.data
        lusername = form.lusername.data
        password = form.password.data

        dataBase = sql.connect("ogretmenim.com.db")
        cursor = dataBase.cursor()
        query = "Select username,password from Accounts where id = ?"
        cursor.execute(query,(session["userid"],))
        data = cursor.fetchone()
        username = data[0]
        secretpassword = data[1]
        try:
            if fusername == username:
                if sha256_crypt.verify(password,secretpassword):
                    query2 = "Update Accounts set username = ? where id = ?"
                    cursor.execute(query2,(lusername,session["userid"]))
                    query3 = "Update Questions set author = ? where author = ?"
                    cursor.execute(query3,(lusername,fusername))
                    dataBase.commit()
                    query4 = "Update Comments set author = ? where author = ?"
                    cursor.execute(query4,(lusername,fusername))
                    dataBase.commit()
                    cursor.close()
                    dataBase.close()
                    flash("Kullanıcı adı güncellendi","success")
                    session["username"] = lusername
                    return redirect(url_for("myAccount"))
                else:
                    flash("Girdiğiniz şifre yanlış","danger")
                    return redirect(url_for("myAccount"))
            else:
                flash("Girdiğiniz şuanki kullanıcı adı yanlış","danger")
                return redirect(url_for("myAccount"))
        except IntegrityError:
            flash("Kullanıcı adı kullanılıyor","danger")
            return redirect(url_for("changeUsername"))
        
    else:
        return render_template("changeusername.html",form=form)

#Change Email Page
@app.route('/change-email',methods=["GET","POST"])
@login_required
def changeEmail():
    form = ChangeEmailForm(request.form)
    if request.method == "POST":
        femail = form.femail.data
        lemail = form.lemail.data
        password = form.password.data

        dataBase = sql.connect("ogretmenim.com.db")
        cursor = dataBase.cursor()
        query = "Select email,password from Accounts where id = ?"
        cursor.execute(query,(session["userid"],))
        data = cursor.fetchone()
        email = data[0]
        userPassword = data[1]
        if femail == email:
            if sha256_crypt.verify(password,userPassword):
                query2 = "Update Accounts set email = ? where id = ?"
                cursor.execute(query2,(lemail,session["userid"]))
                dataBase.commit()
                cursor.close()
                dataBase.close()
                flash("Email hesabınız güncellendi","success")
                session["email"] = email
                return redirect(url_for("myAccount"))
            else:
                flash("Girdiğiniz şifre yanlış","danger")
                return redirect(url_for("myAccount"))
        else:
            flash("Girdiğiniz şuanki kullanıcı adı yanlış","danger")
    else:
        return render_template("changeemail.html",form=form)

#Change Password Page
@app.route("/change-password",methods=["GET","POST"])
@login_required
def changePassword():
    form = ChangePasswordForm(request.form)
    if request.method == "POST":
        oldPassword = form.oldPassword.data
        newPassword = form.newPassword.data
        confirm = form.confirm.data
        if confirm == newPassword:
            dataBase = sql.connect("ogretmenim.com.db")
            cursor = dataBase.cursor()
            query = "Select password from Accounts where id = ?"
            cursor.execute(query,(session["userid"],))
            dataPassword = cursor.fetchone()
            userPassword = dataPassword[0]
            if sha256_crypt.verify(oldPassword,userPassword):
                queryPassword = "Update Accounts set password = ? where id = ?"
                secretPassword = sha256_crypt.hash(newPassword)
                cursor.execute(queryPassword,(secretPassword,session["userid"]))
                dataBase.commit()
                cursor.close()
                dataBase.close()
                flash("Şifreniz başarıyla güncellendi","success")
                return redirect(url_for("myAccount"))
        else:
            flash("Yeni şifreniz ile şifre doğrulama farklı")
            return redirect(url_for("changePassword"))
    else:
        return render_template("changepassword.html",form=form)

#Teacher Verify Page
@app.route('/verify-teacher',methods=["GET","POST"])
@login_required
def teacherVerify():
    if session["teacher"]:

        if session["teacherVerify"]:
            return redirect(url_for("index"))

        else:

            if request.method == "POST":
                dataBase = sql.connect("ogretmenim.com.db")
                cursor = dataBase.cursor()
                query = "Select cityCode,name,familyname,branch from Accounts where username = ?"
                userList = (session["username"],)
                cursor.execute(query,userList)
                info = cursor.fetchone()
                cityCode = info[0]
                name = info[1]
                familyname = info[2]
                branch = info[3]
                cursor.close()
                dataBase.close()
                schoolName = request.form.get("school")
                schoolWebAdress = findSchoolWebAdress(cityCode,schoolName)
                verify = teacherVerifyControl(name,familyname,schoolWebAdress,branch)

                if verify:
                    dataBase = sql.connect("ogretmenim.com.db")
                    cursor = dataBase.cursor()
                    query2 = "Update Accounts set teacherVerify = 1 where id = ?"
                    query3 = "Update Accounts set school = ? where id = ?"
                    cursor.execute(query2,(session["userid"],))
                    cursor.execute(query3,(schoolName,session["userid"]))
                    dataBase.commit()
                    cursor.close()
                    dataBase.close()
                    session["school"] = schoolName
                    session["teacherVerify"] = 1
                    session["branch"] = branch
                    flash("Öğretmen hesabınız başarıyla doğrulandı","success")
                    return redirect(url_for("index"))
                    
                else:
                    flash("Öğretmen hesabınız doğrulanamadı","danger")
                    return redirect(url_for("index"))

            else:
                dataBase = sql.connect("ogretmenim.com.db")
                cursor = dataBase.cursor()
                query = "Select cityCode from Accounts where username = ?"
                userList = (session["username"],)
                cursor.execute(query,userList)
                cityCode = cursor.fetchone()
                cityCode = cityCode[0]
                cursor.close()
                dataBase.close()
                schools = schoolList(cityCode)
                schools.sort()
                return render_template("teacherverify.html",schools=schools)

    if session["teacher"] == "False":
        return redirect(url_for("index"))

#Questions Page
@app.route('/questions',methods=["GET","POST"])
def questions():
    
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    cursor.execute("Select * from Questions")
    datas = cursor.fetchall()
    if request.args.get("searchkeyword") or request.args.get("lessonfilter"):
        if request.args.get("lessonfilter") == "All" and request.args.get("searchkeyword") != "":
            searchKeyword = request.args.get("searchkeyword")
            querySearchwithKeyword = "Select * from Questions where title LIKE "
            querySearchwithKeyword = querySearchwithKeyword + "'%" + str(searchKeyword) + "%'"
            cursor.execute(querySearchwithKeyword)
            datas = cursor.fetchall()
        
        elif request.args.get("searchkeyword") == "" and request.args.get("lessonfilter") != "All":
            lesson = request.args.get("lessonfilter")
            queryLessonFilter = "Select * from Questions where lesson = ?"
            cursor.execute(queryLessonFilter,(lesson,))
            datas = cursor.fetchall()

        elif request.args.get("lessonfilter") != "All" and request.args.get("searchkeyword") != "":
            searchKeyword = request.args.get("searchkeyword")
            lesson = request.args.get("lessonfilter")
            querySearchwithKeywordandLesson = "Select * from Questions where title LIKE "
            querySearchwithKeywordandLesson = querySearchwithKeywordandLesson + "'%" + str(searchKeyword) + "%'"
            querySearchwithKeywordandLesson = querySearchwithKeywordandLesson + " " + "and" + " " + "lesson = ?"
            cursor.execute(querySearchwithKeywordandLesson,(lesson,))
            datas = cursor.fetchall()

    cursor.close()
    dataBase.close()
    return render_template("questions.html",datas=datas)

#My Questions Page
@app.route('/my-questions')
@login_required
def myQuestions():
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    author = session["username"]
    query = "Select id,title,lesson,date from Questions where author = ?"
    cursor.execute(query,(author,))
    datas = cursor.fetchall()
    return render_template("myquestions.html",datas=datas)

#View Question
@app.route("/view-question/<string:id>",methods=["GET","POST"])
def viewQuestion(id):
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()

    query = "Select * from Questions where id = ?"
    cursor.execute(query,(id,))
    question = cursor.fetchone()
    query2 = "Select * from Comments where QuestionID = ?"
    cursor.execute(query2,(id,))
    comments = cursor.fetchall()
    commentCount = len(comments)
    try:
        userLikes = []
        userid = str(session["userid"])
        queryUserLikes = "Select id,likesid from Comments"
        cursor.execute(queryUserLikes)
        datas = cursor.fetchall()
        for data in datas:
            if data[1] is not None:
                if userid in data[1]:
                    userLikes.append(data[0])
    except KeyError:
        userLikes = []
        userid = 0
    
    queryTeachers = "Select username from Accounts where teacherVerify = ?"
    cursor.execute(queryTeachers,(1,))
    teachersData = cursor.fetchall()
    teachers = []
    for teacher in teachersData:
        if len(teacher[0]) >= 3:
            teachers.append(teacher[0])
    cursor.close()
    dataBase.close()
    
    return render_template("questiondetail.html",question=question,comments=comments,commentCount=commentCount,userid=userid,userLikes=userLikes,teachers=teachers)

#Add Question Page
@app.route('/add-question',methods=["GET","POST"])
@login_required
def addQuestion():
    form = QuestionForm(request.form)
    if request.method == "POST":
        dataBase = sql.connect("ogretmenim.com.db")
        cursor = dataBase.cursor()
        title = form.title.data
        lesson = request.form.get("lesson")
        content = form.content.data
        time = datetime.now()
        time = str(time)
        time = time.split(" ")
        time = time[0]
        imageName = False      
        if request.files["file"]:
            if 'file' in request.files:
                image = request.files["file"]
                if image.filename != "":
                    if image and allowed_file(image.filename):
                        imageName = secure_filename(image.filename)
                        imageName = str(imageName)
                        uzantı = imageName.split(".")
                        uzantı = uzantı[-1]
                        if uzantı == "png" or uzantı == "jpg" or uzantı == "jpeg":
                            secretImageName = str(sha256_crypt.hash(imageName))
                            secretImageName = secretImageName.replace("$","a")
                            secretImageName = secretImageName.replace(".","a")
                            secretImageName = secretImageName.replace("/","a")
                            secretImageName = secretImageName.replace("=","a")
                            filename = str(secretImageName) + "." + uzantı
                            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        else:
                            flash("Lütfen resim dosyası dışında bir şey yüklemeyi denemeyin","danger")
                            return redirect(url_for("addQuestion"))

        if imageName != False:
            query = "Insert into Questions(title,content,author,lesson,date,imageName) values(?,?,?,?,?,?)"
            info = (title,content,session["username"],lesson,time,filename)
        else:
            query = "Insert into Questions(title,content,author,lesson,date) values(?,?,?,?,?)"
            info = (title,content,session["username"],lesson,time)
            
        cursor.execute(query,info)
        dataBase.commit()
        
        query2 = "Select note from Accounts where id = ?"
        cursor.execute(query2,(session["userid"],))
        data = cursor.fetchone()
        note = data[0]
        note += 20
        query3 = "Update Accounts set note = ? where id = ?"
        cursor.execute(query3,(note,session["userid"]))
        dataBase.commit()
        cursor.close()
        dataBase.close()
        flash("Soru başarıyla eklendi","success")
        flash("Soru eklediğiniz için 20 puan kazandınız. TEBRİKLER!","success")
        return redirect(url_for("myQuestions"))
    else:
        return render_template("addquestion.html",form=form)

#Update Question Page
@app.route("/update-question/<string:id>",methods=["POST","GET"])
@login_required
def updateQuestion(id):
    if request.method == "POST":
        form = QuestionForm(request.form)
        title = form.title.data
        content = form.content.data
        time = datetime.now()
        time = str(time)
        time = time.split(" ")
        date = time[0]
        dataBase = sql.connect("ogretmenim.com.db")
        cursor = dataBase.cursor()
        query = "Update Questions set title = ?, content = ?, date = ? where id = ?"
        cursor.execute(query,(title,content,date,id))
        dataBase.commit()
        cursor.close()
        dataBase.close()
        flash("Soru başarıyla güncellendi","success")
        return redirect(url_for("myQuestions"))

    else:
        dataBase = sql.connect("ogretmenim.com.db")
        cursor = dataBase.cursor()
        query = "Select title,content,author from Questions where id = ?"
        cursor.execute(query,(id,))
        data = cursor.fetchone()
        title = data[0]
        content = data[1]
        author = data[2]
        if author == session["username"]:
            cursor.close()
            dataBase.close()
            form = QuestionForm(title=title,content=content)
            return render_template("updatequestion.html",form=form)
        else:
            return redirect(url_for("myQuestions"))

#Delete Question
@app.route("/delete-question/<string:id>")
@login_required
def deleteQuestion(id):
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    query = "Select imageName,author from Questions where id = ?"
    cursor.execute(query,(id,))
    data = cursor.fetchone()
    imageName = data[0]
    author = data[1]
    if author == session["username"]:
        deleteQuery = "Delete from Questions where id = ?"
        cursor.execute(deleteQuery,(id,))
        query2 = "Select note from Accounts where id = ?"
        cursor.execute(query2,(session["userid"],))
        dataNote = cursor.fetchone()
        note = dataNote[0]
        note -= 20
        query3 = "Update Accounts set note = ? where id = ?"
        cursor.execute(query3,(note,session["userid"]))
        query4 = "Delete from Comments where questionID = ?"
        cursor.execute(query4,(id,))
        dataBase.commit()
        cursor.close()
        dataBase.close()
        if imageName != None:
            imgurl = "C:\\Users\\armin\\Desktop\\ogretmenim.com\\static\\img\\"
            imgurl = imgurl + str(imageName)
            os.remove(imgurl)
        
        flash("Soru silindi","success")
        flash("Soru sildiğiniz için 20 puan kaybettiniz","warning")
        return redirect(url_for("myQuestions"))

    else:
        flash("Silmeye çalıştığınız soru size ait değil","danger")
        return redirect(url_for("myQuestions"))

#Add Comment
@app.route("/add-comment/<string:questionID>",methods=["GET","POST"])
@login_required
def addComment(questionID):
    comment = request.form.get("comment")
    author = session["username"]
    time = datetime.now()
    time = str(time)
    time = time.split(" ")
    date = time[0]
    likeCounter = 0
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    query = "Insert into Comments(content,author,questionID,likecounter,date) values(?,?,?,?,?)"
    cursor.execute(query,(comment,author,questionID,likeCounter,date))
    query2 = "Select note from Accounts where id = ?"
    cursor.execute(query2,(session["userid"],))
    dataNote = cursor.fetchone()
    note = dataNote[0]
    note += 5
    query3 = "Update Accounts set note = ? where id = ?"
    cursor.execute(query3,(note,session["userid"]))
    dataBase.commit()
    cursor.close()
    dataBase.close()
    flash("Cevabınız eklendi","success")
    flash("Yorum yazdığınız için 5 puan kazandınız. TEBRİKLER!","success")
    return redirect(url_for("viewQuestion",id=questionID))

#Delete Comment
@app.route("/delete-comment/<string:questionID>/<string:id>")
@login_required
def deleteComment(questionID,id):
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    queryComment = "Select * from Comments where id = ?"
    cursor.execute(queryComment,(id,))
    commentData = cursor.fetchone()
    commentAuthor = commentData[2]
    if session["username"] == commentAuthor or session["admin"]:
        queryDeleteComment = "Delete from Comments where id = ?"
        cursor.execute(queryDeleteComment,(id,))
        dataBase.commit()
        cursor.close()
        dataBase.close()
        flash("Yorum başarıyla kaldırıldı","success")
        return redirect(url_for("viewQuestion",id=questionID))
    else:
        cursor.close()
        dataBase.close()
        flash("Bu işleme yetkiniz yok","danger")
        return redirect(url_for("viewQuestion",id=questionID))

#Update Comment
@app.route("/update-comment/<string:questionID>/<string:id>",methods=["POST","GET"])
@login_required
def updateComment(questionID,id):
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    queryComment = "Select * from Comments where id = ?"
    cursor.execute(queryComment,(id,))
    commentData = cursor.fetchone()
    commentAuthor = commentData[2]
    commentContent = commentData[1]
    if session["username"] == commentAuthor or session["admin"]:
        if request.method == "POST":
            comment = request.form.get("comment")
            comment = str(comment)
            time = datetime.now()
            time = str(time)
            time = time.split(" ")
            date = time[0]
            likeCounter = 0
            likesID = ""
            queryUpdateComment = "Update Comments set content = ?, likecounter = ?, date = ?, likesid = ? where id = ?"
            cursor.execute(queryUpdateComment,(comment,likeCounter,date,likesID,id))
            dataBase.commit()
            cursor.close()
            dataBase.close()
            flash("Yorum başarıyla güncellendi","success")
            return redirect(url_for("viewQuestion",id=questionID))
        else:
            return render_template("updatecomment.html",comment=commentContent)
    else:
        flash("Bu işleme izniniz yok","danger")
        return redirect(url_for("viewQuestion",id=questionID))

#Like-Dislike Comment
@app.route("/like-dislike-comment/<string:questionID>/<string:commentID>",methods=["GET","POST"])
@login_required
def likedislikeComment(questionID,commentID):
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    userid = session["userid"]
    commentID = commentID
    queryLikes = "Select likesid,likecounter from Comments where questionID = ? and id = ?"
    cursor.execute(queryLikes,(questionID,commentID))
    dataLikes = cursor.fetchone()
    commentlikes = dataLikes[0]
    commentlikes = str(commentlikes)
    likecounter = dataLikes[1]
    likes = commentlikes.split(",")
    sentence = ""
    if commentlikes == "None":
        sentence = sentence + str(userid)
        queryLike1 = "Update Comments set likesid = ?, likecounter = ? where id = ?"
        likecounter += 1
        cursor.execute(queryLike1,(sentence,likecounter,commentID))
        dataBase.commit()
        flash("Yorum beğenildi","success")
    elif str(userid) in likes:
        likes.remove(str(userid))
        for like in likes:
            if like == likes[0]:
                sentence = sentence + str(like)
            if len(like) > 0:
                sentence = sentence + "," + str(like)
            else:
                sentence = ""
        queryRemoveLike = "Update Comments set likesid = ?, likecounter = ? where id = ?"
        likecounter -= 1
        cursor.execute(queryRemoveLike,(sentence,likecounter,commentID))
        dataBase.commit()
        flash("Beğeni kaldırıldı","success")
    elif commentlikes != "None" and not(userid in likes):
        commentlikes = commentlikes + "," + str(userid)
        sentence = commentlikes
        query4 = "Update Comments set likesid = ?, likecounter = ? where id = ?"
        likecounter += 1
        cursor.execute(query4,(sentence,likecounter,commentID))
        dataBase.commit()

    return redirect(url_for("viewQuestion",id=questionID))


#Ranking Page
@app.route("/ranking")
def ranking():
    rankSelect = request.args.get("rankSelect")
    dataBase = sql.connect("ogretmenim.com.db")
    cursor = dataBase.cursor()
    users = False
    lenUsers = False
    if rankSelect != None:
        users = []
        querySelect = "Select username,teacher,branch,teacherVerify,note,admin from Accounts order by note"
        cursor.execute(querySelect)
        datas = cursor.fetchall()
        if rankSelect == "Teacher":
            for data in datas:
                if data[3] == 1 and data[5] == 0:
                    users.append(data)
        elif rankSelect == "Normal":
            for data in datas:
                if data[1] == 0 and data[5] == 0:
                    users.append(data)
        users.reverse()
        lenUsers = len(users)
    
    return render_template("ranking.html",users=users,rankSelect=rankSelect,lenUsers=lenUsers)

if __name__ == "__main__":
    app.run(debug=True)