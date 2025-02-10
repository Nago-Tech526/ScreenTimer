import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt, QTime, QPoint
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath

class GradientLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._alignment = Qt.AlignCenter
        self._font = QFont("Arial", 67, QFont.Bold)
        # 初期状態：すべて白
        self.baseColor = Qt.white
        self.transitionColor = Qt.white
        # グラデーションの切り替え位置（初期値は6で全体が白）
        self.white_level = 6

    def setText(self, text):
        self._text = text
        self.update()  # テキスト変更時に再描画を依頼

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
        # このメソッドは update() もしくは repaint() が呼ばれると実行されます
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self._font)
        rect = self.rect()

        # フォントメトリクスでテキストのバウンディングボックスを取得
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(self._text)

        # ウィジェット内で横中央に配置、かつテキストの上端がウィジェット上端に来るように調整
        x = (rect.width() - text_rect.width()) // 2 - text_rect.left()
        y = -text_rect.top()  # テキストの上端をウィジェット上端に合わせる

        # QPainterPath にテキストを追加
        path = QPainterPath()
        path.addText(x, y, self._font, self._text)

        # テキストの高さに合わせたグラデーションの範囲を設定
        gradient = QLinearGradient(0, 0, 0, text_rect.height())
        if self.white_level >= 6:
            gradient.setColorAt(0.0, self.baseColor)
            gradient.setColorAt(1.0, self.baseColor)
        elif self.white_level == 5:
            gradient.setColorAt(0.0, self.baseColor)
            gradient.setColorAt(0.77, self.baseColor)
            gradient.setColorAt(0.78, self.transitionColor)
            gradient.setColorAt(1.0, self.transitionColor)
        elif self.white_level == 1:
            gradient.setColorAt(0.0, self.baseColor)
            gradient.setColorAt(0.22, self.baseColor)
            gradient.setColorAt(0.23, self.transitionColor)
            gradient.setColorAt(1.0, self.transitionColor)
        else:
            ratio = self.white_level / 6.0
            gradient.setColorAt(0.0, self.baseColor)
            gradient.setColorAt(max(0.0, ratio - 0.01), self.baseColor)
            gradient.setColorAt(ratio, self.transitionColor)
            gradient.setColorAt(1.0, self.transitionColor)

        # まずアウトラインを描画（アウトライン色はグレー、幅は2）
        outline_pen = QPen(QColor(211, 211, 211), 2)
        painter.setPen(outline_pen)
        painter.drawPath(path)

        # 次にグラデーションでテキスト内部を塗りつぶす
        painter.setPen(QPen(QBrush(gradient), 0))
        painter.fillPath(path, QBrush(gradient))

        painter.end()

class TransparentClock(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # マウスドラッグ用の変数
        self.dragPos = QPoint()

    def initUI(self):
        # ウィンドウ枠なし、常に最前面、背景透過に設定
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # アプリ起動時の分を記憶（再起動判定に使用）
        self.start_minute = QTime.currentTime().minute()

        # カスタムラベル（グラデーション描画）
        self.label = GradientLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 67, QFont.Bold)
        self.label.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # タイマー：1秒ごとに updateTime() を呼び出し
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        # 起動時は必ず一度更新（初回描画）
        self.updateTime(force=True)

        # ウィンドウサイズ設定と左上に配置
        self.resize(210, 100)
        self.moveToTopLeft()

    def moveToTopLeft(self):
        self.move(0, 0)

    def updateTime(self, force=False):
        currentTime = QTime.currentTime()
        seconds = currentTime.second()
        minute = currentTime.minute()

        # 60秒経過（分が変わったタイミング）の場合、再起動する
        # ※初回（force=True）のときは判定しない
        if not force and seconds == 0 and minute != self.start_minute:
            # os.execl により、現在のプロセスを置き換えて再起動する
            os.execl(sys.executable, sys.executable, *sys.argv)

        # 初回以降、秒が 10 の倍数（例: 10,20,30,40,50,0）でのみ更新
        if not force and seconds % 10 != 0:
            return

        # 10秒ごとのタイミングで、6段階に変化させる例（例：下部の色が変化）
        orange_levels = seconds // 10
        white_level = 6 - orange_levels

        # 色の設定：orange_levels が 0 のときは全体白、そうでなければ下部がゴールド
        self.label.baseColor = Qt.white
        self.label.transitionColor = QColor(255, 200, 0) if orange_levels > 0 else Qt.white

        # white_level をラベルに反映
        self.label.white_level = white_level

        # 時計の表示を更新（例: hh:mm 形式）
        self.label.setText(currentTime.toString("hh:mm"))

    # マウスドラッグによるウィンドウ移動のためのイベント処理
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