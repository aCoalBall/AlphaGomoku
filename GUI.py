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
    '''
    Using messagebox to show the error if there is one
    '''
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
        self.init_ui()  # initialize the game interface
        self.g = Game()  # initilize Game content
        self.last_pos = (-1, -1)
        self.res = 0  # record the result
        self.operate_status = 0  # permission to input。0 means allowed，1 means prohibited

    def init_ui(self):
        """初始化游戏界面"""
        # 1. the title
        self.setObjectName('MainWindow')
        self.setWindowTitle('五子棋')
        self.setFixedSize(650, 650)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap('imgs/cosmos.jpg')))
        self.setPalette(palette)
        # 2. turn on mouse track
        self.setMouseTracking(True)
        # 3. locate the mouse using a red widget
        self.corner_widget = CornerWidget(self)
        self.corner_widget.repaint()
        self.corner_widget.hide()
        # 4. blink when the game ends
        self.end_timer = QTimer(self)
        self.end_timer.timeout.connect(self.end_flash)
        self.flash_cnt = 0  # record blink times
        self.flash_pieces = ((-1, -1), )  # the pieces need to blink
        # 5. show the initial interface
        self.show()

    @run_with_exc
    def paintEvent(self, e):
        '''draw game contents'''
        def draw_map():
            '''draw the chessboard'''
            qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))  # black lines
            # draw horizontal lines
            for x in range(BOARD_SIZE):
                qp.drawLine(interval * (x + 1), interval, interval * (x + 1), 600)
            # draw vertical lines
            for y in range(BOARD_SIZE):
                qp.drawLine(interval, interval * (y + 1), 600, interval * (y + 1))
            
        def draw_pieces():
            '''draw pieces'''
            # draw black pieces
            qp.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
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
            # draw white pieces
            qp.setPen(QPen(QColor(160, 160, 160), 1, Qt.SolidLine))
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

        if hasattr(self, 'g'):  # if initiated
            qp = QPainter()
            qp.begin(self)
            draw_map()  # draw chessboard
            draw_pieces()  #draw pieces
            qp.end()


    
    @run_with_exc
    def mouseMoveEvent(self, e):
        mouse_x = e.windowPos().x()
        mouse_y = e.windowPos().y()
        if (interval - 15) <= mouse_x <= 615 and (interval - 15) <= mouse_y <= 615 and (mouse_x % interval <= 15 or mouse_x % interval >= (interval - 15)) and (mouse_y % interval <= 15 or mouse_y % interval >= (interval - 15)):
            game_x = int((mouse_x + 15) // interval) - 1
            game_y = int((mouse_y + 15) // interval) - 1
        else: 
            game_x = -1
            game_y = -1

        pos_change = False 
        if game_x != self.last_pos[0] or game_y != self.last_pos[1]:
            pos_change = True
        self.last_pos = (game_x, game_y)
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
        if not (hasattr(self, 'operate_status') and self.operate_status == 0):
            return
        if e.button() == Qt.LeftButton:
            mouse_x = e.windowPos().x()
            mouse_y = e.windowPos().y()
            if (mouse_x % interval <= 15 or mouse_x % interval >= (interval - 15)) and (mouse_y % interval <= 15 or mouse_y % interval >= (interval - 15)):
                game_x = int((mouse_x + 15) // interval) - 1
                game_y = int((mouse_y + 15) // interval) - 1
            else:  
                return
            self.g.player_move(True, game_x, game_y)

            res = self.g.check_game_result(show=True)[0]  
            self.flash_pieces = self.g.check_game_result(show=True)[1]
            if res != 0:  
                self.repaint(0, 0, 650, 650)
                self.game_restart(res)
                return
            self.g.ai_move()  
            res, self.flash_pieces = self.g.check_game_result(show=True)
            if res != 0:
                self.repaint(0, 0, 650, 650)
                self.game_restart(res)
                return
            self.repaint(0, 0, 650, 650)  

        
    @run_with_exc
    def end_flash(self):
        if self.flash_cnt <= 5:
            self.flash_cnt += 1
            self.repaint()
        else:
            self.end_timer.stop()
            if self.res == BLACK:
                QMessageBox.about(self, '游戏结束', '算你厉害!')
            elif self.res == WHITE:
                QMessageBox.about(self, '游戏结束', '丢人!')
            elif self.res == DRAW:
                QMessageBox.about(self, '游戏结束', '平局!')
            else:
                raise ValueError('当前游戏结束的标志位为' + self.res + '. 而游戏结束的标志位必须为1, 2 或 3')
            self.res = 0
            self.operate_status = 0
            self.flash_cnt = 0
            self.g = Game() 
            self.repaint(0, 0, 650, 650) 

    def game_restart(self, res):
        """游戏出现开始"""
        self.res = res 
        self.operate_status = 1 
        self.end_timer.start(300)  