import sqlite3
import sys
from configparser import ConfigParser

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QDateTime, QTimer, QDate
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem, \
    QGridLayout, QWidget, QAbstractItemView, QPushButton, QComboBox, QDateEdit, QCheckBox

config = ConfigParser()


class Function:
    def __init__(self):
        self.db = DataBase()
        self.subjects = ['Математика', 'Русский язык', 'Литература', 'Английский язык']

    def font(self, name='Yandex Sans Display', size=10):
        return QFont(name, size)

    def windowsdialog(self, dialogtype, title, text, buttons=None):
        msg = QMessageBox()
        msg.setIcon(dialogtype)
        msg.setWindowTitle(title + ' - Яндекс.Дневник')
        msg.setText(text)
        msg.setWindowIcon(QIcon('files/design/images/icon.png'))
        if buttons:
            msg.setStandardButtons(QMessageBox.Yes)
            buttonYes = msg.button(QMessageBox.Yes)
            buttonYes.setText(buttons[0])
            if len(buttons) == 2:
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                buttonYes = msg.button(QMessageBox.Yes)
                buttonYes.setText(buttons[0])
                buttonNo = msg.button(QMessageBox.No)
                buttonNo.setText(buttons[1])
                return msg, buttonYes, buttonNo
            return msg, buttonYes
        else:
            msg.exec_()


class DataBase:
    def __init__(self):
        try:
            self.con = sqlite3.connect('files/db.db')
            self.cur = self.con.cursor()
        except sqlite3.OperationalError:
            func.windowsdialog(QMessageBox.Critical, 'Ошибка', 'Невозможно подключиться к базе '
                                                               'данных! Переустановите программу!')

    def disconnect(self):
        self.con.close()

    def request(self, text, params=None, commit=False):
        if commit:
            self.cur.execute(f"""{text}""", params)
            self.con.commit()
            return True
        else:
            return self.cur.execute(f"""{text}""", params).fetchall()


class UserClass:
    def __init__(self):
        self.info = {'id': None, 'login': None, 'password': None, 'name': None,
                     'surname': None, 'role': None, 'klass': 0}

    def authorization(self, acc_id, login, password, name, surname, role, klass=0):
        self.info = {'id': acc_id, 'login': login, 'password': password, 'name': name,
                     'surname': surname, 'role': role, 'klass': klass}

        userwidget.show()
        userwidget.showinfo()

        if login and password:
            config.read('files/config.ini')
            config.set('User', 'login', f'{login}')
            config.set('User', 'password', f'{password}')
            with open('files/config.ini', 'w') as f:
                config.write(f)

    def update(self, name, surname):
        if len(name) == 0 or len(surname) == 0:
            func.windowsdialog(QMessageBox.Warning, 'Ошибка',
                               'Все поля должны быть заполнены!')
        else:
            if name != self.name or surname != self.surname:
                func.windowsdialog(QMessageBox.Information, 'Сохранено',
                                   f"{name} {surname}, ваша новая информация сохранена!")

                func.db.request("UPDATE accounts set (name, surname) = (?, ?) WHERE login = ?",
                                params=(name, surname, self.login), commit=True)

    def quit(self):
        close, buttonYes, buttonNo = func.windowsdialog(QMessageBox.Warning, 'Выход',
                                                        'Вы действительно хотите выйти из '
                                                        'аккаунта?\nДля использования приложения '
                                                        'в дальнейшем, потребуется '
                                                        'войти в аккаунт заного!',
                                                        buttons=('Да', 'Нет'))
        close.exec_()

        if close.clickedButton() == buttonYes:
            self.info = {'id': None, 'login': None, 'password': None, 'name': None,
                         'surname': None, 'role': None, 'klass': 0}

            config.read('files/config.ini')
            config.set('User', 'login', 'null')
            config.set('User', 'password', 'null')
            with open('files/config.ini', 'w') as f:
                config.write(f)

            global userwidget
            userwidget.timetimer.timeout.disconnect()

            userwidget.hide()
            mainwidget.show()


class RegisterWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('files/design/registerwidget.ui', self)

        self.setWindowIcon(QtGui.QIcon('files/design/images/icon.png'))

        self.regbut.clicked.connect(self.logining)

    def logining(self):
        loginvalue = self.login.text()
        passwordvalue = self.password.text()
        namevalue = self.name.text()
        surnamevalue = self.surname.text()

        if len(loginvalue) == 0 or len(passwordvalue) == 0 or len(namevalue) == 0 or \
                len(surnamevalue) == 0:
            func.windowsdialog(QMessageBox.Warning, 'Ошибка',
                               'Все поля должны быть заполнены!')
        else:
            result = func.db.request("SELECT * FROM accounts WHERE login = ?",
                                     params=[loginvalue])
            if len(result) == 0:
                func.windowsdialog(QMessageBox.Information, 'Успешная регистрация!',
                                   f"{namevalue} {surnamevalue}, вы успешно зарегистрировались!")

                func.db.request("INSERT INTO accounts (login, password, name, surname) "
                                "VALUES (?, ?, ?, ?)", params=(loginvalue, passwordvalue,
                                                               namevalue, surnamevalue),
                                commit=True)
            else:
                func.windowsdialog(QMessageBox.Warning, 'Ошибка',
                                   'Данный логин уже используется!')

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        mainwidget.show()


class LoginWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('files/design/loginwidget.ui', self)

        self.setWindowIcon(QtGui.QIcon('files/design/images/icon.png'))

        self.loginbut.clicked.connect(self.logining)

    def logining(self):
        loginvalue = self.login.text()
        passwordvalue = self.password.text()

        if len(loginvalue) == 0 or len(passwordvalue) == 0:
            func.windowsdialog(QMessageBox.Warning, 'Ошибка',
                               'Введите логин или пароль!')
        else:
            result = func.db.request("SELECT * FROM accounts WHERE login = ? AND password = ?",
                                     params=(loginvalue, passwordvalue))

            if len(result) == 0:
                func.windowsdialog(QMessageBox.Warning, 'Ошибка',
                                   'Неверный логин или пароль!')
            else:
                for enum in result:
                    func.windowsdialog(QMessageBox.Information, 'Успешный вход!',
                                       f"Добро пожаловать, {enum[4]} {enum[5]}!")
                    self.hide()
                    user.authorization(enum[0], loginvalue, passwordvalue, enum[4], enum[5], enum[3],
                                       enum[6])

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        mainwidget.show()


class UserWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('files/design/images/icon.png'))
        uic.loadUi(f'files/design/userwidget.ui', self)

    def openpage(self):
        self.hide()
        but = self.sender().objectName()
        if but == 'onebut':
            actionwidget.show()
            actionwidget.openpage(actionwidget.markspage)
        elif but == 'twobut':
            actionwidget.show()
            actionwidget.openpage(actionwidget.lessonspage)

    def save(self):
        user.update(self.nameline.text(), self.surnameline.text())

    def showinfo(self):
        self.savebut.clicked.connect(self.save)
        self.quitbut.clicked.connect(user.quit)
        self.onebut.clicked.connect(self.openpage)
        self.twobut.clicked.connect(self.openpage)
        self.roleline.setEnabled(False)
        self.klassline.setEnabled(False)
        if user.info['role'] != 'teacher':
            self.klassline.setHidden(False)
            self.label_4.setHidden(False)
            self.klassline.setText(str(user.info["klass"]))
        else:
            self.klassline.setHidden(True)
            self.label_4.setHidden(True)

        self.onebut.setText('Оценки')
        self.twobut.setText('Уроки')
        self.nameline.setText(user.info["name"])
        self.surnameline.setText(user.info["surname"])
        if user.info["role"] == 'teacher':
            self.roleline.setText('Учитель')
        else:
            self.roleline.setText('Ученик')

        self.datetime.setDateTime(QDateTime.currentDateTime().toPyDateTime())

        self.setWindowTitle(f'{user.info["name"]} {user.info["surname"]} - Яндекс.Дневник')
        self.update()

        self.timetimer = QTimer()
        self.timetimer.timeout.connect(self.updatedatetime)
        self.timetimer.start(10000)

    def updatedatetime(self):
        self.datetime.setDateTime(QDateTime.currentDateTime().toPyDateTime())
        self.update()

    def closeEvent(self, event):
        close, buttonYes, buttonNo = func.windowsdialog(QMessageBox.Warning, 'Выход',
                                                        'Вы действительно хотите выйти из '
                                                        'приложения?\nНесохранённые данные будут '
                                                        'утеряны!',
                                                        buttons=('Да', 'Нет'))
        close.exec_()

        if close.clickedButton() == buttonYes:
            event.accept()
        else:
            event.ignore()


class ActionWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('files/design/images/icon.png'))
        self.setGeometry(0, 0, 1200, 800)
        self.setMaximumSize(1200, 800)
        self.setMinimumSize(1200, 800)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout(self)
        self.central_widget.setLayout(self.grid_layout)

    def lessonspage(self):
        self.setWindowTitle(f'Уроки - {user.info["name"]} {user.info["surname"]} '
                            f'- Яндекс.Дневник')

        self.table = QTableWidget()
        self.table.setGeometry(0, 30, 1200, 770)
        self.setFixedSize(1200, 770)
        self.table.setFont(func.font(size=12))

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Предмет', 'Дата урока', 'Тема',
                                              'Домашнее задание', 'Статус'])
        self.table.setRowCount(0)

        self.lessons = {}

        result = func.db.request("SELECT * FROM lessons", [])
        if len(result) != 0:
            counter = 0
            for enum in result:
                lesson = {'date': enum[1], 'topic': enum[2], 'homework': enum[3],
                          'status': enum[4], 'subject_id': enum[5], 'row': counter}
                self.lessons[enum[0]] = lesson
                counter += 1

        self.table.setRowCount(len(self.lessons))

        for lesson in self.lessons:
            lessonstatus = QCheckBox()
            lessonstatus.setText("Проведён")
            if self.lessons[lesson]['status'] == 1:
                lessonstatus.setChecked(True)
            else:
                lessonstatus.setChecked(False)

            lessonsubjest = QComboBox()
            for subject in func.subjects:
                lessonsubjest.addItem(subject)
            lessonsubjest.setCurrentIndex(self.lessons[lesson]['subject_id'])

            currentitem = QDateEdit()
            currentitem.setDate(QDate.fromString(self.lessons[lesson]['date'], "dd.MM.yyyy"))
            currentitem.setDisplayFormat("dd.MM.yyyy")

            if user.info['role'] != 'teacher':
                currentitem.setEnabled(False)
                lessonstatus.setEnabled(False)
                lessonsubjest.setEnabled(False)
            else:
                currentitem.setCalendarPopup(True)

            self.table.setCellWidget(lesson - 1, 0, lessonsubjest)
            self.table.setCellWidget(lesson - 1, 1, currentitem)
            self.table.setItem(lesson - 1, 2,
                               QTableWidgetItem(str(self.lessons[lesson]['topic'])))
            self.table.setItem(lesson - 1, 3, QTableWidgetItem(str(self.lessons[lesson]
                                                                   ['homework'])))
            self.table.setCellWidget(lesson - 1, 4, lessonstatus)

        self.table.resizeRowsToContents()

        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 250)
        self.table.setColumnWidth(4, 100)

        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        if user.info['role'] != 'teacher':
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.savebut = QPushButton()
            self.savebut.setText('Сохранить')
            self.savebut.setFont(func.font('Yandex Sans Text Bold', 11))
            self.savebut.clicked.connect(self.savetable)
            self.savebut.setGeometry(0, 770, 1200, 30)

            self.addbut = QPushButton()
            self.addbut.setText('Добавить')
            self.addbut.setFont(func.font('Yandex Sans Text Bold', 11))
            self.addbut.clicked.connect(lessonwidget.open)
            self.addbut.setGeometry(0, 790, 1200, 30)

            self.grid_layout.addWidget(self.savebut)
            self.grid_layout.addWidget(self.addbut)

        self.grid_layout.addWidget(self.table)

        self.update()

    def markspage(self):
        self.setWindowTitle(f'Оценки - {user.info["name"]} {user.info["surname"]} '
                            f'- Яндекс.Дневник')

        self.table = QTableWidget()
        self.table.setFont(func.font(size=12))

        self.table.setColumnCount(0)
        self.table.setRowCount(0)

        self.table.setRowCount(len(func.subjects))
        self.table.setVerticalHeaderLabels(func.subjects)

        self.lessons = []
        self.lessonsinfo = {}
        result = func.db.request("SELECT id, date, subject_id FROM lessons ORDER BY date", [])

        counter = 0
        if len(result) != 0:
            for enum in result:
                if user.info["role"] != "teacher":
                    self.lessons.append(str(enum[1]))
                else:
                    self.lessons.append(str(f'{enum[1]}\n({func.subjects[enum[2]]})'))
                self.lessonsinfo[enum[0]] = {'column': counter,
                                             'subject_id': enum[2]}
                counter += 1
        self.table.setColumnCount(counter)

        self.table.setHorizontalHeaderLabels(self.lessons)

        if user.info["role"] != "teacher":
            self.setFixedSize(1000, 175)

            result = func.db.request("SELECT lesson_id, mark FROM marks WHERE "
                                     "student_id = ? ORDER BY lesson_id",
                                     [user.info["id"]])
            if len(result) != 0:
                for enum in result:
                    if enum[1] == 'н':
                        tooltip = 'Отсутствовал(-а) по неизвестной причине'
                    elif enum[1] == 'у':
                        tooltip = 'Отсутствовал(-а) по уважительной причине'
                    elif enum[1] == 'б':
                        tooltip = 'Отсутствовал(-а) по болезни'
                    else:
                        tooltip = ""
                    thisitem = QTableWidgetItem(str(enum[1]))
                    thisitem.setToolTip(tooltip)
                    thisitem.setTextAlignment(5)

                    self.table.setItem(self.lessonsinfo[enum[0]]['column'],
                                       self.lessonsinfo[enum[0]]['subject_id'],
                                       thisitem)

            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        else:
            self.marks = ["", "1", "2", "3", "4", "5", "б", "у", "н"]
            self.table.setGeometry(0, 30, 1200, 770)

            self.peoples = []
            self.peoplesinfo = {}
            result = func.db.request("SELECT id, name, surname FROM accounts WHERE role = "
                                     "'student'", [])

            self.setFixedSize(1200, 600)
            counter = 0
            if len(result) != 0:
                for enum in result:
                    self.peoples.append(str(f'{enum[1]} {enum[2]}'))
                    self.peoplesinfo[counter] = {'id': enum[0], 'name': enum[1],
                                                 'surname': enum[2]}
                    counter += 1
            self.table.setRowCount(counter)

            self.table.setVerticalHeaderLabels(self.peoples)

            for i in range(self.table.rowCount()):
                for j in range(self.table.columnCount()):
                    thisitem = QComboBox()
                    for mark in self.marks:
                        thisitem.addItem(mark)
                    self.table.setCellWidget(i, j, thisitem)

                result = func.db.request(
                    "SELECT lesson_id, mark FROM marks WHERE student_id = ?"
                    "ORDER BY lesson_id",
                    [self.peoplesinfo[i]['id']])
                if len(result) != 0:
                    for enum in result:
                        if enum[1] == 'н':
                            tooltip = 'Отсутствовал(-а) по неизвестной причине'
                        elif enum[1] == 'у':
                            tooltip = 'Отсутствовал(-а) по уважительной причине'
                        elif enum[1] == 'б':
                            tooltip = 'Отсутствовал(-а) по болезни'
                        else:
                            tooltip = ''

                        thisitem = QComboBox()
                        for mark in self.marks:
                            thisitem.addItem(mark)
                        thisitem.setCurrentIndex(self.marks.index(enum[1]))
                        thisitem.setToolTip(tooltip)

                        self.table.setCellWidget(i, self.lessonsinfo[enum[0]]['subject_id'],
                                                 thisitem)

            self.savebut = QPushButton()
            self.savebut.setText('Сохранить')
            self.savebut.setFont(func.font('Yandex Sans Text Bold', 11))
            self.savebut.clicked.connect(self.savemarks)
            self.savebut.setGeometry(0, 770, 1200, 30)

            self.grid_layout.addWidget(self.savebut)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)

        self.grid_layout.addWidget(self.table)

        self.update()

    def openpage(self, openfunction):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.removeWidget(self.grid_layout.itemAt(i).widget())
        openfunction()
        self.update()

    def savemarks(self):
        for i in range(self.table.rowCount()):
            peopleid = self.peoplesinfo[i]['id']
            for j in range(self.table.columnCount()):
                for lesson in self.lessonsinfo:
                    if self.lessonsinfo[lesson]['column'] == j:
                        lesson_id = lesson
                mark = self.table.cellWidget(i, j).currentText()
                result = func.db.request("SELECT id FROM marks WHERE lesson_id = ? AND "
                                         "student_id = ?", params=(lesson_id, peopleid))

                if len(result) != 0:
                    if mark != "":
                        func.db.request("UPDATE marks set mark = ? WHERE lesson_id = ? AND "
                                        "student_id = ?",
                                        params=(mark, lesson_id, peopleid), commit=False)
                    else:
                        func.db.request("DELETE FROM marks WHERE lesson_id = ? AND "
                                        "student_id = ?", params=(lesson_id, peopleid),
                                        commit=False)
                else:
                    if mark != "":
                        func.db.request("INSERT INTO marks(lesson_id, mark, student_id) VALUES "
                                        "(?, ?, ?)",
                                        params=(lesson_id, mark, peopleid), commit=False)
                        if mark == 'н':
                            tooltip = 'Отсутствовал(-а) по неизвестной причине'
                        elif mark == 'у':
                            tooltip = 'Отсутствовал(-а) по уважительной причине'
                        elif mark == 'б':
                            tooltip = 'Отсутствовал(-а) по болезни'
                        else:
                            tooltip = ''

                        thisitem = QTableWidgetItem(str(mark))
                        thisitem.setToolTip(tooltip)
                        thisitem.setTextAlignment(5)
                        self.table.setItem(i, j, thisitem)
        func.db.con.commit()

    def savetable(self):
        for i in range(self.table.rowCount()):
            subjectid = func.subjects.index(self.table.cellWidget(i, 0).currentText())
            lessondate = self.table.cellWidget(i, 1).date().toPyDate().strftime("%d.%m.%Y")
            topic = self.table.item(i, 2).text()
            homework = self.table.item(i, 3).text()

            if self.table.cellWidget(i, 4).isChecked():
                status = 1
            else:
                status = 0

            if len(topic) < 1 or len(topic) > 100:
                func.windowsdialog(QMessageBox.Critical, 'Ошибка данных!',
                                   f'Тема не может быть пустой или быть длиннее чем 100 символов!'
                                   f'\nСтрока №{i + 1}.')
                break
            elif len(homework) > 250:
                func.windowsdialog(QMessageBox.Critical, 'Ошибка данных!',
                                   f'Домашнее задание не может быть длиннее чем 250 символов!'
                                   f'\nСтрока №{i + 1}.')
                break

            if len(homework) < 1:
                homework = "Не задано"
                self.table.setItem(i, 3, QTableWidgetItem("Не задано"))

            for lesson in self.lessons:
                if self.lessons[lesson]['row'] == i:
                    lesson_id = lesson

            func.db.request("""UPDATE lessons set (topic, homework, status, date, subject_id) = 
            (?, ?, ?, ?, ?) WHERE id = ?""",
                            params=(topic, homework, status, lessondate,
                                    subjectid, lesson_id), commit=False)
            func.db.con.commit()

    def closeEvent(self, event):
        close, buttonYes, buttonNo = func.windowsdialog(QMessageBox.Warning,
                                                        'Внимание', 'Вы действительно хотите выйти '
                                                                    'на страницу профиля?\nВсе '
                                                                    'несохранённые изменения будут '
                                                                    'утеряны!',
                                                        buttons=('Да', 'Нет'))
        close.exec_()

        if close.clickedButton() == buttonYes:
            self.hide()
            userwidget.show()
        else:
            event.ignore()


class LessonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('files/design/images/icon.png'))
        uic.loadUi(f'files/design/lessonwidget.ui', self)

        for subject in func.subjects:
            self.subjectlesson.addItem(subject)

    def open(self):
        self.topic.setText("")
        self.homework.setPlainText("")

        self.datelesson.setDateTime(QDateTime.currentDateTime().toPyDateTime())

        self.savebut.clicked.connect(self.addlesson)

        actionwidget.hide()
        self.update()
        self.show()

    def addlesson(self):
        lessonsubject = func.subjects.index(self.subjectlesson.currentText())
        lessondate = self.datelesson.date().toPyDate().strftime("%d.%m.%Y")
        lessontopic = self.topic.text()
        lessonhomework = self.homework.toPlainText()

        if self.status.isChecked():
            lessonstatus = 1
        else:
            lessonstatus = 0

        error = False

        if len(lessontopic) < 1 or len(lessontopic) > 100:
            func.windowsdialog(QMessageBox.Critical, 'Ошибка данных!',
                               f'Тема не может быть пустой или быть длиннее чем 100 символов!')
            error = True
        elif len(lessonhomework) > 250:
            func.windowsdialog(QMessageBox.Critical, 'Ошибка данных!',
                               f'Домашнее задание не может быть длиннее чем 250 символов!')
            error = True

        if len(lessonhomework) < 1:
            lessonhomework = "Не задано"

        if not error:
            func.db.request("""INSERT INTO lessons(topic, homework, status, date, subject_id) VALUES 
            (?, ?, ?, ?, ?)""",
                            params=(lessontopic, lessonhomework, lessonstatus, lessondate,
                                    lessonsubject), commit=False)
            func.db.con.commit()

            func.windowsdialog(QMessageBox.Information, 'Успешно',
                               f'Новый урок по предмету {self.subjectlesson.currentText()} '
                               f'({lessondate}) добавлен!')

            self.hide()
            actionwidget.show()
            actionwidget.openpage(actionwidget.lessonspage)

    def closeEvent(self, event):
        close, buttonYes, buttonNo = func.windowsdialog(QMessageBox.Warning,
                                                        'Внимание', 'Вы действительно хотите выйти '
                                                                    'на страницу уроков?\nВсе '
                                                                    'несохранённые изменения будут '
                                                                    'утеряны!',
                                                        buttons=('Да', 'Нет'))
        close.exec_()

        if close.clickedButton() == buttonYes:
            self.hide()
            actionwidget.show()
            actionwidget.openpage(actionwidget.lessonspage)
        else:
            event.ignore()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('files/design/mainwidget.ui', self)
        self.setWindowIcon(QtGui.QIcon('files/design/images/icon.png'))

        self.but_2.clicked.connect(self.go)
        self.but.clicked.connect(self.go)

    def go(self):
        if self.sender().objectName() == 'but_2':
            self.hide()
            loginwidget.show()
        else:
            self.hide()
            regwidget.show()

    def closeEvent(self, event):
        close, buttonYes, buttonNo = func.windowsdialog(QMessageBox.Question,
                                                        'Выход', 'Вы действительно хотите выйти?',
                                                        buttons=('Да', 'Нет'))
        close.exec_()

        if close.clickedButton() == buttonYes:
            event.accept()
        else:
            event.ignore()


def exception_hook(exctype, value, traceback):
    func.windowsdialog(QMessageBox.Critical, 'Ошибка при работе приложения',
                       f'Приносим свои извинения, но во время работы произошла ошибка!\n'
                       f'Попробуйте перезапустить приложение.\n\n\nИнформация об ошибке:\n'
                       f'{exctype.__module__} > {exctype.__name__}:\n{value}')
    sys.exit(1)


def load():
    config.read('files/config.ini')
    flag = False
    if not config.sections():
        config.add_section('User')
        config.set('User', 'login', 'null')
        config.set('User', 'password', 'null')
        with open('files/config.ini', 'w') as f:
            config.write(f)
    else:
        userlogin = config['User']['login']
        password = config['User']['password']
        if userlogin != 'null' and password != 'null':
            flag = True
            result = func.db.request("SELECT * FROM accounts WHERE login = ? AND password = ?",
                                     params=(userlogin, password))

            if len(result) != 0:
                for enum in result:
                    user.authorization(enum[0], userlogin, password, enum[4], enum[5], enum[3],
                                       enum[6])
            else:
                func.windowsdialog(QMessageBox.Warning, 'Внимание!',
                                   f"Сохранены неверные данные!\nАвторизуйтесь в аккаунт ещё раз.")

                config.set('User', 'login', 'null')
                config.set('User', 'password', 'null')
                with open('files/config.ini', 'w') as f:
                    config.write(f)
                loginwidget.show()
    if not flag:
        mainwidget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    func = Function()
    user = UserClass()

    regwidget = RegisterWidget()
    loginwidget = LoginWidget()
    mainwidget = MainWindow()
    userwidget = UserWidget()
    actionwidget = ActionWidget()
    lessonwidget = LessonWidget()

    load()
    sys.excepthook = exception_hook
    sys.exit(app.exec_())
