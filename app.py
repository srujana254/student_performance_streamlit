import pymysql
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

conn = pymysql.connect(
    host="localhost", user="root", password="Sql@3117", database="student_db"
)
cursor = conn.cursor()


def insert_student(name, age, subject, marks):
    try:
        cursor.execute(
            "SELECT id FROM student WHERE name = %s AND age = %s AND subject = %s",
            (name, age, subject),
        )
        if cursor.fetchone() is not None:
            st.warning("⚠️ Student with same name, age, and subject already exists!")
            return
        cursor.execute(
            "INSERT INTO student(name, age, subject, marks) VALUES(%s, %s, %s, %s)",
            (name, age, subject, marks),
        )
        conn.commit()
        st.success("✅ Student added successfully!")
    except Exception as e:
        st.error(f"❌ Error adding student: {e}")


def get_all_students():
    try:
        cursor.execute("SELECT id, name, age, subject, marks FROM student")
        data = cursor.fetchall()
        if data:
            return pd.DataFrame(data, columns=["ID", "Name", "Age", "Subject", "Marks"])
        return None
    except Exception as e:
        st.error(f"Error retrieving students: {e}")
        return None


def update_student_field(student_id, field, new_value):
    try:
        # Check if student exists
        cursor.execute("SELECT id FROM student WHERE id = %s", (student_id,))
        if cursor.fetchone() is None:
            st.error(f"❌ Student ID {student_id} not found in database!")
            return

        allowed_fields = {
            "Name": "name",
            "Age": "age",
            "Subject": "subject",
            "Marks": "marks",
        }
        if field not in allowed_fields:
            st.error("❌ Invalid field selected!")
            return

        column = allowed_fields[field]
        query = f"UPDATE student SET {column} = %s WHERE id = %s"
        cursor.execute(query, (new_value, student_id))
        conn.commit()
        st.success(f"✅ {field} updated for Student ID {student_id}!")
    except Exception as e:
        st.error(f"❌ Error updating student: {e}")


def delete_student(student_id):
    try:
        # Check if student exists
        cursor.execute("SELECT id FROM student WHERE id = %s", (student_id,))
        if cursor.fetchone() is None:
            st.error(f"❌ Student ID {student_id} not found in database!")
            return

        cursor.execute("DELETE FROM student WHERE id = %s", (student_id,))
        conn.commit()
        st.success(f"✅ Student ID {student_id} deleted successfully!")
    except Exception as e:
        st.error(f"❌ Error deleting student: {e}")


def get_pass_fail_status(marks, pass_marks=40):
    return "PASS" if marks >= pass_marks else "FAIL"


def calculate_statistics():
    try:
        df = get_all_students()
        if df is None or df.empty:
            st.warning("⚠️ No student data available!")
            return None

        # Add Pass/Fail column
        df["Status"] = df["Marks"].apply(get_pass_fail_status)

        # Calculate statistics
        avg_marks = df["Marks"].mean()
        pass_count = len(df[df["Status"] == "PASS"])
        fail_count = len(df[df["Status"] == "FAIL"])
        pass_percentage = (pass_count / len(df)) * 100 if len(df) > 0 else 0
        top_scorer = df.loc[df["Marks"].idxmax()] if not df.empty else None
        avg_by_subject = df.groupby("Subject")["Marks"].mean()

        return {
            "df": df,
            "avg_marks": avg_marks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_percentage": pass_percentage,
            "top_scorer": top_scorer,
            "avg_by_subject": avg_by_subject,
        }
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")
        return None


# ==================== STREAMLIT UI ====================

st.set_page_config(page_title="Student Performance Manager", layout="wide")
st.title("📚 Student Performance Management System")

# Navigation sidebar
menu = st.sidebar.radio(
    "Select Option",
    [
        "➕ Add Student",
        "📊 View All Students",
        "✏️ Update Marks",
        "🗑️ Delete Student",
        "📈 Analytics & Visualization",
    ],
)

# ==================== ADD STUDENT ====================
if menu == "➕ Add Student":
    st.header("Add New Student")
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Student Name", placeholder="Enter full name")
            age = st.number_input("Age", min_value=5, max_value=50, value=18)
        with col2:
            subject = st.text_input(
                "Subject", placeholder="e.g., Math, Science, English"
            )
            marks = st.number_input("Marks", min_value=0, max_value=100, value=50)

        submitted = st.form_submit_button("✅ Add Student")
        if submitted:
            if name and subject:
                insert_student(name, age, subject, marks)
            else:
                st.error("Please fill in all fields!")

# ==================== VIEW ALL STUDENTS ====================
elif menu == "📊 View All Students":
    st.header("All Students")
    df = get_all_students()
    if df is not None and not df.empty:
        # Add Pass/Fail status
        df["Status"] = df["Marks"].apply(get_pass_fail_status)
        st.table(df)

        st.info(f"📊 Total Students: {len(df)}")
    else:
        st.info("No students in the database yet.")

# ==================== UPDATE MARKS ====================
elif menu == "✏️ Update Marks":
    st.header("Update Student Marks")
    df = get_all_students()
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.number_input("Enter Student ID to Update", min_value=1)
        with col2:
            field_to_update = st.selectbox(
                "Select Field to Update", ["Name", "Age", "Subject", "Marks"]
            )

        if field_to_update == "Name":
            new_value = st.text_input("Enter New Name")
        elif field_to_update == "Age":
            new_value = st.number_input(
                "Enter New Age", min_value=5, max_value=50, value=18
            )
        elif field_to_update == "Subject":
            new_value = st.text_input("Enter New Subject")
        else:
            new_value = st.number_input(
                "Enter New Marks", min_value=0, max_value=100, value=50
            )

        if st.button("🔄 Update Student"):
            if field_to_update in ["Name", "Subject"] and not str(new_value).strip():
                st.error("Please enter a valid value!")
            else:
                update_student_field(student_id, field_to_update, new_value)
    else:
        st.info("No students in the database yet.")

# ==================== DELETE STUDENT ====================
elif menu == "🗑️ Delete Student":
    st.header("Delete Student Record")
    df = get_all_students()
    if df is not None and not df.empty:
        st.table(df)
        student_id = st.number_input("Enter Student ID to Delete", min_value=1)
        if st.button("🗑️ Delete Student", type="secondary"):
            delete_student(student_id)
    else:
        st.info("No students in the database yet.")

# ==================== ANALYTICS & VISUALIZATION ====================
elif menu == "📈 Analytics & Visualization":
    st.header("Analytics & Visualization")

    stats = calculate_statistics()
    if stats:
        # Display Top Scorer
        st.subheader("🏆 Top Scorer")
        if stats["top_scorer"] is not None:
            top = stats["top_scorer"]
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write(f"**ID:** {top['ID']}")
            with col2:
                st.write(f"**Name:** {top['Name']}")
            with col3:
                st.write(f"**Age:** {top['Age']}")
            with col4:
                st.write(f"**Subject:** {top['Subject']}")
            with col5:
                st.write(f"**Marks:** {top['Marks']}")

        # Display Average Marks by Subject
        st.subheader("📚 Average Marks by Subject")
        if not stats["avg_by_subject"].empty:
            st.dataframe(
                stats["avg_by_subject"].rename("Average Marks"),
                use_container_width=True,
            )

        # Visualizations
        st.subheader("📈 Visualizations")
        col1, col2 = st.columns(2)

        with col1:
            # Bar Chart: Subject vs Average Marks
            st.write("**Bar Chart: Subject vs Average Marks**")
            fig, ax = plt.subplots(figsize=(10, 5))
            stats["avg_by_subject"].plot(kind="bar", ax=ax, color="skyblue")
            ax.set_title("Average Marks per Subject", fontsize=14, fontweight="bold")
            ax.set_xlabel("Subject", fontsize=12)
            ax.set_ylabel("Average Marks", fontsize=12)
            ax.set_ylim(0, 100)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            # Pie Chart: Pass/Fail Ratio
            st.write("**Pie Chart: Pass/Fail Ratio**")
            fig, ax = plt.subplots(figsize=(8, 6))
            sizes = [stats["pass_count"], stats["fail_count"]]
            labels = [f"PASS ({stats['pass_count']})", f"FAIL ({stats['fail_count']})"]
            colors = ["#90EE90", "#FFB6C6"]
            ax.pie(
                sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90
            )
            ax.set_title("Pass/Fail Ratio", fontsize=14, fontweight="bold")
            st.pyplot(fig)

        # Show detailed Pass/Fail table
        st.subheader("📋 Student Pass/Fail Status")
        st.dataframe(
            stats["df"][["ID", "Name", "Subject", "Marks", "Status"]],
            use_container_width=True,
        )
