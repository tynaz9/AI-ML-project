import streamlit as st
from backend.ai_engine import get_response_from_ollama
from backend.classroom import list_courses, get_assignments, get_classroom_service
from backend.vector_store import embed_and_upload_assignments, search_similar_assignments


st.set_page_config(page_title="EduTutor AI", page_icon="🎓")
st.title("🎓 EduTutor AI (Powered by Ollama & Google Classroom)")

st.markdown("""
Welcome to **EduTutor AI**!  
Ask academic questions and explore your synced Google Classroom data.
""")

# ----------------- AI Chat Section -----------------
st.header("💬 Ask EduTutor AI")
query = st.text_input("📚 What would you like to learn or ask about?")

if query:
    with st.spinner("Thinking..."):
        response = get_response_from_ollama(query)

    if response:
        st.success(response)
    else:
        st.error("No response received from the AI.")

st.markdown("---")

# ----------------- Google Classroom Section -----------------
st.header("📘 Google Classroom Sync")

# Sync and display Google Classroom Courses
if st.button("🔄 Sync Courses"):
    with st.spinner("Fetching courses..."):
        try:
            course_names = list_courses()
            if course_names:
                st.session_state.courses = course_names
                st.success("Courses synced!")
            else:
                st.warning("No courses found.")
        except Exception as e:
            st.error(f"Error syncing: {e}")

# Show dropdown if courses are loaded
if "courses" in st.session_state:
    selected_course = st.selectbox("Select a course to view assignments:", st.session_state.courses)

    if selected_course and st.button("📄 Show Assignments"):
        try:
            # Get actual course ID by name
            service = get_classroom_service()
            course_list = service.courses().list().execute().get("courses", [])
            course_id = next((c['id'] for c in course_list if c['name'] == selected_course), None)

            if course_id:
                assignments = get_assignments(course_id)
                if assignments:
                    st.subheader("📋 Assignments:")
                    for a in assignments:
                        st.write("•", a)
                else:
                    st.info("No assignments found.")
            else:
                st.warning("Could not find course ID.")
        except Exception as e:
            st.error(f"Failed to get assignments: {e}")
st.header("🔎 Ask Based on Your Assignments")
query2 = st.text_input("Type a question related to your assignments:")

if query2 and st.button("🧠 Ask with Context"):
    try:
        similar = search_similar_assignments(query2)
        st.subheader("📚 Related Assignments:")
        for item in similar:
            st.markdown(f"• {item}")

        context = "\n".join(similar)
        full_prompt = f"Based on the following assignments:\n{context}\n\nAnswer this question:\n{query2}"
        ai_response = get_response_from_ollama(full_prompt)
        st.success(ai_response)
    except Exception as e:
        st.error(f"Search failed: {e}")

