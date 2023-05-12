"""2021/12/02 myweb_Login_V2_5
完成進度：
    1.Login & Sign up：可以登入及註冊
    2.Book Room：可以進行新增會議和編輯會議
    3.My Meeting：可以查看已參加的會議，有編輯及刪除的功能
完成部分的現有問題：
    1.Login & Sign up：
        1-1.登入錯誤時，不會有提示訊息
        1-2.註冊錯誤時，不會有提示訊息
        1-3.重複註冊(包含：已註冊的Email、已註冊的Username)會進入例外畫面 (應顯示提示錯誤即可)
    2.Book Room：
        2-1.Start Time 應早於 End Time (相同時間、或已被預約的時段應列入無效預定、編輯會議)
        2-2.第一次新增會議時，在Attendees會自動新增建立者的username(該欄位可能需要以Email來表示，方便後續自動寄信時，可以直接使用該欄位的資料)
        2-3.編輯會議時，Room顯示的是預設值1，而不是實際的Room號碼
    3.My Meeting：
        3-1.目前已username來判斷是否參加該會議，同2-2
        3-2.編輯建及刪除鍵的權限，尚未設定(建立者:有編輯和刪除的權限、參與者：沒有編輯和刪除的權限)
未完成部分：
    1.Home：
        1-1.呈現目前會議室的預約情況
        1-2.管理員登入時的頁面，類似My Meeting 列出所有會議，且僅有刪除的權限
    2.在新增會議、刪除會議或編輯會議完成時，在自動寄信給所有參與者，或是被踢出會議的人
"""
"""
工作紀錄：
    2021/12/03
        2-2.已更改為 Email 來表示
        2-3.已解決，原因為 SelectField('Room', choices=room_choices, validators=[DataRequired()])
            其中 validators=[DataRequired()所傳入的值必須與 room_choices 的 tpye相同且在 room_choices的array當中，
            因此，在 class Meeting(db.Model):中，把 room = db.Column(db.Integer) 改為 room = db.Column(db.String(64))
        3-1.已更改，同2-2.
    2021/12/05
        自動寄信功能已完成
        SMTP Sever email
        帳：swroomie15@gmail.com
        密：@SWRoomie1500
        1-1.已加上(不存在用戶、輸入錯誤帳號或密碼、登入成功)的提示訊息
    2021/12/06
        1-2.、1-3.已加上提示訊息及解決重複註冊的例外畫面
        3-2.權限已補上，非主持人無法編輯和刪除會議
        2-1.預約、編輯會議時間的判斷已補上
    2021/12/13
        新增對外連線
        1-1.、1-2.已可依照日期來搜尋對應的會議，並設定管理員登入後的刪除會議權限，頁面的不同。
        PS.管理員的帳號為
            Email：swroomie15@gmail.com
            Username：admin
            Password：admin
    2021/12/15
        修改 UI介面 (主要為 Home Page 的呈現)
"""

from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from myproject import app, db
from myproject.models import Meeting, User
from myproject.forms import LoginForm, RegistrationForm, BookRoomForm, HomePageForm
import datetime
from wtforms import ValidationError
from flask import redirect
from flask import Flask

# 已入自動寄信 function
from myproject.models import sendmailSMTP

import numpy

# flask對外連線
@app.route("/goto/<path:url>", methods=["GET"])
def _goto(url):
    return redirect(url)


@app.route("/")
def welcome():

    return render_template("welcome.html")


@app.route("/Login", methods=["GET", "POST"])
def Login():
    form = LoginForm()

    if not "@" in str(form.email.data) and form.email.data != None:
        flash("錯誤的 Email 格式", category="danger")
        return render_template("Login.html", form=form)

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user == None:  # 使用者不存在
            flash("找不到該帳戶", category="danger")
            return render_template("Login.html", form=form)
        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash("成功登入系統", category="success")
            next = request.args.get("next")
            if next == None or not next[0] == "/":
                next = url_for("Home")
            return redirect(next)
        else:
            flash("錯誤的 Email 或 Password", category="danger")
    return render_template("Login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("您已經登出系統", category="success")
    return redirect(url_for("welcome"))


@app.route("/Sign_Up", methods=["GET", "POST"])
def Sign_Up():
    form = RegistrationForm()

    if not "@" in str(form.email.data) and form.email.data != None:
        flash("錯誤的 Email 格式", category="danger")
        return render_template("Sign_Up.html", form=form)

    if form.password.data != form.pass_confirm.data:
        flash("兩個密碼並不相符", category="danger")
        return render_template("Sign_Up.html", form=form)

    if form.validate_on_submit():

        checkEmail = User.query.filter_by(email=form.email.data).first()
        if checkEmail != None:
            flash("該 Email 已被註冊", category="danger")
            return render_template("Sign_Up.html", form=form)

        checkUsername = User.query.filter_by(username=form.username.data).first()
        if checkUsername != None:
            flash("該 Username 已被註冊", category="danger")
            return render_template("Sign_Up.html", form=form)

        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )

        # add to db table
        db.session.add(user)
        db.session.commit()
        flash("已成功註冊本系統會員", category="success")
        return redirect(url_for("Login"))

    return render_template("Sign_Up.html", form=form)


@app.route("/Home", methods=["GET", "POST"])
@login_required
def Home():
    form = HomePageForm()

    date = str(form.date.data)

    meetings = Meeting.query.filter(
            Meeting.date.contains(date)
            )  # 查詢所搜尋日期的會議

    confirmStatus = numpy.full((9, 5), False)

    for meeting in meetings:
        roomIndex = int(meeting.room) - 1
        startIndex = int(meeting.start_time[0:2]) - 9
        endIndex = int(meeting.end_time[0:2]) - 9

        for i in range(startIndex,endIndex):
            confirmStatus[i][roomIndex] = True

    if form.validate_on_submit():
        date = str(form.date.data)

        meetings = Meeting.query.filter(
            Meeting.date.contains(date)
            )  # 查詢所搜尋日期的會議

        for meeting in meetings:
            roomIndex = int(meeting.room) - 1
            startIndex = int(meeting.start_time[0:2]) - 9
            endIndex = int(meeting.end_time[0:2]) - 9

            for i in range(startIndex,endIndex):
                confirmStatus[i][roomIndex] = True

        if meetings.first() == None:  # 查詢後沒有符合的結果，則設為None
            meetings = None

        return render_template("Home.html", form=form, meetings=meetings, confirmStatus=confirmStatus)

    if request.method == "POST":
        DeleteRequest = request.form.get("delete")
        # https://stackoverflow.com/questions/19794695/flask-python-buttons
        if DeleteRequest != None:
            ID = request.form["delete"]
            query = Meeting.query.filter_by(id=ID).first()

            # 寄信給所有參與者
            subject = "Delete Meeting"
            messageContent = (
                current_user.username
                + " deleted the meeting!\n\n"
                + "Host: "
                + query.host
                + "\n"
                + "Meeting Name: "
                + query.meeting_name
                + "\n"
                + "Date： "
                + query.date
                + "\n"
                + "Start Time: "
                + query.start_time
                + "\n"
                + "End Time: "
                + query.end_time
                + "\n"
                + "Room: "
                + query.room
                + "\n"
                + "Attendees: "
                + query.attendees
                + "\n"
                + "Description: "
                + query.description
            )
            sendmailSMTP(subject, messageContent, query.attendees)

            db.session.delete(query)
            db.session.commit()

            flash("刪除會議成功", category="success")

            return redirect(url_for("Home"))    

    if meetings.first() == None:  # 查詢後沒有符合的結果，則設為None
        meetings = None
    #return render_template("My_Meeting.html", meetings=meetings)

    return render_template("Home.html", form=form, meetings=meetings, confirmStatus=confirmStatus)


@app.route("/Book_Room", methods=["GET", "POST"])
@login_required
def Book_Room(id=None):
    form = BookRoomForm()
    id = request.args.get("id")
    if id != None and request.method == "GET":  # 代表是編輯會議，而不是新增會議
        query = Meeting.query.filter_by(id=id).first()  # 把該meeting資料寫入form，讓使用者修改
        form.date.data = datetime.datetime.strptime(query.date, "%Y-%m-%d").date()
        form.start_time.data = query.start_time
        form.end_time.data = query.end_time
        form.room.data = query.room
        form.attendee.data = query.attendees
        form.meeting_name.data = query.meeting_name
        form.description.data = query.description
        form.id.data = id

        return render_template("Book_Room.html", form=form)

    if form.validate_on_submit():
        if form.start_time.data >= form.end_time.data:  # start time 早於 end time
            flash("預約時間錯誤", category="danger")
        else:
            if form.id.data != "":  # 編輯會議

                date = str(form.date.data)  # 填入的時間(日期)
                room = form.room.data  # 填入的Room
                meetings = Meeting.query.filter(
                    Meeting.date.contains(date), Meeting.room.contains(room)
                )  # 找尋相同日期和Room 的會議

                for meeting in meetings:
                    if (
                        form.start_time.data < meeting.end_time
                        and form.end_time.data > meeting.start_time
                        and int(form.id.data) != meeting.id
                    ):
                        flash("該時段已被預約", category="danger")
                        return redirect(url_for("Book_Room", id=id))

                query = Meeting.query.filter_by(id=id).first()  # 接收修改後的form，寫入meeting
                query.date = form.date.data
                query.start_time = form.start_time.data
                query.end_time = form.end_time.data
                query.room = form.room.data
                tempAttendees = query.attendees  # 暫存編輯前的參與者名單，以便寄信通知時比對名單使用
                query.attendees = form.attendee.data
                query.meeting_name = form.meeting_name.data
                query.description = form.description.data

                # 寄信給所有(包含:新加入、原先)參與者皆會通知，信件內容為更新後的參與者名單
                attendees = tempAttendees
                for x in query.attendees.split(","):
                    if not x in tempAttendees:  # 比對編輯前後的參與者名單，並列出所有參與者一同寄信通知
                        attendees = attendees + "," + x

                subject = "Update Meeting"
                messageContent = (
                    current_user.username
                    + " updated the meeting!\n\n"
                    + "Host: "
                    + query.host
                    + "\n"
                    + "Meeting Name: "
                    + query.meeting_name
                    + "\n"
                    + "Date： "
                    + str(query.date)
                    + "\n"
                    + "Start Time: "
                    + query.start_time
                    + "\n"
                    + "End Time: "
                    + query.end_time
                    + "\n"
                    + "Room: "
                    + query.room
                    + "\n"
                    + "Attendees: "
                    + query.attendees
                    + "\n"
                    + "Description: "
                    + query.description
                )
                sendmailSMTP(subject, messageContent, attendees)

                db.session.add(query)
                db.session.commit()
                flash("編輯會議成功", category="success")
            else:  # 新增會議
                date = str(form.date.data)  # 填入的時間(日期)
                room = form.room.data  # 填入的Room
                meetings = Meeting.query.filter(
                    Meeting.date.contains(date), Meeting.room.contains(room)
                )  # 找尋相同日期和Room 的會議

                for meeting in meetings:
                    if (
                        form.start_time.data < meeting.end_time
                        and form.end_time.data > meeting.start_time
                    ):
                        flash("該時段已被預約", category="danger")
                        return redirect(url_for("Book_Room"))

                if (
                    form.attendee.data.find(current_user.email) == -1
                ):  # 如果新增會議時沒把自己寫進去     #current_user.username 換成 current_user.email 2021/12/03
                    attendees = (
                        current_user.email + "," + form.attendee.data
                    )  # current_user.username 換成 current_user.email 2021/12/03
                else:
                    attendees = form.attendee.data

                # 寄信給所有參與者
                subject = "Book Meeting"
                messageContent = (
                    current_user.username
                    + " created the new meeting!\n\n"
                    + "Host: "
                    + current_user.username
                    + "\n"
                    + "Meeting Name: "
                    + form.meeting_name.data
                    + "\n"
                    + "Date： "
                    + str(form.date.data)
                    + "\n"
                    + "Start Time: "
                    + form.start_time.data
                    + "\n"
                    + "End Time: "
                    + form.end_time.data
                    + "\n"
                    + "Room: "
                    + form.room.data
                    + "\n"
                    + "Attendees: "
                    + attendees
                    + "\n"
                    + "Description: "
                    + form.description.data
                )
                sendmailSMTP(subject, messageContent, attendees)

                meeting = Meeting(
                    host=current_user.username,
                    date=form.date.data,
                    start_time=form.start_time.data,
                    end_time=form.end_time.data,
                    room=form.room.data,
                    description=form.description.data,
                    attendees=attendees,
                    meeting_name=form.meeting_name.data,
                )
                db.session.add(meeting)
                db.session.commit()

                flash("新增會議成功", category="success")
        return redirect(url_for("Book_Room", id=id))
    return render_template("Book_Room.html", form=form)


@app.route("/My_Meeting", methods=["GET", "POST"])
@login_required
def My_Meeting():
    userEmail = (
        current_user.email
    )  # 當前登入的使用者    #userName = current_user.username  換成 userEmail = current_user.email 2021/12/03
    meetings = Meeting.query.filter(
        Meeting.attendees.contains(userEmail)
    )  # 與會者字串包含使用者名稱的會議們   #userName 換成 userEmail 2021/12/03

    if request.method == "POST":
        DeleteRequest = request.form.get("delete")
        EditRequest = request.form.get("edit")
        # https://stackoverflow.com/questions/19794695/flask-python-buttons
        if DeleteRequest != None:
            ID = request.form["delete"]
            query = Meeting.query.filter_by(id=ID).first()

            # 寄信給所有參與者
            subject = "Delete Meeting"
            messageContent = (
                current_user.username
                + " deleted the meeting!\n\n"
                + "Host: "
                + query.host
                + "\n"
                + "Meeting Name: "
                + query.meeting_name
                + "\n"
                + "Date： "
                + query.date
                + "\n"
                + "Start Time: "
                + query.start_time
                + "\n"
                + "End Time: "
                + query.end_time
                + "\n"
                + "Room: "
                + query.room
                + "\n"
                + "Attendees: "
                + query.attendees
                + "\n"
                + "Description: "
                + query.description
            )
            sendmailSMTP(subject, messageContent, query.attendees)

            db.session.delete(query)
            db.session.commit()

            flash("刪除會議成功", category="success")

            return redirect(url_for("My_Meeting"))
        # print(request.form['edit'])
        if EditRequest != None:  # 跳轉後匯入原始資料，待補
            ID = request.form["edit"]
            query = Meeting.query.filter_by(id=ID).first()
            # db.session.delete(query)
            # db.session.commit()
            return redirect(url_for("Book_Room", id=ID))
    if meetings.first() == None:  # 查詢後沒有符合的結果，則設為None
        meetings = None
    return render_template("My_Meeting.html", meetings=meetings)


# 建立資料表，對外連線
db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
