import streamlit as st
from models.student import Student
from pydantic import ValidationError
from utils import load_students, save_students
import pandas as pd
import altair as alt

st.set_page_config(page_title="🎓 Student Registration", layout="centered")

st.image("logo.png", width=200, use_container_width=True)
st.title("📘 Student Registration Form")


# --- Sidebar ---
st.sidebar.image("school.png", width=200, use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.markdown("## 🧑‍🏫 Student Management System")
st.sidebar.write("Track, update, and visualize student performance easily. Great for teachers, parents, and admins!")

st.sidebar.markdown("### 📚 Features")
st.sidebar.write("- Add new students")
st.sidebar.write("- Edit/delete existing records")
st.sidebar.write("- Visualize subject-wise marks")
st.sidebar.write("- View class-wide averages")

st.sidebar.markdown("### 📘 Quick Tip")
st.sidebar.info("💡 Use the '➕ Add Another Subject' button to dynamically add more subjects for a student.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠 Developer Contact")
st.sidebar.write("📧 [Email Us](mailto:ismailahmedshahpk@gmail.com)")
st.sidebar.write("🔗 [Connect on LinkedIn](https://www.linkedin.com/in/ismail-ahmed-shah-2455b01ba/)")
st.sidebar.write("💬 [Chat on WhatsApp](https://wa.me/923322241405)")

st.sidebar.markdown("---")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/219/219969.png", width=90, use_container_width=True)
st.sidebar.markdown("<p style='text-align: center; color: grey;'>Built with ❤️ for Educators & Learners</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Load existing students
students = load_students()

# Initialize dynamic subjects
if "subject_count" not in st.session_state:
    st.session_state.subject_count = 3

# Form for adding student
with st.form("student_form"):
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=1, max_value=100, value=16)
    class_level = st.number_input("Class Level", min_value=1, max_value=12, value=10)
    address = st.text_input("Address")

    st.subheader("Subjects and Marks (0-100)")

    # Dynamic subject input
    subjects = {}
    for i in range(st.session_state.subject_count):
        subj_name = st.text_input(f"Subject {i+1} Name", key=f"subj_name_{i}")
        subj_marks = st.number_input(f"Marks for {subj_name or f'Subject {i+1}'}", min_value=0, max_value=100, key=f"subj_marks_{i}")
        if subj_name:
            subjects[subj_name] = subj_marks

    col_add, col_submit = st.columns([1, 3])
    with col_add:
        if st.form_submit_button("➕ Add Another Subject"):
            st.session_state.subject_count += 1
            st.rerun()

    with col_submit:
        submit = st.form_submit_button("✅ Submit")

if submit:
    if not subjects:
        st.warning("⚠️ Please enter at least one subject.")
    else:
        try:
            student = Student(
                name=name,
                age=age,
                class_level=class_level,
                subjects=subjects,
                address=address
            )
            students.append(student)
            save_students(students)
            st.success("✅ Student saved to JSON!")
            st.write(student.model_dump())
        except ValidationError as e:
            st.error("❌ Validation Error")
            for err in e.errors():
                st.write(f"🔴 {err['msg']}")


# --- Search / Filter Students ---
st.divider()
st.subheader("🔎 Search / Filter Students")

# Initialize session state only once
if "search_name" not in st.session_state:
    st.session_state.search_name = ""
if "filter_class" not in st.session_state:
    st.session_state.filter_class = 0

# Callback to reset filters
def reset_filters():
    st.session_state.search_name = ""
    st.session_state.filter_class = 0

# Use session state for inputs
st.text_input("Search by name", key="search_name")
st.number_input("Filter by class level (optional)", min_value=0, value=st.session_state.filter_class, step=1, key="filter_class")

# Reset button calls callback
st.button("🔄 Reset Filters", on_click=reset_filters)

# Apply filters
filtered_students = [
    s for s in students
    if (st.session_state.search_name.lower() in s.name.lower()) and
       (st.session_state.filter_class == 0 or s.class_level == st.session_state.filter_class)
]



st.divider()
st.subheader("✏️ Manage Existing Students")

if filtered_students:
    names = [s.name for s in filtered_students]
    selected_name = st.selectbox("Select a student to manage", names, key="manage_select")

    selected_student = next((s for s in students if s.name == selected_name), None)

    if selected_student:
        with st.expander("👁️ View Details"):
            st.json(selected_student.model_dump())

        new_name = st.text_input("Edit Name", value=selected_student.name)
        new_age = st.number_input("Edit Age", value=selected_student.age)
        new_class = st.number_input("Edit Class Level", value=selected_student.class_level)
        new_address = st.text_input("Edit Address", value=selected_student.address)

        new_subjects = {}
        for subj, mark in selected_student.subjects.items():
            new_mark = st.number_input(f"Edit {subj}", value=mark, key=f"edit_{subj}")
            new_subjects[subj] = new_mark

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Update Student"):
                try:
                    updated_student = Student(
                        name=new_name,
                        age=new_age,
                        class_level=new_class,
                        address=new_address,
                        subjects=new_subjects
                    )
                    index = students.index(selected_student)
                    students[index] = updated_student
                    save_students(students)
                    st.success("✅ Student updated successfully!")
                except ValidationError as e:
                    st.error("❌ Validation Error")
                    for err in e.errors():
                        st.write(f"🔴 {err['msg']}")

        with col2:
            if st.button("🗑️ Delete Student"):
                students.remove(selected_student)
                save_students(students)
                st.success("🗑️ Student deleted successfully!")
                st.rerun()
else:
    st.info("No students found yet.")

st.divider()
st.subheader("📊 Student Marks Visualization")

if students:
    st.markdown("### 👤 Select a Student to View Marks")
    selected = st.selectbox("Choose a student", [s.name for s in students], key="viz_student")

    student_obj = next((s for s in students if s.name == selected), None)
    if student_obj:
        df = pd.DataFrame({
            "Subject": list(student_obj.subjects.keys()),
            "Marks": list(student_obj.subjects.values())
        })
        st.bar_chart(df.set_index("Subject"))

    st.markdown("### 📈 Subject-wise Class Average")

    subject_totals = {}
    subject_counts = {}

    for s in students:
        for subject, mark in s.subjects.items():
            subject_totals[subject] = subject_totals.get(subject, 0) + mark
            subject_counts[subject] = subject_counts.get(subject, 0) + 1

    averages = {
        subject: subject_totals[subject] / subject_counts[subject]
        for subject in subject_totals
    }

    avg_df = pd.DataFrame({
        "Subject": list(averages.keys()),
        "Average Marks": list(averages.values())
    })

    chart = alt.Chart(avg_df).mark_bar().encode(
        x="Subject",
        y="Average Marks",
        color=alt.value("#007acc")
    ).properties(
        width=600,
        height=400,
        title="📊 Class Average per Subject"
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("⚠️ No students available to visualize yet.")



theme = st.get_option("theme.base")
if theme == "dark":
    st.write("🌙 Dark mode is active")
else:
    st.write("🌞 Light mode is active")