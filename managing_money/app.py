import android
from android.graphics import Paint, PorterDuff
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

def _create_layout_params():
    params = RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT,
                                         RelativeLayout.LayoutParams.WRAP_CONTENT)
    params.addRule(RelativeLayout.ALIGN_PARENT_RIGHT)
    return params

class StrikeableTextView(extends=android.widget.TextView):
    @super({context: android.content.Context})
    def __init__(self, context, striked=False):
        self.striked = striked
        self._repaint_strike()

    def setStriked(self, striked):
        self.striked = bool(striked)
        self._repaint_strike()

    def _repaint_strike(self):
        if self.striked:
            flags = self.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG
            self.setTextColor(0xffaaaaaa)
        else:
            flags = self.getPaintFlags() & ~Paint.STRIKE_THRU_TEXT_FLAG
            self.setTextColor(0xff111111)
        self.setPaintFlags(flags)


class SaleItem:
    def __init__(self, sale, context, callback=None):
        print('DEBUG CALLBACK =', callback)
        self.sale = sale
        self.context = context
        self.callback = callback

        self.layout = LinearLayout(self.context)
        self.checkbox = CheckBox(self.context)
        self.checkbox.setOnClickListener(ButtonClick(self.pay))
        self.layout.addView(self.checkbox)
            
        self.text_view = StrikeableTextView(self.context, striked=sale['payed'])
        self.text_view.setTextSize(25)
        self.layout.addView(self.text_view)

        self.text_view.setText(self.sale['person'] + '      ||      ' + str(self.sale['value']))
        self.checkbox.setChecked(bool(self.sale['payed']))

    def pay(self):
        self.sale['payed'] = self.checkbox.isChecked()
        self.text_view.setStriked(self.sale['payed'])
        self.callback(self.sale)

    def getView(self):
        return self.layout

class SalesListAdapter(extends=android.widget.BaseAdapter):
    def __init__(self, context, sales, listener=None):
        print('DEBUG LISTENER =', listener)
        self.context = context
        self.sales = list(sales)
        self.listener = listener

    def getCount(self) -> int:
        return len(self.sales)

    def getItem(self, position: int) -> java.lang.Object:
        return self.sales[position]

    def getItemId(self, position: int) -> long:
        return self.sales[position]['id']

    def getView(self, position: int,
                view: android.view.View,
                container: android.view.ViewGroup) -> android.view.View:
        sale = self.getItem(position)
        saleItem = SaleItem(sale, self.context, callback=self.listener)
        return saleItem.getView()

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

        self.sale_person = EditText(self._activity)
        self.sale_person.setHint('Client')
        self.vlayout.addView(self.sale_person)

        self.sale_description = EditText(self._activity)
        self.sale_description.setHint('product: quantity')
        self.vlayout.addView(self.sale_description)

        self.sale_value = EditText(self._activity)
        self.sale_value.setInputType(0x00000002 | 0x00002000)
        self.sale_value.setHint('Value')
        self.vlayout.addView(self.sale_value)

        hlayout = LinearLayout(self._activity)

        text = TextView(self._activity)
        text.setText('Payed')
        hlayout.addView(text)
        self.sale_payed = CheckBox(self._activity)
        hlayout.addView(self.sale_payed)

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
        
        self.adapter = ProductsListAdapter(self._activity, self.productsItems)
        self.listView = ListView(self._activity)
        self.listView.setAdapter(self.adapter)

        self.vlayout.addView(self.listView)

    def sales_view(self):
        self.vlayout.removeAllViews()

        self.salesItems = self.db.fetch_sales()
        self.adapter = SalesListAdapter(self._activity, self.salesItems,
                                        listener=self.update_sale)
        self.listView = ListView(self._activity)
        self.listView.setAdapter(self.adapter)

        self.vlayout.addView(self.listView)

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
        sale = {}
        sale['person'] = str(self.sale_person.getText())
        if len(sale['person']) == 0:
            self.sale_person.setHint('Enter a valid name please')
            return

        sale['description'] = str(self.sale_description.getText())
        if len(sale['description']) == 0:
            self.sale_description.setHint('Enter a valid description please')
            return

        try:
            sale['value'] = float(str(self.sale_value.getText()))
        except ValueError:
            self.sale_value.setHint('Enter a valid value please')
            return

        sale['payed'] = int(self.sale_payed.isChecked())

        self.db.create_sale(sale)
        self.main_view()

    def update_sale(self, sale):
        self.db.update_sale(sale)

def main():
    MainApp()
