from datetime import datetime, timedelta

import streamlit as st


def generate_summary(data):
    summary = f"Summary for {data['profileInfo']['firstName']} {data['profileInfo']['lastName']}:\n"
    summary += f"Email: {data['profileInfo']['email']}\n"
    summary += f"Atlassian - Confluence: {data['atlassianInfo']['confluenceUsername']}, Jira: {data['atlassianInfo']['jiraUsername']}\n"
    summary += f"GitHub Username: {data['githubInfo']['username']}\n"
    summary += (
        f"Time Range: {data['timeRange']['start']} to {data['timeRange']['end']}\n"
    )
    return summary


st.set_page_config(page_title="PathForge Employee Assistant", layout="wide")


def create_section(title, color):
    st.markdown(
        f"""
    <style>
        .section-{color} {{
            background-color: {color};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )
    return st.container()


def create_box(content, color):
    st.markdown(
        f"""
    <style>
        .box-{color} {{
            background-color: {color};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
    </style>
    <div class="box-{color}">{content}</div>
    """,
        unsafe_allow_html=True,
    )


def main():
    st.markdown(
        """
    <style>
    .title-container {
        background: linear-gradient(to right, #4e54c8, #8f94fb);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .title {
        color: white;
        text-align: center;
        font-size: 3em;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(to right, #4e54c8, #8f94fb);
        color: white;
        border: none;
        padding: 0.5em 1em;
        font-size: 1.25em;
        font-weight: bold;
        border-radius: 5px;
        cursor: pointer;
        transition: opacity 0.3s;
    }
    .stButton > button:hover {
        opacity: 0.8;
    }
    .stButton > button:disabled {
        background: #cccccc;
        cursor: not-allowed;
    }
    input, select {
        tab-index: 0;
    }
    .error-message {
        color: red;
        margin-top: 5px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="title-container"><h1 class="title">PathForge Employee Assistant</h1></div>',
        unsafe_allow_html=True,
    )

    # Initialize session state for form fields
    if "form_fields" not in st.session_state:
        st.session_state.form_fields = {
            "first_name": "",
            "last_name": "",
            "email": "",
            "confluence_username": "",
            "jira_username": "",
            "atlassian_api_token": "",
            "github_username": "",
            "github_token": "",
            "selected_range": "Last year",
            "start_date": None,
            "end_date": None,
        }

    if "date_error" not in st.session_state:
        st.session_state.date_error = None

    with create_section("User Information", "#f0f0f0"):
        st.header("User Information")

        with st.container():
            create_box(
                """
            <h3 style='margin-top: 0;'>Profile Information</h3>
            """,
                "#e6f2ff",
            )
            st.session_state.form_fields["first_name"] = st.text_input(
                "First Name",
                value=st.session_state.form_fields["first_name"],
                key="first_name",
            )
            st.session_state.form_fields["last_name"] = st.text_input(
                "Last Name",
                value=st.session_state.form_fields["last_name"],
                key="last_name",
            )
            st.session_state.form_fields["email"] = st.text_input(
                "Email", value=st.session_state.form_fields["email"], key="email"
            )

        with st.container():
            create_box(
                """
            <h3 style='margin-top: 0;'>Atlassian Information</h3>
            """,
                "#e6ffe6",
            )
            st.session_state.form_fields["confluence_username"] = st.text_input(
                "Confluence Username",
                value=st.session_state.form_fields["confluence_username"],
                key="confluence_username",
            )
            st.session_state.form_fields["jira_username"] = st.text_input(
                "Jira Username",
                value=st.session_state.form_fields["jira_username"],
                key="jira_username",
            )
            st.session_state.form_fields["atlassian_api_token"] = st.text_input(
                "Atlassian API Token",
                type="password",
                value=st.session_state.form_fields["atlassian_api_token"],
                key="atlassian_api_token",
            )

        with st.container():
            create_box(
                """
            <h3 style='margin-top: 0;'>GitHub Information</h3>
            """,
                "#fff2e6",
            )
            st.session_state.form_fields["github_username"] = st.text_input(
                "GitHub Username",
                value=st.session_state.form_fields["github_username"],
                key="github_username",
            )
            st.session_state.form_fields["github_token"] = st.text_input(
                "GitHub Token",
                type="password",
                value=st.session_state.form_fields["github_token"],
                key="github_token",
            )

    with create_section("Time Range", "#f2e6ff"):
        st.header("Time Range")

        today = datetime.now().date()
        default_start = today - timedelta(days=365)
        two_years_ago = today - timedelta(days=730)

        time_range_options = {
            "Last week": (today - timedelta(days=7), today),
            "Last month": (today - timedelta(days=30), today),
            "Last quarter": (today - timedelta(days=90), today),
            "Last half year": (today - timedelta(days=180), today),
            "Last year": (today - timedelta(days=365), today),
            "Custom": (default_start, today),
        }

        st.session_state.form_fields["selected_range"] = st.selectbox(
            "Select Time Range", list(time_range_options.keys()), key="selected_range"
        )

        if st.session_state.form_fields["selected_range"] == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.form_fields["start_date"] = st.date_input(
                    "Start Date",
                    value=default_start,
                    min_value=two_years_ago,
                    max_value=today,
                    key="start_date",
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=today,
                    min_value=two_years_ago,
                    max_value=today,
                    key="end_date",
                )
                if end_date > today:
                    st.session_state.date_error = "Error: End date cannot be in the future. Please select a valid date."
                    st.session_state.form_fields["end_date"] = None
                else:
                    st.session_state.form_fields["end_date"] = end_date
                    st.session_state.date_error = None

            # Display error message if exists
            if st.session_state.date_error:
                st.markdown(
                    f'<p class="error-message">{st.session_state.date_error}</p>',
                    unsafe_allow_html=True,
                )

            # Validate custom date range
            if (
                st.session_state.form_fields["start_date"]
                and st.session_state.form_fields["end_date"]
                and st.session_state.form_fields["start_date"]
                > st.session_state.form_fields["end_date"]
            ):
                st.session_state.date_error = "Error: Start date must be before end date. Please adjust the dates."
                st.markdown(
                    f'<p class="error-message">{st.session_state.date_error}</p>',
                    unsafe_allow_html=True,
                )
            elif not st.session_state.date_error:
                st.session_state.date_error = None

        else:
            (
                st.session_state.form_fields["start_date"],
                st.session_state.form_fields["end_date"],
            ) = time_range_options[st.session_state.form_fields["selected_range"]]
            st.session_state.date_error = None

        # Ensure start date is not more than 2 years ago
        if st.session_state.form_fields["start_date"]:
            st.session_state.form_fields["start_date"] = max(
                st.session_state.form_fields["start_date"], two_years_ago
            )

        if (
            st.session_state.form_fields["start_date"]
            and st.session_state.form_fields["end_date"]
            and not st.session_state.date_error
        ):
            st.write(
                f"Selected range: {st.session_state.form_fields['start_date']} to {st.session_state.form_fields['end_date']}"
            )

    # Check if all fields are filled and there are no date errors
    all_fields_filled = (
        all(st.session_state.form_fields.values()) and not st.session_state.date_error
    )

    # Disable the button if not all fields are filled or there are date errors
    button_disabled = not all_fields_filled

    if st.button("Generate Summary", disabled=button_disabled):
        data = {
            "profileInfo": {
                "firstName": st.session_state.form_fields["first_name"],
                "lastName": st.session_state.form_fields["last_name"],
                "email": st.session_state.form_fields["email"],
            },
            "atlassianInfo": {
                "confluenceUsername": st.session_state.form_fields[
                    "confluence_username"
                ],
                "jiraUsername": st.session_state.form_fields["jira_username"],
                "atlassianApiToken": st.session_state.form_fields[
                    "atlassian_api_token"
                ],
            },
            "githubInfo": {
                "username": st.session_state.form_fields["github_username"],
                "token": st.session_state.form_fields["github_token"],
            },
            "timeRange": {
                "start": st.session_state.form_fields["start_date"].isoformat(),
                "end": st.session_state.form_fields["end_date"].isoformat(),
            },
        }

        summary = generate_summary(data)

        with create_section("Summary", "#e6e6e6"):
            st.header("Summary")
            st.text_area("", summary, height=200)
    elif button_disabled:
        st.warning(
            "Please fill in all fields and resolve any date errors before generating the summary."
        )


if __name__ == "__main__":
    main()
