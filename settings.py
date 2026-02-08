import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import database as db
import io
from email_helper import send_low_stock_notification, send_overdue_payment_notification

def settings_page(default_tab=0):
    """Settings page with shop info, data export, and notifications"""
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.error("Please login first!")
        st.session_state.page = "home"
        st.rerun()
        return
    
    user_id = st.session_state.user['id']
    username = st.session_state.user['username']
    
    st.title("⚙️ Settings & Notifications")
    
    # Create tabs for different settings
    tabs = st.tabs(["🏪 Shop Settings", "📧 Email Settings", "📥 Export Data", "🔔 Notifications"])
    
    # Get notification count for badge
    low_stock_items = get_low_stock_items(user_id)
    overdue_customers = get_overdue_customers(user_id)
    total_notifications = len(low_stock_items) + len(overdue_customers)
    
    # Show notification badge at top if there are notifications
    if total_notifications > 0:
        st.error(f"⚠️ {total_notifications} notifications require your attention!")
    
    # ============ TAB 1: SHOP SETTINGS ============
    with tabs[0]:
        st.subheader("Shop Information")
        st.write("")
        
        # Initialize shop settings in session state if not exists
        if 'shop_settings' not in st.session_state:
            st.session_state.shop_settings = {
                'shop_address': '',
                'shop_phone': '',
                'currency': '₹ INR',
                'tax_rate': 0.0,
                'low_stock_alert': 10
            }
        
        # Initialize email settings if not exists
        if 'email_settings' not in st.session_state:
            st.session_state.email_settings = {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_email': '',
                'smtp_password': ''
            }
        
        with st.form("shop_settings_form"):
            shop_address = st.text_area(
                "Shop Address",
                value=st.session_state.shop_settings.get('shop_address', ''),
                placeholder="Enter your shop's complete address"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                shop_phone = st.text_input(
                    "Shop Contact Number",
                    value=st.session_state.shop_settings.get('shop_phone', ''),
                    placeholder="+91 XXXXXXXXXX"
                )
            
            with col2:
                currency = st.selectbox(
                    "Currency",
                    options=['₹ INR', '$ USD', '€ EUR', '£ GBP', '¥ JPY'],
                    index=['₹ INR', '$ USD', '€ EUR', '£ GBP', '¥ JPY'].index(
                        st.session_state.shop_settings.get('currency', '₹ INR')
                    )
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                tax_rate = st.number_input(
                    "Tax Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=st.session_state.shop_settings.get('tax_rate', 0.0),
                    step=0.5
                )
            
            with col4:
                low_stock_alert = st.number_input(
                    "Low Stock Alert Threshold",
                    min_value=1,
                    max_value=100,
                    value=st.session_state.shop_settings.get('low_stock_alert', 10),
                    step=1,
                    help="Get notified when stock falls below this quantity"
                )
            
            submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
            
            if submitted:
                st.session_state.shop_settings = {
                    'shop_address': shop_address,
                    'shop_phone': shop_phone,
                    'currency': currency,
                    'tax_rate': tax_rate,
                    'low_stock_alert': low_stock_alert
                }
                st.success("✅ Settings saved successfully!")
        
        st.divider()
        
        # Display current settings
        st.subheader("Current Settings")
        settings_data = pd.DataFrame({
            "Setting": ["Shop Address", "Contact Number", "Currency", "Tax Rate", "Low Stock Alert"],
            "Value": [
                st.session_state.shop_settings['shop_address'] or "Not set",
                st.session_state.shop_settings['shop_phone'] or "Not set",
                st.session_state.shop_settings['currency'],
                f"{st.session_state.shop_settings['tax_rate']}%",
                f"{st.session_state.shop_settings['low_stock_alert']} units"
            ]
        })
        
        # Use st.dataframe with proper config for theme compatibility
        st.dataframe(
            settings_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Setting": st.column_config.TextColumn("Setting", width="medium"),
                "Value": st.column_config.TextColumn("Value", width="large")
            }
        )
    
    # ============ TAB 2: EMAIL SETTINGS ============
    with tabs[1]:
        st.subheader("📧 Email Notification Settings")
        st.write("")
        
        st.info("Configure email notifications to receive alerts for low stock and overdue payments directly in your inbox.")
        
        with st.form("email_settings_form"):
            enable_email = st.checkbox(
                "Enable Email Notifications",
                value=st.session_state.email_settings.get('enabled', False),
                help="Turn on to receive email alerts"
            )
            
            st.markdown("### SMTP Configuration")
            st.caption("For Gmail: Use your email and an [App Password](https://support.google.com/accounts/answer/185833)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                smtp_server = st.text_input(
                    "SMTP Server",
                    value=st.session_state.email_settings.get('smtp_server', 'smtp.gmail.com'),
                    placeholder="smtp.gmail.com",
                    help="Gmail: smtp.gmail.com, Outlook: smtp-mail.outlook.com"
                )
            
            with col2:
                smtp_port = st.number_input(
                    "SMTP Port",
                    value=st.session_state.email_settings.get('smtp_port', 587),
                    min_value=1,
                    max_value=65535,
                    help="Usually 587 for TLS or 465 for SSL"
                )
            
            smtp_email = st.text_input(
                "Email Address (From)",
                value=st.session_state.email_settings.get('smtp_email', ''),
                placeholder="your-email@gmail.com",
                help="Email address to send notifications from"
            )
            
            smtp_password = st.text_input(
                "Email Password / App Password",
                value=st.session_state.email_settings.get('smtp_password', ''),
                type="password",
                placeholder="Enter your app password",
                help="For Gmail, use App Password, not your regular password"
            )
            
            st.divider()
            
            col_save, col_test = st.columns(2)
            
            with col_save:
                save_email_settings = st.form_submit_button("💾 Save Email Settings", use_container_width=True)
            
            with col_test:
                test_email = st.form_submit_button("📧 Send Test Email", use_container_width=True)
            
            if save_email_settings:
                st.session_state.email_settings = {
                    'enabled': enable_email,
                    'smtp_server': smtp_server,
                    'smtp_port': smtp_port,
                    'smtp_email': smtp_email,
                    'smtp_password': smtp_password
                }
                st.success("✅ Email settings saved successfully!")
                
                if enable_email:
                    st.info("📧 Email notifications are now enabled. You will receive alerts for low stock and overdue payments.")
                else:
                    st.warning("⚠️ Email notifications are disabled. Enable them to receive alerts.")
            
            if test_email:
                if not enable_email:
                    st.error("❌ Please enable email notifications first!")
                elif not smtp_email or not smtp_password:
                    st.error("❌ Please fill in all email settings!")
                else:
                    # Save settings first
                    st.session_state.email_settings = {
                        'enabled': enable_email,
                        'smtp_server': smtp_server,
                        'smtp_port': smtp_port,
                        'smtp_email': smtp_email,
                        'smtp_password': smtp_password
                    }
                    
                    # Send test email
                    from email_helper import send_notification_email
                    test_subject = "🔔 Test Email from Vyapar DigiKhata"
                    test_body = f"""
                    <h2>Test Email Successful! ✅</h2>
                    <p>Congratulations! Your email notification settings are working correctly.</p>
                    <p>You will now receive alerts for:</p>
                    <ul>
                        <li>📦 Low Stock Items</li>
                        <li>💰 Overdue Customer Payments</li>
                    </ul>
                    <p><b>Shop Owner:</b> {username}</p>
                    <p><b>User Email:</b> {st.session_state.user['email']}</p>
                    """
                    
                    success, message = send_notification_email(
                        st.session_state.user['email'],
                        test_subject,
                        test_body
                    )
                    
                    if success:
                        st.success("✅ Test email sent successfully! Check your inbox.")
                    else:
                        st.error(f"❌ Failed to send test email: {message}")
        
        st.divider()
        
        # Display current email settings
        st.subheader("Current Email Settings")
        email_status = "✅ Enabled" if st.session_state.email_settings.get('enabled', False) else "❌ Disabled"
        
        email_config_data = pd.DataFrame({
            "Setting": ["Status", "SMTP Server", "SMTP Port", "Email Address"],
            "Value": [
                email_status,
                st.session_state.email_settings.get('smtp_server', 'Not set'),
                str(st.session_state.email_settings.get('smtp_port', 'Not set')),
                st.session_state.email_settings.get('smtp_email', 'Not set')
            ]
        })
        
        st.dataframe(
            email_config_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Setting": st.column_config.TextColumn("Setting", width="medium"),
                "Value": st.column_config.TextColumn("Value", width="large")
            }
        )
        
        if st.session_state.email_settings.get('enabled', False):
            st.success("📧 Email notifications are active. You will receive alerts automatically when notifications are generated.")
        else:
            st.warning("⚠️ Email notifications are disabled. Enable them above to receive automatic alerts.")
    
    # ============ TAB 3: EXPORT DATA ============
    with tabs[2]:
        st.subheader("📥 Download Your Data")
        st.write("Export your business data as CSV files for backup or analysis")
        st.write("")
        
        col1, col2 = st.columns(2)
        
        # Export Customers
        with col1:
            st.markdown("#### 👥 Customer Data")
            customers = db.get_customers(user_id)
            if customers:
                df_customers = pd.DataFrame(customers)
                csv_customers = df_customers.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download Customers CSV",
                    data=csv_customers,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.info(f"Total Customers: {len(customers)}")
            else:
                st.warning("No customer data available")
        
        # Export Customer Transactions
        with col2:
            st.markdown("#### 💳 Customer Transactions")
            transactions = db.get_transactions(user_id)
            if transactions:
                df_transactions = pd.DataFrame(transactions)
                csv_transactions = df_transactions.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download Transactions CSV",
                    data=csv_transactions,
                    file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.info(f"Total Transactions: {len(transactions)}")
            else:
                st.warning("No transaction data available")
        
        st.write("")
        
        col3, col4 = st.columns(2)
        
        # Export Inventory
        with col3:
            st.markdown("#### 📦 Inventory Data")
            inventory = db.get_inventory(user_id)
            if inventory:
                df_inventory = pd.DataFrame(inventory)
                csv_inventory = df_inventory.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download Inventory CSV",
                    data=csv_inventory,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.info(f"Total Items: {len(inventory)}")
            else:
                st.warning("No inventory data available")
        
        # Export Suppliers
        with col4:
            st.markdown("#### 🏭 Supplier Data")
            suppliers = db.get_suppliers(user_id)
            if suppliers:
                df_suppliers = pd.DataFrame(suppliers)
                csv_suppliers = df_suppliers.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download Suppliers CSV",
                    data=csv_suppliers,
                    file_name=f"suppliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.info(f"Total Suppliers: {len(suppliers)}")
            else:
                st.warning("No supplier data available")
        
        st.divider()
        
        # Complete Business Summary
        st.markdown("#### 📊 Complete Business Summary")
        st.write("Generate a comprehensive text report of your entire business data")
        
        if st.button("📄 Generate Summary Report", use_container_width=True):
            report = []
            report.append("=" * 60)
            report.append("VYAPAR DIGIKHATA - BUSINESS SUMMARY REPORT")
            report.append("=" * 60)
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Business Owner: {username}")
            report.append("")
            
            # Add all data to report
            report.append("CUSTOMERS:")
            report.append("-" * 60)
            customers = db.get_customers(user_id)
            for c in customers:
                report.append(f"  - {c['name']} | {c['contact']} | {c['address']}")
            report.append("")
            
            report.append("INVENTORY:")
            report.append("-" * 60)
            inventory = db.get_inventory(user_id)
            for i in inventory:
                report.append(f"  - {i['item_name']} | Qty: {i['quantity']} | Price: ₹{i['price_per_unit']}")
            report.append("")
            
            report.append("RECENT TRANSACTIONS:")
            report.append("-" * 60)
            transactions = db.get_transactions(user_id)[:20]  # Last 20 transactions
            for t in transactions:
                report.append(f"  - {t['date']} | {t['type']} | ₹{t['amount']} | {t['description']}")
            report.append("")
            
            report.append("SUMMARY:")
            report.append("-" * 60)
            report.append(f"Total Customers: {len(customers) if customers else 0}")
            report.append(f"Total Transactions: {len(transactions) if transactions else 0}")
            report.append("")
            
            report_text = "\n".join(report)
            
            st.download_button(
                label="📄 Download Business Summary Report",
                data=report_text.encode('utf-8'),
                file_name=f"business_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.success("✅ Report generated successfully!")
    
    # ============ TAB 4: NOTIFICATIONS ============
    with tabs[3]:
        st.subheader("🔔 Notifications & Alerts")
        st.write("")
        
        # Display notification summary with color indicator
        if total_notifications > 0:
            st.error(f"⚠️ You have **{total_notifications}** notifications requiring attention!")
        else:
            st.success("✅ All good! No pending notifications.")
        
        st.divider()
        
        # Low Stock Alerts
        st.markdown("#### 📦 Low Stock Alerts")
        
        if low_stock_items:
            st.warning(f"⚠️ **{len(low_stock_items)}** item(s) running low on stock!")
            
            df_low_stock = pd.DataFrame(low_stock_items)
            df_low_stock = df_low_stock[['item_name', 'quantity', 'price_per_unit']]
            df_low_stock.columns = ['Item Name', 'Current Stock', 'Price/Unit (₹)']
            
            # Separate critical and low stock items
            critical_items = df_low_stock[df_low_stock['Current Stock'] <= 5]
            low_items = df_low_stock[df_low_stock['Current Stock'] > 5]
            
            # Show critical items first
            if not critical_items.empty:
                st.error(f"🔴 **Critical Stock ({len(critical_items)} items with ≤5 units)**")
                st.dataframe(
                    critical_items,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Item Name": st.column_config.TextColumn("Item Name", width="medium"),
                        "Current Stock": st.column_config.NumberColumn("Current Stock", width="small"),
                        "Price/Unit (₹)": st.column_config.NumberColumn("Price/Unit (₹)", format="₹%.2f", width="medium")
                    }
                )
            
            # Show low stock items
            if not low_items.empty:
                st.warning(f"🟡 **Low Stock ({len(low_items)} items with 6-10 units)**")
                st.dataframe(
                    low_items,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Item Name": st.column_config.TextColumn("Item Name", width="medium"),
                        "Current Stock": st.column_config.NumberColumn("Current Stock", width="small"),
                        "Price/Unit (₹)": st.column_config.NumberColumn("Price/Unit (₹)", format="₹%.2f", width="medium")
                    }
                )
            
            st.info("💡 Tip: Restock these items soon to avoid running out!")
            
            # Email notification button for low stock
            st.write("")
            if st.session_state.email_settings.get('enabled', False):
                if st.button("📧 Email Low Stock Alert to Me", key="email_low_stock", use_container_width=True):
                    user_email = st.session_state.user['email']
                    shop_name = st.session_state.shop_settings.get('shop_name', 'Your Shop')
                    
                    with st.spinner("Sending email..."):
                        success, message = send_low_stock_notification(user_email, low_stock_items, shop_name)
                    
                    if success:
                        st.success("✅ Low stock alert email sent successfully!")
                    else:
                        st.error(f"❌ Failed to send email: {message}")
            else:
                st.info("📧 Enable email notifications in 'Email Settings' tab to receive alerts via email.")
        else:
            st.success("✅ All inventory items are well-stocked!")
        
        st.divider()
        
        # Overdue Customer Payments
        st.markdown("#### 💰 Overdue Customer Payments")
        
        if overdue_customers:
            st.warning(f"⚠️ **{len(overdue_customers)}** customer(s) have overdue payments!")
            
            df_overdue = pd.DataFrame(overdue_customers)
            df_overdue = df_overdue[['customer_name', 'pending_amount', 'days_overdue', 'last_transaction_date']]
            df_overdue.columns = ['Customer Name', 'Pending Amount (₹)', 'Days Overdue', 'Last Transaction']
            
            # Use st.dataframe with column config for better theme compatibility
            st.dataframe(
                df_overdue,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Customer Name": st.column_config.TextColumn("Customer Name", width="medium"),
                    "Pending Amount (₹)": st.column_config.NumberColumn("Pending Amount (₹)", format="₹%.2f", width="medium"),
                    "Days Overdue": st.column_config.NumberColumn("Days Overdue", width="small"),
                    "Last Transaction": st.column_config.DateColumn("Last Transaction", width="medium")
                }
            )
            
            total_overdue = df_overdue['Pending Amount (₹)'].sum()
            st.error(f"💵 Total Overdue Amount: ₹{total_overdue:,.2f}")
            
            st.info("💡 Tip: Follow up with these customers to collect pending payments!")
            
            # Email notification button for overdue payments
            st.write("")
            if st.session_state.email_settings.get('enabled', False):
                if st.button("📧 Email Overdue Payment Alert to Me", key="email_overdue", use_container_width=True):
                    user_email = st.session_state.user['email']
                    shop_name = st.session_state.shop_settings.get('shop_name', 'Your Shop')
                    
                    with st.spinner("Sending email..."):
                        success, message = send_overdue_payment_notification(user_email, overdue_customers, shop_name)
                    
                    if success:
                        st.success("✅ Overdue payment alert email sent successfully!")
                    else:
                        st.error(f"❌ Failed to send email: {message}")
            else:
                st.info("📧 Enable email notifications in 'Email Settings' tab to receive alerts via email.")
        else:
            st.success("✅ No overdue customer payments!")

def get_low_stock_items(user_id):
    """Get items with low stock"""
    inventory = db.get_inventory(user_id)
    
    # Get threshold from settings
    threshold = 10
    if 'shop_settings' in st.session_state:
        threshold = st.session_state.shop_settings.get('low_stock_alert', 10)
    
    low_stock = [item for item in inventory if item['quantity'] < threshold]
    return low_stock

def get_overdue_customers(user_id):
    """Get customers with overdue payments (Debit transactions older than 30 days)"""
    customers = db.get_customers(user_id)
    transactions = db.get_transactions(user_id)
    
    overdue_list = []
    current_date = datetime.now()
    
    for customer in customers:
        customer_id = customer['id']
        customer_name = customer['name']
        customer_phone = customer.get('contact', '')
        
        # Get all transactions for this customer
        customer_transactions = [t for t in transactions if t['customer_id'] == customer_id]
        
        if not customer_transactions:
            continue
        
        # Calculate pending amount (Credit - Debit)
        total_credit = sum(t['amount'] for t in customer_transactions if t['type'] == 'Credit')
        total_debit = sum(t['amount'] for t in customer_transactions if t['type'] == 'Debit')
        pending_amount = total_credit - total_debit
        
        # Only check if there's pending amount
        if pending_amount > 0:
            # Get last transaction date
            last_transaction = max(customer_transactions, key=lambda x: x['date'])
            last_date = datetime.strptime(last_transaction['date'], '%Y-%m-%d')
            
            # Calculate days overdue
            days_diff = (current_date - last_date).days
            
            # If more than 30 days and pending amount exists
            if days_diff > 30:
                overdue_list.append({
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'customer_phone': customer_phone,
                    'pending_amount': pending_amount,
                    'days_overdue': days_diff,
                    'last_transaction_date': last_transaction['date']
                })
    
    # Sort by days overdue (descending)
    overdue_list.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    return overdue_list