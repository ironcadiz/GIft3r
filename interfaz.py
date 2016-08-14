from PyQt5 import QtGui, uic, QtCore, QtWidgets
import urllib.request
import webbrowser
from EbaySearcher import EbaySearcher
from twython import Twython
from monkeylearn import MonkeyLearn
from main import recomender
from time import time

formulario = uic.loadUiType("ingreso_wg.ui")
mainwin = uic.loadUiType("ingresar.ui")
ebay = EbaySearcher(660)


class MainWindow(mainwin[0], mainwin[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('¡Encuentra el regalo perfecto!')

        self.form = IngresoWidget(self)
        self.setCentralWidget(self.form)
        self.setStyleSheet("background-color: white")


class IngresoWidget(formulario[0], formulario[1]):
    def __init__(self, mainWindow):
        super().__init__()

        self.setupUi(self)

        self.mainWindow = mainWindow

        self.TWITTER_CONSUMER_KEY = 'SJ3glU25jK3swUhRAraJ8GQXc'
        self.TWITTER_CONSUMER_SECRET = 'bfXDwwJIa2emh61MFNLSduMSGQx60VIHTcZmDuvoMg5zaVoDzm'
        self.TWITTER_ACCESS_TOKEN_KEY = '744463552992403456-51Ek3Oh2fFe52XxF1rvw29CG5uA1pFL'
        self.TWITTER_ACCESS_TOKEN_SECRET = 'j4laK9F7abRvcc0ZgkunMTWpdYEy4eZmQgBsSpbftOs7v'
        self.ml = MonkeyLearn('30007d9d8a696dc3c0a7700d68299a07e91915e2')
        self.MONKEYLEARN_LANG_CLASSIFIER_ID = 'cl_hDDngsX8'
        self.MONKEYLEARN_TOPIC_CLASSIFIER_ID = 'cl_5icAVzKR'
        self.MONKEYLEARN_EXTRACTOR_ID = 'ex_eV2dppYE'
        self.TWITTER_USER = 'agustin'

        self.twitter = Twython(self.TWITTER_CONSUMER_KEY, self.TWITTER_CONSUMER_SECRET ,self.TWITTER_ACCESS_TOKEN_KEY, self.TWITTER_ACCESS_TOKEN_SECRET)

        self.lang = "Spanish"
        self.spanishRadioButton.setChecked(True)
        self.spanishRadioButton.toggled.connect(lambda:self.btnstate(self.spanishRadioButton))
        self.englishRadioButton.toggled.connect(lambda:self.btnstate(self.englishRadioButton))

        self.setStyleSheet("QPushButton {background-color: rgb(230, 246, 255)}")
        self.pushButton_buscar.clicked.connect(self.buscar_regalo)
        self.pushButton_goStore.clicked.connect(self.ir_tienda)

        pixmap_logo = QtGui.QPixmap('gifter.png')
        scaled_logo = pixmap_logo.scaled(self.label_logo.size(), QtCore.Qt.KeepAspectRatio)
        self.label_logo.setPixmap(scaled_logo)

        self.listWidget_urls.itemClicked.connect(self.actualizar_datos)
        self.last_product_clicked = None

        self.cargandoLabel.setText("")

        self.hide_product_data()

    def btnstate(self,b):
        if b.text().startswith("Esp"):
            if b.isChecked() == True:
                self.lang = "Spanish"

        elif b.text().startswith("Ing"):
            if b.isChecked() == True:
                self.lang = "English"


    def hide_product_data(self):
        self.label_4.hide()
        self.label_2.hide()
        self.label_productName.hide()
        self.label_price.hide()

    def show_product_data(self):
        self.label_4.show()
        self.label_2.show()
        self.label_productName.show()
        self.label_price.show()


    def buscar_regalo(self):

        t0 = time()

        self.listWidget_urls.clear()

        self.TWITTER_USER = self.lineEdit_user.text()
        if self.lineEdit_precioMin.text() == "" or self.lineEdit_precioMax.text() == "":
            precio_min = 0
            precio_max = 999999999
        else:
            precio_min = float(self.lineEdit_precioMin.text())
            precio_max = float(self.lineEdit_precioMax.text())
        # REALIZAR BUSQUEDA DE INTERESES

        keywords = recomender(self.twitter, self.ml, self.TWITTER_USER, self.lang)

        gifts = ebay.getItem(keywords, precio_min, precio_max)

        if gifts:
            for gift in gifts:

                img_url = gift.photoUrl
                store_url = gift.itemUrl
                precio = gift.value
                nombre = gift.title

                #img_url = 'https://i.kinja-img.com/gawker-media/image/upload/s--7098ugfu--/c_scale,fl_progressive,q_80,w_800/dociw4fbzf2fs4tvywgl.jpg'
                #store_url = "http://9gag.com/"
                #precio = "1500"
                #nombre = "Einstein"

                new_item = ListItemUrl(store_url, img_url, precio, nombre)
                new_item.setText(nombre)

                self.listWidget_urls.addItem(new_item)

            #self.cargandoLabel.setText("")

        else:
            #self.cargandoLabel.setText("Error de Búsqueda")
            self.cargandoLabel.setText("")

        print(time() - t0, "seconds")



    def ir_tienda(self):
        url = self.listWidget_urls.currentItem().store_url
        webbrowser.open(url, 2)

    def actualizar_datos(self):
        self.mainWindow.statusBar().showMessage('Actualizando datos...')

        current_product = self.listWidget_urls.currentItem()
        if current_product != self.last_product_clicked:
            self.last_product_clicked = current_product

            img_url = current_product.img_url
            precio = current_product.precio
            nombre = current_product.nombre

            data = urllib.request.urlopen(img_url).read()
            image = QtGui.QImage()
            image.loadFromData(data)
            photo = QtGui.QPixmap(image)
            scaled_photo = photo.scaled(self.label_image.size(), QtCore.Qt.KeepAspectRatio)
            self.label_image.setPixmap(scaled_photo)

            self.label_productName.setText(nombre)
            self.label_price.setText("${}".format(precio))

            self.show_product_data()

        self.mainWindow.statusBar().showMessage('')

class ListItemUrl(QtWidgets.QListWidgetItem):
    def __init__(self, store_url, img_url, precio, nombre):
        super().__init__()
        self.store_url = store_url
        self.img_url = img_url
        self.precio = precio
        self.nombre = nombre



if __name__ == '__main__':

    app = QtWidgets.QApplication([])
    form = MainWindow()
    form.show()
    app.exec_()