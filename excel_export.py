from pathlib import Path
from datetime import datetime
import xlsxwriter
from database import now_str, get_all_customers, get_products, get_sale_items, supabase

BASE_DIR=Path(__file__).resolve().parent
EXCEL_FILE=BASE_DIR/'coconut_sales.xlsx'

def _sales():
    return supabase.table('sales').select('*').order('created_at',desc=True).order('id',desc=True).execute().data or []

def _payments():
    return supabase.table('payments').select('*').order('created_at',desc=True).order('id',desc=True).execute().data or []

def export_all_to_excel():
    sr=_sales(); pr=_payments(); cs=get_all_customers(); ps=get_products(False); cmap={c['id']:c for c in cs}
    sales=[]
    for s in sr:
        c=cmap.get(s.get('customer_id'),{}); rec=sum(float(p.get('amount') or 0) for p in pr if p.get('sale_id')==s.get('id'))
        sales.append({'id':s.get('id'),'created_at':s.get('created_at') or '','total':float(s.get('total') or 0),'payment_status':s.get('payment_status') or '','payment_method':s.get('payment_method') or '','sale_status':s.get('sale_status') or '','customer':c.get('name','Unknown'),'phone':c.get('phone','') or '','received':rec})
    pays=[]
    for p in pr:
        s=next((x for x in sr if x.get('id')==p.get('sale_id')),{}); c=cmap.get(s.get('customer_id'),{})
        pays.append({'id':p.get('id'),'sale_id':p.get('sale_id'),'created_at':p.get('created_at') or '','amount':float(p.get('amount') or 0),'method':p.get('method') or '','note':p.get('note') or '','customer':c.get('name','Unknown')})
    cust=[]
    for c in cs:
        active_ids={s.get('id') for s in sr if s.get('customer_id')==c.get('id') and s.get('sale_status')=='ACTIVE'}
        purchase=sum(float(s.get('total') or 0) for s in sr if s.get('customer_id')==c.get('id') and s.get('sale_status')=='ACTIVE')
        paid=sum(float(p.get('amount') or 0) for p in pr if p.get('sale_id') in active_ids)
        cust.append({'id':c.get('id'),'name':c.get('name',''),'phone':c.get('phone','') or '','active':c.get('active'),'total_purchase':purchase,'total_paid':paid})
    items={s.get('id'):get_sale_items(s.get('id')) for s in sr}
    try:
        _write(EXCEL_FILE,sales,pays,cust,ps,items); return EXCEL_FILE
    except PermissionError:
        f=BASE_DIR/f'coconut_sales_{datetime.now():%Y%m%d_%H%M%S}.xlsx'; _write(f,sales,pays,cust,ps,items); return f

def _write(path,sales,pays,customers,products,items):
    wb=xlsxwriter.Workbook(str(path)); title=wb.add_format({'bold':True,'font_size':16}); header=wb.add_format({'bold':True,'border':1,'bg_color':'#DDEBDD'}); normal=wb.add_format({'border':1}); money=wb.add_format({'border':1,'num_format':'₹#,##0.00'})
    sh=wb.add_worksheet('Sales'); sh.merge_range('A1:J1','Coconut Business - Sales',title); hs=['Sale ID','Date & Time','Customer','Phone','Items','Total','Received','Remaining','Payment Status','Sale Status']
    for c,v in enumerate(hs): sh.write(2,c,v,header)
    for r,s in enumerate(sales,3):
        rem=max(s['total']-s['received'],0); vals=[s['id'],s['created_at'],s['customer'],s['phone'],'\n'.join(f"{i['name']} × {i['quantity']} = ₹{i['subtotal']:.2f}" for i in items.get(s['id'],[])),s['total'],s['received'],rem,s['payment_status'],s['sale_status']]
        for c,v in enumerate(vals): sh.write(r,c,v,money if c in (5,6,7) else normal)
    sh.set_column('A:A',10); sh.set_column('B:B',21); sh.set_column('C:C',24); sh.set_column('D:D',17); sh.set_column('E:E',42); sh.set_column('F:H',15); sh.set_column('I:J',19)
    sh=wb.add_worksheet('Payments'); sh.merge_range('A1:G1','Payment History',title); hs=['Payment ID','Sale ID','Date & Time','Customer','Amount','Method','Note']
    for c,v in enumerate(hs): sh.write(2,c,v,header)
    for r,p in enumerate(pays,3):
        for c,v in enumerate([p['id'],p['sale_id'],p['created_at'],p['customer'],p['amount'],p['method'],p['note']]): sh.write(r,c,v,money if c==4 else normal)
    sh.set_column('A:B',11); sh.set_column('C:C',21); sh.set_column('D:D',24); sh.set_column('E:E',15); sh.set_column('F:F',15); sh.set_column('G:G',28)
    sh=wb.add_worksheet('Customers'); sh.merge_range('A1:G1','Customer Register',title); hs=['ID','Customer','Phone','Active','Total Purchase','Total Paid','Outstanding']
    for c,v in enumerate(hs): sh.write(2,c,v,header)
    for r,cust in enumerate(customers,3):
        vals=[cust['id'],cust['name'],cust['phone'],'Yes' if cust['active'] else 'No',cust['total_purchase'],cust['total_paid'],max(cust['total_purchase']-cust['total_paid'],0)]
        for c,v in enumerate(vals): sh.write(r,c,v,money if c>=4 else normal)
    sh.set_column('A:A',10); sh.set_column('B:B',24); sh.set_column('C:C',17); sh.set_column('D:D',12); sh.set_column('E:G',18)
    sh=wb.add_worksheet('Products'); sh.merge_range('A1:F1','Product Register',title); hs=['ID','Item','Price','Active','Created','Updated']
    for c,v in enumerate(hs): sh.write(2,c,v,header)
    for r,p in enumerate(products,3):
        for c,v in enumerate([p['id'],p['name'],float(p['price'] or 0),'Yes' if p['active'] else 'No',p.get('created_at') or '',p.get('updated_at') or '']): sh.write(r,c,v,money if c==2 else normal)
    sh.set_column('A:A',10); sh.set_column('B:B',25); sh.set_column('C:C',15); sh.set_column('D:D',12); sh.set_column('E:F',22)
    sh=wb.add_worksheet('Summary'); sh.merge_range('A1:B1','Coconut POS Summary',title); active=[s for s in sales if s['sale_status']=='ACTIVE']; ts=sum(s['total'] for s in active); tr=sum(s['received'] for s in active); sh.write('A3','Generated At',header); sh.write('B3',now_str(),normal); sh.write('A5','Total Sales',header); sh.write('B5',ts,money); sh.write('A6','Total Received',header); sh.write('B6',tr,money); sh.write('A7','Total Pending',header); sh.write('B7',max(ts-tr,0),money); sh.write('A8','Transactions',header); sh.write('B8',len(active),normal); sh.set_column('A:A',24); sh.set_column('B:B',22); wb.close()

def reset_excel_workbook():
    tmp=BASE_DIR/'coconut_sales_reset_tmp.xlsx'; products=[{'id':1,'name':'Coconut','price':20,'active':True,'created_at':now_str(),'updated_at':now_str()},{'id':2,'name':'Oti Saman','price':2,'active':True,'created_at':now_str(),'updated_at':now_str()},{'id':3,'name':'Tel','price':5,'active':True,'created_at':now_str(),'updated_at':now_str()},{'id':4,'name':'Sadi','price':50,'active':True,'created_at':now_str(),'updated_at':now_str()}]
    try: _write(tmp,[],[],[],products,{}) ; tmp.replace(EXCEL_FILE)
    finally:
        if tmp.exists():
            try: tmp.unlink()
            except PermissionError: pass
    return EXCEL_FILE

def get_received(sale_id):
    return sum(float(x.get('amount') or 0) for x in (supabase.table('payments').select('amount').eq('sale_id',sale_id).execute().data or []))
