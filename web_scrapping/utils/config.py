import streamlit as st
class Config:
    _config = {
        "email": st.secrets["EMAIL"],
        "password": st.secrets["PASSWORD"],
        "search_link": "https://www.linkedin.com/jobs/search/?currentJobId=4199415386&geoId=103697962&keywords=AI%20Engineer&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
        "link_file": 'output.txt',
        "detail_file": "details.txt",
        "job_data": "job_data.csv",
        "host_aiven":st.secrets["HOST_AIVEN"],
        "port_aiven":st.secrets["PORT_AIVEN"],
        "user_aiven":st.secrets["USER_AIVEN"],
        "password_aiven":st.secrets["PASSWORD_AIVEN"],
        "bucket_name": st.secrets["S3_BUCKET_JOB"],
        "domain_login": "https://linkedin.com/login",
        "domain_logout": "https://www.linkedin.com/m/logout/",
        "domain": "https://www.linkedin.com",
        "s3_bucket": st.secrets["S3_BUCKET_JOB"],
        "ul_class": "ul.artdeco-pagination__pages",
        "li_class": ".//li[@data-test-pagination-page-btn]",
        "btn_class": "data-test-pagination-page-btn",
        "li_active": ".//li[contains(@class, 'active')]",
    }

    @classmethod
    def get_config(cls):
        """Get general configuration values"""
        return cls._config.copy()