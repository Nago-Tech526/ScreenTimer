import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt, QTime, QPoint
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient

class GradientLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._alignment = Qt.AlignCenter
        self._font = QFont("Arial", 50, QFont.Bold)
        # 初期状態：上半分白、下半分白
        self.baseColor = Qt.white
        self.transitionColor = Qt.white  # 初期は下半分も白
    
    def setText(self, text):
        self._text = text
        self.update()
    
    def text(self):
        return self._text

    def setAlignment(self, alignment):
        self._alignment = alignment
        self.update()
    
    def alignment(self):
        return self._alignment

    def setFont(self, font):
        self._font = font
        self.update()
    
    def font(self):
        return self._font

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self._font)
        rect = self.rect()
        # 上半分と下半分を分けるグラデーション（中央で急激に切り替え）
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0.0, self.baseColor)
        gradient.setColorAt(0.49, self.baseColor)
        gradient.setColorAt(0.5, self.transitionColor)
        gradient.setColorAt(1.0, self.transitionColor)
        painter.setPen(QPen(QBrush(gradient), 0))
        painter.drawText(rect, self._alignment, self._text)

class TransparentClock(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # ドラッグ用の変数
        self.dragPos = QPoint()

    def initUI(self):
        # ウィンドウ枠をなくし、常に最前面・背景透過に設定
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # カスタムラベル（グラデーションで描画するラベル）を作成
        self.label = GradientLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 50, QFont.Bold)
        self.label.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 時刻更新タイマー（1秒ごと）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        self.updateTime()

        # ウィンドウサイズ設定し、右上に配置
        self.resize(300, 100)
        self.moveToTopRight()

    def moveToTopRight(self):
        # QDesktopWidgetを用いて画面の右上に移動
        screen = QDesktopWidget().availableGeometry()
        x = screen.width() - self.width()
        y = 0
        self.move(x, y)

    def updateTime(self):
        # 現在の秒数を取得
        currentTime = QTime.currentTime()
        seconds = currentTime.second()

        # 00秒〜29秒: 上半分白、下半分白
        # 30秒〜59秒: 上半分白、下半分オレンジ
        if seconds < 30:
            self.label.baseColor = Qt.white
            self.label.transitionColor = Qt.white  # 下半分も白
        else:
            self.label.baseColor = Qt.white
            self.label.transitionColor = QColor(255, 165, 0) #オレンジ

        # 時計の表示を更新
        self.label.setText(currentTime.toString("hh:mm:ss"))

    # マウスドラッグによるウィンドウ移動のためのイベント
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = TransparentClock()
    clock.show()
    sys.exit(app.exec_())