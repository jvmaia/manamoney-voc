import android
from android.graphics import Paint, PorterDuff
import android.view
from android.widget import (
    Button, EditText, LinearLayout,
    RelativeLayout, ListView, TextView, CheckBox
    )
from android.view import Gravity
from .models import manamoneyDB

def _create_layout_params(side):
    params = RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT,
                                         RelativeLayout.LayoutParams.WRAP_CONTENT)
    if side == 'right':
        params.addRule(RelativeLayout.ALIGN_PARENT_RIGHT)
    elif side == 'bottom':
        params.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM)

    return params

class ButtonClick(implements=android.view.View[OnClickListener]):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def onClick(self, view: android.view.View) -> void:
        self.callback(*self.args, **self.kwargs)

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
        self.sale = sale
        self.context = context
        self.callback = callback
        self.layout = LinearLayout(self.context)

        self.button_details = Button(self.context)
        self.button_details.setOnClickListener(ButtonClick(self.details))
        self.button_details.setText('+')
        self.button_details.getBackground().setColorFilter(0xff9e9e9e, PorterDuff.Mode.MULTIPLY)
        self.layout.addView(self.button_details)

        self.text_view = StrikeableTextView(self.context, striked=sale['paid'])
        self.text_view.setText(self.sale['person'])
        self.text_view.setTextSize(22)
        self.layout.addView(self.text_view)

        self.button_pay = Button(self.context)
        self.button_pay.setOnClickListener(ButtonClick(self.pay))
        self.button_pay.setText('V')
        self.button_pay.getBackground().setColorFilter(0xff8bc34a, PorterDuff.Mode.MULTIPLY)

        relative1 = RelativeLayout(self.context)
        relative1.addView(self.button_pay, _create_layout_params('right'))

        self.layout.addView(relative1)

    def details(self):
        self.callback(event='details_sale', value=self.sale)

    def pay(self):
        self.sale['paid'] = True
        self.text_view.setStriked(self.sale['paid'])
        self.callback(event='update_sale', value=self.sale)

    def getView(self):
        return self.layout

class ProductItem:
    def __init__(self, product, context, callback=None):
        self.product = product
        self.context = context
        self.callback = callback

        self.layout = LinearLayout(self.context)
        self.text_view = TextView(self.context) 
        self.text_view.setTextSize(20)
        self.text_view.setText('%s | %d | R$%.2f' % (self.product['name'],
                                self.product['quantity'], self.product['value']))
        self.layout.addView(self.text_view)

        hbuttons = LinearLayout(self.context)
        hbuttons.setOrientation(LinearLayout.HORIZONTAL)

        self.add_button = Button(self.context)
        self.add_button.setOnClickListener(ButtonClick(self.add))
        self.add_button.getBackground().setColorFilter(0xff8bc34a, PorterDuff.Mode.MULTIPLY)
        self.add_button.setText('+')
        hbuttons.addView(self.add_button)

        self.remove_button = Button(self.context)
        self.remove_button.setOnClickListener(ButtonClick(self.remove))
        self.remove_button.getBackground().setColorFilter(0xffff0000, PorterDuff.Mode.MULTIPLY)
        self.remove_button.setText('-')
        hbuttons.addView(self.remove_button)

        relative = RelativeLayout(self.context)
        relative.addView(hbuttons, _create_layout_params('right'))

        self.layout.addView(relative)

    def add(self):
        self.product['quantity'] += 1
        self.text_view.setText('%s | %d | R$%.2f' % (self.product['name'],
                                self.product['quantity'], self.product['value']))
        self.callback(event='update_product', value=self.product)

    def remove(self):
        self.product['quantity'] -= 1
        self.text_view.setText('%s | %d | R$%.2f' % (self.product['name'],
                                self.product['quantity'], self.product['value']))
        self.callback(event='update_product', value=self.product)

    def getView(self):
        return self.layout

class SalesListAdapter(extends=android.widget.BaseAdapter):
    def __init__(self, context, sales, listener=None):
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

class ProductsListAdapter(extends=android.widget.BaseAdapter):
    def __init__(self, context, products, listener=None):
        self.context = context
        self.products = list(products)
        self.listener = listener

    def getCount(self) -> int:
        return len(self.products)

    def getItem(self, position: int) -> java.lang.Object:
        return self.products[position]

    def getItemId(self, position: int) -> long:
        return self.products[position]['id']

    def getView(self, position: int,
                view: android.view.View,
                container: android.view.ViewGroup) -> android.view.View:
        product = self.getItem(position)
        productItem = ProductItem(product, self.context, callback=self.listener)
        return productItem.getView()

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

        hlayout = LinearLayout(self._activity)
        hlayout.setOrientation(LinearLayout.HORIZONTAL)
        relative_bottom = RelativeLayout(self._activity)
        relative_right = RelativeLayout(self._activity)

        received, to_receive = self.get_balance()
        received_view = TextView(self._activity)
        received_view.setText('Received %.2f' % (float(received)))
        received_view.setTextSize(18)
        to_receive_view = TextView(self._activity)
        to_receive_view.setText('To receive %.2f' % (float(to_receive)))
        to_receive_view.setTextSize(18)

        relative_right.addView(to_receive_view, _create_layout_params('right'))
        hlayout.addView(received_view)
        hlayout.addView(relative_right)
        relative_bottom.addView(hlayout, _create_layout_params('bottom'))
        self.vlayout.addView(relative_bottom)

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
        self.add_return_button('main')

    def create_sale_view(self):
        self.vlayout.removeAllViews()

        self.sale_person = EditText(self._activity)
        self.sale_person.setHint('Client')
        self.vlayout.addView(self.sale_person)

        self.sale_description = EditText(self._activity)
        self.sale_description.setHint('product:quantity')
        self.vlayout.addView(self.sale_description)

        self.sale_value = EditText(self._activity)
        self.sale_value.setInputType(0x00000002 | 0x00002000)
        self.sale_value.setHint('Value')
        self.vlayout.addView(self.sale_value)

        hlayout = LinearLayout(self._activity)

        text = TextView(self._activity)
        text.setText('Paid')
        text.setTextSize(22)
        hlayout.addView(text)
        self.sale_paid = CheckBox(self._activity)
        hlayout.addView(self.sale_paid)

        self.vlayout.addView(hlayout)

        create_button = Button(self._activity)
        create_button.setOnClickListener(ButtonClick(self.create_sale))
        create_button.setText('Sale')
        self.vlayout.addView(create_button)
        self.add_return_button('main')        

    def products_view(self):
        self.vlayout.removeAllViews()
        
        self.productsItems = self.db.fetch_products()
        self.adapter = ProductsListAdapter(self._activity, self.productsItems,
                                            listener=self._dispatch_event)
        self.listView = ListView(self._activity)
        self.listView.setAdapter(self.adapter)

        self.vlayout.addView(self.listView)
        self.add_return_button('main')

    def sales_view(self):
        self.vlayout.removeAllViews()

        self.salesItems = self.db.fetch_sales()
        self.adapter = SalesListAdapter(self._activity, self.salesItems,
                                        listener=self._dispatch_event)
        self.listView = ListView(self._activity)
        self.listView.setAdapter(self.adapter)

        self.vlayout.addView(self.listView)
        self.add_return_button('main')

    def details_sale_view(self, sale):
        self.vlayout.removeAllViews()

        person_text = TextView(self._activity)
        person_text.setText('Client: %s' % (sale['person']))
        person_text.setTextSize(22)
        self.vlayout.addView(person_text)
        
        value_text = TextView(self._activity)
        value_text.setText('Value: R$%.2f' % (sale['value']))
        value_text.setTextSize(22)
        self.vlayout.addView(value_text)

        description_text = TextView(self._activity)
        description_text.setText('Description: %s' % (sale['description']))
        description_text.setTextSize(22)
        self.vlayout.addView(description_text)

        date_text = TextView(self._activity)
        date_text.setText('Date: %s' % (sale['date']))
        date_text.setTextSize(22)
        self.vlayout.addView(date_text)

        self.add_return_button('sales_view')

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
        self.product_name.setInputType(0) # close keyboard after create
        self.product_quantity.setInputType(0) # close keyboard after create
        self.product_price.setInputType(0) # close keyboard after create
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

        sale['paid'] = int(self.sale_paid.isChecked())

        self.db.create_sale(sale)
        self.sale_person.setInputType(0) # close keyboard after create
        self.sale_description.setInputType(0) # close keyboard after create
        self.sale_value.setInputType(0) # close keyboard after create
        self.main_view()

    def _dispatch_event(self, event, value):
        if event == 'update_sale':
            self.db.update_sale(sale=value)
        elif event == 'update_product':
            self.db.changeQuantity_product(sale=value)
        elif event == 'details_sale':
            self.details_sale_view(sale=value)

    def add_return_button(self, view):
        return_button = Button(self._activity)
        return_button.setOnClickListener(ButtonClick(self.return_view, view))
        return_button.setText('Return')
        relative = RelativeLayout(self._activity)
        relative.addView(return_button, _create_layout_params('bottom'))
        self.vlayout.addView(relative)

    def return_view(self, view):
        if view == 'main':
            self.main_view()
        elif view == 'sales_view':
            self.sales_view()

    def get_balance(self):
        return self.db.get_balance()

def main():
    MainApp()
