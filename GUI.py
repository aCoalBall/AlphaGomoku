import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gomoku import *
import traceback
from corner_widget import CornerWidget

from global_var import BOARD_SIZE, ONGOING, BLACK, WHITE, DRAW, UNCHECKED

interval = 600 / BOARD_SIZE

def run_with_exc(f):
    """游戏运行出现错误时，用messagebox把错误信息显示出来"""
    def call(window, *args, **kwargs):
        try:
            return f(window, *args, **kwargs)
        except Exception:
            exc_info = traceback.format_exc()
            QMessageBox.about(window, '错误信息', exc_info)
    return call


class GomokuWindow(QMainWindow) :
    def __init__(self):
        super().__init__()
        self.init_ui()  # 初始化游戏界面
        self.g = Game()  # 初始化游戏内容

        self.last_pos = (-1, -1)
        self.res = 0  # 记录那边获得了胜利
        self.operate_status = 0  # 游戏操作状态。0为游戏中（可操作），1为游戏结束闪烁过程中（不可操作）

    def init_ui(self):
        """初始化游戏界面"""
        # 1. 确定游戏界面的标题，大小和背景颜色
        self.setObjectName('MainWindow')
        self.setWindowTitle('五子棋')
        self.setFixedSize(650, 650)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap('imgs/cosmos.jpg')))
        self.setPalette(palette)
        # 2. 开启鼠标位置的追踪。并在鼠标位置移动时，使用特殊符号标记当前的位置
        self.setMouseTracking(True)
        # 3. 鼠标位置移动时，对鼠标位置的特殊标记
        self.corner_widget = CornerWidget(self)
        self.corner_widget.repaint()
        self.corner_widget.hide()
        # 4. 游戏结束时闪烁的定时器
        self.end_timer = QTimer(self)
        self.end_timer.timeout.connect(self.end_flash)
        self.flash_cnt = 0  # 游戏结束之前闪烁了多少次
        self.flash_pieces = ((-1, -1), )  # 哪些棋子需要闪烁
        # 5. 显示初始化的游戏界面
        self.show()

    @run_with_exc
    def paintEvent(self, e):
        """绘制游戏内容"""
        def draw_map():
            """绘制棋盘"""
            qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))  # 棋盘的颜色为黑色
            # 绘制横线
            for x in range(BOARD_SIZE):
                qp.drawLine(interval * (x + 1), interval, interval * (x + 1), 600)
            # 绘制竖线
            for y in range(BOARD_SIZE):
                qp.drawLine(interval, interval * (y + 1), 600, interval * (y + 1))
            # 绘制棋盘中的黑点
            qp.setBrush(QColor(0, 0, 0))
            '''
            key_points = [(4, 4), (12, 4), (4, 12), (12, 12), (8, 8)]
            for t in key_points:
                qp.drawEllipse(QPoint(40 * t[0], 40 * t[1]), 5, 5)
            '''

        def draw_pieces():
            """绘制棋子"""
            # 绘制黑棋子
            qp.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
            # qp.setBrush(QColor(0, 0, 0))
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    if self.g.chessboard[x][y] == BLACK:
                        if self.flash_cnt % 2 == 1 and (x, y) in self.flash_pieces:
                            continue
                        radial = QRadialGradient(interval * (x + 1), interval * (y + 1), 15, interval * x + 35, interval * y + 35)  # 棋子的渐变效果
                        radial.setColorAt(0, QColor(0, 0, 0))
                        radial.setColorAt(1, QColor(0, 0, 0))
                        qp.setBrush(QBrush(radial))
                        qp.drawEllipse(QPoint(interval * (x + 1), interval * (y + 1)), BOARD_SIZE, BOARD_SIZE)
            # 绘制白棋子
            qp.setPen(QPen(QColor(160, 160, 160), 1, Qt.SolidLine))
            # qp.setBrush(QColor(255, 255, 255))
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    if self.g.chessboard[x][y] == WHITE:
                        if self.flash_cnt % 2 == 1 and (x, y) in self.flash_pieces:
                            continue
                        radial = QRadialGradient(interval * (x + 1), interval * (y + 1), 15, interval * x + 35, interval * y + 35)  # 棋子的渐变效果
                        radial.setColorAt(0, QColor(255, 255, 255))
                        radial.setColorAt(1, QColor(255, 255, 255))
                        qp.setBrush(QBrush(radial))
                        qp.drawEllipse(QPoint(interval * (x + 1), interval * (y + 1)), BOARD_SIZE, BOARD_SIZE)

        if hasattr(self, 'g'):  # 游戏还没开始的话，就不用画了
            qp = QPainter()
            qp.begin(self)
            draw_map()  # 绘制棋盘
            draw_pieces()  # 绘制棋子
            qp.end()


    
    @run_with_exc
    def mouseMoveEvent(self, e):
        # 1. 首先判断鼠标位置对应棋盘中的哪一个格子
        mouse_x = e.windowPos().x()
        mouse_y = e.windowPos().y()
        if (interval - 15) <= mouse_x <= 615 and (interval - 15) <= mouse_y <= 615 and (mouse_x % interval <= 15 or mouse_x % interval >= (interval - 15)) and (mouse_y % interval <= 15 or mouse_y % interval >= (interval - 15)):
            game_x = int((mouse_x + 15) // interval) - 1
            game_y = int((mouse_y + 15) // interval) - 1
        else:  # 鼠标当前的位置不对应任何一个游戏格子，将其标记为(01, 01
            game_x = -1
            game_y = -1

        # 2. 然后判断鼠标位置较前一时刻是否发生了变化
        pos_change = False  # 标记鼠标位置是否发生了变化
        if game_x != self.last_pos[0] or game_y != self.last_pos[1]:
            pos_change = True
        self.last_pos = (game_x, game_y)
        # 3. 最后根据鼠标位置的变化，绘制特殊标记
        if pos_change and game_x != -1:
            self.setCursor(Qt.PointingHandCursor)
        if pos_change and game_x == -1:
            self.setCursor(Qt.ArrowCursor)
        if pos_change and game_x != -1:
            self.corner_widget.move((interval - 15) + game_x * interval, (interval - 15) + game_y * interval)
            self.corner_widget.show()
        if pos_change and game_x == -1:
            self.corner_widget.hide()

    @run_with_exc
    def mousePressEvent(self, e):
        """根据鼠标的动作，确定落子位置"""
        if not (hasattr(self, 'operate_status') and self.operate_status == 0):
            return
        if e.button() == Qt.LeftButton:
            # 1. 首先判断按下了哪个格子
            mouse_x = e.windowPos().x()
            mouse_y = e.windowPos().y()
            if (mouse_x % interval <= 15 or mouse_x % interval >= (interval - 15)) and (mouse_y % interval <= 15 or mouse_y % interval >= (interval - 15)):
                game_x = int((mouse_x + 15) // interval) - 1
                game_y = int((mouse_y + 15) // interval) - 1
            else:  # 鼠标点击的位置不正确
                return
            self.g.player_move(True, game_x, game_y)

            # 2. 根据操作结果进行一轮游戏循环
            res = self.g.check_game_result(show=True)[0]  # 判断游戏结果
            self.flash_pieces = self.g.check_game_result(show=True)[1]
            if res != 0:  # 如果游戏结果为“已经结束”，则显示游戏内容，并退出主循环
                self.repaint(0, 0, 650, 650)
                self.game_restart(res)
                return
            self.g.ai_move()  # 电脑下一步
            res, self.flash_pieces = self.g.check_game_result(show=True)
            if res != 0:
                self.repaint(0, 0, 650, 650)
                self.game_restart(res)
                return
            self.repaint(0, 0, 650, 650)  # 在游戏还没有结束的情况下，显示游戏内容，并继续下一轮循环

        
    @run_with_exc
    def end_flash(self):
        # 游戏结束时的闪烁操作
        if self.flash_cnt <= 5:
            # 执行闪烁
            self.flash_cnt += 1
            self.repaint()
        else:
            # 闪烁完毕，执行重新开始的操作
            self.end_timer.stop()
            # 1. 显示游戏结束的信息
            if self.res == BLACK:
                QMessageBox.about(self, '游戏结束', '算你厉害!')
            elif self.res == WHITE:
                QMessageBox.about(self, '游戏结束', '丢人!')
            elif self.res == DRAW:
                QMessageBox.about(self, '游戏结束', '平局!')
            else:
                raise ValueError('当前游戏结束的标志位为' + self.res + '. 而游戏结束的标志位必须为1, 2 或 3')
            # 2. 游戏重新开始的操作
            self.res = 0
            self.operate_status = 0
            self.flash_cnt = 0
            self.g = Game()  # 重新初始化游戏内容
            self.repaint(0, 0, 650, 650)  # 重新绘制游戏界面

    def game_restart(self, res):
        """游戏出现开始"""
        self.res = res  # 标记谁获胜了
        self.operate_status = 1  # 游戏结束时的闪烁过程中，不可操作
        self.end_timer.start(300)  # 开始结束时闪烁的计时器