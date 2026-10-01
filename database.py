from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
from supabase import create_client

IST = ZoneInfo('Asia/Kolkata')
DEFAULT_PRODUCTS = [('Coconut',20),('Oti Saman',2),('Tel',5),('Sadi',50)]
FIXED_CUSTOMERS = ['Raju','Harvali','Bhakt']

def get_supabase():
    return create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY'])

supabase = get_supabase()
DB_PATH = None
BACKUP_DIR = None

def now_str():
    return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

def _dt(v):
    if not v: return None
    if isinstance(v, datetime): return v if v.tzinfo else v.replace(tzinfo=IST)
    s = str(v).strip()
    try:
        d = datetime.fromisoformat(s.replace('Z','+00:00'))
        return d if d.tzinfo else d.replace(tzinfo=IST)
    except ValueError:
        for f in ('%Y-%m-%d %H:%M:%S','%Y-%m-%dT%H:%M:%S'):
            try: return datetime.strptime(s,f).replace(tzinfo=IST)
            except ValueError: pass
    return None

def init_database():
    supabase.table('products').select('id').limit(1).execute()
    ts = now_str()
    for name, price in DEFAULT_PRODUCTS:
        rows = supabase.table('products').select('id').ilike('name',name).limit(1).execute().data or []
        if rows:
            supabase.table('products').update({'price':price,'active':True,'updated_at':ts}).eq('id',rows[0]['id']).execute()
        else:
            supabase.table('products').insert({'name':name,'price':price,'active':True,'created_at':ts,'updated_at':ts}).execute()
    for name in FIXED_CUSTOMERS:
        rows = supabase.table('customers').select('id').ilike('name',name).limit(1).execute().data or []
        if rows:
            supabase.table('customers').update({'active':True,'updated_at':ts}).eq('id',rows[0]['id']).execute()
        else:
            supabase.table('customers').insert({'name':name,'phone':'','active':True,'created_at':ts,'updated_at':ts}).execute()

def get_customers():
    return supabase.table('customers').select('*').eq('active',True).order('name').execute().data or []

def get_all_customers():
    return supabase.table('customers').select('*').order('name').execute().data or []

def add_customer(name, phone=''):
    name, phone = str(name or '').strip(), str(phone or '').strip()
    if not name: raise ValueError('Customer name is required.')
    ts = now_str()
    if phone:
        rows = supabase.table('customers').select('id').eq('phone',phone).limit(1).execute().data or []
        if rows:
            cid = rows[0]['id']; supabase.table('customers').update({'name':name,'active':True,'updated_at':ts}).eq('id',cid).execute(); return cid
    rows = supabase.table('customers').select('id').ilike('name',name).limit(1).execute().data or []
    if rows:
        cid=rows[0]['id']
        if phone: supabase.table('customers').update({'phone':phone,'active':True,'updated_at':ts}).eq('id',cid).execute()
        return cid
    data = supabase.table('customers').insert({'name':name,'phone':phone,'active':True,'created_at':ts,'updated_at':ts}).execute().data or []
    if not data: raise RuntimeError('Customer could not be created.')
    return data[0]['id']

def get_products(active_only=True):
    q = supabase.table('products').select('*').order('name')
    if active_only: q=q.eq('active',True)
    return q.execute().data or []

def get_products_for_sale(sale_id):
    products = supabase.table('products').select('*').order('name').execute().data or []
    active = [p for p in products if p.get('active')]
    items = supabase.table('sale_items').select('*').eq('sale_id',sale_id).order('id').execute().data or []
    qty={i['product_id']:i['quantity'] for i in items}
    out=[{'id':p['id'],'name':p['name'],'price':float(p['price']),'active':p['active'],'quantity':qty.get(p['id'],0)} for p in active]
    ids={x['id'] for x in out}
    for i in items:
        p=next((p for p in products if p['id']==i['product_id']),None)
        if p and p['id'] not in ids:
            out.append({'id':p['id'],'name':p['name'],'price':float(i['price']),'active':p['active'],'quantity':i['quantity']})
    return out

def add_product(name, price):
    name, price=str(name or '').strip(), float(price)
    if not name: raise ValueError('Item name is required.')
    if price<=0: raise ValueError('Price must be greater than 0.')
    ts=now_str(); rows=supabase.table('products').select('id').ilike('name',name).limit(1).execute().data or []
    if rows:
        pid=rows[0]['id']; supabase.table('products').update({'price':price,'active':True,'updated_at':ts}).eq('id',pid).execute(); return pid
    data=supabase.table('products').insert({'name':name,'price':price,'active':True,'created_at':ts,'updated_at':ts}).execute().data or []
    if not data: raise RuntimeError('Item could not be created.')
    return data[0]['id']

def update_product(product_id,name,price):
    name, price=str(name or '').strip(),float(price)
    if not name: raise ValueError('Item name is required.')
    if price<=0: raise ValueError('Price must be greater than 0.')
    supabase.table('products').update({'name':name,'price':price,'updated_at':now_str()}).eq('id',product_id).execute()

def set_product_active(product_id,active):
    supabase.table('products').update({'active':bool(active),'updated_at':now_str()}).eq('id',product_id).execute()

def calculate_status(total,received):
    if received<=0: return 'Unpaid'
    if received>=total: return 'Paid'
    return 'Partially Paid'

def create_sale(customer_id,items,received_amount,payment_method=None,note=''):
    total=sum(float(x['subtotal']) for x in items); received_amount=float(received_amount)
    if total<=0: raise ValueError('Sale total must be greater than 0.')
    if received_amount<0: raise ValueError('Payment cannot be negative.')
    if received_amount>total: raise ValueError('Payment cannot be greater than total.')
    if not items: raise ValueError('At least one item is required.')
    if customer_id is not None:
        rows=supabase.table('sales').select('id,created_at').eq('customer_id',customer_id).eq('sale_status','ACTIVE').order('id',desc=True).limit(1).execute().data or []
        if rows:
            d=_dt(rows[0].get('created_at'))
            if d:
                sec=(datetime.now(IST)-d).total_seconds()
                if 0<=sec<30:
                    wait=max(1,int(30-sec)); raise ValueError(f'A sale for this customer was just saved. Please wait {wait} seconds before creating another sale for the same customer.')
    ts=now_str(); status=calculate_status(total,received_amount); sale_id=None
    try:
        data=supabase.table('sales').insert({'customer_id':customer_id,'total':total,'payment_status':status,'payment_method':payment_method,'sale_status':'ACTIVE','created_at':ts,'updated_at':ts,'notes':str(note or '')}).execute().data or []
        if not data: raise RuntimeError('Sale could not be created.')
        sale_id=data[0]['id']
        rows=[{'sale_id':sale_id,'product_id':x['product_id'],'quantity':int(x['quantity']),'price':float(x['price']),'subtotal':float(x['subtotal'])} for x in items]
        supabase.table('sale_items').insert(rows).execute()
        if received_amount>0:
            supabase.table('payments').insert({'sale_id':sale_id,'amount':received_amount,'method':payment_method or 'Cash','note':'Initial payment','created_at':ts}).execute()
        return sale_id
    except Exception:
        if sale_id is not None:
            for table,col in [('payments','sale_id'),('sale_items','sale_id'),('sales','id')]:
                try: supabase.table(table).delete().eq(col,sale_id).execute()
                except Exception: pass
        raise

def get_sales(period='All Time',search=''):
    sales=supabase.table('sales').select('*').order('created_at',desc=True).order('id',desc=True).execute().data or []
    customers=get_all_customers(); cmap={c['id']:c for c in customers}
    payments=supabase.table('payments').select('sale_id,amount').execute().data or []
    received={}
    for p in payments: received[p['sale_id']]=received.get(p['sale_id'],0)+float(p.get('amount') or 0)
    today=datetime.now(IST).date(); term=str(search or '').strip().lower(); out=[]
    for s in sales:
        if s.get('sale_status')!='ACTIVE': continue
        d=_dt(s.get('created_at'))
        if not d: continue
        sd=d.date()
        if period=='Today' and sd!=today: continue
        if period=='This Week' and sd < today-timedelta(days=today.weekday()): continue
        if period=='This Month' and (sd.year,sd.month)!=(today.year,today.month): continue
        c=cmap.get(s.get('customer_id'),{}); name=c.get('name','Unknown'); phone=c.get('phone','') or ''
        if term and term not in f'{name} {phone} {s.get("id","")}'.lower(): continue
        total=float(s.get('total') or 0); rec=float(received.get(s['id'],0))
        out.append({'id':s['id'],'customer_id':s.get('customer_id'),'customer_name':name,'phone':phone,'total':total,'received':rec,'remaining':max(total-rec,0),'status':s.get('payment_status','Unpaid'),'method':s.get('payment_method') or '-','sale_status':s.get('sale_status','ACTIVE'),'created_at':s.get('created_at',''),'updated_at':s.get('updated_at','')})
    return out

def get_sale(sale_id):
    rows=supabase.table('sales').select('*').eq('id',sale_id).limit(1).execute().data or []
    if not rows: return None
    s=rows[0]; crows=supabase.table('customers').select('name,phone').eq('id',s.get('customer_id')).limit(1).execute().data or []
    c=crows[0] if crows else {}; pays=supabase.table('payments').select('amount').eq('sale_id',sale_id).execute().data or []
    s['customer_name']=c.get('name','Unknown'); s['phone']=c.get('phone','') or ''; s['received']=sum(float(p.get('amount') or 0) for p in pays)
    return s

def get_sale_items(sale_id):
    rows=supabase.table('sale_items').select('*').eq('sale_id',sale_id).order('id').execute().data or []
    products=supabase.table('products').select('id,name').execute().data or []; pmap={p['id']:p['name'] for p in products}
    return [{'id':r['id'],'product_id':r['product_id'],'name':pmap.get(r['product_id'],'Unknown Item'),'quantity':r['quantity'],'price':float(r['price'] or 0),'subtotal':float(r['subtotal'] or 0)} for r in rows]

def get_payment_history(sale_id):
    return supabase.table('payments').select('id,amount,method,note,created_at').eq('sale_id',sale_id).order('created_at',desc=True).order('id',desc=True).execute().data or []

def mark_sale_paid(sale_id,method='Cash'):
    sale=get_sale(sale_id)
    if not sale: raise ValueError('Sale not found.')
    if sale.get('sale_status')!='ACTIVE': raise ValueError('This sale is not active.')
    rem=max(float(sale.get('total') or 0)-float(sale.get('received') or 0),0); ts=now_str()
    if rem<=0:
        supabase.table('sales').update({'payment_status':'Paid','updated_at':ts}).eq('id',sale_id).execute(); return 0
    supabase.table('payments').insert({'sale_id':sale_id,'amount':rem,'method':method or 'Cash','note':'Marked as Paid','created_at':ts}).execute()
    supabase.table('sales').update({'payment_status':'Paid','payment_method':method or 'Cash','updated_at':ts}).eq('id',sale_id).execute()
    return rem

def add_payment(sale_id,amount,method,note=''):
    amount=float(amount)
    if amount<=0: raise ValueError('Payment amount must be greater than 0.')
    sale=get_sale(sale_id)
    if not sale: raise ValueError('Sale not found.')
    if sale.get('sale_status')!='ACTIVE': raise ValueError('Sale is not active.')
    total=float(sale.get('total') or 0); rec=float(sale.get('received') or 0); rem=max(total-rec,0)
    if amount>rem: raise ValueError(f'Only ₹{rem:.2f} is remaining.')
    ts=now_str(); supabase.table('payments').insert({'sale_id':sale_id,'amount':amount,'method':method,'note':note or '','created_at':ts}).execute()
    supabase.table('sales').update({'payment_status':calculate_status(total,rec+amount),'payment_method':method,'updated_at':ts}).eq('id',sale_id).execute()

def cancel_sale(sale_id):
    ts=now_str(); supabase.table('sales').update({'sale_status':'CANCELLED','payment_status':'Cancelled','cancelled_at':ts,'updated_at':ts}).eq('id',sale_id).execute()

def reset_all_data():
    try:
        supabase.rpc('reset_coconut_pos').execute()
    except Exception as e:
        raise RuntimeError('Supabase reset function is not installed yet. Run reset_coconut_pos.sql in Supabase first.') from e
    init_database()

def create_daily_backup():
    return None
