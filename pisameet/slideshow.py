import glob
import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer


class SlideShow(QWidget):

    """Basic slideshow class.
    """

    def __init__(self, folder_path, persistence=1.):
        """
        """
        super().__init__()
        self.label = QLabel()
        self._grid = QGridLayout()
        self._grid.setColumnStretch(0, 1)
        self._grid.setColumnStretch(2, 1)
        self._grid.addWidget(self.label, 1, 1)
        self.setLayout(self._grid)
        self.setWindowTitle('15th Pisa Meeting on Advanced Detectors')
        self.pixmap_list, self.pixmap_keys = self._load_images(folder_path)
        self.__current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance)
        self.showMaximized()
        self.show_image()
        self.timer.start(int(1000 * persistence))
        #self.showFullScreen()

    def keyPressEvent(self, e):
        """
        """
        if e.text() in self.pixmap_keys:
            index = int(e.text()) - 1
            self.show_image(index)
            self.timer.stop()
            self.timer.singleShot(5000, self.timer.start)

    def _load_images(self, folder_path, filter=('png', 'jpg'), height=1000):
        """Load all the images from the target folder.
        """
        patterns = [os.path.join(folder_path, f'*.{ext}') for ext in filter]
        file_list = []
        # Cannot use sum with start in python 3.7?
        for pattern in patterns:
            file_list += glob.glob(pattern)
        file_list.sort()
        pixmap_list = []
        pixmap_keys  = []
        for i, file_path in enumerate(file_list):
            print(f'Loading {file_path}...')
            pixmap_list.append(QPixmap(file_path).scaledToHeight(height))
            pixmap_keys.append(f'{i + 1}')
        self.__current_index = 0
        return pixmap_list, pixmap_keys

    def show_image(self, index=0):
        """Show a given image.
        """
        self.__current_index = index % len(self.pixmap_list)
        self.label.setPixmap(self.pixmap_list[self.__current_index])

    def advance(self):
        """Advance to the next image.
        """
        self.show_image(self.__current_index + 1)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    slideshow = SlideShow('posters')
    sys.exit(app.exec_())