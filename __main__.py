import sys
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
        # グラデーションの切り替え位置 (初期値は6で全体が白)
        self.white_level = 6

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
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self._font)
        rect = self.rect()

        # フォントメトリクスを利用してテキストのバウンディングボックスを取得
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(self._text)

        # テキストをウィジェット内で横中央、かつテキストの上端がウィジェット上端に来るように配置
        # boundingRect() はテキストの内部でのオフセット（left, top）を含むので、それを補正します
        x = (rect.width() - text_rect.width()) // 2 - text_rect.left()
        # y 座標はテキストの top が 0 になるように調整
        y = -text_rect.top()

        # QPainterPath にテキストを追加
        path = QPainterPath()
        path.addText(x, y, self._font, self._text)

        # テキストの実際の高さを使ってグラデーションの範囲を設定
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
        # まずアウトラインを描画（ここではアウトラインの色をグレー、幅を2に設定）
        outline_pen = QPen(QColor(211, 211, 211), 2)
        painter.setPen(outline_pen)
        painter.drawPath(path)
        # 次に、グラデーションブラシでテキスト内部を塗りつぶす
        painter.setPen(QPen(QBrush(gradient), 0))
        painter.fillPath(path, QBrush(gradient))

        painter.end()

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
        font = QFont("Arial", 67, QFont.Bold)
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

        # ウィンドウサイズ設定し、左上に配置
        self.resize(210, 100)
        self.moveToTopLeft()

    def moveToTopLeft(self):
        # 画面の右上に移動
        x = 0
        y = 0
        self.move(x, y)

    def updateTime(self):
        # 現在の秒数を取得
        currentTime = QTime.currentTime()
        seconds = currentTime.second()

        # 10秒ごとに6段階で変化
        orange_levels = seconds // 10
        white_level = 6 - orange_levels

        # 色の設定：orange_levelsが0の場合は全体白、そうでなければ下部がゴールド
        self.label.baseColor = Qt.white
        self.label.transitionColor = QColor(255, 215, 0) if orange_levels > 0 else Qt.white

        # white_level をラベルに設定して再描画を依頼
        self.label.white_level = white_level

        # 時計の表示を更新
        self.label.setText(currentTime.toString("hh:mm"))

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