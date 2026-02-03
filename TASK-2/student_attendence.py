import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="Student Attendance & Marks Portal", layout="wide", initial_sidebar_state="expanded")
CLASSES = ["AI", "DS", "CSE"]
SUBJECTS = ["Math", "English", "Science", "History", "Geography"]

def get_connection():
    try:
        return pymysql.connect(host="localhost", user="root", password="Sql@3117", database="task_db")
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=()):
    conn = get_connection()
    if not conn : 
        return None
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def execute_update(query, params=()):
    conn = get_connection()
    if not conn : 
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False
    finally:
        conn.close()

def add_student():
    st.subheader("➕ Add Student")
    with st.form("add_student_form"):
        roll_no, name, class_name = st.number_input("Roll No:", min_value=1), st.text_input("Student Name:"), st.selectbox("Class:", CLASSES)
        if st.form_submit_button("Add Student"):
            if not name: 
                st.error("Please enter student name!")
            elif execute_update("INSERT INTO students (roll_no, name, class) VALUES (%s, %s, %s)", (roll_no, name, class_name)):
                st.success(f"Student {name} added successfully!")

def mark_attendance():
    st.subheader("📋 Mark Attendance")
    selected_class = st.selectbox("Select Class:", CLASSES)
    students = execute_query("SELECT id, roll_no, name FROM students WHERE class = %s ORDER BY roll_no", (selected_class,))
    if students:
        with st.form("attendance_form"):
            attendance_date = st.date_input("Select Date:")
            attendance_data = []
            for student_id, roll_no, name in students:
                col1, col2, col3 = st.columns([1, 2, 2])
                col1.write(f"**{roll_no}**")
                col2.write(name)
                status = col3.radio("Status", ["Present", "Absent"], key=f"attendance_{student_id}", horizontal=True)
                attendance_data.append((student_id, status))
            if st.form_submit_button("Save Attendance"):
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    for student_id, status in attendance_data:
                        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE status = %s", 
                                     (student_id, attendance_date, status, status))
                    conn.commit()
                    conn.close()
                    st.success(f"Attendance marked for {len(attendance_data)} students!")
    else: 
        st.info(f"No students found in {selected_class} class.")

def add_marks():
    st.subheader("📊 Add Marks")
    students = execute_query("SELECT id, roll_no, name FROM students ORDER BY roll_no")
    if students:
        student_dict = {f"{roll_no} - {name}": student_id for student_id, roll_no, name in students}
        with st.form("add_marks_form"):
            student_name, subject, marks = st.selectbox("Select Student:", list(student_dict.keys())), st.selectbox("Subject:", SUBJECTS), st.number_input("Marks (0-100):", min_value=0, max_value=100)
            if st.form_submit_button("Add Marks"):
                student_id = student_dict[student_name]
                if execute_update("INSERT INTO marks (student_id, subject, marks) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE marks = %s", (student_id, subject, marks, marks)):
                    st.success(f"Marks added/updated for {student_name}!")
    else: 
        st.info("No students found.")

def view_attendance():
    st.subheader("📅 View Attendance")
    view_type = st.radio("View By:", ["Student", "Class"], horizontal=True)
    if view_type == "Student":
        students = execute_query("SELECT id, roll_no, name FROM students ORDER BY roll_no")
        if students:
            student_dict = {f"{roll_no} - {name}": student_id for student_id, roll_no, name in students}
            student_id = student_dict[st.selectbox("Select Student:", list(student_dict.keys()))]
            records = execute_query("SELECT a.date, a.status FROM attendance a WHERE a.student_id = %s ORDER BY a.date DESC", (student_id,))
            if records: 
                st.dataframe(pd.DataFrame(records, columns=["Date", "Status"]), use_container_width=True)
            else: 
                st.info("No attendance records found for this student.")
        else:
            st.info("No students found.")
    else:
        selected_class, attendance_date = st.selectbox("Select Class:", CLASSES), st.date_input("Select Date:")
        records = execute_query("SELECT s.roll_no, s.name, a.status FROM students s LEFT JOIN attendance a ON s.id = a.student_id AND a.date = %s WHERE s.class = %s ORDER BY s.roll_no", 
                               (attendance_date, selected_class))
        if records: 
            st.dataframe(pd.DataFrame(records, columns=["Roll No", "Name", "Status"]), use_container_width=True)
        else: 
            st.info("No students found for this class.")

def calculate_attendance():
    st.subheader("📈 Calculate Attendance")
    students = execute_query("SELECT id, roll_no, name FROM students ORDER BY roll_no")
    if students:
        student_dict = {f"{roll_no} - {name}": (student_id, roll_no, name) for student_id, roll_no, name in students}
        student_id, roll_no, name = student_dict[st.selectbox("Select Student:", list(student_dict.keys()), key="attendance_calc")]
        col1, col2 = st.columns(2)
        col1.markdown(f"**Roll No:** {roll_no}")
        col2.markdown(f"**Name:** {name}")
        result = execute_query("SELECT COUNT(CASE WHEN status = 'Present' THEN 1 END) as present_days, COUNT(*) as total_days FROM attendance WHERE student_id = %s", (student_id,))[0]
        if result and result[1] > 0:
            present, total, percentage = result[0], result[1], (result[0] / result[1]) * 100
            col1, col2, col3 = st.columns(3)
            col1.metric("Present Days", present)
            col2.metric("Total Days", total)
            col3.metric("Attendance %", f"{percentage:.2f}%")
        else: 
            st.info("No attendance records found.")
    else: 
        st.info("No students found.")

def show_pass_fail_status():
    st.subheader("✅ Pass/Fail Status Report")
    view_type = st.radio("View By:", ["Student", "Class"], horizontal=True)
    if view_type == "Student":
        students = execute_query("SELECT id, roll_no, name FROM students ORDER BY roll_no")
        if students:
            student_dict = {f"{roll_no} - {name}": (student_id, roll_no, name) for student_id, roll_no, name in students}
            student_id, roll_no, name = student_dict[st.selectbox("Select Student:", list(student_dict.keys()), key="pass_fail")]
            col1, col2 = st.columns(2)
            col1.markdown(f"**Roll No:** {roll_no}")
            col2.markdown(f"**Name:** {name}")
            st.markdown("---")
            marks_data = execute_query("SELECT subject, marks, status FROM marks WHERE student_id = %s ORDER BY subject", (student_id,))
            if marks_data:
                st.dataframe(pd.DataFrame(marks_data, columns=["Subject", "Marks", "Status"]), use_container_width=True)
                st.markdown("---")
                result = execute_query("SELECT AVG(marks), COUNT(*), SUM(CASE WHEN status = 'Pass' THEN 1 ELSE 0 END) FROM marks WHERE student_id = %s", (student_id,))[0]
                if result[0]:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Average Marks", f"{result[0]:.2f}")
                    col2.metric("Total Subjects", int(result[1]))
                    col3.metric("Passed Subjects", int(result[2]) if result[2] else 0)
                    col4.metric("Failed Subjects", int(result[1]) - (int(result[2]) if result[2] else 0))
            else: 
                st.info("No marks records found for this student.")
        else: 
            st.info("No students found.")
    else:
        selected_class = st.selectbox("Select Class:", CLASSES)
        class_data = execute_query("SELECT s.id, s.roll_no, s.name, AVG(m.marks), COUNT(m.subject), SUM(CASE WHEN m.status = 'Pass' THEN 1 ELSE 0 END) FROM students s LEFT JOIN marks m ON s.id = m.student_id WHERE s.class = %s GROUP BY s.id, s.roll_no, s.name ORDER BY s.roll_no", (selected_class,))
        if class_data:
            df = pd.DataFrame(class_data, columns=["ID", "Roll No", "Name", "Avg Marks", "Total Subjects", "Passed Subjects"]).drop("ID", axis=1)
            st.dataframe(df, use_container_width=True)
        else: 
            st.info("No students found for this class.")

def main():
    st.title("🎓 Student Attendance & Marks System")
    menu = st.sidebar.radio("Select Operation", ["Add Student", "Mark Attendance", "Add Marks", "View Attendance", "Calculate Attendance", "Show Status"])
    if menu == "Add Student": 
        add_student()
    elif menu == "Mark Attendance": 
        mark_attendance()
    elif menu == "Add Marks": 
        add_marks()
    elif menu == "View Attendance": 
        view_attendance()
    elif menu == "Calculate Attendance": 
        calculate_attendance()
    else:
        show_pass_fail_status()

if __name__ == "__main__":
    main()