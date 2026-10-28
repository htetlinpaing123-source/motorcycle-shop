import streamlit as st
import sqlite3

# --- (၀) Database ဇယားများ တည်ဆောက်ခြင်း ---
def init_db():
    conn = sqlite3.connect('motorcycle_shop.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_model TEXT NOT NULL,
        engine_power TEXT,
        color TEXT,
        chassis_no TEXT UNIQUE,
        engine_no TEXT UNIQUE,
        buying_price REAL,
        selling_price REAL,
        stock_status TEXT DEFAULT 'Available'
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nrc_no TEXT,
        phone TEXT,
        address TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
        invoice_no INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        item_id INTEGER,
        payment_type TEXT,
        total_amount REAL,
        paid_amount REAL,
        sale_date DATE DEFAULT (date('now', 'localtime'))
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS installments (
        installment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no INTEGER,
        bank_name TEXT,
        monthly_due REAL,
        due_date DATE,
        status TEXT DEFAULT 'Unpaid'
    )''')
    conn.commit()
    conn.close()

init_db()

# --- (၁) Database မှ အချက်အလက်များ ဆွဲထုတ်ခြင်း ---
def get_available_motorcycles():
    conn = sqlite3.connect('motorcycle_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, brand_model, chassis_no FROM inventory WHERE stock_status = 'Available'")
    motos = cursor.fetchall()
    conn.close()
    return {f"ID:{m[0]} | {m[1]} ({m[2]})": m[0] for m in motos}

def get_customers():
    conn = sqlite3.connect('motorcycle_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, name, phone FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return {f"ID:{c[0]} | {c[1]} ({c[2]})": c[0] for c in customers}

def get_installment_invoices():
    conn = sqlite3.connect('motorcycle_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT s.invoice_no, c.name FROM sales s JOIN customers c ON s.customer_id = c.customer_id WHERE s.payment_type LIKE '%Installment%'")
    invoices = cursor.fetchall()
    conn.close()
    return {f"Inv:{inv[0]} | {inv[1]}": inv[0] for inv in invoices}

# --- (၂) Streamlit UI ဒီဇိုင်း ---
st.set_page_config(page_title="ဆိုင်ကယ်အရောင်းဆိုင် စီမံခန့်ခွဲမှု စနစ်", layout="centered")

st.title("🏍️ ဆိုင်ကယ်အရောင်းဆိုင် စီမံခန့်ခွဲမှု စနစ်")

menu = st.sidebar.selectbox("မီနူး ရွေးချယ်ရန်", ["ဆိုင်ကယ်စာရင်း", "ဖောက်သည်စာရင်း", "အရောင်း / ဘေလ်ထုတ်", "အရစ်ကျ မှတ်တမ်း", "အစီရင်ခံစာ (Report)"])

# --- ဆိုင်ကယ်စာရင်း Tab ---
if menu == "ဆိုင်ကယ်စာရင်း":
    st.header("📦 ဆိုင်ကယ်အသစ် ထည့်သွင်းခြင်း")
    with st.form("moto_form"):
        brand = st.text_input("မော်ဒယ် (Brand & Model)")
        power = st.text_input("အင်ဂျင်ပါဝါ (Engine Power)")
        color = st.text_input("အရောင် (Color)")
        chassis = st.text_input("ဘောင်နံပါတ် (Chassis No)")
        engine = st.text_input("အင်ဂျင်နံပါတ် (Engine No)")
        buy_price = st.number_input("ဝယ်ရင်းဈေး (Buying Price)", min_value=0.0, step=1000.0)
        sell_price = st.number_input("ရောင်းဈေး (Selling Price)", min_value=0.0, step=1000.0)
        
        submit_moto = st.form_submit_button("ဆိုင်ကယ် စာရင်းသွင်းမည်")
        if submit_moto:
            if brand and chassis:
                try:
                    conn = sqlite3.connect('motorcycle_shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO inventory (brand_model, engine_power, color, chassis_no, engine_no, buying_price, selling_price)
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (brand, power, color, chassis, engine, buy_price, sell_price))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{brand}' ကို အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ။")
                except Exception as e:
                    st.error(f"❌ အမှား: {e}")
            else:
                st.warning("⚠️ ကျေးဇူးပြု၍ မော်ဒယ်နှင့် ဘောင်နံပါတ်ကို ထည့်သွင်းပါ။")

# --- ဖောက်သည်စာရင်း Tab ---
elif menu == "ဖောက်သည်စာရင်း":
    st.header("👥 ဖောက်သည်အသစ် ထည့်သွင်းခြင်း")
    with st.form("cust_form"):
        name = st.text_input("အမည်")
        phone = st.text_input("ဖုန်းနံပါတ်")
        nrc = st.text_input("မှတ်ပုံတင်နံပါတ် (NRC)")
        address = st.text_input("လိပ်စာ")
        
        submit_cust = st.form_submit_button("ဖောက်သည် စာရင်းသွင်းမည်")
        if submit_cust:
            if name:
                try:
                    conn = sqlite3.connect('motorcycle_shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO customers (name, nrc_no, phone, address) VALUES (?, ?, ?, ?)''', (name, nrc, phone, address))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ ဖောက်သည် '{name}' ကို အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ။")
                except Exception as e:
                    st.error(f"❌ အမှား: {e}")
            else:
                st.warning("⚠️ ကျေးဇူးပြု၍ ဖောက်သည်အမည် ထည့်သွင်းပါ။")

# --- အရောင်း / ဘေလ်ထုတ် Tab ---
elif menu == "အရောင်း / ဘေလ်ထုတ်":
    st.header("💰 အရောင်းစာရင်းနှင့် ဘေလ်ထုတ်ခြင်း")
    
    customers = get_customers()
    motorcycles = get_available_motorcycles()
    
    if not customers:
        st.warning("⚠️ ကျေးဇူးပြု၍ ပထမဆုံး ဖောက်သည်စာရင်း အရင်သွင်းပါ။")
    if not motorcycles:
        st.warning("⚠️ ရောင်းရန် ဆိုင်ကယ် လက်ကျန် မရှိသေးပါ။")
        
    if customers and motorcycles:
        with st.form("sale_form"):
            selected_cust = st.selectbox("ဖောက်သည် ရွေးပါ", list(customers.keys()))
            selected_moto = st.selectbox("ဆိုင်ကယ် ရွေးပါ", list(motorcycles.keys()))
            pay_type = st.selectbox("ငွေချေစနစ်", ["Cash (ငွေသား)", "Bank Transfer (ဘဏ်)", "Installment (အရစ်ကျ)"])
            total_amt = st.number_input("ကျသင့်ငွေ", min_value=0.0, step=1000.0)
            paid_amt = st.number_input("ပေးသွင်းငွေ", min_value=0.0, step=1000.0)
            
            submit_sale = st.form_submit_button("အရောင်းစာရင်းသွင်းမည်")
            if submit_sale:
                cust_id = customers[selected_cust]
                moto_id = motorcycles[selected_moto]
                try:
                    conn = sqlite3.connect('motorcycle_shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO sales (customer_id, item_id, payment_type, total_amount, paid_amount)
                                      VALUES (?, ?, ?, ?, ?)''', (cust_id, moto_id, pay_type, total_amt, paid_amt))
                    invoice_no = cursor.lastrowid
                    cursor.execute("UPDATE inventory SET stock_status = 'Sold' WHERE item_id = ?", (moto_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ အောင်မြင်ပါသည်။ ဘေလ်နံပါတ်: {invoice_no} ဖြင့် အရောင်းမှတ်တမ်း တင်ပြီးပါပြီ။")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ အမှား: {e}")

# --- အရစ်ကျ မှတ်တမ်း Tab ---
elif menu == "အရစ်ကျ မှတ်တမ်း":
    st.header("📅 အရစ်ကျ ငွေသွင်းရန် မှတ်တမ်း")
    
    invoices = get_installment_invoices()
    if not invoices:
        st.warning("⚠️ အရစ်ကျစနစ်ဖြင့် ရောင်းချထားသော ဘေလ်နံပါတ် မရှိသေးပါ။")
    else:
        with st.form("inst_form"):
            selected_inv = st.selectbox("အရစ်ကျ ဘေလ်နံပါတ် ရွေးပါ", list(invoices.keys()))
            bank_name = st.text_input("ဘဏ်/ကုမ္ပဏီ အမည်")
            monthly_due = st.number_input("လစဉ်သွင်းငွေ", min_value=0.0, step=1000.0)
            due_date = st.text_input("ငွေသွင်းရမည့်ရက် (ဥပမာ - 2026-12-01)")
            
            submit_inst = st.form_submit_button("အရစ်ကျ မှတ်တမ်းသွင်းမည်")
            if submit_inst:
                inv_no = invoices[selected_inv]
                try:
                    conn = sqlite3.connect('motorcycle_shop.db')
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO installments (invoice_no, bank_name, monthly_due, due_date)
                                      VALUES (?, ?, ?, ?)''', (inv_no, bank_name, monthly_due, due_date))
                    conn.commit()
                    conn.close()
                    st.success("✅ အရစ်ကျမှတ်တမ်း အောင်မြင်စွာ သွင်းပြီးပါပြီ။")
                except Exception as e:
                    st.error(f"❌ အမှား: {e}")

# --- အစီရင်ခံစာ Tab ---
elif menu == "အစီရင်ခံစာ (Report)":
    st.header("📊 အရောင်း အကျဉ်းချုပ် အစီရင်ခံစာ")
    
    if st.button("📊 စာရင်းများကို တွက်ချက်ပြသပါ"):
        try:
            conn = sqlite3.connect('motorcycle_shop.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(total_amount), COUNT(invoice_no) FROM sales")
            sales_data = cursor.fetchone()
            total_revenue = sales_data[0] if sales_data[0] else 0
            total_sales_count = sales_data[1] if sales_data[1] else 0
            
            cursor.execute("SELECT COUNT(item_id) FROM inventory WHERE stock_status = 'Available'")
            stock_count = cursor.fetchone()[0]
            conn.close()
            
            st.metric("စုစုပေါင်း ရောင်းရစီးရေ", f"{total_sales_count} စီး")
            st.metric("စုစုပေါင်း ရောင်းရငွေ", f"{total_revenue:,.0f} ကျပ်")
            st.metric("လက်ကျန် ဆိုင်ကယ်စီးရေ", f"{stock_count} စီး")
        except Exception as e:
            st.error(f"❌ အမှား: {e}")