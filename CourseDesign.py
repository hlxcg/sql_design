from PyQt5.QtWidgets import (QDialog, QLabel, QCheckBox, QHBoxLayout,
                             QLineEdit, QPushButton, QToolButton, QTableWidget,
                             QVBoxLayout, QApplication, QWidget, QFrame,
                             QMainWindow, QMessageBox, QTableWidgetItem,
                             QScrollArea, QTextEdit, QAction, QMenu,
                             QFileDialog, QComboBox, QAbstractItemView,
                             QDialogButtonBox)
from PyQt5.QtCore import Qt, QDateTime, QSize, QRect, QUrl, pyqtSlot
from PyQt5.QtGui import (QPixmap, QColor, QPalette, QFont,
                         QMovie, QMouseEvent, QCursor, QDesktopServices)
import sys
import os
import pymysql

# 全局变量
db_connection = None
main_window = None
switch_win = None

books_att = {
    "BNO": "馆藏号",
    "ISBN": "书号",
    "BNAME": "书名",
    "WRITER": "作者",
    "PUB": "出版社",
    "PRICE": "定价",
    "CNO": "存放书架号",
    "STATE": "状态",
    "RNO": "借阅读者号"
}
books_att_r = {v: k for k, v in books_att.items()}

manager_att = {
    "WNO": "工号",
    "WNAME": "姓名",
    "WSEX": "性别",
    "WBRITH": "出生日期",
    "WID": "身份证号",
    "WTEL": "电话",
    "UNM": "用户名"
}
manager_att_r = {v: k for k, v in manager_att.items()}

reader_att = {
    "RNO": "读者号",
    "RNAME": "姓名",
    "RSEX": "性别",
    "RBIRTH": "出生日期",
    "RID": "身份证号",
    "RTEL": "电话",
    "BD": "已借本数",
    "LIM": "限借本数"
}
reader_att_r = {v: k for k, v in reader_att.items()}

shell_att = {
    "CNO": "书架号",
    "CNAME": "书架名",
    "KIND": "分类",
    "WNO": "管理员工号"
}
shell_att_r = {v: k for k, v in shell_att.items()}

match_att = {
    "相关匹配": "LIKE \'%{}%\'",
    "前字匹配": "LIKE \'%{}\'",
    "后字匹配": "LIKE \'{}%\'",
    "绝对匹配": "=\'{}\'"
}

sort_att = {
    "升序": "ASC",
    "降序": "DESC"
}


class MySQL:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("数据库连接成功！")
            return True
        except pymysql.Error as e:
            print(f"数据库连接失败：{e}")
            return False

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except pymysql.Error as e:
            QMessageBox.critical(None, "错误", f"数据库语句执行出错:{e}")
            print(f"数据库语句执行出错:{e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("数据库连接已关闭！")


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("管理员登录界面")
        screen = app.desktop().screenGeometry()
        x = 300
        y = 100
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)

        layout = QVBoxLayout()

        label_username = QLabel("账号:", self)
        self.text_username = QLineEdit(self)
        label_password = QLabel("密码:", self)
        self.text_password = QLineEdit(self)
        self.text_password.setEchoMode(QLineEdit.Password)

        # 添加显示密码的复选框
        checkbox_layout = QHBoxLayout()
        self.checkbox_show_password = QCheckBox("显示密码", self)
        self.checkbox_show_password.setCursor(Qt.PointingHandCursor)
        self.checkbox_show_password.stateChanged.connect(
            self.toggle_password_visibility)
        checkbox_layout.addStretch()

        button_login = QPushButton("登录", self)
        button_login.setCursor(Qt.PointingHandCursor)
        button_login.clicked.connect(self.login)

        layout.addWidget(label_username)
        layout.addWidget(self.text_username)
        layout.addWidget(label_password)
        layout.addWidget(self.text_password)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.checkbox_show_password)
        layout.addWidget(button_login)

        self.setLayout(layout)

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.text_password.setEchoMode(QLineEdit.Normal)
        else:
            self.text_password.setEchoMode(QLineEdit.Password)

    def login(self):
        username = self.text_username.text()
        password = self.text_password.text()
        # username = "hlxcg"
        # password = "Ccyisaboy229@"
        db = MySQL(host="36.139.236.110",
                   user=username,
                   password=password,
                   database="homework5")

        if username == "" or password == "":
            QMessageBox.critical(None, "登录失败", "账号或密码不能为空")
        elif db.connect():
            global db_connection
            db_connection = db
            self.accept()  # 登录成功，关闭登录界面
        else:
            QMessageBox.critical(None, "登录失败", "账号或密码错误")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', '确定要退出吗?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            exit()
        else:
            event.ignore()


class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加图书")
        screen = app.desktop().screenGeometry()
        x, y = 300, 400
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)
        self.label1 = QLabel("馆藏号:", self)
        self.input1 = QLineEdit(self)
        self.label2 = QLabel("书号:", self)
        self.input2 = QLineEdit(self)
        self.label3 = QLabel("书名:", self)
        self.input3 = QLineEdit(self)
        self.label4 = QLabel("作者:", self)
        self.input4 = QLineEdit(self)
        self.label5 = QLabel("出版社:", self)
        self.input5 = QLineEdit(self)
        self.label6 = QLabel("定价:", self)
        self.input6 = QLineEdit(self)
        self.label7 = QLabel("存放书架号:", self)
        self.input7 = QLineEdit(self)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.button.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input2)
        layout.addWidget(self.label3)
        layout.addWidget(self.input3)
        layout.addWidget(self.label4)
        layout.addWidget(self.input4)
        layout.addWidget(self.label5)
        layout.addWidget(self.input5)
        layout.addWidget(self.label6)
        layout.addWidget(self.input6)
        layout.addWidget(self.label7)
        layout.addWidget(self.input7)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def get_data(self):
        return (self.input1.text(), self.input2.text(), self.input3.text(),
                self.input4.text(), self.input5.text(), self.input6.text(),
                self.input7.text(), '在馆')


class EditBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改图书")
        screen = app.desktop().screenGeometry()
        x, y = 300, 400
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)

        # 创建标签和输入框
        self.label1 = QLabel("馆藏号:", self)
        self.input1 = QLineEdit(self)
        self.label2 = QLabel("书号:", self)
        self.input2 = QLineEdit(self)
        self.label3 = QLabel("书名:", self)
        self.input3 = QLineEdit(self)
        self.label4 = QLabel("作者:", self)
        self.input4 = QLineEdit(self)
        self.label5 = QLabel("出版社:", self)
        self.input5 = QLineEdit(self)
        self.label6 = QLabel("定价:", self)
        self.input6 = QLineEdit(self)
        self.label7 = QLabel("存放书架号:", self)
        self.input7 = QLineEdit(self)
        self.label8 = QLabel("状态:", self)
        self.input8 = QLineEdit(self)
        self.label9 = QLabel("借阅读者号:", self)
        self.input9 = QLineEdit(self)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.button.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input2)
        layout.addWidget(self.label3)
        layout.addWidget(self.input3)
        layout.addWidget(self.label4)
        layout.addWidget(self.input4)
        layout.addWidget(self.label5)
        layout.addWidget(self.input5)
        layout.addWidget(self.label6)
        layout.addWidget(self.input6)
        layout.addWidget(self.label7)
        layout.addWidget(self.input7)
        layout.addWidget(self.label8)
        layout.addWidget(self.input8)
        layout.addWidget(self.label9)
        layout.addWidget(self.input9)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # 连接按钮的点击事件处理函数
        self.button.clicked.connect(self.accept)

    def setValues(self, values):
        # 设置输入框的初始值
        self.input1.setText(str(values[0]))
        self.input2.setText(str(values[1]))
        self.input3.setText(str(values[2]))
        self.input4.setText(str(values[3]))
        self.input5.setText(str(values[4]))
        self.input6.setText(str(values[5]))
        self.input7.setText(str(values[6]))
        self.input8.setText(str(values[7]))
        self.input9.setText(str(values[8]))

    def get_data(self):
        return (self.input1.text(), self.input2.text(), self.input3.text(),
                self.input4.text(), self.input5.text(), self.input6.text(),
                self.input7.text(), self.input7.text(), self.input9.text())


class BookManagementWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_win = main_window
        self.setWindowTitle("图书管理")
        self.setGeometry(0, 0, 888, 690)

        self.result_textbox = QTableWidget(self)
        self.result_textbox.setGeometry(2, 0, 884, 600)
        self.result_textbox.setSelectionBehavior(QAbstractItemView.SelectRows)
        print("与图书管理窗口建立链接")
        self.result_textbox.cellClicked.connect(self.handle_cell_clicked)

        self.label_input = QLabel("请输入关键文字:", self)
        self.label_input.setGeometry(2, 601, 138, 30)
        self.input_textbox = QLineEdit(self)
        self.input_textbox.setGeometry(2, 632, 138, 30)

        self.label_sort_order_combo = QLabel("排序:", self)
        self.label_sort_order_combo.setGeometry(142, 601, 40, 30)
        self.sort_order_combo = QComboBox(self)
        self.sort_order_combo.addItem("升序")
        self.sort_order_combo.addItem("降序")
        self.sort_order_combo.setGeometry(142, 632, 60, 30)

        self.label_sort_property_combo = QLabel("排序属性:", self)
        self.label_sort_property_combo.setGeometry(204, 601, 110, 30)
        self.sort_property_combo = QComboBox(self)
        self.sort_property_combo.addItem("馆藏号")
        self.sort_property_combo.addItem("书号")
        self.sort_property_combo.addItem("书名")
        self.sort_property_combo.addItem("作者")
        self.sort_property_combo.addItem("出版社")
        self.sort_property_combo.addItem("定价")
        self.sort_property_combo.addItem("存放书架号")
        self.sort_property_combo.addItem("状态")
        self.sort_property_combo.setGeometry(204, 632, 110, 30)

        self.match_type_combo = QLabel("正则匹配:", self)
        self.match_type_combo.setGeometry(316, 601, 100, 30)
        self.match_type_combo = QComboBox(self)
        self.match_type_combo.addItem("相关匹配")
        self.match_type_combo.addItem("前字匹配")
        self.match_type_combo.addItem("后字匹配")
        self.match_type_combo.addItem("绝对匹配")
        self.match_type_combo.setGeometry(316, 632, 100, 30)

        self.regex_property_combo = QLabel("匹配属性:", self)
        self.regex_property_combo.setGeometry(418, 601, 110, 30)
        self.regex_property_combo = QComboBox(self)
        self.regex_property_combo.addItem("书名")
        self.regex_property_combo.addItem("馆藏号")
        self.regex_property_combo.addItem("书号")
        self.regex_property_combo.addItem("作者")
        self.regex_property_combo.addItem("出版社")
        self.regex_property_combo.addItem("定价")
        self.regex_property_combo.addItem("存放书架号")
        self.regex_property_combo.addItem("状态")
        self.regex_property_combo.addItem("借阅读者号")
        self.regex_property_combo.setGeometry(418, 632, 110, 30)

        self.query_button = QLabel("点击查询:", self)
        self.query_button.setGeometry(530, 601, 70, 30)
        self.query_button = QPushButton("查询", self)
        self.query_button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.query_button.setCursor(Qt.PointingHandCursor)
        self.query_button.setGeometry(530, 632, 70, 30)
        self.query_button.clicked.connect(self.handle_query)

        self.add_button = QLabel("点击增加:", self)
        self.add_button.setGeometry(602, 601, 70, 30)
        self.add_button = QPushButton("增加", self)
        self.add_button.setStyleSheet("color: green;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setGeometry(602, 632, 70, 30)
        self.add_button.clicked.connect(self.handle_add)

        self.change_button = QLabel("点击修改:", self)
        self.change_button.setGeometry(674, 601, 70, 30)
        self.change_button = QPushButton("修改", self)
        self.change_button.setStyleSheet("color: yellow;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.change_button.setCursor(Qt.PointingHandCursor)
        self.change_button.setGeometry(674, 632, 70, 30)
        self.change_button.clicked.connect(self.handle_change)

        self.delete_button = QLabel("点击删除:", self)
        self.delete_button.setGeometry(746, 601, 70, 30)
        self.delete_button = QPushButton("删除", self)
        self.delete_button.setStyleSheet("color: red;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setGeometry(746, 632, 70, 30)
        self.delete_button.clicked.connect(self.handle_delete)

        self.borrow_button = QLabel("点击借还:", self)
        self.borrow_button.setGeometry(818, 601, 70, 30)
        self.borrow_button = QPushButton("借还", self)
        self.borrow_button.setStyleSheet("color: blue;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.borrow_button.setCursor(Qt.PointingHandCursor)
        self.borrow_button.setGeometry(818, 632, 70, 30)
        self.borrow_button.clicked.connect(self.handle_borrow)

        self.handle_query()

    def handle_query(self):
        key_text = self.input_textbox.text()
        sort_text = self.sort_order_combo.currentText()
        sort_property = self.sort_property_combo.currentText()
        match_text = self.match_type_combo.currentText()
        regex_property = self.regex_property_combo.currentText()
        query_text = ("SELECT * FROM books WHERE {0} {1} ORDER BY {2} {3}"
                      .format(books_att_r[regex_property],
                              match_att[match_text],
                              books_att_r[sort_property], sort_att[sort_text]))
        query_text = query_text.format(key_text)
        print(query_text)
        result = (db_connection.execute_query(query_text))
        # 设置表格的行数和列数
        self.result_textbox.clearContents()
        if result:
            self.result_textbox.setRowCount(len(result))
            self.result_textbox.setColumnCount(len(result[0]))

            # 设置列属性名
            column_names = [desc[0] for desc in db_connection.cursor
                            .description]
            column_names = [books_att[desc] for desc in column_names]
            self.result_textbox.setHorizontalHeaderLabels(column_names)

            # 填充表格数据
            self.result_textbox.horizontalHeader().setVisible(True)
            for i, row in enumerate(result):
                for j, item in enumerate(row):
                    table_item = QTableWidgetItem(str(item))
                    self.result_textbox.setItem(i, j, table_item)

            self.result_textbox.setEditTriggers(QAbstractItemView
                                                .NoEditTriggers)
            self.result_textbox.resizeColumnsToContents()
            self.result_textbox.resizeRowsToContents()
        else:
            # 清空表格数据并显示查询结果为空的提示消息
            self.result_textbox.clearContents()
            self.result_textbox.setRowCount(1)
            self.result_textbox.setColumnCount(1)
            self.result_textbox.horizontalHeader().setVisible(False)
            self.result_textbox.setColumnWidth(0, 100)  # 设置第一列的宽度为300
            self.result_textbox.setItem(0, 0, QTableWidgetItem("查询结果为空"))
        self.main_win.renew_bs()

    def handle_delete(self):
        reply = QMessageBox.question(self, '提示',
                                     '确定要删除吗?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(self.result_textbox.selectedRanges()) != 0:
                delete_text = ("DELETE FROM books WHERE BNO=\'{}\'"
                               .format(self.choice_id))
                print(delete_text)
                db_connection.execute_query(delete_text)
                db_connection.execute_query("COMMIT")

                self.main_win.renew_bs()
                self.handle_query()
            else:
                QMessageBox.critical(None, "删除失败", "未选择元组")

    def handle_borrow(self):
        dialog = QDialog()
        dialog.setWindowTitle('请输入借阅信息')
        dialog.setFixedSize(300, 160)  # 设置弹窗的大小

        layout = QVBoxLayout()

        book_no_label = QLabel('馆藏号:')
        book_no_input = QLineEdit()
        layout.addWidget(book_no_label)
        layout.addWidget(book_no_input)

        borrower_no_label = QLabel('借阅读者号:')
        borrower_no_input = QLineEdit()
        layout.addWidget(borrower_no_label)
        layout.addWidget(borrower_no_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            book_no = book_no_input.text()
            borrower_no = borrower_no_input.text()
            if book_no == '' or borrower_no == '':
                QMessageBox.critical(None, "借还失败", "馆藏号或借阅读者号不能为空")
                self.handle_borrow()
            else:
                print('馆藏号:', book_no)
                print('借阅读者号:', borrower_no)
                borrow_text_st1 = ("select * FROM books WHERE BNO=\'{}\'"
                                   .format(book_no))
                borrow_text_st2 = ("select * FROM reader WHERE RNO=\'{}\'"
                                   .format(borrower_no))
                print(borrow_text_st1)
                print(borrow_text_st2)
                result_q1 = db_connection.execute_query(borrow_text_st1)
                result_q2 = db_connection.execute_query(borrow_text_st2)
                if len(result_q1) == 0 or len(result_q2) == 0:
                    QMessageBox.critical(None, "借还失败", "不存在该书或该读者")
                    self.handle_borrow()
                elif result_q1[0][7] == '在馆':
                    if result_q2[0][6] + 1 > result_q2[0][7]:
                        QMessageBox.critical(None, "借还失败", "超出借阅数量")
                        self.handle_borrow()
                    else:
                        borrow_text_st3 = ("UPDATE books SET STATE='在借', RNO=\
                            \'{0}\' WHERE BNO=\'{1}\'".format(borrower_no,
                                                              book_no))
                        borrow_text_st4 = ("UPDATE reader SET BD=BD+1\
                            WHERE RNO=\'{}\'".format(borrower_no))
                        db_connection.execute_query(borrow_text_st2)
                        print(borrow_text_st3)
                        print(borrow_text_st4)
                        db_connection.execute_query(borrow_text_st3)
                        db_connection.execute_query(borrow_text_st4)
                        db_connection.execute_query("COMMIT")

                        self.main_win.renew_bs()
                        self.handle_query()
                elif (result_q1[0][7] == '在借' and
                      result_q1[0][8] == borrower_no):
                    borrow_text_st3 = ("UPDATE books SET STATE='在馆',\
                        RNO=NULL WHERE BNO=\'{}\'".format(book_no))
                    borrow_text_st4 = ("UPDATE reader SET BD=BD-1\
                        WHERE RNO=\'{}\'".format(borrower_no))
                    db_connection.execute_query(borrow_text_st2)
                    print(borrow_text_st3)
                    print(borrow_text_st4)
                    db_connection.execute_query(borrow_text_st3)
                    db_connection.execute_query(borrow_text_st4)
                    db_connection.execute_query("COMMIT")

                    self.main_win.renew_bs()
                    self.handle_query()
                else:
                    QMessageBox.critical(None, "借还失败", "不存在该借阅关系")
                    self.handle_borrow()

    def handle_add(self):
        dialog = AddBookDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            print(data)
            insert_text = "INSERT INTO books (BNO,ISBN,BNAME,WRITER,PUB,PRICE,\
                CNO,STATE) VALUES{}".format(data)
            print(insert_text)
            db_connection.execute_query(insert_text)
            db_connection.execute_query("COMMIT")

            self.main_win.renew_bs()
            self.handle_query()

    def handle_change(self):
        reply = QMessageBox.question(self, '提示',
                                     '确定要修改吗?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(self.result_textbox.selectedRanges()) != 0:
                dialog = EditBookDialog()
                dialog.setValues(db_connection.execute_query("SELECT * FROM\
                    books WHERE BNO=\'{}\'".format(self.choice_id))[0])
                if dialog.exec_() == QDialog.Accepted:
                    change_text = ("UPDATE books SET BNO=\'{0}\',ISBN=\'{1}\',\
                        BNAME=\'{2}\',WRITER=\'{3}\',PUB=\'{4}\',PRICE=\'{5}\',CNO=\'{6}\',\
                            STATE=\'{7}\',RNO=\'{8}\' WHERE BNO=\'{9}\'\
                                ".format(dialog.get_data()[0],
                                         dialog.get_data()[1],
                                         dialog.get_data()[2],
                                         dialog.get_data()[3],
                                         dialog.get_data()[4],
                                         dialog.get_data()[5],
                                         dialog.get_data()[6],
                                         dialog.get_data()[7],
                                         dialog.get_data()[8],
                                         self.choice_id))
                    print(change_text)
                    db_connection.execute_query(change_text)
                    db_connection.execute_query("COMMIT")

                    self.main_win.renew_bs()
                    self.handle_query()
            else:
                QMessageBox.critical(None, "修改失败", "未选择元组")

    def handle_cell_clicked(self, row, column):
        self.selected_range = self.result_textbox.selectedRanges()[0]
        selected_row = self.selected_range.topRow()
        self.choice_id = self.result_textbox.item(selected_row, 0).text()
        print("该元组唯一标识符:{}".format(self.choice_id))


class AddShelfDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加书架")
        screen = app.desktop().screenGeometry()
        x, y = 300, 200
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)
        self.label1 = QLabel("书架号:", self)
        self.input1 = QLineEdit(self)
        self.label2 = QLabel("书架名:", self)
        self.input2 = QLineEdit(self)
        self.label3 = QLabel("分类:", self)
        self.input3 = QLineEdit(self)
        self.label4 = QLabel("管理员工号:", self)
        self.input4 = QLineEdit(self)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.button.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input2)
        layout.addWidget(self.label3)
        layout.addWidget(self.input3)
        layout.addWidget(self.label4)
        layout.addWidget(self.input4)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def get_data(self):
        return (self.input1.text(), self.input2.text(), self.input3.text(),
                self.input4.text())


class EditShelfDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改书架")
        screen = app.desktop().screenGeometry()
        x, y = 300, 200
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)

        # 创建标签和输入框
        self.label1 = QLabel("书架号:", self)
        self.input1 = QLineEdit(self)
        self.label2 = QLabel("书架名:", self)
        self.input2 = QLineEdit(self)
        self.label3 = QLabel("分类:", self)
        self.input3 = QLineEdit(self)
        self.label4 = QLabel("管理员工号:", self)
        self.input4 = QLineEdit(self)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.button.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input2)
        layout.addWidget(self.label3)
        layout.addWidget(self.input3)
        layout.addWidget(self.label4)
        layout.addWidget(self.input4)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # 连接按钮的点击事件处理函数
        self.button.clicked.connect(self.accept)

    def setValues(self, values):
        # 设置输入框的初始值
        self.input1.setText(str(values[0]))
        self.input2.setText(str(values[1]))
        self.input3.setText(str(values[2]))
        self.input4.setText(str(values[3]))

    def get_data(self):
        return (self.input1.text(), self.input2.text(), self.input3.text(),
                self.input4.text())


class ShelfManagementWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_win = main_window
        self.setWindowTitle("书架管理")
        self.setGeometry(0, 0, 888, 690)

        self.result_textbox = QTableWidget(self)
        self.result_textbox.setGeometry(2, 0, 884, 600)
        self.result_textbox.setSelectionBehavior(QAbstractItemView.SelectRows)
        print("与书架管理窗口建立链接")
        self.result_textbox.cellClicked.connect(self.handle_cell_clicked)

        self.label_input = QLabel("请输入关键文字:", self)
        self.label_input.setGeometry(2, 601, 198, 30)
        self.input_textbox = QLineEdit(self)
        self.input_textbox.setGeometry(2, 632, 198, 30)

        self.label_sort_order_combo = QLabel("排序:", self)
        self.label_sort_order_combo.setGeometry(202, 601, 40, 30)
        self.sort_order_combo = QComboBox(self)
        self.sort_order_combo.addItem("升序")
        self.sort_order_combo.addItem("降序")
        self.sort_order_combo.setGeometry(202, 632, 60, 30)

        self.label_sort_property_combo = QLabel("排序属性:", self)
        self.label_sort_property_combo.setGeometry(264, 601, 110, 30)
        self.sort_property_combo = QComboBox(self)
        self.sort_property_combo.addItem("书架号")
        self.sort_property_combo.addItem("书架名")
        self.sort_property_combo.addItem("分类")
        self.sort_property_combo.addItem("管理员工号")
        self.sort_property_combo.setGeometry(264, 632, 110, 30)

        self.match_type_combo = QLabel("正则匹配:", self)
        self.match_type_combo.setGeometry(376, 601, 100, 30)
        self.match_type_combo = QComboBox(self)
        self.match_type_combo.addItem("相关匹配")
        self.match_type_combo.addItem("前字匹配")
        self.match_type_combo.addItem("后字匹配")
        self.match_type_combo.addItem("绝对匹配")
        self.match_type_combo.setGeometry(376, 632, 100, 30)

        self.regex_property_combo = QLabel("匹配属性:", self)
        self.regex_property_combo.setGeometry(478, 601, 110, 30)
        self.regex_property_combo = QComboBox(self)
        self.regex_property_combo.addItem("分类")
        self.regex_property_combo.addItem("书架号")
        self.regex_property_combo.addItem("书架名")
        self.regex_property_combo.addItem("管理员工号")
        self.regex_property_combo.setGeometry(478, 632, 110, 30)

        self.query_button = QLabel("点击查询:", self)
        self.query_button.setGeometry(592, 601, 70, 30)
        self.query_button = QPushButton("查询", self)
        self.query_button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.query_button.setCursor(Qt.PointingHandCursor)
        self.query_button.setGeometry(592, 632, 70, 30)
        self.query_button.clicked.connect(self.handle_query)

        self.add_button = QLabel("点击增加:", self)
        self.add_button.setGeometry(666, 601, 70, 30)
        self.add_button = QPushButton("增加", self)
        self.add_button.setStyleSheet("color: green;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setGeometry(666, 632, 70, 30)
        self.add_button.clicked.connect(self.handle_add)

        self.change_button = QLabel("点击修改:", self)
        self.change_button.setGeometry(740, 601, 70, 30)
        self.change_button = QPushButton("修改", self)
        self.change_button.setStyleSheet("color: yellow;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.change_button.setCursor(Qt.PointingHandCursor)
        self.change_button.setGeometry(740, 632, 70, 30)
        self.change_button.clicked.connect(self.handle_change)

        self.delete_button = QLabel("点击删除:", self)
        self.delete_button.setGeometry(814, 601, 70, 30)
        self.delete_button = QPushButton("删除", self)
        self.delete_button.setStyleSheet("color: red;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setGeometry(814, 632, 70, 30)
        self.delete_button.clicked.connect(self.handle_delete)

        self.handle_query()

    def handle_query(self):
        key_text = self.input_textbox.text()
        sort_text = self.sort_order_combo.currentText()
        sort_property = self.sort_property_combo.currentText()
        match_text = self.match_type_combo.currentText()
        regex_property = self.regex_property_combo.currentText()
        query_text = ("SELECT * FROM shell WHERE {0} {1} ORDER BY {2} {3}"
                      .format(shell_att_r[regex_property],
                              match_att[match_text],
                              shell_att_r[sort_property], sort_att[sort_text]))
        query_text = query_text.format(key_text)
        print(query_text)
        result = (db_connection.execute_query(query_text))
        # 设置表格的行数和列数
        self.result_textbox.clearContents()
        if result:
            self.result_textbox.setRowCount(len(result))
            self.result_textbox.setColumnCount(len(result[0]))

            # 设置列属性名
            column_names = [desc[0] for desc in db_connection.cursor
                            .description]
            column_names = [shell_att[desc] for desc in column_names]
            self.result_textbox.setHorizontalHeaderLabels(column_names)

            # 填充表格数据
            self.result_textbox.horizontalHeader().setVisible(True)
            for i, row in enumerate(result):
                for j, item in enumerate(row):
                    table_item = QTableWidgetItem(str(item))
                    self.result_textbox.setItem(i, j, table_item)

            self.result_textbox.setEditTriggers(QAbstractItemView
                                                .NoEditTriggers)
            self.result_textbox.resizeColumnsToContents()
            self.result_textbox.resizeRowsToContents()
        else:
            # 清空表格数据并显示查询结果为空的提示消息
            self.result_textbox.clearContents()
            self.result_textbox.setRowCount(1)
            self.result_textbox.setColumnCount(1)
            self.result_textbox.horizontalHeader().setVisible(False)
            self.result_textbox.setColumnWidth(0, 100)  # 设置第一列的宽度为300
            self.result_textbox.setItem(0, 0, QTableWidgetItem("查询结果为空"))
        self.main_win.renew_bs()

    def handle_delete(self):
        reply = QMessageBox.question(self, '提示',
                                     '确定要删除吗?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(self.result_textbox.selectedRanges()) != 0:
                delete_text = ("DELETE FROM shell WHERE CNO=\'{}\'"
                               .format(self.choice_id))
                print(delete_text)
                db_connection.execute_query(delete_text)
                db_connection.execute_query("COMMIT")

                self.main_win.renew_bs()
                self.handle_query()
            else:
                QMessageBox.critical(None, "删除失败", "未选择元组")

    def handle_add(self):
        dialog = AddShelfDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            print(data)
            #  (CNO,CNAME,KIND,WNO)
            insert_text = ("INSERT INTO shell VALUES{}"
                           .format(data))
            print(insert_text)
            db_connection.execute_query(insert_text)
            db_connection.execute_query("COMMIT")

            self.main_win.renew_bs()
            self.handle_query()

    def handle_change(self):
        reply = QMessageBox.question(self, '提示',
                                     '确定要修改吗?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(self.result_textbox.selectedRanges()) != 0:
                dialog = EditShelfDialog()
                dialog.setValues(db_connection.execute_query("SELECT * FROM\
                    shell WHERE CNO=\'{}\'".format(self.choice_id))[0])
                if dialog.exec_() == QDialog.Accepted:
                    change_text = ("UPDATE shell SET CNO=\'{0}\',CNAME=\'{1}\'\
                        ,KIND=\'{2}\',WNO=\'{3}\' WHERE CNO=\'{4}\'\
                                ".format(dialog.get_data()[0],
                                         dialog.get_data()[1],
                                         dialog.get_data()[2],
                                         dialog.get_data()[3],
                                         self.choice_id))
                    print(change_text)
                    db_connection.execute_query(change_text)
                    db_connection.execute_query("COMMIT")

                    self.main_win.renew_bs()
                    self.handle_query()
            else:
                QMessageBox.critical(None, "修改失败", "未选择元组")

    def handle_cell_clicked(self, row, column):
        self.selected_range = self.result_textbox.selectedRanges()[0]
        selected_row = self.selected_range.topRow()
        self.choice_id = self.result_textbox.item(selected_row, 0).text()
        print("该元组唯一标识符:{}".format(self.choice_id))


class AddReaderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加读者")
        screen = app.desktop().screenGeometry()
        x, y = 300, 400
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)
        self.label1 = QLabel("读者号:", self)
        self.input1 = QLineEdit(self)
        self.label2 = QLabel("姓名:", self)
        self.input2 = QLineEdit(self)
        self.label3 = QLabel("性别:", self)
        self.input3 = QLineEdit(self)
        self.label4 = QLabel("出生日期:", self)
        self.input4 = QLineEdit(self)
        self.label5 = QLabel("身份证号:", self)
        self.input5 = QLineEdit(self)
        self.label6 = QLabel("电话:", self)
        self.input6 = QLineEdit(self)
        self.label7 = QLabel("限借本数:", self)
        self.input7 = QLineEdit(self)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.button.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input2)
        layout.addWidget(self.label3)
        layout.addWidget(self.input3)
        layout.addWidget(self.label4)
        layout.addWidget(self.input4)
        layout.addWidget(self.label5)
        layout.addWidget(self.input5)
        layout.addWidget(self.label6)
        layout.addWidget(self.input6)
        layout.addWidget(self.label7)
        layout.addWidget(self.input7)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def get_data(self):
        return (self.input1.text(), self.input2.text(), self.input3.text(),
                self.input4.text(), self.input5.text(), self.input6.text(),
                0, self.input7.text())


class EditReaderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改读者")
        screen = app.desktop().screenGeometry()
        x, y = 300, 400
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)
        # 创建标签和输入框
        self.label1 = QLabel("读者号:", self)
        self.input1 = QLineEdit(self)
        self.label2 = QLabel("姓名:", self)
        self.input2 = QLineEdit(self)
        self.label3 = QLabel("性别:", self)
        self.input3 = QLineEdit(self)
        self.label4 = QLabel("出生日期:", self)
        self.input4 = QLineEdit(self)
        self.label5 = QLabel("身份证号:", self)
        self.input5 = QLineEdit(self)
        self.label6 = QLabel("电话:", self)
        self.input6 = QLineEdit(self)
        self.label7 = QLabel("已借本数:", self)
        self.input7 = QLineEdit(self)
        self.label8 = QLabel("限借本数:", self)
        self.input8 = QLineEdit(self)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.button.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.input1)
        layout.addWidget(self.label2)
        layout.addWidget(self.input2)
        layout.addWidget(self.label3)
        layout.addWidget(self.input3)
        layout.addWidget(self.label4)
        layout.addWidget(self.input4)
        layout.addWidget(self.label5)
        layout.addWidget(self.input5)
        layout.addWidget(self.label6)
        layout.addWidget(self.input6)
        layout.addWidget(self.label7)
        layout.addWidget(self.input7)
        layout.addWidget(self.label8)
        layout.addWidget(self.input8)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # 连接按钮的点击事件处理函数
        self.button.clicked.connect(self.accept)

    def setValues(self, values):
        # 设置输入框的初始值
        self.input1.setText(str(values[0]))
        self.input2.setText(str(values[1]))
        self.input3.setText(str(values[2]))
        self.input4.setText(str(values[3]))
        self.input5.setText(str(values[4]))
        self.input6.setText(str(values[5]))
        self.input7.setText(str(values[6]))
        self.input8.setText(str(values[7]))

    def get_data(self):
        return (self.input1.text(), self.input2.text(), self.input3.text(),
                self.input4.text(), self.input5.text(), self.input6.text(),
                self.input7.text(), self.input7.text())


class ReaderManagementWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_win = main_window
        self.setWindowTitle("读者管理")
        self.setGeometry(0, 0, 888, 690)

        self.result_textbox = QTableWidget(self)
        self.result_textbox.setGeometry(2, 0, 884, 600)
        self.result_textbox.setSelectionBehavior(QAbstractItemView.SelectRows)
        print("与读者管理窗口建立链接")
        self.result_textbox.cellClicked.connect(self.handle_cell_clicked)

        self.label_input = QLabel("请输入关键文字:", self)
        self.label_input.setGeometry(2, 601, 198, 30)
        self.input_textbox = QLineEdit(self)
        self.input_textbox.setGeometry(2, 632, 198, 30)

        self.label_sort_order_combo = QLabel("排序:", self)
        self.label_sort_order_combo.setGeometry(202, 601, 40, 30)
        self.sort_order_combo = QComboBox(self)
        self.sort_order_combo.addItem("升序")
        self.sort_order_combo.addItem("降序")
        self.sort_order_combo.setGeometry(202, 632, 60, 30)

        self.label_sort_property_combo = QLabel("排序属性:", self)
        self.label_sort_property_combo.setGeometry(264, 601, 110, 30)
        self.sort_property_combo = QComboBox(self)
        self.sort_property_combo.addItem("读者号")
        self.sort_property_combo.addItem("姓名")
        self.sort_property_combo.addItem("出生日期")
        self.sort_property_combo.addItem("已借本数")
        self.sort_property_combo.addItem("限借本数")
        self.sort_property_combo.setGeometry(264, 632, 110, 30)

        self.match_type_combo = QLabel("正则匹配:", self)
        self.match_type_combo.setGeometry(376, 601, 100, 30)
        self.match_type_combo = QComboBox(self)
        self.match_type_combo.addItem("相关匹配")
        self.match_type_combo.addItem("前字匹配")
        self.match_type_combo.addItem("后字匹配")
        self.match_type_combo.addItem("绝对匹配")
        self.match_type_combo.setGeometry(376, 632, 100, 30)

        self.regex_property_combo = QLabel("匹配属性:", self)
        self.regex_property_combo.setGeometry(478, 601, 110, 30)
        self.regex_property_combo = QComboBox(self)
        self.regex_property_combo.addItem("姓名")
        self.regex_property_combo.addItem("读者号")
        self.regex_property_combo.addItem("性别")
        self.regex_property_combo.addItem("身份证号")
        self.regex_property_combo.addItem("电话")
        self.regex_property_combo.addItem("已借本数")
        self.regex_property_combo.addItem("限借本数")
        self.regex_property_combo.setGeometry(478, 632, 110, 30)

        self.query_button = QLabel("点击查询:", self)
        self.query_button.setGeometry(592, 601, 70, 30)
        self.query_button = QPushButton("查询", self)
        self.query_button.setStyleSheet("color: white;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.query_button.setCursor(Qt.PointingHandCursor)
        self.query_button.setGeometry(592, 632, 70, 30)
        self.query_button.clicked.connect(self.handle_query)

        self.add_button = QLabel("点击增加:", self)
        self.add_button.setGeometry(666, 601, 70, 30)
        self.add_button = QPushButton("增加", self)
        self.add_button.setStyleSheet("color: green;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setGeometry(666, 632, 70, 30)
        self.add_button.clicked.connect(self.handle_add)

        self.change_button = QLabel("点击修改:", self)
        self.change_button.setGeometry(740, 601, 70, 30)
        self.change_button = QPushButton("修改", self)
        self.change_button.setStyleSheet("color: yellow;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.change_button.setCursor(Qt.PointingHandCursor)
        self.change_button.setGeometry(740, 632, 70, 30)
        self.change_button.clicked.connect(self.handle_change)

        self.delete_button = QLabel("点击删除:", self)
        self.delete_button.setGeometry(814, 601, 70, 30)
        self.delete_button = QPushButton("删除", self)
        self.delete_button.setStyleSheet("color: red;\
                                         background-color: lightblue;\
                                         font-weight: bold")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setGeometry(814, 632, 70, 30)
        self.delete_button.clicked.connect(self.handle_delete)

        self.handle_query()

    def handle_query(self):
        key_text = self.input_textbox.text()
        sort_text = self.sort_order_combo.currentText()
        sort_property = self.sort_property_combo.currentText()
        match_text = self.match_type_combo.currentText()
        regex_property = self.regex_property_combo.currentText()
        query_text = ("SELECT * FROM reader WHERE {0} {1} ORDER BY {2} {3}"
                      .format(reader_att_r[regex_property],
                              match_att[match_text],
                              reader_att_r[sort_property],
                              sort_att[sort_text]))
        query_text = query_text.format(key_text)
        print(query_text)
        result = (db_connection.execute_query(query_text))
        # 设置表格的行数和列数
        self.result_textbox.clearContents()
        if result:
            self.result_textbox.setRowCount(len(result))
            self.result_textbox.setColumnCount(len(result[0]))

            # 设置列属性名
            column_names = [desc[0] for desc in db_connection.cursor
                            .description]
            column_names = [reader_att[desc] for desc in column_names]
            self.result_textbox.setHorizontalHeaderLabels(column_names)

            # 填充表格数据
            self.result_textbox.horizontalHeader().setVisible(True)
            for i, row in enumerate(result):
                for j, item in enumerate(row):
                    table_item = QTableWidgetItem(str(item))
                    self.result_textbox.setItem(i, j, table_item)

            self.result_textbox.setEditTriggers(QAbstractItemView
                                                .NoEditTriggers)
            self.result_textbox.resizeColumnsToContents()
            self.result_textbox.resizeRowsToContents()
        else:
            # 清空表格数据并显示查询结果为空的提示消息
            self.result_textbox.clearContents()
            self.result_textbox.setRowCount(1)
            self.result_textbox.setColumnCount(1)
            self.result_textbox.horizontalHeader().setVisible(False)
            self.result_textbox.setColumnWidth(0, 100)  # 设置第一列的宽度为300
            self.result_textbox.setItem(0, 0, QTableWidgetItem("查询结果为空"))
        self.main_win.renew_bs()

    def handle_delete(self):
        print("在图书管理窗口点击了{}按钮".format(self.sender().text()))
        reply = QMessageBox.question(self, '提示',
                                     '确定要删除吗?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(self.result_textbox.selectedRanges()) != 0:
                delete_text = ("DELETE FROM reader WHERE RNO=\'{}\'"
                               .format(self.choice_id))
                print(delete_text)
                db_connection.execute_query(delete_text)
                db_connection.execute_query("COMMIT")

                self.main_win.renew_bs()
                self.handle_query()
            else:
                QMessageBox.critical(None, "删除失败", "未选择元组")

    def handle_add(self):
        dialog = AddReaderDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            print(data)
            insert_text = ("INSERT INTO reader (RNO,RNAME,RSEX,RBIRTH,RID,\
                           RTEL,BD,LIM) VALUES{}".format(data))
            print(insert_text)
            db_connection.execute_query(insert_text)
            db_connection.execute_query("COMMIT")

            self.main_win.renew_bs()
            self.handle_query()

    def handle_change(self):
        reply = QMessageBox.question(self, '提示',
                                     '确定要修改吗?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if len(self.result_textbox.selectedRanges()) != 0:
                dialog = EditReaderDialog()
                dialog.setValues(db_connection.execute_query("SELECT * FROM\
                    reader WHERE RNO=\'{}\'".format(self.choice_id))[0])
                if dialog.exec_() == QDialog.Accepted:
                    change_text = ("UPDATE reader SET RNO=\'{0}\',RNAME=\
                        \'{1}\',RSEX=\'{2}\',RBIRTH=\'{3}\',RID=\'{4}\',RTEL=\'{5}\',BD=\'{6}\',\
                            LIM=\'{7}\' WHERE RNO=\'{8}\'\
                                ".format(dialog.get_data()[0],
                                         dialog.get_data()[1],
                                         dialog.get_data()[2],
                                         dialog.get_data()[3],
                                         dialog.get_data()[4],
                                         dialog.get_data()[5],
                                         dialog.get_data()[6],
                                         dialog.get_data()[7],
                                         self.choice_id))
                    print(change_text)
                    db_connection.execute_query(change_text)
                    db_connection.execute_query("COMMIT")

                    self.main_win.renew_bs()
                    self.handle_query()
            else:
                QMessageBox.critical(None, "修改失败", "未选择元组")

    def handle_cell_clicked(self, row, column):
        self.selected_range = self.result_textbox.selectedRanges()[0]
        selected_row = self.selected_range.topRow()
        self.choice_id = self.result_textbox.item(selected_row, 0).text()
        print("该元组唯一标识符:{}".format(self.choice_id))


class HelpDialog(QDialog):
    def __init__(self, content):
        super().__init__()

        self.setWindowTitle("帮助")
        screen = app.desktop().screenGeometry()
        x = 600
        y = 371
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)

        # 创建滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # 创建内容标签
        content_label = QLabel(content, self)
        content_label.setWordWrap(True)

        # 将内容标签放入滚动区域
        scroll_area.setWidget(content_label)

        # 创建垂直布局，并将滚动区域添加到布局中
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 登录界面
        self.login_window = LoginWindow()

        # 登录成功
        self.login_window.accepted.connect(self.on_login_accepted)
        self.login_window.exec_()

    def on_login_accepted(self):
        # 清空账号和密码
        self.login_window.text_username.setText('')
        self.login_window.text_password.setText('')
        # 系统主窗口名称
        self.setWindowTitle("图书借阅管理系统")

        # 设定窗口大小,且固定大小
        screen = app.desktop().screenGeometry()
        x = 1186
        y = 733
        self.setFixedSize(x, y)
        self.setGeometry((screen.width() - x) // 2,
                         (screen.height() - y) // 2,
                         x, y)

        # 获取管理员账号名
        admin_name = db_connection.user
        res = db_connection.execute_query("SELECT WNAME FROM manager WHERE\
            UNM=\"{}\"".format(admin_name))
        self.usrname = res[0][0]
        label_lg = QLabel(u"当前登录,管理员:{0}".format(self.usrname), self)
        label_lg.setGeometry(self.width() - 290, 2, 190, 20)
        label_lg.setStyleSheet("color: red; background-color: transparent;")

        # 顶部工具栏
        self.create_toolbar()
        self.container = QWidget(self)
        self.container.setGeometry(0, 27, 1186, 693)

        # 底部信息以及主界面分界线
        self.create_footer()

        # 创建“帮助”和“关于”按钮
        self.create_help_button()

        # 插入图片
        self.insert_pt()

        # 创建“切换账号”按钮
        switch_account_button = QToolButton(self)
        switch_account_button.setCursor(Qt.PointingHandCursor)
        switch_account_button.setText("切换账号")
        switch_account_button.setStyleSheet("background-color: grey;")
        switch_account_button.setGeometry(self.width() - 82, 1, 80, 24)
        switch_account_button.clicked.connect(self.handle_switch_account)

        # 创建一个QTextEdit用于显示时间
        self.time_textedit = QTextEdit(self)
        self.time_textedit.setStyleSheet("color: blue;\
                                         background-color: transparent;")
        self.time_textedit.setReadOnly(True)
        self.time_textedit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.time_textedit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.time_textedit.setContextMenuPolicy(Qt.CustomContextMenu)
        # 设置时间标签的位置和大小
        self.time_textedit.setGeometry(889, 320, 300, 76)

        # 创建一个QTextEdit用于显示借书统计
        self.book_textedit = QTextEdit(self)
        self.book_textedit.setStyleSheet("color: green;\
                                         background-color: transparent;")
        self.book_textedit.setReadOnly(True)
        self.book_textedit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.book_textedit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置借书统计标签的位置和大小
        self.book_textedit.setGeometry(889, 398, 300, 103)
        self.book_textedit.setContextMenuPolicy(Qt.CustomContextMenu)
        (self.book_textedit.customContextMenuRequested
         .connect(self.show_context_menu_rf))
        self.renew_bs()

        # 显示主窗口
        self.show()

    def show_context_menu_rf(self, pos):
        if self.is_in_custom_area(pos):
            menu = QMenu(self)

            refresh_action = QAction("刷新", self)
            refresh_action.triggered.connect(self.renew_bs)

            menu.addAction(refresh_action)

            menu.exec_(QCursor.pos())

    def is_in_custom_area(self, pos):
        custom_area = QRect(889, 398, 300, 103)
        return custom_area.contains(pos)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            pos = event.pos()
            if self.is_in_custom_area(pos):
                self.show_context_menu_rf(pos)
        else:
            super().mousePressEvent(event)

    @pyqtSlot()
    def renew_bs(self):
        # 修改图书情况标签的文本内容、字体和大小
        res_bk = db_connection.execute_query("SELECT COUNT(*) FROM books")
        res_bbk = db_connection.execute_query("SELECT COUNT(*) FROM books\
                                              WHERE STATE != \"在馆\"")
        res_rd = db_connection.execute_query("SELECT COUNT(*) FROM reader")
        res_brd = db_connection.execute_query("SELECT COUNT(*)\
            FROM reader WHERE BD > 0")
        (self.book_textedit.setText("馆藏图书数量: {0}\n已借阅图书数量: {1}\n注册读者数量: {2}\
            \n已借书读者数量: {3}".format(res_bk[0][0], res_bbk[0][0],
                                   res_rd[0][0], res_brd[0][0])))
        self.book_textedit.setFont(QFont("Microsoft YaHei", 10))
        self.book_textedit.show()

    def paintEvent(self, event):
        # 获取当前时间
        current_datetime = QDateTime.currentDateTime()
        # 格式化时间
        current_time = (current_datetime
                        .toString("当前时间:yyyy年M月d日\n北京时间:h:mm:ss"))
        # 修改时间标签的文本内容、字体和大小
        self.time_textedit.setText(current_time)
        self.time_textedit.setFont(QFont("Microsoft YaHei", 15))
        self.time_textedit.show()

    def insert_pt(self):
        # 创建一个 QLabel 控件用于显示图片
        self.image_label_main = QLabel(self)
        self.image_label_ms = QLabel(self)

        # 加载图片并设置到 QLabel 上
        pixmap_main = QPixmap('resource/images/main_win.jpg')
        self.image_label_main.setPixmap(pixmap_main)
        # 调整 QLabel 的位置和大小
        self.image_label_main.setGeometry(2, 27, pixmap_main.width(),
                                          pixmap_main.height())

        pixmap_ms = QPixmap('resource/images/msyql.png')
        pixmap_ms_scaled = pixmap_ms.scaled(294, 168, aspectRatioMode=Qt
                                            .KeepAspectRatio)
        self.image_label_ms.setPixmap(pixmap_ms_scaled)
        # 调整 QLabel 的位置和大小
        self.image_label_ms.setGeometry(891, 503, pixmap_ms_scaled.width(),
                                        pixmap_ms_scaled.height())
        palette = self.image_label_ms.palette()
        palette.setColor(QPalette.Window, QColor(40, 40, 40))  # 设置浅黑色背景
        # 将QPalette对象应用于标签
        self.image_label_ms.setAutoFillBackground(True)
        self.image_label_ms.setPalette(palette)

        self.init_picture()

    def init_picture(self):
        # 创建一个QLabel用于显示GIF图像
        self.image_label_ys = QLabel(self)

        # 加载GIF图像并创建QMovie对象
        with open('resource/picture_path.txt', "r") as f:
            path = f.read()
        movie_ys = QMovie(path)
        movie_ys.setScaledSize(QSize(294, 294))

        # 将QMovie对象与QLabel关联
        self.image_label_ys.setMovie(movie_ys)
        self.image_label_ys.setGeometry(890, 26, 294, 294)

        # 设置QMovie循环播放
        movie_ys.setCacheMode(QMovie.CacheAll)
        movie_ys.setSpeed(100)
        movie_ys.setPaused(False)

        self.image_label_ys.setContextMenuPolicy(Qt.CustomContextMenu)
        (self.image_label_ys.customContextMenuRequested
         .connect(self.show_context_menu_cp))

    def show_context_menu_cp(self, pos):
        menu = QMenu(self)
        action_change_image = menu.addAction("切换图片")
        action_change_image.triggered.connect(self.change_image)
        menu.exec_(self.image_label_ys.mapToGlobal(pos))

    def change_image(self):
        file_dialog = QFileDialog()
        file_dialog.setDirectory("resource/images")
        file_path, _ = (file_dialog
                        .getOpenFileName(self, "选择图片", "",
                                         "Images (*.png *.xpm *.jpg *.gif)"))
        if file_path:
            relative_path = os.path.relpath(file_path)
            with open('resource/picture_path.txt', 'w') as f:
                f.write(relative_path)
            movie = QMovie(relative_path)
            movie.setScaledSize(QSize(294, 294))
            self.image_label_ys.setMovie(movie)
            movie.start()

    def handle_switch_account(self):
        reply = QMessageBox.question(self, '提示', '确定要切换账号吗？',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            global switch_win, main_window
            switch_win = 1
            self.close()
            switch_win = None
            main_window = MainWindow()

    def create_footer(self):
        line_h = QFrame(self)
        line_h.setGeometry(0, 691, 1186, 1)  # 设置分割线的位置和大小
        line_h.setFrameShape(QFrame.HLine)  # 设置分割线的形状为水平线
        line_h.setStyleSheet("border-color: black;")  # 设置分割线的颜色为灰色

        line_v = QFrame(self)
        line_v.setGeometry(888, 25, 1, 666)  # 设置分割线的位置和大小
        line_v.setFrameShape(QFrame.VLine)  # 设置分割线的形状为竖直线
        line_v.setStyleSheet("border-color: black;")  # 设置分割线的颜色为灰色

        label_version = QLabel("图书借阅管理系统测试版V1.0", self)
        label_version.setAlignment(Qt.AlignCenter)
        label_version.setGeometry((1186 - 260) // 2, 692, 240, 20)

        label_copyright = QLabel("Copyright @2024 CML", self)
        label_copyright.setAlignment(Qt.AlignCenter)
        label_copyright.setGeometry((1186 - 260) // 2, 712, 240, 20)

    def create_toolbar(self):
        # 创建工具栏
        self.toolbar = self.addToolBar("显示工具栏")
        self.toolbar.setStyleSheet("color: #8B4513;")

        # 分隔符
        self.toolbar.addSeparator()

        # 创建“图书管理”按钮
        self.button_book = QToolButton(self)
        self.button_book.setCursor(Qt.PointingHandCursor)
        self.button_book.setText("图书管理")
        self.button_book.clicked.connect(self.show_book_management_window)
        self.toolbar.addWidget(self.button_book)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        # 创建“书架管理”按钮
        self.button_shelf = QToolButton(self)
        self.button_shelf.setCursor(Qt.PointingHandCursor)
        self.button_shelf.setText("书架管理")
        self.button_shelf.clicked.connect(self.show_shelf_management_window)
        self.toolbar.addWidget(self.button_shelf)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        # 创建“读者管理”按钮
        self.button_reader = QToolButton(self)
        self.button_reader.setCursor(Qt.PointingHandCursor)
        self.button_reader.setText("读者管理")
        self.button_reader.clicked.connect(self.show_reader_management_window)
        self.toolbar.addWidget(self.button_reader)

        self.toolbar.addSeparator()

    def set_button_text_bold(self, button):
        button.setStyleSheet("QToolButton { font-weight: bold; }")

    def set_button_normal(self, button):
        button.setStyleSheet("QToolButton { font-weight: normal; }")

    def show_book_management_window(self):
        if hasattr(self, "book_window"):
            if self.button_book.font().weight() != QFont.Bold:
                self.image_label_main.hide()
                if hasattr(self, "shelf_window"):
                    self.shelf_window.hide()
                if hasattr(self, "reader_window"):
                    self.reader_window.hide()
                self.set_button_normal(self.button_shelf)
                self.set_button_normal(self.button_reader)
                self.set_button_text_bold(self.button_book)
                self.book_window.handle_query()
                self.book_window.show()
            else:
                self.set_button_normal(self.button_book)
                self.book_window.hide()
                self.image_label_main.show()
        else:
            self.image_label_main.hide()
            if hasattr(self, "shelf_window"):
                self.shelf_window.hide()
            if hasattr(self, "reader_window"):
                self.reader_window.hide()
            self.set_button_normal(self.button_shelf)
            self.set_button_normal(self.button_reader)
            self.set_button_text_bold(self.button_book)
            self.book_window = BookManagementWindow(self)
            self.book_window.setParent(self.container)  # 将子窗口设置为容器部件的子部件
            self.book_window.show()

    def show_shelf_management_window(self):
        if hasattr(self, "shelf_window"):
            if self.button_shelf.font().weight() != QFont.Bold:
                self.image_label_main.hide()
                if hasattr(self, "book_window"):
                    self.book_window.hide()
                if hasattr(self, "reader_window"):
                    self.reader_window.hide()
                self.set_button_normal(self.button_book)
                self.set_button_normal(self.button_reader)
                self.set_button_text_bold(self.button_shelf)
                self.shelf_window.handle_query()
                self.shelf_window.show()
            else:
                self.set_button_normal(self.button_shelf)
                self.shelf_window.hide()
                self.image_label_main.show()
        else:
            self.image_label_main.hide()
            if hasattr(self, "book_window"):
                self.book_window.hide()
            if hasattr(self, "reader_window"):
                self.reader_window.hide()
            self.set_button_normal(self.button_book)
            self.set_button_normal(self.button_reader)
            self.set_button_text_bold(self.button_shelf)
            self.shelf_window = ShelfManagementWindow(self)
            self.shelf_window.setParent(self.container)  # 将子窗口设置为容器部件的子部件
            self.shelf_window.show()

    def show_reader_management_window(self):
        if hasattr(self, "reader_window"):
            if self.button_reader.font().weight() != QFont.Bold:
                self.image_label_main.hide()
                if hasattr(self, "book_window"):
                    self.book_window.hide()
                if hasattr(self, "shelf_window"):
                    self.shelf_window.hide()
                self.set_button_normal(self.button_book)
                self.set_button_normal(self.button_shelf)
                self.set_button_text_bold(self.button_reader)
                self.reader_window.handle_query()
                self.reader_window.show()
            else:
                self.set_button_normal(self.button_reader)
                self.reader_window.hide()
                self.image_label_main.show()
        else:
            self.image_label_main.hide()
            if hasattr(self, "book_window"):
                self.book_window.hide()
            if hasattr(self, "shelf_window"):
                self.shelf_window.hide()
            self.set_button_normal(self.button_book)
            self.set_button_normal(self.button_shelf)
            self.set_button_text_bold(self.button_reader)
            self.reader_window = ReaderManagementWindow(self)
            self.reader_window.setParent(self.container)  # 将子窗口设置为容器部件的子部件
            self.reader_window.show()

    def create_help_button(self):
        # 创建帮助信息按钮
        self.help_label = QLabel(self)
        help_text = "帮助"
        self.help_label.setText(help_text)
        self.help_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.help_label.setStyleSheet("color: blue; text-decoration:\
            underline;")
        self.help_label.setCursor(Qt.PointingHandCursor)
        self.help_label.mousePressEvent = self.show_help
        self.help_label.setGeometry(1152, 659, 32, 30)

        # 创建关于按钮
        self.about_label = QLabel(self)
        about_text = "关于"
        self.about_label.setText(about_text)
        self.about_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.about_label.setStyleSheet("color: blue; text-decoration:\
            underline;")
        self.about_label.setCursor(Qt.PointingHandCursor)
        self.about_label.mousePressEvent = self.open_website
        self.about_label.setGeometry(890, 659, 32, 30)

    def open_website(self, event):
        reply = QMessageBox.question(self, '提示',
                                     '源码给出仅供参考学习,是否前往?', QMessageBox
                                     .Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            url = QUrl("https://github.com/hlxcg/sql_design")
            QDesktopServices.openUrl(url)
            event.accept()
        else:
            event.ignore()

    def show_help(self, event):
        with open("resource/help.txt", encoding="utf-8") as f:
            help_text = f.read()

        dialog = HelpDialog(help_text)
        dialog.exec_()

    def closeEvent(self, event):
        if switch_win == 1:
            if db_connection:
                db_connection.close()
            event.accept()
        else:
            reply = QMessageBox.question(self, '提示',
                                         '确定要退出吗?', QMessageBox
                                         .Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if hasattr(self, "book_window"):
                    (self.book_window.result_textbox
                     .cellClicked.disconnect(self.book_window
                                             .handle_cell_clicked))
                    print("与图书管理窗口链接断开")
                if hasattr(self, "shelf_window"):
                    (self.shelf_window.result_textbox
                     .cellClicked.disconnect(self.shelf_window
                                             .handle_cell_clicked))
                    print("与书架管理窗口链接断开")
                if hasattr(self, "reader_window"):
                    (self.reader_window.result_textbox
                     .cellClicked.disconnect(self.reader_window
                                             .handle_cell_clicked))
                    print("与读者管理窗口链接断开")
                if db_connection:
                    db_connection.close()
                event.accept()
            else:
                event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()

    sys.exit(app.exec_())
