import android
import android.view
from android.widget import (
    Button, EditText, LinearLayout,
    RelativeLayout, ListView, TextView
    )
from android.view import Gravity
from .models import manamoneyDB

class ButtonClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)

class MainApp:
    def __init__(self):
        self._activity = android.PythonActivity.setListener(self)
        self.db = manamoneyDB(self._activity)

    def onCreate(self):
        self.vlayout = LinearLayout(self._activity)
        self.vlayout.setOrientation(LinearLayout.VERTICAL)
        self.vlayout.setGravity(Gravity.CENTER)
        self._activity.setContentView(self.vlayout)
        self.main_view()

    def main_view(self):
        self.vlayout.removeAllViews()

        create_sale = Button(self._activity)
        create_sale.setText('Create sale')
        create_sale.setOnClickListener(ButtonClick(self.create_sale_view))
        self.vlayout.addView(create_sale)

        create_product = Button(self._activity)
        create_product.setText('Create product')
        create_product.setOnClickListener(ButtonClick(self.create_product_view))
        self.vlayout.addView(create_product)

        sales_view = Button(self._activity)
        sales_view.setText('View sales')
        sales_view.setOnClickListener(ButtonClick(self.sales_view))
        self.vlayout.addView(sales_view)

        products_view = Button(self._activity)
        products_view.setText('View products')
        products_view.setOnClickListener(ButtonClick(self.products_view))
        self.vlayout.addView(products_view)

    def create_product_view(self):
        self.vlayout.removeAllViews()

        product_name = EditText(self._activity)
        product_name.setHint('Product name')
        self.vlayout.addView(product_name)

        product_quantity = EditText(self._activity)
        product_quantity.setHint('Product quantity')
        product_quantity.setInputType(0x00000002) 
        self.vlayout.addView(product_quantity)

        product_value = EditText(self._activity)
        product_value.setHint('Product value')
        product_value.setInputType(0x00000002 | 0x00002000)
        self.vlayout.addView(product_value)

        create_button = Button(self._activity)
        create_button.setOnClickListener(ButtonClick(self.create_product))
        create_button.setText('Create product')
        self.vlayout.addView(create_button)

    def create_sale_view(self):
        self.vlayout.removeAllViews()
        pass

    def products_view(self):
        self.vlayout.removeAllViews()
        pass

    def sales_view(self):
        self.vlayout.removeAllViews()
        pass

    def create_product(self):
        pass

def main():
    MainApp()
