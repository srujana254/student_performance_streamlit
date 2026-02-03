import streamlit as st
import pymysql
import re

st.set_page_config(
    page_title="Complaint Management System",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_connection():
    try:
        return pymysql.connect(
            host="localhost", user="root", password="Sql@3117", database="complaint_db"
        )
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def validate_email(email):
    return (
        re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) is not None
    )


def get_status_icon(status):
    return "🟢" if status == "Resolved" else "🟡" if status == "In Progress" else "🔴"


def display_complaint(complaint):
    col1, col2 = st.columns(2)
    col1.markdown(
        f"**Complaint ID:** {complaint[0]}\n**Name:** {complaint[1]}\n**Email:** {complaint[2]}"
    )
    col2.markdown(
        f"**Category:** {complaint[3]}\n**Created:** {complaint[6]}\n**Status:** {get_status_icon(complaint[5])} {complaint[5]}"
    )
    st.markdown("---\n**Description**")
    st.write(complaint[4])


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None


def login_page():
    st.title("📋 Complaint Management System")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Login")
        role = st.radio("Select Role:", ["User", "Admin"], horizontal=True)
        if role == "User":
            if st.button("Login as User", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_role = "User"
                st.success("User login successful!")
                st.rerun()
        else:
            if st.button("Login as Admin", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_role = "Admin"
                st.success("Admin login successful!")
                st.rerun()


def user_section():
    st.title("📝 Submit a Complaint")
    menu = st.sidebar.radio("Menu", ["Submit Complaint", "Track Complaint", "Logout"])

    if menu == "Submit Complaint":
        st.subheader("➕ Register Your Complaint")
        with st.form("complaint_form"):
            name, email = (
                st.text_input("Full Name:", placeholder="Enter your full name"),
                st.text_input("Email:", placeholder="Enter your email"),
            )
            category = st.selectbox(
                "Complaint Category:",
                [
                    "Product Quality",
                    "Service Issue",
                    "Billing Problem",
                    "Delivery Delay",
                    "Customer Service",
                    "Other",
                ],
            )
            description = st.text_area(
                "Complaint Description:",
                placeholder="Describe your complaint in detail",
                height=150,
            )
            if st.form_submit_button("Submit Complaint", use_container_width=True):
                errors = []
                if not name or len(name.strip()) < 3:
                    errors.append("Name must be at least 3 characters!")
                if not email or not validate_email(email):
                    errors.append("Please enter a valid email!")
                if not description or len(description.strip()) < 10:
                    errors.append("Description must be at least 10 characters!")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor()
                        try:
                            cursor.execute(
                                "INSERT INTO complaints (name, email, category, description, status) VALUES (%s, %s, %s, %s, 'Open')",
                                (name, email, category, description),
                            )
                            conn.commit()
                            st.success("✅ Complaint submitted successfully!")
                            st.info(f"📌 Your Complaint ID: **{cursor.lastrowid}**")
                            st.write(
                                "Please save this ID to track your complaint status."
                            )
                        except Exception as e:
                            st.error(f"Error submitting complaint: {e}")
                        finally:
                            conn.close()

    elif menu == "Track Complaint":
        st.subheader("🔍 Track Your Complaint")
        complaint_id = st.number_input("Enter Complaint ID:", min_value=1)
        if st.button("Search", use_container_width=True):
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, email, category, description, status, created_at FROM complaints WHERE id = %s",
                    (complaint_id,),
                )
                complaint = cursor.fetchone()
                conn.close()
                if complaint:
                    st.markdown("---")
                    display_complaint(complaint)
                else:
                    st.error("Complaint not found!")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.success("Logged out successfully!")
        st.rerun()


def admin_section():
    st.title("👨‍💼 Admin Dashboard")
    menu = st.sidebar.radio(
        "Admin Menu",
        ["View All Complaints", "Search Complaint", "Update Status", "Logout"],
    )

    if menu == "View All Complaints":
        st.subheader("📋 All Complaints")
        filter_status = st.selectbox(
            "Filter by Status:", ["All", "Open", "In Progress", "Resolved", "Closed"]
        )
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT id, name, email, category, description, status, created_at FROM complaints"
            params = ()
            if filter_status != "All":
                query += " WHERE status = %s"
                params = (filter_status,)
            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            complaints = cursor.fetchall()
            conn.close()
            if complaints:
                st.markdown(f"**Total Complaints:** {len(complaints)}\n---")
                for complaint in complaints:
                    with st.expander(
                        f"ID: {complaint[0]} | {complaint[2]} | {complaint[3]} | Status: {complaint[5]}"
                    ):
                        display_complaint(complaint)
            else:
                st.info("No complaints found.")

    elif menu == "Search Complaint":
        st.subheader("🔍 Search Complaint")
        search_type = st.radio("Search by:", ["Complaint ID", "Email"], horizontal=True)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            if search_type == "Complaint ID":
                complaint_id = st.number_input("Enter Complaint ID:", min_value=1)
                if st.button("Search", use_container_width=True):
                    cursor.execute(
                        "SELECT id, name, email, category, description, status, created_at FROM complaints WHERE id = %s",
                        (complaint_id,),
                    )
                    complaint = cursor.fetchone()
                    if complaint:
                        st.markdown("---")
                        display_complaint(complaint)
                    else:
                        st.error("Complaint not found!")
            else:
                email = st.text_input("Enter Email Address:")
                if st.button("Search", use_container_width=True):
                    cursor.execute(
                        "SELECT id, name, email, category, description, status, created_at FROM complaints WHERE email = %s ORDER BY created_at DESC",
                        (email,),
                    )
                    complaints = cursor.fetchall()
                    if complaints:
                        st.markdown(f"**Total Complaints:** {len(complaints)}\n---")
                        for complaint in complaints:
                            with st.expander(
                                f"ID: {complaint[0]} | {complaint[3]} | Status: {complaint[5]}"
                            ):
                                display_complaint(complaint)
                    else:
                        st.error("No complaints found for this email!")
            conn.close()

    elif menu == "Update Status":
        st.subheader("📝 Update Complaint Status")
        complaint_id = st.number_input("Enter Complaint ID:", min_value=1)
        new_status = st.selectbox(
            "New Status:", ["Open", "In Progress", "Resolved", "Closed"]
        )
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, category, status, created_at FROM complaints WHERE id = %s",
                (complaint_id,),
            )
            complaint = cursor.fetchone()
            if complaint:
                col1, col2 = st.columns(2)
                col1.markdown(f"**Name:** {complaint[1]}\n**Category:** {complaint[3]}")
                col2.markdown(
                    f"**Current Status:** {complaint[4]}\n**Created:** {complaint[5]}"
                )
                if st.button("Update Status", use_container_width=True):
                    cursor.execute(
                        "UPDATE complaints SET status = %s WHERE id = %s",
                        (new_status, complaint_id),
                    )
                    conn.commit()
                    st.success(f"✅ Status updated to: {new_status}")
            else:
                st.error("Complaint not found!")
            conn.close()

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.success("Logged out successfully!")
        st.rerun()


def main():
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.user_role == "User":
        user_section()
    elif st.session_state.user_role == "Admin":
        admin_section()


if __name__ == "__main__":
    main()
