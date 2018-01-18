import android
from android.graphics import Paint, PorterDuff
import android.view
from android.widget import (
    Button, EditText, LinearLayout, FrameLayout,
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
    def __init__(self, sale, context, callback=None, back=None):
        self.sale = sale
        self.back = back
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
        self.callback(event='details_sale', value=self.sale, back=self.back)

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

class ClientItem:
    def __init__(self, client, context, callback=None):
        self.client = client
        self.callback = callback
        self.context = context
        self.layout = LinearLayout(self.context)

        self.text_view = TextView(self.context)
        self.text_view.setText(self.client)
        self.text_view.setTextSize(22)
        self.layout.addView(self.text_view)

        self.add_button = Button(self.context)
        self.add_button.setOnClickListener(ButtonClick(self.view_sales))
        self.add_button.getBackground().setColorFilter(0xff8bc34a, PorterDuff.Mode.MULTIPLY)
        self.add_button.setText('+')
        relative = RelativeLayout(self.context)
        relative.addView(self.add_button, _create_layout_params('right'))
        self.layout.addView(relative)

    def view_sales(self):
        self.callback(event='sales_client', value=self.client, back='clients')

    def getView(self):
        return self.layout

class SalesListAdapter(extends=android.widget.BaseAdapter):
    def __init__(self, context, sales, listener=None, back=None):
        self.context = context
        self.sales = list(sales)
        self.listener = listener
        self.back = back

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
        saleItem = SaleItem(sale, self.context, callback=self.listener, back=self.back)
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

class ClientsListAdapter(extends=android.widget.BaseAdapter):
    def __init__(self, context, clients, listener=None):
        self.context = context
        self.clients = list(clients)
        self.listener = listener

    def getCount(self) -> int:
        return len(self.clients)

    def getItem(self, position: int) -> java.lang.Object:
        return self.clients[position]

    def getItemId(self, position: int) -> long:
        return position

    def getView(self, position: int,
                view: android.view.View,
                container: android.view.ViewGroup) -> android.view.View:
        client = self.getItem(position)
        clientItem = ClientItem(client, self.context, callback=self.listener)
        return clientItem.getView()

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

        clients_view = Button(self._activity)
        clients_view.setText('View clients')
        clients_view.setOnClickListener(ButtonClick(self.clients_view))
        self.vlayout.addView(clients_view)

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

        self.add_error_text()
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

        generate_price_button = Button(self._activity)
        generate_price_button.setOnClickListener(ButtonClick(self.generate_price))
        generate_price_button.setText('Generate price')
        self.vlayout.addView(generate_price_button)

        create_button = Button(self._activity)
        create_button.setOnClickListener(ButtonClick(self.create_sale))
        create_button.setText('Sale')
        self.vlayout.addView(create_button)

        self.add_error_text()
        self.add_return_button('main')

    def products_view(self):
        self.vlayout.removeAllViews()

        self.productsItems = self.db.fetch_products()
        self.adapterProducts = ProductsListAdapter(self._activity, self.productsItems,
                                            listener=self._dispatch_event)
        self.listViewProducts = ListView(self._activity)
        self.listViewProducts.setAdapter(self.adapterProducts)

        self.add_return_button('main', bottom=False)
        self.vlayout.addView(self.listViewProducts)

    def sales_view(self, sales=None, back=None):
        self.vlayout.removeAllViews()

        if sales:
            self.salesItems = sales
        else:
            self.salesItems = self.db.fetch_sales()

        self.adapterSales = SalesListAdapter(self._activity, self.salesItems,
                                            listener=self._dispatch_event, back=back)
        self.listViewSales = ListView(self._activity)
        self.listViewSales.setAdapter(self.adapterSales)
        
        if back:
            self.add_return_button('clients', bottom=False)
        else:
            self.add_return_button('main', bottom=False)

        self.vlayout.addView(self.listViewSales)

    def clients_view(self):
        self.vlayout.removeAllViews()

        self.clientsItems = self.db.fetch_clients()
        self.adapterClients = ClientsListAdapter(self._activity, self.clientsItems,
                                                listener=self._dispatch_event)
        self.listViewClients = ListView(self._activity)
        self.listViewClients.setAdapter(self.adapterClients)

        self.add_return_button('main', bottom=False)
        self.vlayout.addView(self.listViewClients)

    def details_sale_view(self, sale, back=None):
        self.vlayout.removeAllViews()

        person_text = TextView(self._activity)
        person_text.setText('Client: %s' % (sale['person']))
        person_text.setTextSize(22)
        self.vlayout.addView(person_text)

        value_text = TextView(self._activity)
        value_text.setText('\nValue: R$%.2f' % (sale['value']))
        value_text.setTextSize(22)
        self.vlayout.addView(value_text)

        discount_text = TextView(self._activity)
        total_price = self.db.get_price(sale['description'].replace(' ', '\n'))
        discount = total_price - sale['value']
        discount_p = discount*100.0 / sale['value']
        discount_text.setText('\nDiscount: %.2f%% = R$%.2f' % (discount_p, discount))
        discount_text.setTextSize(22)
        self.vlayout.addView(discount_text)

        description_text = TextView(self._activity)
        description_text.setText('\nDescription: %s' % (sale['description']))
        description_text.setTextSize(22)
        self.vlayout.addView(description_text)

        date_text = TextView(self._activity)
        date = sale['date'].replace(' ', '-')
        date_text.setText('\nDate: %s' % (date))
        date_text.setTextSize(22)
        self.vlayout.addView(date_text)

        if back:
            self.add_return_button('sales_client', value=sale['person'])
        else:
            self.add_return_button('sales_view')

    def create_product(self):
        product = {}
        product['name'] = str(self.product_name.getText())
        if len(product['name']) == 0:
            self.error_text.setText('Enter a valid name please')
            return

        try:
            product['quantity'] = int(str(self.product_quantity.getText()))
            product['price'] = float(str(self.product_price.getText()))
        except ValueError:
            self.error_text.setText('Enter a valid number please')
            return

        self.db.create_product(product)
        self.main_view()

    def create_sale(self):
        sale = {}
        sale['person'] = str(self.sale_person.getText())
        if len(sale['person']) == 0:
            self.error_text.setText('Enter a valid name please')
            return

        sale['description'] = str(self.sale_description.getText())
        if len(sale['description']) == 0:
            self.error_text.setText('Enter a valid description please')
            return

        try:
            sale['value'] = float(str(self.sale_value.getText()))
        except ValueError:
            self.error_text.setText('Enter a valid value please')
            return

        sale['paid'] = int(self.sale_paid.isChecked())

        self.db.create_sale(sale)
        self.main_view()

    def _dispatch_event(self, event, value, back=None):
        if event == 'update_sale':
            self.db.update_sale(sale=value)
        elif event == 'update_product':
            self.db.changeQuantity_product(sale=value)
        elif event == 'details_sale':
            self.details_sale_view(sale=value, back=back)
        elif event == 'sales_client':
            sales = self.db.fetch_sales(client=value)
            self.sales_view(sales=sales, back='sales_clients')
        elif event == 'clients':
            self.return_view('clients')

    def add_return_button(self, view, bottom=True, value=None):
        self.return_button = Button(self._activity)
        self.return_button.setOnClickListener(ButtonClick(self.return_view, view, value=value))
        self.return_button.setText('Return')
        self.relative_rb = RelativeLayout(self._activity)
        if bottom:
            self.relative_rb.addView(self.return_button, _create_layout_params('bottom'))
        else:
            self.relative_rb.addView(self.return_button)
        self.vlayout.addView(self.relative_rb)

    def add_error_text(self):
        self.error_text = TextView(self._activity)
        self.vlayout.addView(self.error_text)

    def return_view(self, view, value=None):
        if view == 'main':
            self.main_view()
        elif view == 'sales_view':
            self.sales_view()
        elif view == 'clients':
            self.clients_view()
        elif view == 'sales_client':
            self._dispatch_event('sales_client', back=view, value=value)

    def get_balance(self):
        return self.db.get_balance()

    def generate_price(self):
        description = str(self.sale_description.getText())
        value = self.db.get_price(description)
        if type(value) == str:
            self.error_text.setText(value)
            return
        value = '%.2f' % value
        self.sale_value.setText(value.replace(',', '.'))

def main():
    MainApp()
