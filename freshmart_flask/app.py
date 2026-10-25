from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3, os
from datetime import date, datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'freshmart.db')
app = Flask(__name__)
app.secret_key = 'freshmart-local-dev-key'
CATEGORIES = [
 ('fruits','Fruits','Apples, bananas, oranges, mangoes and grapes'),
 ('vegetables','Vegetables','Potatoes, onions, tomatoes, carrots and cucumbers'),
 ('grocery','Grocery items','Rice, flour, sugar, salt, cooking oil and spices'),
 ('dairy','Dairy products','Milk, yogurt, butter and cheese'),
 ('other','Other mart products','Biscuits, snacks, beverages and cleaning products')]
UNITS = ['kg','dozen','litre','pack','bottle','piece']
REASONS = ['Sale','Damaged','Expired']
SEED_PRODUCTS = [
('Apples (Kala Kulu)','fruits',350,'kg',42,20,'2026-11-08'),('Bananas','fruits',200,'dozen',18,20,'2026-10-28'),('Oranges (Kinnow)','fruits',220,'kg',35,15,'2026-11-05'),('Mangoes (Sindhri)','fruits',300,'kg',8,15,'2026-10-30'),('Grapes','fruits',400,'kg',22,10,'2026-10-29'),
('Potatoes','vegetables',90,'kg',120,50,None),('Onions','vegetables',150,'kg',85,50,None),('Tomatoes','vegetables',160,'kg',30,40,'2026-10-29'),('Carrots','vegetables',120,'kg',26,20,'2026-11-04'),('Cucumbers','vegetables',120,'kg',12,15,'2026-10-28'),
('Basmati Rice','grocery',380,'kg',210,100,'2027-09-30'),('Wheat Flour (Atta)','grocery',130,'kg',160,80,'2027-01-15'),('Sugar','grocery',165,'kg',70,60,None),('Iodised Salt','grocery',60,'pack',48,30,'2028-06-30'),('Cooking Oil','grocery',560,'litre',28,30,'2027-05-31'),('Garam Masala','grocery',180,'pack',40,20,'2027-04-30'),
('Fresh Milk','dairy',220,'litre',45,40,'2026-10-27'),('Yogurt (Dahi)','dairy',240,'pack',24,20,'2026-10-24'),('Salted Butter','dairy',450,'pack',16,12,'2026-11-20'),('Cheese Slices','dairy',750,'pack',9,10,'2026-11-02'),
('Biscuits','other',60,'pack',96,40,'2027-02-15'),('Potato Chips','other',50,'pack',60,30,'2026-11-01'),('Instant Noodles','other',70,'pack',120,50,'2026-10-30'),('Soft Drink 1.5 L','other',200,'bottle',72,36,'2027-03-01'),('Dish Wash Liquid','other',350,'bottle',14,10,None),('Floor Cleaner','other',450,'bottle',0,8,None)]
SEED_TX = [
('p-milk','Fresh Milk','litre','in',40,'Supplier delivery','Al-Noor Dairy','2026-10-25','Morning delivery'),('p-tomatoes','Tomatoes','kg','out',18,'Sale','','2026-10-24',''),('p-yogurt','Yogurt (Dahi)','pack','out',6,'Expired','','2026-10-24','Batch dated 23 Oct'),('p-apples','Apples (Kala Kulu)','kg','in',30,'Supplier delivery','Fruit Mandi Lahore','2026-10-23',''),('p-rice','Basmati Rice','kg','out',25,'Sale','','2026-10-23',''),('p-bananas','Bananas','dozen','out',3,'Damaged','','2026-10-22','Over-ripe'),('p-floorcleaner','Floor Cleaner','bottle','out',6,'Sale','','2026-10-21',''),('p-flour','Wheat Flour (Atta)','kg','in',100,'Supplier delivery','Al-Madina Traders','2026-10-20','10 × 10 kg bags'),('p-potatoes','Potatoes','kg','in',80,'Supplier delivery','Sabzi Mandi','2026-10-19',''),('p-oil','Cooking Oil','litre','out',12,'Sale','','2026-10-18',''),('p-biscuits','Biscuits','pack','in',60,'Supplier delivery','Karachi Wholesale','2026-10-16',''),('p-mangoes','Mangoes (Sindhri)','kg','out',4,'Damaged','','2026-10-15','Bruised in transit')]

def db():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn

def init_db():
    with db() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL COLLATE NOCASE UNIQUE,category TEXT NOT NULL,price REAL NOT NULL,unit TEXT NOT NULL,quantity INTEGER NOT NULL,reorder_level INTEGER NOT NULL,expiry_date TEXT);
        CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER,product_name TEXT NOT NULL,unit TEXT NOT NULL,type TEXT NOT NULL,quantity INTEGER NOT NULL,reason TEXT NOT NULL,party TEXT DEFAULT '',date TEXT NOT NULL,note TEXT DEFAULT '',FOREIGN KEY(product_id) REFERENCES products(id));''')
        if c.execute('SELECT COUNT(*) FROM products').fetchone()[0]==0:
            for i,p in enumerate(SEED_PRODUCTS): c.execute('INSERT INTO products(name,category,price,unit,quantity,reorder_level,expiry_date) VALUES(?,?,?,?,?,?,?)',p)
            ids={r['name']:r['id'] for r in c.execute('SELECT id,name FROM products')}
            for tx in SEED_TX:
                pid=ids.get(tx[1]); c.execute('INSERT INTO transactions(product_id,product_name,unit,type,quantity,reason,party,date,note) VALUES(?,?,?,?,?,?,?,?,?)',(pid,*tx[1:]))

def all_products():
    with db() as c: return [dict(r) for r in c.execute('SELECT * FROM products ORDER BY name')]
def all_transactions():
    with db() as c: return [dict(r) for r in c.execute('SELECT * FROM transactions ORDER BY date DESC,id DESC')]
def stock_status(p): return 'out' if p['quantity']<=0 else ('low' if p['quantity']<=p['reorder_level'] else 'ok')
def expiry_status(p):
    if not p.get('expiry_date'): return ('none',None)
    days=(date.fromisoformat(p['expiry_date'])-date.today()).days
    return ('expired' if days<0 else 'soon' if days<=7 else 'ok',days)
def common():
    products=all_products(); tx=all_transactions()
    low=[p for p in products if p['quantity']<=p['reorder_level']]
    expiry=[]
    for p in products:
        st,days=expiry_status(p)
        if st in ('expired','soon'): expiry.append({**p,'expiry_status':st,'days':days})
    expiry.sort(key=lambda x:x['days'])
    return dict(products=products,transactions=tx,categories=CATEGORIES,units=UNITS,reasons=REASONS,low_stock=low,expiry_watch=expiry)
@app.context_processor
def inject(): return {'today':date.today().isoformat(),'money':lambda n:'Rs {:,.0f}'.format(n),'qty':lambda n,u:f'{n:,} {u}','category_name':lambda cid:next((x[1] for x in CATEGORIES if x[0]==cid),cid),'stock_status':stock_status,'expiry_status':expiry_status}
@app.route('/')
def dashboard():
    d=common(); p=d['products']; d.update(total_units=sum(x['quantity'] for x in p),stock_value=sum(x['price']*x['quantity'] for x in p),recent=d['transactions'][:6],category_stats=[])
    for cat in CATEGORIES:
        items=[x for x in p if x['category']==cat[0]]; d['category_stats'].append({'id':cat[0],'name':cat[1],'count':len(items),'units':sum(x['quantity'] for x in items),'low':sum(x['quantity']<=x['reorder_level'] for x in items)})
    return render_template('dashboard.html',**d,title='Dashboard')
@app.route('/products')
def products_page():
    d=common(); q=request.args.get('q','').strip().lower(); cat=request.args.get('category','all')
    d['products']=[p for p in d['products'] if (cat=='all' or p['category']==cat) and q in p['name'].lower()]; d.update(q=q,selected_category=cat)
    return render_template('products.html',**d,title='Products')
def product_from_form():
    name=request.form.get('name','').strip(); category=request.form.get('category','fruits'); unit=request.form.get('unit','kg')
    try: price=float(request.form.get('price','')); quantity=int(request.form.get('quantity','')); reorder=int(request.form.get('reorder_level',''))
    except ValueError: raise ValueError('Price, quantity and reorder level must be valid numbers.')
    if not name: raise ValueError('Product name is required.')
    if category not in [x[0] for x in CATEGORIES] or unit not in UNITS: raise ValueError('Choose a valid category and unit.')
    if price<0 or quantity<0 or reorder<0: raise ValueError('Numbers cannot be negative.')
    return (name,category,price,unit,quantity,reorder,request.form.get('expiry_date') or None)
@app.route('/products/add',methods=['POST'])
def add_product():
    try:
        p=product_from_form()
        with db() as c:
            c.execute('INSERT INTO products(name,category,price,unit,quantity,reorder_level,expiry_date) VALUES(?,?,?,?,?,?,?)',p)
            pid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            if p[4]>0: c.execute('INSERT INTO transactions(product_id,product_name,unit,type,quantity,reason,party,date,note) VALUES(?,?,?,?,?,?,?,?,?)',(pid,p[0],p[3],'in',p[4],'Opening stock','',''+date.today().isoformat(),'Added with new product'))
        flash(f'{p[0]} added to inventory.','success')
    except sqlite3.IntegrityError: flash('A product with this name already exists.','error')
    except ValueError as e: flash(str(e),'error')
    return redirect(url_for('products_page'))
@app.route('/products/<int:pid>/edit',methods=['POST'])
def edit_product(pid):
    try:
        p=product_from_form()
        with db() as c: c.execute('UPDATE products SET name=?,category=?,price=?,unit=?,quantity=?,reorder_level=?,expiry_date=? WHERE id=?',(*p,pid))
        flash('Product updated.','success')
    except sqlite3.IntegrityError: flash('A product with this name already exists.','error')
    except ValueError as e: flash(str(e),'error')
    return redirect(url_for('products_page'))
@app.route('/products/<int:pid>/delete',methods=['POST'])
def delete_product(pid):
    with db() as c:
        p=c.execute('SELECT name FROM products WHERE id=?',(pid,)).fetchone()
        if p: c.execute('DELETE FROM products WHERE id=?',(pid,)); flash(f'{p[0]} removed from inventory.','success')
    return redirect(url_for('products_page'))
@app.route('/stock',methods=['GET','POST'])
def stock_page():
    if request.method=='POST':
        try:
            pid=int(request.form.get('product_id','')); typ=request.form.get('type','in'); amount=int(request.form.get('quantity','')); reason=request.form.get('reason','Supplier delivery' if typ=='in' else 'Sale'); party=request.form.get('party','').strip(); txdate=request.form.get('date') or date.today().isoformat(); note=request.form.get('note','').strip(); exp=request.form.get('expiry_date') or None
            with db() as c:
                p=c.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
                if not p: raise ValueError('Choose a product first.')
                if typ not in ('in','out') or amount<=0: raise ValueError('Quantity must be greater than zero.')
                if typ=='out' and amount>p['quantity']: raise ValueError(f"Only {p['quantity']} {p['unit']} of {p['name']} is in stock.")
                newqty=p['quantity']+(amount if typ=='in' else -amount)
                c.execute('UPDATE products SET quantity=?, expiry_date=CASE WHEN ? IS NOT NULL THEN ? ELSE expiry_date END WHERE id=?',(newqty,exp if typ=='in' else None,exp,pid))
                c.execute('INSERT INTO transactions(product_id,product_name,unit,type,quantity,reason,party,date,note) VALUES(?,?,?,?,?,?,?,?,?)',(pid,p['name'],p['unit'],typ,amount,reason,party if typ=='in' else '',txdate,note))
            flash('Stock movement recorded.','success')
            return redirect(url_for('stock_page'))
        except (ValueError,TypeError) as e: flash(str(e),'error')
    d=common(); d.update(filter=request.args.get('filter','all'),initial_type=request.args.get('type','in'),initial_product=request.args.get('product',''),initial_reason=request.args.get('reason','Sale'))
    if d['filter']!='all': d['transactions']=[t for t in d['transactions'] if t['type']==d['filter']]
    return render_template('stock.html',**d,title='Stock in / out')
@app.route('/alerts')
def alerts_page():
    d=common(); filt=request.args.get('expiry','attention'); rows=[]
    for p in d['products']:
        if p['expiry_date']:
            st,days=expiry_status(p)
            if filt=='all' or (filt=='expired' and st=='expired') or (filt=='attention' and st in ('expired','soon')): rows.append({**p,'expiry_status':st,'days':days})
    rows.sort(key=lambda x:x['days'] if x['days'] is not None else 999999); d.update(expiry_rows=rows,expiry_filter=filt)
    return render_template('alerts.html',**d,title='Alerts')
@app.route('/categories')
def categories_page(): return render_template('categories.html',**common(),title='Categories')
@app.route('/reports')
def reports_page():
    d=common(); period=request.args.get('period','all'); cutoff=None
    if period in ('7','30'): cutoff=(date.today()-timedelta(days=int(period))).isoformat()
    tx=[t for t in d['transactions'] if not cutoff or t['date']>=cutoff]
    d.update(period=period,report_transactions=tx,stock_in=sum(t['quantity'] for t in tx if t['type']=='in'),stock_out=sum(t['quantity'] for t in tx if t['type']=='out'),total_units=sum(p['quantity'] for p in d['products']),stock_value=sum(p['quantity']*p['price'] for p in d['products']))
    return render_template('reports.html',**d,title='Inventory report')
if __name__=='__main__':
    init_db(); app.run(debug=True)
else: init_db()
