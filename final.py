# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

import warnings
warnings.filterwarnings('ignore')

# +
try:
    import streamlit as st
    import sqlite3
    from sqlite3 import Error
    import pandas as pd
    from datetime import datetime
    from streamlit_option_menu import option_menu
    import subprocess
    import sys
    import plotly.express as px
    import matplotlib.pyplot as plt
    
    
    def create_connection():
        conn = None
        try:
            conn = sqlite3.connect('exp_track.db')
        except Error as e:
            print(e)
        return conn
    
   
    def create_table(conn):
        try:
            c = conn.cursor()
          
            c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)''')
            
            
            c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, date TEXT NOT NULL, amount REAL NOT NULL, payee TEXT NOT NULL, category TEXT, account TEXT, note TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS payee (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS category (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
    
           
            c.execute('''CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY, date TEXT NOT NULL, amount REAL NOT NULL, payer TEXT NOT NULL, categoryI TEXT, account TEXT, note TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS payer (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS categoryI (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
            conn.commit()
        except Error as e:
            print(e)
    
    
    def register_user(conn, username, password):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except Error as e:
            print(e)
    
    def authenticate_user(conn, username, password):
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            return c.fetchone() is not None
        except Error as e:
            print(e)
            return False
        
    
    # def create_table(conn):
    #     try:
    #         c = conn.cursor()
            
    #         c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, date text NOT NULL, amount numeric(5,2) NOT NULL, payee text NOT NULL, category text, account text, note text)''')
    #         c.execute(
    #             '''CREATE TABLE IF NOT EXISTS payee (id INTEGER PRIMARY KEY, name text NOT NULL)''')
    #         c.execute(
    #             '''CREATE TABLE IF NOT EXISTS category (id INTEGER PRIMARY KEY, name text NOT NULL)''')
    #         c.execute(
    #             '''CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY, name text NOT NULL)''')
    #         c.execute('''CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY, date text NOT NULL, amount numeric(5,2) NOT NULL, payer text NOT NULL, categoryI text, account text, note text)''')
    #         c.execute(
    #             '''CREATE TABLE IF NOT EXISTS payer (id INTEGER PRIMARY KEY, name text NOT NULL)''')
    #         c.execute(
    #             '''CREATE TABLE IF NOT EXISTS categoryI (id INTEGER PRIMARY KEY, name text NOT NULL)''')
    #         conn.commit()
    #     except Error as e:
    #         print(e)
    
   
    
    
    def add_expense(conn, date, amount, payee, category, account, note):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO expenses (date, amount, payee, category, account, note) VALUES (?, ?, ?, ?, ?, ?)",
                      (date, amount, payee, category, account, note))
            conn.commit()
        except Error as e:
            print(e)
    
    
    
    def add_payee(conn, name):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO payee (name) VALUES (?)", (name,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def add_category(conn, name):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO category (name) VALUES (?)", (name,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def add_account(conn, name):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO account (name) VALUES (?)", (name,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def get_payees(conn):
        try:
            c = conn.cursor()
            c.execute("SELECT name FROM payee")
            rows = c.fetchall()
            names = [row[0] for row in rows]
            return names
        except Error as e:
            print(e)
    
    
    def get_categories(conn):
        try:
            c = conn.cursor()
            c.execute("SELECT name FROM category")
            rows = c.fetchall()
            names = [row[0] for row in rows]
            return names
        except Error as e:
            print(e)
    
    
    def get_accounts(conn):
        try:
            c = conn.cursor()
            c.execute("SELECT name FROM account")
            rows = c.fetchall()
            names = [row[0] for row in rows]
            return names
        except Error as e:
            print(e)
    
    
    def get_expenses_by_month(conn, month):
        try:
            c = conn.cursor()
            query = '''
            SELECT e.id, e.date, e.amount, p.name as payee, c.name as category, a.name as account, e.note
            FROM expenses e
            JOIN payee p ON e.payee = p.name
            JOIN category c ON e.category = c.name
            JOIN account a ON e.account = a.name
            WHERE strftime('%m', e.date) = ?
            '''
            c.execute(query, (month,))
            rows = c.fetchall()
            df = pd.DataFrame(rows, columns=['ID', 'Date', 'Amount', 'Payee', 'Category', 'Account', 'Note'])
            return df
        except Error as e:
            print(e)
    
    
    def delete_expense(conn, id):
        try:
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE id=?", (id,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def delete_payee(conn, id):
        try:
            c = conn.cursor()
            c.execute("DELETE FROM payee WHERE id=?", (id,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def delete_category(conn, id):
        try:
            c = conn.cursor()
            c.execute("DELETE FROM category WHERE id=?", (id,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def export_expenses_to_csv(conn):
        try:
            df = pd.read_sql_query("SELECT * FROM expenses", conn)
            df.to_csv('expenses.csv', index=False)
        except Error as e:
            print(e)
    
    
    def add_income(conn, date, amount, payer, categoryI, account, note):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO income (date, amount, payer, categoryI, account, note) VALUES (?, ?, ?, ?, ?, ?)",
                      (date, amount, payer, categoryI, account, note))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def add_payer(conn, name):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO payer (name) VALUES (?)", (name,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def add_categoryI(conn, name):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO categoryI (name) VALUES (?)", (name,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def get_payers(conn):
        try:
            c = conn.cursor()
            c.execute("SELECT name FROM payer")
            rows = c.fetchall()
            names = [row[0] for row in rows]
            return names
        except Error as e:
            print(e)
    
    
    def get_categoryI(conn):
        try:
            c = conn.cursor()
            c.execute("SELECT name FROM categoryI")
            rows = c.fetchall()
            names = [row[0] for row in rows]
            return names
        except Error as e:
            print(e)
    
    
    def get_income_by_month(conn, month):
        try:
            c = conn.cursor()
            query = '''
            SELECT i.id, i.date, i.amount, p.name as payer, ci.name as category, a.name as account, i.note
            FROM income i
            JOIN payer p ON i.payer = p.name
            JOIN categoryI ci ON i.categoryI = ci.name
            JOIN account a ON i.account = a.name
            WHERE strftime('%m', i.date) = ?
            '''
            c.execute(query, (month,))
            rows = c.fetchall()
            df = pd.DataFrame(rows, columns=['ID', 'Date', 'Amount', 'Payer', 'Category', 'Account', 'Note'])
            return df
        except Error as e:
            print(e)
    
    
    
    def delete_income(conn, id):
        try:
            c = conn.cursor()
            c.execute("DELETE FROM income WHERE id=?", (id,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def delete_payer(conn, id):
        try:
            c = conn.cursor()
            c.execute("DELETE FROM payer WHERE id=?", (id,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def delete_categoryI(conn, id):
        try:
            c = conn.cursor()
            c.execute("DELETE FROM categoryI WHERE id=?", (id,))
            conn.commit()
        except Error as e:
            print(e)
    
    
    def export_expenses_to_csv(conn):
        try:
            query = '''
            SELECT e.id, e.date, e.amount, p.name as payee, c.name as category, a.name as account, e.note
            FROM expenses e
            JOIN payee p ON e.payee = p.name
            JOIN category c ON e.category = c.name
            JOIN account a ON e.account = a.name
            '''
            df = pd.read_sql_query(query, conn)
            df.to_csv('expenses.csv', index=False)
        except Error as e:
            print(e)
    
       
        
    
    def reset_session():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    conn = create_connection()
    create_table(conn)
    
    st.set_page_config(page_title='Finance Tracker', page_icon=':coin:', layout='wide')
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        auth_option = st.sidebar.radio("Login/Register", ["Login", "Register"])
    
        if auth_option == "Register":
            st.subheader("Register")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
    
            if st.button("Register"):
                if new_password == confirm_password:
                    register_user(conn, new_username, new_password)
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Passwords do not match.")
    
        elif auth_option == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
    
            if st.button("Login"):
                if authenticate_user(conn, username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.success(f"Welcome {username}!")
                else:
                    st.error("Invalid username or password.")
    else:
        st.sidebar.write(f"Logged in as: {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            reset_session()
            st.experimental_rerun()
    
        menu_tabs = ['Expense', 'Income', 'Summary']
        selected_tab = option_menu(
            menu_title=None,
            options=menu_tabs,
            icons=['pencil-fill', 'pencil-fill', 'bar-chart-fill'],
            orientation='horizontal'
        )
    
    
        html_code = """
        <style>
        div.stButton > button:first-child {
            background-color: #ff4b4b;
            color: white;
        }
        </style>
        """
        st.markdown(html_code, unsafe_allow_html=True)
    
        st.markdown("""
        <style>
            .streamlit-expanderHeader > div:nth-child(1) > p:nth-child(1) > strong:nth-child(1) {
                font-size: 24px;
                color: red;
            }
        </style>
        """, unsafe_allow_html=True)
        
        if selected_tab == "Expense":
            date = st.date_input('Date', value=None)
            amount = st.number_input('Amount ($)', value=0.00)
            payee = st.selectbox('Payee', get_payees(conn))
            category = st.selectbox('Category', get_categories(conn))
            account = st.selectbox('Account', get_accounts(conn))
            note = st.text_area('Note', max_chars=150)
    
            if st.button('Submit Expense'):
                add_expense(conn, date, amount, payee, category, account, note)
                st.success('Expense added!')
                import streamlit as st
                st.experimental_rerun() 
    
            st.subheader('View Expenses by Month')
            month_options = ['01', '02', '03', '04', '05',
                            '06', '07', '08', '09', '10', '11', '12']
            current_month = datetime.now().strftime('%m')
            selected_month = st.selectbox(
                'Month', month_options, index=month_options.index(current_month))
    
            if st.button('View Expenses'):
                df = get_expenses_by_month(conn, selected_month)
                st.dataframe(df)
                st.write('Total: $', df['Amount'].sum())
    
            with st.expander("**EXPENSE FUNCTIONS** - *Add New Payee, Category, Account & to CSV*"):
                st.subheader('Add Payee')
                new_payee = st.text_input('New Payee')
                if st.button('Add Payee'):
                    if new_payee:
                        add_payee(conn, new_payee)
                        st.success('Payee added!')
                        import streamlit as st
                        st.experimental_rerun() 
    
                st.subheader('Add Category')
                new_category = st.text_input('New Category')
                if st.button('Add Category'):
                    add_category(conn, new_category)
                    st.success('Category added!')
    
                st.subheader('Add Account')
                new_account = st.text_input('New Account')
                if st.button('Add Account'):
                    add_account(conn, new_account)
                    st.success('Account added!')
    
                if st.button('Export Expenses to CSV'):
                    export_expenses_to_csv(conn)
                    subprocess.run([f"{sys.executable}", fileRunE])
                    st.success('Expense data exported to expenses.csv')
    
        elif selected_tab == "Income":
            date = st.date_input('Date', value=None)
            amount = st.number_input('Amount ($)', value=0.0)
            payer = st.selectbox('Payer', get_payers(conn))
            categoryI = st.selectbox('Income Category', get_categoryI(conn))
            account = st.selectbox('Account', get_accounts(conn))
            note = st.text_area('Note', max_chars=150)
    
            if st.button('Submit'):
                add_income(conn, date.strftime('%Y-%m-%d'),
                        amount, payer, categoryI, account, note)
                st.success('Income added!')
                st.experimental_rerun()
    
            st.subheader('View Income by Month')
            month_options = ['01', '02', '03', '04', '05',
                            '06', '07', '08', '09', '10', '11', '12']
            current_month = datetime.now().strftime('%m')
            selected_month = st.selectbox(
                'Month', month_options, index=month_options.index(current_month))
    
            if st.button('View Income'):
                df = get_income_by_month(conn, selected_month)
                st.dataframe(df)
                st.write('Total: $', df['Amount'].sum())
    
            with st.expander("**INCOME FUNCTIONS** - *Add New Payer, Category, Account & Export to CSV*"):
                st.subheader('Add Payer')
                new_payer = st.text_input('New Payer')
                if st.button('Add Payer'):
                    if new_payer:
                        add_payer(conn, new_payer)
                        st.success('Payer added!')
                        st.experimental_rerun()
    
                st.subheader('Add Category')
                new_categoryI = st.text_input('New Income Category')
                if st.button('Add Category'):
                    add_categoryI(conn, new_categoryI)
                    st.success('Category added!')
    
                st.subheader('Add Account')
                new_account = st.text_input('New Account')
                if st.button('Add Account'):
                    add_account(conn, new_account)
                    st.success('Account added!')
    
                if st.button('Export Income to CSV'):
                    export_income_to_csv(conn)
                    subprocess.run([f"{sys.executable}", fileRunI])
                    st.success('Income data exported to income.csv')
    
        elif selected_tab == "Summary":
            st.subheader('Monthly Summary')
    
        month_options = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        current_month = datetime.now().strftime('%m')
        selected_month = st.selectbox(
            'Month', month_options, index=month_options.index(current_month)
        )
    
        expenses_df = get_expenses_by_month(conn, selected_month)
        income_df = get_income_by_month(conn, selected_month)
    
        if expenses_df.empty and income_df.empty:
            st.warning("No data available for the selected month.")
        else:
            st.write("Expenses:")
            st.dataframe(expenses_df)
            st.write('Total Expenses:', expenses_df['Amount'].sum())
    
            st.write("Income:")
            st.dataframe(income_df)
            st.write('Total Income:', income_df['Amount'].sum())
    
            net_income = income_df['Amount'].sum() - expenses_df['Amount'].sum()
            st.write('Net Income:', net_income)
    
            st.subheader("Visual Summary")
    
            combined_data = pd.DataFrame({
                'Type': ['Expenses', 'Income'],
                'Total': [expenses_df['Amount'].sum(), income_df['Amount'].sum()]
            })
            fig_combined = px.pie(
                combined_data,
                names='Type',
                values='Total',
                title='Income vs Expenses',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_combined)
            totals = pd.DataFrame({
                'Type': ['Expenses', 'Income'],
                'Total': [expenses_df['Amount'].sum(), income_df['Amount'].sum()]
            })
            fig_bar = px.bar(totals, x='Type', y='Total', title='Expenses vs Income', text='Total')
            st.plotly_chart(fig_bar)
    
            st.download_button(
                label="Download Monthly Summary CSV",
                data=pd.concat([expenses_df, income_df]).to_csv(index=False),
                file_name=f"finance_summary_{selected_month}.csv",
                mime='text/csv',
                help="Download the summary of expenses and income for the selected month."
            )



except Exception as error:
    pass
# -

# !pip install jupytext

# !jupytext --to py final.ipynb

# !streamlit run final.py
