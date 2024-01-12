from PyQt5.QtWidgets import (QDialog, QLabel, QCheckBox, QHBoxLayout,
                             QLineEdit, QPushButton, QToolButton, QTableWidget,
                             QVBoxLayout, QApplication, QWidget, QFrame,
                             QMainWindow, QMessageBox, QTableWidgetItem,
                             QScrollArea, QTextEdit, QAction, QMenu)
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDateTime, QSize, QRect, QUrl
from PyQt5.QtGui import (QPixmap, QColor, QPalette, QFont,
                         QMovie, QMouseEvent, QCursor, QDesktopServices)
import sys
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
    "RNO": "节阅读者号"
}

manager_att = {
    "WNO": "工号",
    "WNAME": "姓名",
    "WSEX": "性别",
    "WBRITH": "出生日期",
    "WID": "身份证号",
    "WTEL": "电话",
    "UNM": "用户名"
}

reader_att = {
    "RNO": "读者号",
    "RNAME": "性名",
    "RSEX": "性别",
    "RBIRTH": "出生日期",
    "RID": "身份证号",
    "RTEL": "电话",
    "BD": "已借本数",
    "LIM": "限借本数"
}

shell_att = {
    "CNO": "书架号",
    "CNAME": "书架名",
    "KIND": "分类",
    "WNO": "管理员工号"
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
            print(f"执行查询出错：{e}")

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
        username = "hlxcg"
        password = "Ccyisaboy229@"
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


class BookManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图书管理")
        self.setGeometry(0, 0, 886, 690)

        self.result_textbox = QTableWidget(self)
        self.result_textbox.setGeometry(2, 0, 884, 600)
        self.result_textbox.setRowCount(0)
        self.result_textbox.setColumnCount(0)

        self.label_input = QLabel("关键字查询:", self)
        self.label_input.setGeometry(2, 601, 198, 30)
        self.input_textbox = QLineEdit("请输入关键字:", self)
        self.input_textbox.setGeometry(2, 632, 198, 30)

        self.query_button = QPushButton("查询", self)
        self.query_button.setCursor(Qt.PointingHandCursor)
        self.query_button.setGeometry(200, 601, 40, 30)
        self.query_button.clicked.connect(self.handle_query)

    def handle_query(self):
        # query_text = self.input_textbox.text()
        # result = (db_connection.execute_query("SELECT * FROM reader WHERE\
        #     RNO LIKE '{}%'".format(query_text)))
        result = (db_connection.execute_query("SELECT * FROM reader"))
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
            for i, row in enumerate(result):
                for j, item in enumerate(row):
                    table_item = QTableWidgetItem(str(item))
                    self.result_textbox.setItem(i, j, table_item)

            self.result_textbox.setEditTriggers(QtWidgets
                                                .QAbstractItemView
                                                .NoEditTriggers)
            self.result_textbox.resizeColumnsToContents()
            self.result_textbox.resizeRowsToContents()


class ShelfManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("书架管理")
        self.setGeometry(0, 30, 520, 480)


class ReaderManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("读者管理")
        self.setGeometry(0, 30, 520, 480)


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
        switch_account_button.setGeometry(self.width() - 80, 0, 80, 25)
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
         .connect(self.show_context_menu))
        self.renew_bs()

        # 显示主窗口
        self.show()

    def show_context_menu(self, pos):
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
                self.show_context_menu(pos)
        else:
            super().mousePressEvent(event)

    def renew_bs(self):
        # 修改图书情况标签的文本内容、字体和大小
        res_bk = db_connection.execute_query("SELECT COUNT(*) FROM books")
        res_bbk = db_connection.execute_query("SELECT COUNT(*) FROM books\
                                              WHERE STATE != \"在馆\"")
        res_rd = db_connection.execute_query("SELECT COUNT(*) FROM reader")
        res_brd = db_connection.execute_query("SELECT DISTINCT COUNT(RNO)\
            FROM books WHERE RNO != NULL")
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
        # self.image_label_main = QLabel(self)
        self.image_label_ms = QLabel(self)

        # 加载图片并设置到 QLabel 上
        # pixmap_main = QPixmap('resource/images/main_win.jpg')
        # self.image_label_main.setPixmap(pixmap_main)
        # # 调整 QLabel 的位置和大小
        # self.image_label_main.setGeometry(2, 27, pixmap_main.width(),
        #                                   pixmap_main.height())

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

        self.init_ui()

    def init_ui(self):
        # 创建一个QLabel用于显示GIF图像
        self.image_label_ys = QLabel(self)

        # 加载GIF图像并创建QMovie对象
        movie_ys = QMovie('resource/images/8.gif')
        movie_ys.setScaledSize(QSize(294, 294))

        # 将QMovie对象与QLabel关联
        self.image_label_ys.setMovie(movie_ys)
        self.image_label_ys.setGeometry(890, 26, 294, 294)

        # 设置QMovie循环播放
        movie_ys.setCacheMode(QMovie.CacheAll)
        movie_ys.setSpeed(100)
        movie_ys.setPaused(False)

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

        # 分隔符
        self.toolbar.addSeparator()

        # 创建“图书管理”按钮
        button_book = QToolButton(self)
        button_book.setCursor(Qt.PointingHandCursor)
        button_book.setText("图书管理")
        button_book.clicked.connect(self.show_book_management_window)
        self.toolbar.addWidget(button_book)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        # 创建“书架管理”按钮
        button_shelf = QToolButton(self)
        button_shelf.setCursor(Qt.PointingHandCursor)
        button_shelf.setText("书架管理")
        button_shelf.clicked.connect(self.show_shelf_management_window)
        self.toolbar.addWidget(button_shelf)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        # 创建“读者管理”按钮
        button_reader = QToolButton(self)
        button_reader.setCursor(Qt.PointingHandCursor)
        button_reader.setText("读者管理")
        button_reader.clicked.connect(self.show_reader_management_window)
        self.toolbar.addWidget(button_reader)

        self.toolbar.addSeparator()

        # 设置按钮文本加粗
        self.set_button_text_bold(button_book)
        self.set_button_text_bold(button_shelf)
        self.set_button_text_bold(button_reader)

    def set_button_text_bold(self, button):
        button.setStyleSheet("QToolButton { font-weight: bold; }")

    def show_book_management_window(self):
        book_window = BookManagementWindow()
        book_window.setParent(self.container)  # 将子窗口设置为容器部件的子部件
        book_window.show()

    def show_shelf_management_window(self):
        shelf_window = ShelfManagementWindow()
        shelf_window.setParent(self.container)  # 将子窗口设置为容器部件的子部件
        shelf_window.show()

    def show_reader_management_window(self):
        reader_window = ReaderManagementWindow()
        reader_window.setParent(self.container)  # 将子窗口设置为容器部件的子部件
        reader_window.show()

    def create_help_button(self):
        # 创建帮助信息按钮
        self.help_label = QLabel(self)
        help_text = "帮助"
        self.help_label.setText(help_text)
        self.help_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.help_label.setStyleSheet("color: blue; text-decoration:\
            underline; padding-right: 10px; padding-bottom: 10px;")
        self.help_label.setCursor(Qt.PointingHandCursor)
        self.help_label.mousePressEvent = self.show_help
        self.help_label.setGeometry(1136, 663, 60, 40)

        # 创建关于按钮
        self.about_label = QLabel(self)
        about_text = "关于"
        self.about_label.setText(about_text)
        self.about_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.about_label.setStyleSheet("color: blue; text-decoration:\
            underline; padding-right: 10px; padding-bottom: 10px;")
        self.about_label.setCursor(Qt.PointingHandCursor)
        self.about_label.mousePressEvent = self.open_website
        self.about_label.setGeometry(888, 663, 60, 40)

    def open_website(self, event):
        url = QUrl("https://github.com/dashboard")  # 替换为你要跳转的网址
        QDesktopServices.openUrl(url)

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
                if db_connection:
                    db_connection.close()
                event.accept()
            else:
                event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()

    sys.exit(app.exec_())