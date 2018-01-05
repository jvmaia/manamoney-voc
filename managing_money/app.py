import android
import android.view
from android.widget import (
    Button, EditText, LinearLayout,
    RelativeLayout, ListView, TextView, CheckBox
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

        self.product_name = EditText(self._activity)
        self.product_name.setHint('Product name')
        self.vlayout.addView(self.product_name)

        self.product_quantity = EditText(self._activity)
        self.product_quantity.setHint('Product quantity')
        self.product_quantity.setInputType(0x00000002) 
        self.vlayout.addView(self.product_quantity)

        self.product_price = EditText(self._activity)
        self.product_price.setHint('Product price')
        self.product_price.setInputType(0x00000002 | 0x00002000)
        self.vlayout.addView(self.product_price)

        create_button = Button(self._activity)
        create_button.setOnClickListener(ButtonClick(self.create_product))
        create_button.setText('Create product')
        self.vlayout.addView(create_button)

        return_button = Button(self._activity)
        return_button.setOnClickListener(ButtonClick(self.main_view))
        return_button.setText('Return')
        self.vlayout.addView(return_button)

    def create_sale_view(self):
        self.vlayout.removeAllViews()

        sale_person = EditText(self._activity)
        sale_person.setHint('Client')
        self.vlayout.addView(sale_person)

        sale_value = EditText(self._activity)
        sale_value.setInputType(0x00000002 | 0x00002000)
        sale_value.setHint('Value')
        self.vlayout.addView(sale_value)

        sale_description = EditText(self._activity)
        sale_description.setHint('Sale description')
        self.vlayout.addView(sale_description)

        hlayout = LinearLayout(self._activity)

        text = TextView(self._activity)
        text.setText('Payed')
        hlayout.addView(text)
        sale_payed = CheckBox(self._activity)
        hlayout.addView(sale_payed)

        self.vlayout.addView(hlayout)

        create_button = Button(self._activity)
        create_button.setOnClickListener(ButtonClick(self.create_sale))
        create_button.setText('Sale')
        self.vlayout.addView(create_button)

        return_button = Button(self._activity)
        return_button.setOnClickListener(ButtonClick(self.main_view))
        return_button.setText('Return')
        self.vlayout.addView(return_button)

    def products_view(self):
        self.vlayout.removeAllViews()
        pass

    def sales_view(self):
        self.vlayout.removeAllViews()
        pass

    def create_product(self):
        product = {}
        product['name'] = str(self.product_name.getText())
        if len(product['name']) == 0:
            self.product_name.setHint('Enter a valid name please')
            return
        
        try:
            product['quantity'] = int(str(self.product_quantity.getText()))
            product['price'] = float(str(self.product_price.getText()))
        except ValueError:
            self.product_quantity.setHint('Enter a valid number please')
            self.product_price.setHint('Enter a valid number please')
            return

        self.db.create_product(product)
        self.main_view()

    def create_sale(self):
        pass

def main():
    MainApp()
