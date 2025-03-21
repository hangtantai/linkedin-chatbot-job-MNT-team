import streamlit as st
class Config:
    _config = {
        "email": st.secrets["EMAIL"],
        "password": st.secrets["PASSWORD"],
        "search_link": "https://www.linkedin.com/jobs/search/?currentJobId=4169177152&distance=25&f_E=1&geoId=104195383&keywords=data%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
        "link_file": 'output.txt',
        "detail_file": "details.txt",
        "job_data": "job_data.csv",
        "bucket_name": st.secrets["S3_BUCKET_JOB"],
        "domain_login": "https://linkedin.com/login",
        "domain_logout": "https://www.linkedin.com/m/logout/",
        "domain": "https://www.linkedin.com",
        "s3_bucket": st.secrets["S3_BUCKET_JOB"],
        "ul_class": "ul.artdeco-pagination__pages",
        "li_class": ".//li[@data-test-pagination-page-btn]",
        "btn_class": "data-test-pagination-page-btn",
        "li_active": ".//li[contains(@class, 'active')]"
    }

    @classmethod
    def get_config(cls):
        """Get general configuration values"""
        return cls._config.copy()