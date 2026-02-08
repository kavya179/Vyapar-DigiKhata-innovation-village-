import streamlit as st
from database import chek_pass, get_users, insert_user

def validate_email_simple(email):
    """Simple email validation using Python string methods"""
    if not email:
        return False, "Email cannot be empty"
    
    if '@' not in email:
        return False, "Email must contain @ symbol"
    
    # Split by @ to check parts
    parts = email.split('@')
    if len(parts) != 2:
        return False, "Email format is invalid"
    
    username, domain = parts
    
    if not username:
        return False, "Email must have a username before @"
    
    if not domain:
        return False, "Email must have a domain after @"
    
    # Check if domain has extension (like .com, .in)
    if '.' not in domain:
        return False, "Email must have domain extension (e.g., @gmail.com)"
    
    domain_parts = domain.split('.')
    if len(domain_parts) < 2:
        return False, "Email must have valid domain extension"
    
    # Check if extension exists and has at least 2 characters
    extension = domain_parts[-1]
    if len(extension) < 2:
        return False, "Domain extension must be at least 2 characters"
    
    return True, ""

def validate_name(name):
    """Validate name using Python string methods"""
    if not name:
        return False, "Name cannot be empty"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    # Check if name contains only letters and spaces
    for char in name:
        if not (char.isalpha() or char.isspace()):
            return False, "Name should contain only letters and spaces"
    
    return True, ""

def validate_password(password):
    """Validate password using Python string methods"""
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) != 6:
        return False, "Password must be exactly 6 characters"
    
    # Check if password contains only digits
    if not password.isdigit():
        return False, "Password must contain only numbers (0-9)"
    
    return True, ""

def sign_up_page():
    # Header
    st.title("📝 Create Account")
    st.write("Join us and start managing your business digitally!")
    st.divider()
    
    # Create centered layout
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    
    with col2:
        st.subheader("Enter Your Details")
        st.write("")
        
        # Shop Owner Name
        name = st.text_input(
            "👤 Shop Owner Name *",
            placeholder="Enter your full name",
            help="Your name (letters only)"
        )
        
        # Shop Name
        shop_name = st.text_input(
            "🏪 Shop Name *",
            placeholder="Enter your shop/business name",
            help="Name of your business"
        )
        
        # Email
        email = st.text_input(
            "📧 Email Address *",
            placeholder="yourname@gmail.com",
            help="Must include @ and domain extension"
        )
        
        # Password
        password = st.text_input(
            "🔒 Create Password *",
            type="password",
            max_chars=6,
            placeholder="6-digit password",
            help="Create a 6-digit numeric password"
        )
        
        # Confirm Password
        confirm_password = st.text_input(
            "🔒 Confirm Password *",
            type="password",
            max_chars=6,
            placeholder="Re-enter password",
            help="Re-enter the same password"
        )
        
        st.caption("* Required fields")
        st.write("")
        
        # Buttons
        col_a, col_b = st.columns(2)
        
        with col_a:
            signup_btn = st.button("✅ Sign Up", key="submit_signup", use_container_width=True, type="primary")
        
        with col_b:
            back_btn = st.button("🏠 Back", key="back_home", use_container_width=True)
        
        # Handle Back Button
        if back_btn:
            st.session_state.page = "home"
            st.rerun()
        
        # Handle Sign Up
        if signup_btn:
            # Validate all inputs
            errors = []
            
            # Validate Name
            name_valid, name_error = validate_name(name)
            if not name_valid:
                errors.append(f"❌ Owner Name: {name_error}")
            
            # Validate Shop Name
            if not shop_name or len(shop_name.strip()) < 2:
                errors.append("❌ Shop Name must be at least 2 characters")
            
            # Validate Email
            email_valid, email_error = validate_email_simple(email)
            if not email_valid:
                errors.append(f"❌ {email_error}")
            else:
                # Check if email already exists
                existing_user = get_users(email)
                if existing_user:
                    errors.append("❌ This email is already registered. Please login instead")
            
            # Validate Password
            password_valid, password_error = validate_password(password)
            if not password_valid:
                errors.append(f"❌ {password_error}")
            else:
                # Check if password already in use
                if chek_pass(password):
                    errors.append("❌ This password is already in use. Choose a different one")
            
            # Validate Confirm Password
            if not confirm_password:
                errors.append("❌ Please confirm your password")
            elif password != confirm_password:
                errors.append("❌ Passwords do not match!")
            
            # Show errors if any
            if errors:
                st.error("**Please fix the following errors:**")
                for error in errors:
                    st.error(error)
            else:
                # All validations passed - Create account
                try:
                    insert_user(
                        name=name.strip(),
                        email=email.strip(),
                        shop_name=shop_name.strip(),
                        password=password
                    )
                    
                    st.success("✅ Account created successfully!")
                    st.balloons()
                    
                    # Auto-login after signup
                    st.info("Redirecting to Shop Settings...")
                    
                    # Get user data
                    user_data = get_users(email)
                    if user_data:
                        user_row = user_data[0]
                        st.session_state['user'] = {
                            'id': user_row[0],
                            'username': user_row[1],
                            'email': user_row[2],
                            'shop_name': user_row[3]  # Store shop name
                        }
                        
                        # Initialize shop settings with the entered shop name
                        st.session_state.shop_settings = {
                            'shop_address': '',
                            'shop_phone': '',
                            'currency': '₹ INR',
                            'tax_rate': 0.0,
                            'low_stock_alert': 10,
                            'shop_name': shop_name.strip()
                        }
                        
                        # Set flag to show shop settings first
                        st.session_state['first_time_user'] = True
                        st.session_state['dashboard_menu'] = 'Settings'
                        
                        st.session_state.page = "dashboard"
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating account: {str(e)}")
        
        st.divider()
        
        # Login link
        st.info("Already have an account?")
        if st.button("🔐 Login Here", key="goto_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        
        st.write("")
        st.caption("By creating an account, you agree to our terms and conditions")