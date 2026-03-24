import streamlit as st
import bcrypt
from database import engine, SessionLocal, Base
from models import Task, User

# Create tables
Base.metadata.create_all(bind=engine)

session = SessionLocal()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- SUCCESS MESSAGE ----------------
if "msg" in st.session_state:
    st.success(st.session_state.msg)
    del st.session_state.msg

# ---------------- LOGIN ----------------
def login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = session.query(User).filter(User.username == username).first()
        if user:
            # Check hashed password
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")
        else:
            st.error("Invalid Credentials")

# ---------------- SIGNUP ----------------
def signup():
    st.title("Signup")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Signup"):
        existing_user = session.query(User).filter(User.username == new_user).first()
        if existing_user:
            st.warning("Username already exists")
        elif new_user == "" or new_pass == "":
            st.warning("Fields cannot be empty")
        else:
            # Hash password
            hashed_pass = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
            user = User(username=new_user, password=hashed_pass.decode('utf-8'))
            session.add(user)
            session.commit()
            st.success("Account created! Go to Login")

# ---------------- LOGOUT ----------------
def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- MAIN APP ----------------
def main_app():
    st.image(
        "https://www.shutterstock.com/image-vector/task-management-web-banner-icon-260nw-2733289787.jpg",
        width=500
    )
    st.title(f"Welcome {st.session_state.username} 👋")

    menu = st.sidebar.selectbox(
        "Menu",
        ["Add Task", "View Tasks", "Update Status", "Edit Task", "Delete Task"]
    )

    # ---------------- ADD TASK ----------------
    if menu == "Add Task":
        st.subheader("Add New Task")

        title = st.text_input("Title")
        description = st.text_area("Description")
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])

        if st.button("Add Task"):
            if title.strip() == "":
                st.warning("Title cannot be empty")
            else:
                new_task = Task(
                    title=title,
                    description=description,
                    status=status,
                    priority=priority
                )
                session.add(new_task)
                session.commit()

                st.session_state.msg = "Task Added Successfully"
                st.rerun()

    # ---------------- VIEW TASKS ----------------
    elif menu == "View Tasks":
        st.subheader("All Tasks")
        tasks = session.query(Task).all()

        if tasks:
            for t in tasks:
                st.write(f"ID: {t.id} | {t.title} | {t.status} | {t.priority}")
        else:
            st.warning("No tasks available")

    # ---------------- UPDATE STATUS ----------------
    elif menu == "Update Status":
        st.subheader("Update Task Status")
        tasks = session.query(Task).all()

        if tasks:
            ids = [t.id for t in tasks]
            task_id = st.selectbox("Select Task ID", ids)
            new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"])

            if st.button("Update Status"):
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = new_status
                    session.commit()

                    st.session_state.msg = "Status Updated Successfully"
                    st.rerun()
        else:
            st.warning("No tasks available")

    # ---------------- EDIT TASK ----------------
    elif menu == "Edit Task":
        st.subheader("Edit Task")
        tasks = session.query(Task).all()

        if tasks:
            ids = [t.id for t in tasks]
            task_id = st.selectbox("Select Task ID", ids)

            task = session.query(Task).filter(Task.id == task_id).first()

            title = st.text_input("Title", task.title)
            description = st.text_area("Description", task.description)
            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"],
                index=["Low", "Medium", "High"].index(task.priority)
            )
            status = st.selectbox(
                "Status",
                ["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(task.status)
            )

            if st.button("Update Task"):
                task.title = title
                task.description = description
                task.priority = priority
                task.status = status
                session.commit()

                st.session_state.msg = "Task Updated Successfully"
                st.rerun()
        else:
            st.warning("No tasks available")

    # ---------------- DELETE TASK ----------------
    elif menu == "Delete Task":
        st.subheader("Delete Task")
        tasks = session.query(Task).all()

        if tasks:
            ids = [t.id for t in tasks]
            task_id = st.selectbox("Select Task ID", ids)

            if st.button("Delete Task"):
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    session.delete(task)
                    session.commit()

                    st.session_state.msg = "Task Deleted Successfully"
                    st.rerun()
        else:
            st.warning("No tasks available")

# ---------------- ROUTING ----------------
if not st.session_state.logged_in:
    choice = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    if choice == "Login":
        login()
    else:
        signup()
else:
    logout()
    main_app()