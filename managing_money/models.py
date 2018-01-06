import android
from android.database.sqlite import SQLiteDatabase
from android.content import ContentValues

class manamoneyDB(extends=android.database.sqlite.SQLiteOpenHelper):
    @super({
        context: android.content.Context,
        "com.jvmaiia.managing_money": java.lang.String,
        None: android.database.sqlite.SQLiteDatabase[CursorFactory],
        1: int
    })
    def __init__(self, context):
        pass

    def onCreate(self, db: android.database.sqlite.SQLiteDatabase) -> void:
        db.execSQL(
            "CREATE TABLE sale ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "person TEXT NOT NULL,"
            "total REAL NOT NULL,"
            "description TEXT NOT NULL,"
            "payed BOOLEAN NOT NULL CHECK (payed IN (0,1))"
            ")"
        )
        db.execSQL(
            "CREATE TABLE product ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "quantity INTEGER NOT NULL,"
            "price REAL NOT NULL"
            ")"
        )

    def onUpgrade(self, db: android.database.sqlite.SQLiteDatabase,
                  oldVersion: int, newVersion: int) -> void:
        print('will upgrade database from', oldVersion, ' to', newVersion)
        raise NotImplementedError

    def create_product(self, product):
        values = ContentValues()
        values.put("name", product['name'])
        values.put("price", product['price'])
        values.put("quantity", product['quantity'])
        db = self.getWritableDatabase()
        db.insertWithOnConflict("product", None, values, SQLiteDatabase.CONFLICT_REPLACE)
        db.close()

    def create_sale(self, sale):
        values = ContentValues()
        values.put("person", sale['person'])
        values.put("total", sale['value'])
        values.put("description", sale['description'])
        values.put("payed", sale['payed'])
        db = self.getWritableDatabase()
        db.insertWithOnConflict("sale", None, values, SQLiteDatabase.CONFLICT_REPLACE)

        #remove quantity from products
        products = sale['description'].split('\n')

        for product in products:
            name, quantity = product.split(':')
            quantity = int(quantity)
            db.execSQL(
                "UPDATE product SET quantity = quantity - %d WHERE name='%s'" % (quantity, name)
            )

    def fetch_products(self):
        result = []

        db = self.getReadableDatabase()
        cursor = db.rawQuery("SELECT * FROM product", None)
        while cursor.moveToNext():
            product_id = int(cursor.getInt(cursor.getColumnIndex('id')))
            name = cursor.getString(cursor.getColumnIndex('name'))
            price = float(cursor.getFloat(cursor.getColumnIndex('price')))
            quantity = int(cursor.getInt(cursor.getColumnIndex('quantity')))
            result.append(dict(id=product_id, name=name, value=price, quantity=quantity))
        db.close()

        return result

    def fetch_sales(self):
        result = []

        db = self.getReadableDatabase()
        cursor = db.rawQuery("SELECT * FROM sale", None)
        while cursor.moveToNext():
            sale_id = int(cursor.getInt(cursor.getColumnIndex('id')))
            person = cursor.getString(cursor.getColumnIndex('person'))
            value = float(cursor.getFloat(cursor.getColumnIndex('total')))
            description = cursor.getInt(cursor.getColumnIndex('description'))
            payed = bool(cursor.getInt(cursor.getColumnIndex('payed')))
            result.append(dict(id=sale_id, person=person, value=value, description=description, payed=payed))
        db.close()

        return result

    def changeQuantity_product(self, value):
        db = self.getReadableDatabase()
        product = db.rawQuery("SELECT * FROM product WHERE id=%d" % (value['id']), None)
        product.moveToNext()
        quantity = value['quantity']
        db.close()

        db = self.getWritableDatabase()
        db.execSQL(
            "UPDATE product SET quantity=%d WHERE id=%d"%(quantity, value['id'])
        )
        db.close()

    def update_sale(self, sale):
        db = self.getWritableDatabase()
        db.execSQL(
            "UPDATE sale SET payed=%d WHERE id=%d"%(int(sale['payed']), sale['id'])
        )
        db.close()

    def get_balance(self):
        received = []
        to_receive = []

        db = self.getReadableDatabase()
        cursor = db.rawQuery("SELECT * FROM sale", None)
        
        while cursor.moveToNext():
            payed = bool(cursor.getInt(cursor.getColumnIndex('payed')))
            value = float(cursor.getFloat(cursor.getColumnIndex('total')))
            if payed:
                received.append(value)
            else:
                to_receive.append(value)
        db.close()

        to_receive = sum(to_receive)
        received = sum(received)

        return received, to_receive
 